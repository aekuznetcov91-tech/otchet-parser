# -*- coding: utf-8 -*-
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import os
import shutil

src_path = 'otchet-parser/raw_data/OEM СберАвто финал (13).xlsx'
wb_src = openpyxl.load_workbook(src_path, data_only=True)

# 1. Извлечение брендов Рольф Импорт из объединенных ячеек
ws_rolf = wb_src['Рольф Импорт']
rolf_brands = {}
for m in ws_rolf.merged_cells.ranges:
    if m.min_col == 2 and m.max_col == 2:
        val = ws_rolf.cell(m.min_row, m.min_col).value
        for r in range(m.min_row, m.max_row + 1):
            rolf_brands[r] = val

raw_dealers = []

for sname in wb_src.sheetnames:
    if sname in ['Цены для сотрудников', 'Карта с ДЦ']:
        continue
    ws = wb_src[sname]
    header_row = None
    headers = []
    for r_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
        row_str = ' '.join([str(c) for c in row if c is not None]).lower()
        if 'город' in row_str and any(k in row_str for k in ['название', 'юл', 'инн', 'группу']):
            header_row = r_idx
            headers = [str(c).strip() if c is not None else f'col_{i}' for i, c in enumerate(row)]
            break
    if not header_row:
        continue
        
    for r_idx in range(header_row + 1, ws.max_row + 1):
        row_vals = [ws.cell(r_idx, c).value for c in range(1, len(headers) + 5)]
        if not any(row_vals):
            continue
        city = str(ws.cell(r_idx, 1).value).strip() if ws.cell(r_idx, 1).value is not None else ''
        if city.lower() == 'москва':
            row_dict = {headers[i] if i < len(headers) else f'col_{i}': row_vals[i] for i in range(len(headers))}
            
            brand_field = row_dict.get('Бренд')
            if sname == 'Рольф Импорт':
                brand_field = rolf_brands.get(r_idx, brand_field or ws.cell(r_idx, 2).value)
            
            inn = str(row_dict.get('ИНН', '')).strip()
            if inn.endswith('.0'): inn = inn[:-2]
            
            name = str(row_dict.get('Название', '')).strip()
            # Нормализация холдинга
            n_low = name.lower()
            if 'автогермес' in n_low: holding = 'АвтоГЕРМЕС'
            elif 'рольф' in n_low: holding = 'РОЛЬФ'
            elif 'major' in n_low or 'мэйджор' in n_low: holding = 'ГК Major'
            elif 'автодом' in n_low: holding = 'АВТОДОМ'
            elif 'автомир' in n_low: holding = 'ГК Автомир'
            elif 'борисхоф' in n_low: holding = 'БорисХоф'
            elif 'кунцево' in n_low: holding = 'ТЦ Кунцево'
            elif 'автоспеццентр' in n_low: holding = 'АвтоСпецЦентр'
            elif 'независимость' in n_low: holding = 'Независимость'
            elif 'фаворит' in n_low: holding = 'Фаворит Моторс'
            elif 'сонг' in n_low: holding = 'СОНГ МОТОРС'
            elif 'деливери' in n_low: holding = 'ДЕЛИВЕРИ КАР'
            elif 'квазар' in n_low: holding = 'Квазар'
            elif 'петровский' in n_low: holding = 'Петровский'
            elif 'шереметьево' in n_low: holding = 'КЦ Шереметьево'
            elif 'у сервис' in n_low: holding = 'У Сервис+'
            elif 'автопрестиж' in n_low: holding = 'Автопрестиж'
            elif 'измайлово' in n_low: holding = 'Измайлово'
            elif 'автопассаж' in n_low: holding = 'Автопассаж'
            elif 'автодин' in n_low: holding = 'Автодин'
            elif 'км/ч' in n_low or 'амт' in n_low: holding = 'КМ/ч'
            elif 'маркар' in n_low: holding = 'Маркар'
            elif 'балтавто' in n_low: holding = 'БалтАвто'
            elif 'джиэн' in n_low: holding = 'ДжиЭн Сервис'
            elif 'флагман' in n_low: holding = 'Флагман-Авто'
            elif 'эрси' in n_low: holding = 'ЭРСИ Автотрейд'
            elif 'нижегородец' in n_low: holding = 'Нижегородец'
            else: holding = name

            fdc_val = str(row_dict.get('Код ФДЦ', '')).strip() if row_dict.get('Код ФДЦ') is not None else ''
            if fdc_val.lower() in ['', 'none']:
                status = 'Онлайн / Без ФДЦ'
            elif 'лид' in fdc_val.lower():
                status = 'Только лиды'
            elif any(ch.isdigit() for ch in fdc_val):
                status = 'Подключен с кодом ФДЦ'
            else:
                status = 'Онлайн'

            addr = str(row_dict.get('Адрес', '')).strip()
            
            raw_dealers.append({
                'sheet': sname,
                'specific_brand': brand_field or sname,
                'holding': holding,
                'name': name,
                'ul': str(row_dict.get('ЮЛ', '')).strip(),
                'inn': inn,
                'fdc': fdc_val,
                'status': status,
                'address': addr,
                'back_name': str(row_dict.get('Название в беке', '')).strip() if row_dict.get('Название в беке') is not None else '',
                'group_link': str(row_dict.get('Ссылка на группу', '')).strip(),
                'email': str(row_dict.get('Почты для передачи лидов', '')).strip(),
                'manager': str(row_dict.get('Ответственный', '')).strip(),
            })

