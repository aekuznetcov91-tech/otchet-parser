import os
import sys
import json
import re
from collections import defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from scripts.oem_kam_resolver import clean_inn, normalize_kam, clean_key

def generate_kam_partners_excel():
    print("=" * 70)
    print("[*] Генерация файла закрепления партнеров по КАМ для передачи на проверку...")
    print("=" * 70)

    data_json_path = os.path.join(PROJECT_ROOT, 'site', 'data.json')
    with open(data_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    partners_reg = data.get('partners_registry', [])
    sys_db_p = data.get('sys_db_partners', [])

    # 1. Загружаем детальные записи из OEM (15)
    oem_file = os.path.join(PROJECT_ROOT, 'raw_data', 'OEM СберАвто финал (15).xlsx')
    wb_oem = openpyxl.load_workbook(oem_file, data_only=True)
    oem_rows = []

    for sname in wb_oem.sheetnames:
        ws = wb_oem[sname]
        headers = []
        resp_col, inn_col, name_col, city_col, brand_col = -1, -1, -1, -1, -1
        header_row = -1

        for r_idx, row in enumerate(ws.iter_rows(values_only=True)):
            if not any(row):
                continue
            r_str = ' '.join(str(c) for c in row if c).lower()
            if 'ответственный' in r_str or 'кам' in r_str:
                header_row = r_idx
                headers = [str(c or '').strip().lower() for c in row]
                for idx, h in enumerate(headers):
                    if 'ответственн' in h or h == 'кам':
                        resp_col = idx
                    elif 'инн' in h and inn_col == -1:
                        inn_col = idx
                    elif any(x in h for x in ['дилер', 'дц', 'партнер', 'юл', 'название', 'холдинг']) and name_col == -1:
                        name_col = idx
                    elif 'город' in h and city_col == -1:
                        city_col = idx
                    elif 'бренд' in h and brand_col == -1:
                        brand_col = idx
                break

        if resp_col == -1:
            continue

        sheet_brand = sname.split('&')[0].strip().upper()

        for row in ws.iter_rows(min_row=header_row + 2, values_only=True):
            if not any(row):
                continue
            resp = str(row[resp_col] or '').strip() if resp_col < len(row) else ''
            if not resp:
                continue
            kam = normalize_kam(resp)
            if kam == 'Не назначен':
                continue

            inn = clean_inn(row[inn_col]) if inn_col != -1 and inn_col < len(row) else ''
            dc_name = str(row[name_col] or '').strip() if name_col != -1 and name_col < len(row) else ''
            city = str(row[city_col] or '').strip() if city_col != -1 and city_col < len(row) else ''
            brand = str(row[brand_col] or '').strip() if brand_col != -1 and brand_col < len(row) else sheet_brand
            if not brand or brand.lower() == 'none':
                brand = sheet_brand

            oem_rows.append({
                'kam': kam,
                'inn': inn,
                'dc_name': dc_name,
                'city': city,
                'brand': brand,
                'source': 'OEM (15)'
            })

    wb_oem.close()
    print(f"[*] Считано записей ДЦ из OEM (15): {len(oem_rows)}")

    # 2. Агрегируем сентябрьские сделки и авансы по КАМ + Партнеру + ИНН
    # (kam, partner_name, inn) -> {'sales': count, 'prepays': count, 'brands': set(), 'cities': set(), 'raw_names': set()}
    sep_stats = defaultdict(lambda: {'sales': 0, 'prepays': 0, 'brands': set(), 'cities': set(), 'raw_names': set()})

    for r in sys_db_p:
        if r.get('Month') == '2026-09':
            kam = normalize_kam(r.get('KAM', 'Не назначен'))
            p_name = r.get('Partner') or r.get('RawPartner') or 'Не указан'
            raw_p = r.get('RawPartner') or ''
            t = r.get('Type')
            b = r.get('Brand') or ''
            c = r.get('City') or ''

            key = (kam, p_name)
            if t == 'Сделка':
                sep_stats[key]['sales'] += 1
            elif t == 'Аванс':
                sep_stats[key]['prepays'] += 1

            if b:
                sep_stats[key]['brands'].add(b)
            if c:
                sep_stats[key]['cities'].add(c)
            if raw_p:
                sep_stats[key]['raw_names'].add(raw_p)

    # 3. Формируем единый реестр партнеров и ДЦ по каждому КАМу
    kams_order = [
        'Андрей Кузнецов',
        'Алексей Чихарев',
        'Евгения Добролюбова',
        'Светлана Дариенко',
        'Валерия Солдатова'
    ]

    kam_data = defaultdict(list)
    seen_dc = set()

    # Сначала добавляем все ДЦ из эталонного OEM (15)
    for r in oem_rows:
        kam = r['kam']
        inn = r['inn']
        dc_name = r['dc_name']
        city = r['city']
        brand = r['brand']

        # Ищем совпадение сделок в сентябре по названию или ключевым словам
        sales_cnt = 0
        prepays_cnt = 0
        matched_partner = ''

        for (s_kam, s_pname), st in sep_stats.items():
            if s_kam == kam:
                # Проверяем пересечение
                if (dc_name and dc_name.lower() in s_pname.lower()) or (s_pname.lower() in dc_name.lower()) or any(dc_name.lower() in rn.lower() for rn in st['raw_names']):
                    sales_cnt += st['sales']
                    prepays_cnt += st['prepays']
                    matched_partner = s_pname
                    break

        kam_data[kam].append({
            'partner': matched_partner or dc_name,
            'dc_name': dc_name,
            'inn': inn,
            'city': city,
            'brand': brand,
            'sales_sep': sales_cnt,
            'prepays_sep': prepays_cnt,
            'total_sep': sales_cnt + prepays_cnt,
            'source': 'OEM СберАвто финал (15)'
        })
        seen_dc.add((kam, inn, dc_name.lower(), brand.lower()))

    # Затем дополняем партнерами из сентябрьских сделок, которых не было в явном виде в OEM (15)
    for (s_kam, s_pname), st in sep_stats.items():
        if s_kam in kams_order:
            # Проверяем, есть ли уже такой партнер у этого КАМа
            already = any(s_pname.lower() in row['partner'].lower() or s_pname.lower() in row['dc_name'].lower() for row in kam_data[s_kam])
            if not already:
                kam_data[s_kam].append({
                    'partner': s_pname,
                    'dc_name': ', '.join(list(st['raw_names'])[:2]) if st['raw_names'] else s_pname,
                    'inn': '',
                    'city': ', '.join(list(st['cities'])[:2]) if st['cities'] else 'РФ',
                    'brand': ', '.join(list(st['brands'])[:3]) if st['brands'] else 'Новые авто',
                    'sales_sep': st['sales'],
                    'prepays_sep': st['prepays'],
                    'total_sep': st['sales'] + st['prepays'],
                    'source': 'Сделки Сентябрь 2026 (Битрикс)'
                })

    # Сортируем записи каждого КАМа: сначала активные в сентябре по убыванию сделок, затем остальные по алфавиту
    for kam in kams_order:
        kam_data[kam].sort(key=lambda x: (-x['total_sep'], -x['sales_sep'], x['partner'].lower()))

    # 4. Создаем Excel книгу
    wb = openpyxl.Workbook()
    # Удаляем дефолтный лист
    wb.remove(wb.active)

    # Стили
    font_title = Font(name='Calibri', size=16, bold=True, color='1F497D')
    font_subtitle = Font(name='Calibri', size=11, italic=True, color='595959')
    font_header = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    font_data = Font(name='Calibri', size=11)
    font_total = Font(name='Calibri', size=11, bold=True)

    fill_header = PatternFill(start_color='1F497D', end_color='1F497D', fill_type='solid')
    fill_summary_hdr = PatternFill(start_color='2C5E8A', end_color='2C5E8A', fill_type='solid')
    fill_zebra = PatternFill(start_color='F9FAFB', end_color='F9FAFB', fill_type='solid')
    fill_active = PatternFill(start_color='E8F5E9', end_color='E8F5E9', fill_type='solid') # светло-зеленый для активных

    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    header_border = Border(
        left=Side(style='thin', color='FFFFFF'),
        right=Side(style='thin', color='FFFFFF'),
        top=Side(style='medium', color='1F497D'),
        bottom=Side(style='medium', color='1F497D')
    )

    # ---------------------------------------------------------------------
    # ВКЛАДКА 1: СВОДКА
    # ---------------------------------------------------------------------
    ws_summary = wb.create_sheet(title="Сводка по КАМ")
    ws_summary.views.sheetView[0].showGridLines = True

    ws_summary['A1'] = "СВОДНЫЙ ОТЧЕТ ЗАКРЕПЛЕНИЯ ПАРТНЕРОВ ПО КАМ МЕНЕДЖЕРАМ"
    ws_summary['A1'].font = font_title
    ws_summary['A2'] = "Сформировано на основе эталонного файла OEM СберАвто финал (15) и данных за Сентябрь 2026"
    ws_summary['A2'].font = font_subtitle

    summary_headers = [
        "№",
        "КАМ менеджер",
        "Всего дилеров / ДЦ",
        "Сделок (Сентябрь 2026)",
        "Авансов (Сентябрь 2026)",
        "Всего операций (Сентябрь 2026)",
        "Ключевые закрепленные холдинги и бренды"
    ]

    for col_idx, h in enumerate(summary_headers, start=1):
        cell = ws_summary.cell(row=4, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_summary_hdr
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = header_border
    ws_summary.row_dimensions[4].height = 28

    kam_key_brands = {
        'Андрей Кузнецов': 'АО «РОЛЬФ», ГК «АГАТ», Автомир, Fresh Auto',
        'Алексей Чихарев': 'ТЦ «Кунцево Лимитед», Автокласс, У Сервис+, Фаворит, Автопассаж',
        'Евгения Добролюбова': 'Нижегородец, ТСАЦ Июль, ГК Башавтоком, ТД Армада-Авто, Юникор, Самара-Лада, Дав-Авто, Сатурн-Р',
        'Светлана Дариенко': 'Автохолдинг Максимум, Вагнер Авто (СПб), Прагматика, Моторленд, Автолига, Дюк и К',
        'Валерия Солдатова': 'ГК Авторитэйл М (Юг), Темп Авто, Боравто, Леон Авто, ГК Глобус, Олимп Кубань'
    }

    sum_row = 5
    total_dcs = 0
    total_sales = 0
    total_prepays = 0
    total_ops = 0

    for idx, kam in enumerate(kams_order, start=1):
        rows = kam_data[kam]
        cnt_dc = len(rows)
        # Подсчитаем сделки сентября для этого КАМ из sep_stats
        s_cnt = sum(st['sales'] for (s_kam, _), st in sep_stats.items() if s_kam == kam)
        p_cnt = sum(st['prepays'] for (s_kam, _), st in sep_stats.items() if s_kam == kam)
        tot_cnt = s_cnt + p_cnt

        total_dcs += cnt_dc
        total_sales += s_cnt
        total_prepays += p_cnt
        total_ops += tot_cnt

        ws_summary.cell(row=sum_row, column=1, value=idx).alignment = Alignment(horizontal='center')
        ws_summary.cell(row=sum_row, column=2, value=kam).font = Font(name='Calibri', size=11, bold=True)
        ws_summary.cell(row=sum_row, column=3, value=cnt_dc).alignment = Alignment(horizontal='right')
        ws_summary.cell(row=sum_row, column=4, value=s_cnt).alignment = Alignment(horizontal='right')
        ws_summary.cell(row=sum_row, column=5, value=p_cnt).alignment = Alignment(horizontal='right')
        ws_summary.cell(row=sum_row, column=6, value=tot_cnt).alignment = Alignment(horizontal='right')
        ws_summary.cell(row=sum_row, column=7, value=kam_key_brands.get(kam, ''))

        for c in range(1, 8):
            ws_summary.cell(row=sum_row, column=c).border = thin_border
            if idx % 2 == 0:
                ws_summary.cell(row=sum_row, column=c).fill = fill_zebra
        ws_summary.row_dimensions[sum_row].height = 22
        sum_row += 1

    # Итоговая строка в сводке
    ws_summary.cell(row=sum_row, column=1, value="")
    ws_summary.cell(row=sum_row, column=2, value="ИТОГО").font = font_total
    ws_summary.cell(row=sum_row, column=3, value=total_dcs).font = font_total
    ws_summary.cell(row=sum_row, column=3).alignment = Alignment(horizontal='right')
    ws_summary.cell(row=sum_row, column=4, value=total_sales).font = font_total
    ws_summary.cell(row=sum_row, column=4).alignment = Alignment(horizontal='right')
    ws_summary.cell(row=sum_row, column=5, value=total_prepays).font = font_total
    ws_summary.cell(row=sum_row, column=5).alignment = Alignment(horizontal='right')
    ws_summary.cell(row=sum_row, column=6, value=total_ops).font = font_total
    ws_summary.cell(row=sum_row, column=6).alignment = Alignment(horizontal='right')
    ws_summary.cell(row=sum_row, column=7, value="").font = font_total

    for c in range(1, 8):
        ws_summary.cell(row=sum_row, column=c).border = Border(top=Side(style='thin'), bottom=Side(style='double'))
    ws_summary.row_dimensions[sum_row].height = 24

    # ---------------------------------------------------------------------
    # ВКЛАДКИ ДЛЯ КАЖДОГО КАМ
    # ---------------------------------------------------------------------
    table_headers = [
        "№",
        "Партнер / Холдинг",
        "Дилерский центр / ДЦ",
        "ИНН",
        "Город",
        "Бренд",
        "Сделок (Сентябрь)",
        "Авансов (Сентябрь)",
        "Всего операций",
        "Источник привязки"
    ]

    for kam in kams_order:
        ws_kam = wb.create_sheet(title=kam)
        ws_kam.views.sheetView[0].showGridLines = True

        ws_kam['A1'] = f"ЗАКРЕПЛЕННЫЕ ПАРТНЕРЫ И ДЦ: {kam.upper()}"
        ws_kam['A1'].font = font_title
        ws_kam['A2'] = f"Всего объектов в портфеле: {len(kam_data[kam])} ДЦ. Источник: OEM СберАвто финал (15)"
        ws_kam['A2'].font = font_subtitle

        for col_idx, h in enumerate(table_headers, start=1):
            cell = ws_kam.cell(row=4, column=col_idx, value=h)
            cell.font = font_header
            cell.fill = fill_header
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = header_border
        ws_kam.row_dimensions[4].height = 28

        curr_row = 5
        kam_rows = kam_data[kam]

        for idx, r in enumerate(kam_rows, start=1):
            ws_kam.cell(row=curr_row, column=1, value=idx).alignment = Alignment(horizontal='center')
            ws_kam.cell(row=curr_row, column=2, value=r['partner'])
            ws_kam.cell(row=curr_row, column=3, value=r['dc_name'])
            ws_kam.cell(row=curr_row, column=4, value=r['inn']).alignment = Alignment(horizontal='center')
            ws_kam.cell(row=curr_row, column=5, value=r['city'])
            ws_kam.cell(row=curr_row, column=6, value=r['brand'])
            ws_kam.cell(row=curr_row, column=7, value=r['sales_sep']).alignment = Alignment(horizontal='right')
            ws_kam.cell(row=curr_row, column=8, value=r['prepays_sep']).alignment = Alignment(horizontal='right')
            ws_kam.cell(row=curr_row, column=9, value=r['total_sep']).alignment = Alignment(horizontal='right')
            ws_kam.cell(row=curr_row, column=10, value=r['source'])

            for c in range(1, 11):
                cell = ws_kam.cell(row=curr_row, column=c)
                cell.border = thin_border
                if r['total_sep'] > 0:
                    cell.fill = fill_active
                elif idx % 2 == 0:
                    cell.fill = fill_zebra

            ws_kam.row_dimensions[curr_row].height = 20
            curr_row += 1

        # Итоговая строка
        ws_kam.cell(row=curr_row, column=1, value="")
        ws_kam.cell(row=curr_row, column=2, value="ИТОГО").font = font_total
        ws_kam.cell(row=curr_row, column=3, value=f"{len(kam_rows)} объектов").font = font_total
        ws_kam.cell(row=curr_row, column=7, value=f"=SUM(G5:G{curr_row-1})").font = font_total
        ws_kam.cell(row=curr_row, column=7).alignment = Alignment(horizontal='right')
        ws_kam.cell(row=curr_row, column=8, value=f"=SUM(H5:H{curr_row-1})").font = font_total
        ws_kam.cell(row=curr_row, column=8).alignment = Alignment(horizontal='right')
        ws_kam.cell(row=curr_row, column=9, value=f"=SUM(I5:I{curr_row-1})").font = font_total
        ws_kam.cell(row=curr_row, column=9).alignment = Alignment(horizontal='right')

        for c in range(1, 11):
            ws_kam.cell(row=curr_row, column=c).border = Border(top=Side(style='thin'), bottom=Side(style='double'))
        ws_kam.row_dimensions[curr_row].height = 24

        # Автофильтр
        ws_kam.auto_filter.ref = f"A4:J{curr_row-1}"

    # Автоподбор ширины колонок для всех листов
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.row in [1, 2]:
                    continue
                v = str(cell.value or '')
                if v.startswith('='):
                    v = '12345'
                max_len = max(max_len, len(v))
            sheet.column_dimensions[col_letter].width = max(max_len + 3, 11)

    ws_summary.column_dimensions['A'].width = 6
    ws_summary.column_dimensions['B'].width = 24
    ws_summary.column_dimensions['C'].width = 20
    ws_summary.column_dimensions['D'].width = 24
    ws_summary.column_dimensions['E'].width = 24
    ws_summary.column_dimensions['F'].width = 28
    ws_summary.column_dimensions['G'].width = 45

    # Сохранение файла в Downloads и в корень проекта
    filename = "Закрепление_партнеров_по_КАМ_Сентябрь_2026.xlsx"
    downloads_dir = os.path.expanduser('~/Downloads')
    downloads_path = os.path.join(downloads_dir, filename)
    root_path = os.path.join(PROJECT_ROOT, filename)

    try:
        wb.save(downloads_path)
        print(f"[+] Успешно сохранен в Downloads: {downloads_path}")
    except Exception as e:
        print(f"[!] Предупреждение при сохранении в Downloads ({e}), сохраняем с суффиксом 'актуально'...")
        alt_path = os.path.join(downloads_dir, "Закрепление_партнеров_по_КАМ_Сентябрь_2026_актуально.xlsx")
        try:
            wb.save(alt_path)
            print(f"[+] Успешно сохранен в Downloads: {alt_path}")
        except Exception as e2:
            print(f"[!] Ошибка сохранения в Downloads: {e2}")

    try:
        wb.save(root_path)
        print(f"[+] Успешно сохранена копия в проекте: {root_path}")
    except Exception as e:
        print(f"[!] Предупреждение при сохранении в проекте: {e}")

    print("=" * 70)
    print("✅ ФАЙЛ УСПЕШНО СФОРМИРОВАН!")
    print("=" * 70)
    return downloads_path

if __name__ == '__main__':
    generate_kam_partners_excel()