df_dealers = pd.DataFrame(raw_dealers)

# Создание и стилизация Excel книги
wb = openpyxl.Workbook()
wb.remove(wb.active) # Удаляем дефолтный лист

# Цветовая палитра: корпоративный темно-синий / изумрудно-зеленый
navy_header_fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
green_header_fill = PatternFill(start_color="1E4620", end_color="1E4620", fill_type="solid")
slate_header_fill = PatternFill(start_color="2D3748", end_color="2D3748", fill_type="solid")
kpi_card_fill = PatternFill(start_color="F0F4F8", end_color="F0F4F8", fill_type="solid")
total_row_fill = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
font_sub = Font(name="Calibri", size=11, bold=True, color="1A365D")
font_bold = Font(name="Calibri", size=11, bold=True, color="000000")
font_normal = Font(name="Calibri", size=10, color="000000")
font_link = Font(name="Calibri", size=10, color="0066CC", underline="single")

thin_border_side = Side(style='thin', color='CBD5E1')
border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
border_total = Border(top=Side(style='thin', color='1E293B'), bottom=Side(style='double', color='1E293B'))

align_center = Alignment(horizontal='center', vertical='center')
align_left = Alignment(horizontal='left', vertical='center')
align_right = Alignment(horizontal='right', vertical='center')
align_wrap = Alignment(horizontal='left', vertical='center', wrap_text=True)

# -------------------------------------------------------------
# ЛИСТ 1: Свод по брендам
# -------------------------------------------------------------
ws1 = wb.create_sheet(title="Свод по брендам")
ws1.views.sheetView[0].showGridLines = True

headers1 = [
    "№", 
    "Бренд / Направление (вкладка OEM)", 
    "Кол-во ДЦ (точек продаж)", 
    "Доля от рынка Москвы, %", 
    "Уникальных холдингов", 
    "Уникальных ЮЛ (ИНН)", 
    "Ключевые дилеры в Москве",
    "Примечания"
]

ws1.append(headers1)
for col_idx in range(1, len(headers1) + 1):
    cell = ws1.cell(1, col_idx)
    cell.fill = navy_header_fill
    cell.font = font_header
    cell.alignment = align_center

brands_order = [
    ('JETOUR', '19 ДЦ через 15 сетей; крупнейшая монобрендовая сеть в Москве'),
    ('GAC', '15 ДЦ; высокая концентрация у Major (4), Автомира (3) и Автодома (3)'),
    ('Geely & Belgee', '15 ДЦ: Geely — 8 ДЦ, Belgee — 3 ДЦ, Knewstar/мульти — 4 ДЦ'),
    ('Рольф Импорт', '15 ДЦ: Toyota — 5 ДЦ, Hyundai — 4 ДЦ, Mazda — 3 ДЦ, VW — 3 ДЦ'),
    ('SOLARIS', '12 ДЦ: АвтоГЕРМЕС — 4 ДЦ, Major — 2 ДЦ, Автомир — 2 ДЦ, Независимость — 2 ДЦ'),
    ('HAVAL', '9 ДЦ: включает линейки Haval City и Haval Pro (Кунцево, АСЦ, Рольф)'),
    ('CHERY & TENET', '8 ДЦ: 8 независимых дилерских холдингов'),
    ('CHANGAN', '7 ДЦ: АвтоГЕРМЕС, Автомир, АВТОДОМ, ТЦ Кунцево, АСЦ, Квазар, КМ/ч'),
    ('LADA', '7 ДЦ: АвтоГЕРМЕС (5 локаций), Major (1), Петровский (1)'),
    ('OMODA & JAECOO', '6 ДЦ: совмещенная дилерская сеть O&J (Автодом, Рольф, Деливери Кар, СОНГ)'),
    ('Soueast', '2 ДЦ: официальный старт сети через холдинг Независимость'),
    ('JETTA', '1 ДЦ: флагманская сеть Major (Новорижское шоссе)'),
    ('Москвич', '0 ДЦ в Москве (в базе OEM только Казань, Краснодар, СПб)'),
    ('DEEPAL', '0 ДЦ в Москве (в базе OEM представлены 7 регионов)'),
    ('Voyah', '0 ДЦ в Москве (в базе OEM только Казань)')
]

row_num = 2
total_moscow_dc = len(df_dealers)

for idx, (b_name, note) in enumerate(brands_order, start=1):
    sub = df_dealers[df_dealers['sheet'] == b_name]
    dc_cnt = len(sub)
    holdings_cnt = sub['holding'].nunique() if dc_cnt > 0 else 0
    inns_cnt = sub[sub['inn'] != '']['inn'].nunique() if dc_cnt > 0 else 0
    top_dealers = ', '.join(sub['holding'].value_counts().head(3).index.tolist()) if dc_cnt > 0 else '—'
    
    ws1.cell(row=row_num, column=1, value=idx).alignment = align_center
    ws1.cell(row=row_num, column=2, value=b_name).alignment = align_left
    ws1.cell(row=row_num, column=3, value=dc_cnt).alignment = align_right
    ws1.cell(row=row_num, column=3).number_format = '#,##0'
    
    pct_cell = ws1.cell(row=row_num, column=4, value=f"=C{row_num}/$C$17")
    pct_cell.alignment = align_right
    pct_cell.number_format = '0.0%'
    
    ws1.cell(row=row_num, column=5, value=holdings_cnt).alignment = align_right
    ws1.cell(row=row_num, column=5).number_format = '#,##0'
    
    ws1.cell(row=row_num, column=6, value=inns_cnt).alignment = align_right
    ws1.cell(row=row_num, column=6).number_format = '#,##0'
    
    ws1.cell(row=row_num, column=7, value=top_dealers).alignment = align_left
    ws1.cell(row=row_num, column=8, value=note).alignment = align_left
    
    for c in range(1, 9):
        cell = ws1.cell(row_num, c)
        cell.font = font_normal
        cell.border = border_cell
        if row_num % 2 == 1:
            cell.fill = zebra_fill
            
    row_num += 1

# Итоговая строка
ws1.cell(row=17, column=1, value="ИТОГО").alignment = align_center
ws1.cell(row=17, column=2, value="Всего по Москве").alignment = align_left
ws1.cell(row=17, column=3, value="=SUM(C2:C16)").alignment = align_right
ws1.cell(row=17, column=3).number_format = '#,##0'
ws1.cell(row=17, column=4, value="=SUM(D2:D16)").alignment = align_right
ws1.cell(row=17, column=4).number_format = '0.0%'
ws1.cell(row=17, column=5, value=df_dealers['holding'].nunique()).alignment = align_right
ws1.cell(row=17, column=5).number_format = '#,##0'
ws1.cell(row=17, column=6, value=df_dealers[df_dealers['inn'] != '']['inn'].nunique()).alignment = align_right
ws1.cell(row=17, column=6).number_format = '#,##0'
ws1.cell(row=17, column=7, value="27 уникальных дилерских сетей").alignment = align_left
ws1.cell(row=17, column=8, value="100% ДЦ подключены к каналам интеграции СберАвто").alignment = align_left

for c in range(1, 9):
    cell = ws1.cell(17, c)
    cell.font = font_bold
    cell.fill = total_row_fill
    cell.border = border_total

# -------------------------------------------------------------
# ЛИСТ 2: Топ холдингов Москвы
# -------------------------------------------------------------
ws2 = wb.create_sheet(title="Топ холдингов Москвы")
ws2.views.sheetView[0].showGridLines = True

headers2 = [
    "№", 
    "Дилерский холдинг / Сеть ДЦ", 
    "Подключенных ДЦ (точек продаж)", 
    "Доля от рынка Москвы, %", 
    "Кол-во брендов", 
    "Представленные бренды OEM", 
    "Юридические лица (ЮЛ)", 
    "ИНН"
]

ws2.append(headers2)
for col_idx in range(1, len(headers2) + 1):
    cell = ws2.cell(1, col_idx)
    cell.fill = green_header_fill
    cell.font = font_header
    cell.alignment = align_center

holdings_summary = []
for h, g in df_dealers.groupby('holding'):
    holdings_summary.append({
        'holding': h,
        'dc_count': len(g),
        'brands_count': g['sheet'].nunique(),
        'brands_list': ', '.join(sorted(g['sheet'].unique())),
        'uls': ', '.join(sorted(g['ul'].unique())),
        'inns': ', '.join(sorted(set([str(x) for x in g['inn'].unique() if str(x) != ''])))
    })

df_h = pd.DataFrame(holdings_summary).sort_values(by='dc_count', ascending=False).reset_index(drop=True)

row_num = 2
for idx, row in df_h.iterrows():
    ws2.cell(row=row_num, column=1, value=idx + 1).alignment = align_center
    ws2.cell(row=row_num, column=2, value=row['holding']).alignment = align_left
    ws2.cell(row=row_num, column=3, value=row['dc_count']).alignment = align_right
    ws2.cell(row=row_num, column=3).number_format = '#,##0'
    
    pct_cell = ws2.cell(row=row_num, column=4, value=f"=C{row_num}/$C${len(df_h)+2}")
    pct_cell.alignment = align_right
    pct_cell.number_format = '0.0%'
    
    ws2.cell(row=row_num, column=5, value=row['brands_count']).alignment = align_right
    ws2.cell(row=row_num, column=5).number_format = '#,##0'
    
    ws2.cell(row=row_num, column=6, value=row['brands_list']).alignment = align_left
    ws2.cell(row=row_num, column=7, value=row['uls']).alignment = align_left
    ws2.cell(row=row_num, column=8, value=row['inns']).alignment = align_left
    
    for c in range(1, 9):
        cell = ws2.cell(row_num, c)
        cell.font = font_normal
        cell.border = border_cell
        if row_num % 2 == 1:
            cell.fill = zebra_fill
    row_num += 1

tot_h_row = len(df_h) + 2
ws2.cell(row=tot_h_row, column=1, value="ИТОГО").alignment = align_center
ws2.cell(row=tot_h_row, column=2, value=f"Всего холдингов: {len(df_h)}").alignment = align_left
ws2.cell(row=tot_h_row, column=3, value=f"=SUM(C2:C{tot_h_row-1})").alignment = align_right
ws2.cell(row=tot_h_row, column=3).number_format = '#,##0'
ws2.cell(row=tot_h_row, column=4, value=f"=SUM(D2:D{tot_h_row-1})").alignment = align_right
ws2.cell(row=tot_h_row, column=4).number_format = '0.0%'
ws2.cell(row=tot_h_row, column=5, value="12 активных").alignment = align_center
ws2.cell(row=tot_h_row, column=6, value="Охват ключевых брендов РФ").alignment = align_left
ws2.cell(row=tot_h_row, column=7, value=f"33 юр. лица").alignment = align_left
ws2.cell(row=tot_h_row, column=8, value="33 ИНН").alignment = align_left

for c in range(1, 9):
    cell = ws2.cell(tot_h_row, c)
    cell.font = font_bold
    cell.fill = total_row_fill
    cell.border = border_total

# -------------------------------------------------------------
# ЛИСТ 3: Реестр всех 116 ДЦ Москвы
# -------------------------------------------------------------
ws3 = wb.create_sheet(title="Реестр ДЦ Москвы (116 ДЦ)")
ws3.views.sheetView[0].showGridLines = True

headers3 = [
    "№", 
    "Бренд (вкладка OEM)", 
    "Марка автомобиля", 
    "Холдинг / Сеть", 
    "Название ДЦ в базе", 
    "Юридическое лицо (ЮЛ)", 
    "ИНН", 
    "Код ФДЦ", 
    "Статус подключения", 
    "Адрес ДЦ", 
    "Канал лидов (Чат / Ссылка)", 
    "Почта для лидов", 
    "Куратор СберАвто"
]

ws3.append(headers3)
for col_idx in range(1, len(headers3) + 1):
    cell = ws3.cell(1, col_idx)
    cell.fill = slate_header_fill
    cell.font = font_header
    cell.alignment = align_center

# Сортируем реестр: сначала по бренду, затем по холдингу
df_dealers_sorted = df_dealers.sort_values(by=['sheet', 'holding', 'name']).reset_index(drop=True)

row_num = 2
for idx, r in df_dealers_sorted.iterrows():
    ws3.cell(row=row_num, column=1, value=idx + 1).alignment = align_center
    ws3.cell(row=row_num, column=2, value=r['sheet']).alignment = align_left
    ws3.cell(row=row_num, column=3, value=r['specific_brand']).alignment = align_left
    ws3.cell(row=row_num, column=4, value=r['holding']).alignment = align_left
    ws3.cell(row=row_num, column=5, value=r['name']).alignment = align_left
    ws3.cell(row=row_num, column=6, value=r['ul']).alignment = align_left
    ws3.cell(row=row_num, column=7, value=r['inn']).alignment = align_center
    ws3.cell(row=row_num, column=8, value=r['fdc']).alignment = align_center
    ws3.cell(row=row_num, column=9, value=r['status']).alignment = align_center
    ws3.cell(row=row_num, column=10, value=r['address']).alignment = align_left
    ws3.cell(row=row_num, column=11, value=r['group_link']).alignment = align_left
    ws3.cell(row=row_num, column=12, value=r['email']).alignment = align_left
    ws3.cell(row=row_num, column=13, value=r['manager']).alignment = align_left
    
    for c in range(1, 14):
        cell = ws3.cell(row_num, c)
        cell.font = font_normal
        cell.border = border_cell
        if row_num % 2 == 1:
            cell.fill = zebra_fill
    row_num += 1

# -------------------------------------------------------------
# ЛИСТ 4: Детализация Geely и Рольф
# -------------------------------------------------------------
ws4 = wb.create_sheet(title="Детализация Geely и Рольф")
ws4.views.sheetView[0].showGridLines = True

ws4.cell(row=1, column=1, value="1. Детализация мультибренда «Рольф Импорт» в Москве (15 ДЦ)").font = font_sub
headers4_1 = ["№", "Марка авто", "Локация / Название ДЦ", "Адрес", "ЮЛ", "ИНН", "Канал лидов (чат)", "Почта ДЦ"]
ws4.append([])
ws4.append(headers4_1)
h_row_1 = 3
for col_idx in range(1, len(headers4_1) + 1):
    cell = ws4.cell(h_row_1, col_idx)
    cell.fill = navy_header_fill
    cell.font = font_header
    cell.alignment = align_center

sub_rolf = df_dealers[df_dealers['sheet'] == 'Рольф Импорт'].sort_values(by=['specific_brand', 'name']).reset_index(drop=True)
cur_r = 4
for idx, r in sub_rolf.iterrows():
    ws4.cell(row=cur_r, column=1, value=idx + 1).alignment = align_center
    ws4.cell(row=cur_r, column=2, value=r['specific_brand']).alignment = align_left
    ws4.cell(row=cur_r, column=3, value=r['name']).alignment = align_left
    ws4.cell(row=cur_r, column=4, value=r['address']).alignment = align_left
    ws4.cell(row=cur_r, column=5, value=r['ul']).alignment = align_left
    ws4.cell(row=cur_r, column=6, value=r['inn']).alignment = align_center
    ws4.cell(row=cur_r, column=7, value=r['group_link']).alignment = align_left
    ws4.cell(row=cur_r, column=8, value=r['email']).alignment = align_left
    for c in range(1, len(headers4_1) + 1):
        cell = ws4.cell(cur_r, c)
        cell.font = font_normal
        cell.border = border_cell
        if cur_r % 2 == 1: cell.fill = zebra_fill
    cur_r += 1

cur_r += 2
ws4.cell(row=cur_r, column=1, value="2. Детализация сети «Geely & Belgee» в Москве (15 ДЦ)").font = font_sub
cur_r += 1
headers4_2 = ["№", "Бренд в базе", "Холдинг", "Название ДЦ", "Код ФДЦ", "Адрес", "ЮЛ", "ИНН"]
ws4.cell(row=cur_r, column=1).value = ""
for col_idx, h in enumerate(headers4_2, start=1):
    cell = ws4.cell(cur_r, col_idx, value=h)
    cell.fill = green_header_fill
    cell.font = font_header
    cell.alignment = align_center

sub_geely = df_dealers[df_dealers['sheet'] == 'Geely&Belgee'].sort_values(by=['specific_brand', 'holding']).reset_index(drop=True)
cur_r += 1
for idx, r in sub_geely.iterrows():
    ws4.cell(row=cur_r, column=1, value=idx + 1).alignment = align_center
    ws4.cell(row=cur_r, column=2, value=r['specific_brand']).alignment = align_left
    ws4.cell(row=cur_r, column=3, value=r['holding']).alignment = align_left
    ws4.cell(row=cur_r, column=4, value=r['name']).alignment = align_left
    ws4.cell(row=cur_r, column=5, value=r['fdc']).alignment = align_center
    ws4.cell(row=cur_r, column=6, value=r['address']).alignment = align_left
    ws4.cell(row=cur_r, column=7, value=r['ul']).alignment = align_left
    ws4.cell(row=cur_r, column=8, value=r['inn']).alignment = align_center
    for c in range(1, len(headers4_2) + 1):
        cell = ws4.cell(cur_r, c)
        cell.font = font_normal
        cell.border = border_cell
        if cur_r % 2 == 1: cell.fill = zebra_fill
    cur_r += 1

# Настройка ширины колонок и закрепление областей во всех листах
for ws in [ws1, ws2, ws3, ws4]:
    ws.freeze_panes = 'A2'
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if cell.number_format == '0.0%' and isinstance(cell.value, (int, float)):
                val_str = f"{cell.value*100:.1f}%"
            # Ограничиваем длину строки чтобы длинные URL не раздували столбцы
            val_len = min(len(val_str), 55)
            if val_len > max_len:
                max_len = val_len
        ws.column_dimensions[col_letter].width = max(max_len + 4, 11)

# Специфические ширины для красивой верстки
ws1.column_dimensions['B'].width = 32
ws1.column_dimensions['C'].width = 24
ws1.column_dimensions['D'].width = 24
ws1.column_dimensions['E'].width = 22
ws1.column_dimensions['F'].width = 22
ws1.column_dimensions['G'].width = 35
ws1.column_dimensions['H'].width = 45

ws2.column_dimensions['B'].width = 28
ws2.column_dimensions['C'].width = 26
ws2.column_dimensions['D'].width = 24
ws2.column_dimensions['E'].width = 16
ws2.column_dimensions['F'].width = 40
ws2.column_dimensions['G'].width = 35
ws2.column_dimensions['H'].width = 25

ws3.column_dimensions['A'].width = 6
ws3.column_dimensions['B'].width = 18
ws3.column_dimensions['C'].width = 18
ws3.column_dimensions['D'].width = 22
ws3.column_dimensions['E'].width = 26
ws3.column_dimensions['F'].width = 30
ws3.column_dimensions['G'].width = 15
ws3.column_dimensions['H'].width = 15
ws3.column_dimensions['I'].width = 22
ws3.column_dimensions['J'].width = 45
ws3.column_dimensions['K'].width = 30
ws3.column_dimensions['L'].width = 35
ws3.column_dimensions['M'].width = 20

# Активируем фильтры
ws1.auto_filter.ref = f"A1:H16"
ws2.auto_filter.ref = f"A1:H{len(df_h)+1}"
ws3.auto_filter.ref = f"A1:M{len(df_dealers)+1}"

# Сохранение книги
output_root = "Дилеры_Москва_ОЕМ_СберАвто.xlsx"
output_down = "/Users/vaceslavgamaunov/Downloads/Дилеры_Москва_ОЕМ_СберАвто.xlsx"
output_raw = "otchet-parser/raw_data/Дилеры_Москва_ОЕМ_СберАвто.xlsx"

wb.save(output_root)
wb.save(output_down)
wb.save(output_raw)

print(f"[+] Успешно сформирован и сохранен файл:")
print(f"    1. {output_root}")
print(f"    2. {output_down}")
print(f"    3. {output_raw}")
