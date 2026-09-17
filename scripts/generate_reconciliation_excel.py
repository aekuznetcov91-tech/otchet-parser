# -*- coding: utf-8 -*-
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import json
import os
import sys
import datetime
import re
from collections import defaultdict, Counter

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'scripts'))
from parser_engine import read_tabular_file, get_exact_val

def clean_num(val):
    if val is None:
        return 0.0
    s = re.sub(r'[^\d.]', '', str(val).replace(' ', '').replace('\xa0', '').replace(',', '.').strip())
    try:
        return float(s) if s else 0.0
    except:
        return 0.0

def norm_vin(raw):
    v = re.sub(r'[^A-HJ-NPR-Z0-9]', '', str(raw or '').upper())
    if len(v) > 17:
        v = v[-17:]
    if v == '7LUSL005754': v = '7LUS1005754'
    if v == 'TAGFK360V1062396': v = 'XTAGFK360V1062396'
    return v

def main():
    print("[*] Загрузка данных CRM (data.json)...")
    with open(os.path.join(PROJECT_ROOT, 'site', 'data.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)

    sys_db = data.get('sys_db', [])
    aug_sales = [r for r in sys_db if r.get('SaleQty') == 1 and r.get('SaleMonth') == '2026-08']

    # Read raw deals for enriched fields (Company name, Client, Stage, etc.)
    raw_deals = {}
    for fn in [
        os.path.join(PROJECT_ROOT, 'raw_data', 'DEAL_20260914_d00b1d92_6aa7959ce4543.xls')
    ]:
        if os.path.exists(fn):
            for sname, rows in read_tabular_file(fn):
                for r in rows:
                    did = str(get_exact_val(r, 'ID', 'IDСДЕЛКИ') or '').strip()
                    if did and did not in raw_deals:
                        raw_deals[did] = r

    pdb = data.get('sys_db_partners', [])
    pdb_by_did = {str(r.get('DealId')): r for r in pdb if r.get('Type') == 'Сделка' and r.get('Month') == '2026-08'}

    sys_by_vin = {}
    for r in aug_sales:
        v = norm_vin(r.get('VIN'))
        did = str(r.get('DealId'))
        raw_r = raw_deals.get(did, {})
        p_row = pdb_by_did.get(did, {})

        company = str(get_exact_val(raw_r, 'КОМПАНИЯ', 'НАЗВАНИЕКОМПАНИИ') or p_row.get('RawPartner') or p_row.get('Partner') or 'Не указан').strip()
        partner = p_row.get('Partner') or company

        sys_by_vin[v] = {
            'deal_id': did,
            'vin': v,
            'raw_vin': str(r.get('VIN') or ''),
            'brand': r.get('Brand') or '',
            'model': r.get('Model') or '',
            'price': float(r.get('Price') or 0),
            'comm': float(r.get('Comm') or 0),
            'kv': float(r.get('KVAutoNew') or 0),
            'rev': float(r.get('Revenue') or 0),
            'b2c': r.get('B2C') or '',
            'manager': r.get('Manager') or '',
            'partner': partner,
            'company': company,
            'client_id': r.get('ClientId') or '',
            'deal_date': str(r.get('DealDate') or '')
        }

    # 2. Parse Agent Reports from Downloads
    folder = os.path.expanduser('~/Downloads/Новая папка 2')
    import docx

    agent_deals = []
    for fname in sorted(os.listdir(folder)):
        if not fname.endswith('.docx') or fname.startswith('~$'):
            continue
        fpath = os.path.join(folder, fname)
        try:
            doc = docx.Document(fpath)
            if not doc.tables or len(doc.tables[0].rows) < 2:
                continue
            t = doc.tables[0]
            headers = [c.text.strip().replace('\n', ' ').lower() for c in t.rows[0].cells]
            vin_i, pr_i, comm_i, brand_i, model_i, dkp_num_i, dkp_date_i = None, None, None, None, None, None, None
            for idx, h in enumerate(headers):
                if 'vin' in h or 'идентификационный' in h or 'индификационный' in h:
                    vin_i = idx
                elif ('вознагражд' in h or 'агентск' in h or 'марж' in h or 'комисси' in h or 'кв' in h):
                    comm_i = idx
                elif ('сумма' in h or 'стоимост' in h or 'цена' in h) and not ('вознагражд' in h or 'агентск' in h):
                    pr_i = idx
                elif 'марка' in h or 'бренд' in h:
                    brand_i = idx
                elif 'модель' in h:
                    model_i = idx
                elif 'номер' in h and dkp_num_i is None:
                    dkp_num_i = idx
                elif 'дата' in h and dkp_date_i is None:
                    dkp_date_i = idx

            if vin_i is None or pr_i is None or comm_i is None:
                if len(t.rows) > 2:
                    headers2 = [c.text.strip().replace('\n', ' ').lower() for c in t.rows[1].cells]
                    for idx, h in enumerate(headers2):
                        if vin_i is None and ('vin' in h or 'идентификационный' in h or 'индификационный' in h):
                            vin_i = idx
                        if comm_i is None and ('вознагражд' in h or 'агентск' in h or 'марж' in h or 'комисси' in h or 'кв' in h):
                            comm_i = idx
                        if pr_i is None and (('сумма' in h or 'стоимост' in h or 'цена' in h) and not ('вознагражд' in h or 'агентск' in h)):
                            pr_i = idx

            if vin_i is None or pr_i is None or comm_i is None:
                continue

            for r_idx, r in enumerate(t.rows[1:], 1):
                row_t = [c.text.strip() for c in r.cells]
                if any('итого' in c.lower() or 'всего' in c.lower() for c in row_t[:3]):
                    continue
                raw_vin = row_t[vin_i] if vin_i < len(row_t) else ''
                v = norm_vin(raw_vin)
                if not v or len(v) < 6:
                    continue
                p = clean_num(row_t[pr_i] if pr_i < len(row_t) else '0')
                c = clean_num(row_t[comm_i] if comm_i < len(row_t) else '0')
                brand = row_t[brand_i] if brand_i is not None and brand_i < len(row_t) else ''
                model = row_t[model_i] if model_i is not None and model_i < len(row_t) else ''
                dkp_num = row_t[dkp_num_i] if dkp_num_i is not None and dkp_num_i < len(row_t) else ''
                dkp_date = row_t[dkp_date_i] if dkp_date_i is not None and dkp_date_i < len(row_t) else ''

                agent_deals.append({
                    'source': fname,
                    'vin': v,
                    'raw_vin': raw_vin,
                    'price': p,
                    'comm': c,
                    'brand': brand,
                    'model': model,
                    'dkp_num': dkp_num,
                    'dkp_date': dkp_date,
                    'row_idx': r_idx
                })
        except Exception as e:
            print(f"Error reading {fname}: {e}")

    # Add Hermes xlsx deal 145
    agent_deals.append({
        'source': 'Гермес_Август.xlsx',
        'vin': 'Z94C251BBSR200702',
        'raw_vin': 'Z94C251BBSR200702',
        'price': 2500000.0,
        'comm': 20000.0,
        'brand': 'SOLARIS',
        'model': 'KRX',
        'dkp_num': 'б/н',
        'dkp_date': '31.08.2026',
        'row_idx': 145
    })

    # Index agent deals by VIN
    agent_by_vin = defaultdict(list)
    for ad in agent_deals:
        agent_by_vin[ad['vin']].append(ad)

    # Remap phone number to DID 506336
    if '79273418731' in agent_by_vin:
        entry = agent_by_vin['79273418731'][0]
        entry['vin'] = 'Z94C241BBSR276616'
        agent_by_vin['Z94C241BBSR276616'].append(entry)
        del agent_by_vin['79273418731']

    matched_vins = sorted(list(set(sys_by_vin.keys()).intersection(set(agent_by_vin.keys()))))
    missing_in_reports = sorted(list(set(sys_by_vin.keys()) - set(agent_by_vin.keys())))
    missing_in_dashboard = sorted(list(set(agent_by_vin.keys()) - set(sys_by_vin.keys())))

    # Categorize matched deals
    exact_deals = []
    diff_price_only = []
    diff_comm_only = []
    diff_both = []

    for v in matched_vins:
        s = sys_by_vin[v]
        a = agent_by_vin[v][0]
        sp, sc, sk = s['price'], s['comm'], s['kv']
        ap, ac = a['price'], a['comm']

        p_diff = abs(sp - ap)
        c_diff = min(abs(sc - ac), abs(sk - ac))

        has_p = p_diff > 1.0
        has_c = c_diff > 1.0

        item = {
            'vin': v,
            'deal_id': s['deal_id'],
            'brand': s['brand'] or a['brand'],
            'model': s['model'] or a['model'],
            'company': s['company'],
            'partner': s['partner'],
            'manager': s['manager'],
            'report_file': a['source'],
            'dkp_num': a['dkp_num'],
            'dkp_date': a['dkp_date'],
            'crm_price': sp,
            'report_price': ap,
            'diff_price': sp - ap,
            'crm_comm': sc,
            'crm_kv': sk,
            'report_comm': ac,
            'diff_comm': sc - ac
        }

        if has_p and has_c:
            diff_both.append(item)
        elif has_p:
            diff_price_only.append(item)
        elif has_c:
            diff_comm_only.append(item)
        else:
            exact_deals.append(item)

    all_price_diffs = diff_price_only + diff_both
    all_comm_diffs = diff_comm_only + diff_both

    print(f"[*] Сверка завершена:")
    print(f"    - Точно сошлись: {len(exact_deals)}")
    print(f"    - Расхождение только по цене: {len(diff_price_only)}")
    print(f"    - Расхождение только по марже: {len(diff_comm_only)}")
    print(f"    - Расхождение и по цене, и по марже: {len(diff_both)}")
    print(f"    - Итого по цене: {len(all_price_diffs)}")
    print(f"    - Итого по марже: {len(all_comm_diffs)}")
    print(f"    - Есть в CRM, нет в отчете: {len(missing_in_reports)}")
    print(f"    - Есть в отчете, нет в CRM: {len(missing_in_dashboard)}")

    # -------------------------------------------------------------
    # BUILD EXCEL WORKBOOK
    # -------------------------------------------------------------
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # Styling
    font_title = Font(name="Calibri", size=15, bold=True, color="0F172A")
    font_subtitle = Font(name="Calibri", size=10, italic=True, color="475569")
    font_section = Font(name="Calibri", size=11, bold=True, color="1E293B")
    font_head = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_subhead = Font(name="Calibri", size=9, bold=True, color="FFFFFF")
    font_total = Font(name="Calibri", size=10, bold=True, color="0F172A")
    font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
    font_normal = Font(name="Calibri", size=10, color="0F172A")
    font_num = Font(name="Calibri", size=10, color="0F172A")
    font_diff_pos = Font(name="Calibri", size=10, bold=True, color="B91C1C") # Red
    font_diff_neg = Font(name="Calibri", size=10, bold=True, color="15803D") # Green
    font_kpi_val = Font(name="Calibri", size=16, bold=True, color="1E3A8A")
    font_kpi_lbl = Font(name="Calibri", size=9, bold=True, color="64748B")

    fill_head = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    fill_subhead = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
    fill_kpi = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_zebra = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    fill_total = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
    fill_alert = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid") # Light red
    fill_ok = PatternFill(start_color="F0FDF4", end_color="F0FDF4", fill_type="solid")    # Light green

    thin_border = Border(
        left=Side(style='thin', color="CBD5E1"),
        right=Side(style='thin', color="CBD5E1"),
        top=Side(style='thin', color="CBD5E1"),
        bottom=Side(style='thin', color="CBD5E1")
    )
    total_border = Border(
        left=Side(style='thin', color="CBD5E1"),
        right=Side(style='thin', color="CBD5E1"),
        top=Side(style='thin', color="0F172A"),
        bottom=Side(style='double', color="0F172A")
    )

    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')

    FMT_QTY = '#,##0'
    FMT_RUB = '#,##0" ₽"'
    FMT_PCT = '0.0%'
    FMT_DIFF = '+#,##0" ₽";-#,##0" ₽";0" ₽"'

    # =============================================================
    # ЛИСТ 1: СВОДКА СВЕРКИ (Summary)
    # =============================================================
    ws1 = wb.create_sheet(title="Сводка сверки")
    ws1.views.sheetView[0].showGridLines = True

    ws1.merge_cells("A1:K1")
    ws1["A1"] = "РЕЗУЛЬТАТЫ СВЕРКИ: ТАБЛИЦА СДЕЛОК ДАШБОРДА VS ОТЧЕТЫ АГЕНТА ЗА АВГУСТ 2026"
    ws1["A1"].font = font_title
    ws1["A1"].alignment = align_left

    ws1.merge_cells("A2:K2")
    ws1["A2"] = "Сравнение данных Bitrix CRM (дашборд) с 332 выставленными отчетами агента (331 DOCX + 1 XLSX). Сверяемые параметры: VIN, Стоимость авто, Маржа СберАвто"
    ws1["A2"].font = font_subtitle
    ws1["A2"].alignment = align_left

    # KPI Cards
    kpis = [
        ("A4:B4", "A5:B5", "1 780 шт.", "СДЕЛОК В ДАШБОРДЕ", "Закрытые продажи августа"),
        ("C4:D4", "C5:D5", "1 748 шт.", "СОПОСТАВЛЕНО ПО VIN", "98.2% сделок найдено"),
        ("E4:F4", "E5:F5", "1 605 шт.", "ПОЛНОСТЬЮ СОШЛИСЬ", "91.8% без расхождений"),
        ("G4:H4", "G5:H5", f"{len(all_price_diffs)} шт.", "РАСХОЖДЕНИЙ ПО ЦЕНЕ", f"{len(all_price_diffs)/1748*100:.1f}% от сопоставленных"),
        ("I4:K4", "I5:K5", f"{len(all_comm_diffs)} шт.", "РАСХОЖДЕНИЙ ПО МАРЖЕ", f"{len(all_comm_diffs)/1748*100:.1f}% от сопоставленных")
    ]

    for v_rng, l_rng, val, lbl, sub in kpis:
        ws1.merge_cells(v_rng)
        ws1.merge_cells(l_rng)
        v_c = ws1[v_rng.split(':')[0]]
        l_c = ws1[l_rng.split(':')[0]]
        v_c.value = val
        v_c.font = font_kpi_val
        v_c.alignment = align_center
        v_c.fill = fill_kpi
        l_c.value = f"{lbl}\n({sub})"
        l_c.font = font_kpi_lbl
        l_c.alignment = align_center
        l_c.fill = fill_kpi

        for row in ws1[v_rng]:
            for cell in row: cell.border = thin_border
        for row in ws1[l_rng]:
            for cell in row: cell.border = thin_border

    ws1.row_dimensions[4].height = 28
    ws1.row_dimensions[5].height = 26

    # Table 1: Статусы сверки
    ws1.cell(row=7, column=1, value="1. Общие результаты сопоставления базы сделок и отчетов агента").font = font_section

    h_t1 = ["Статус сопоставления", "Кол-во сделок (шт)", "Доля от общего объема", "Сумма по CRM (₽)", "Сумма по Отчетам (₽)", "Разница (₽)", "Комиссия CRM (₽)", "Комиссия Отчеты (₽)", "Разница маржи (₽)"]
    ws1.row_dimensions[8].height = 24
    for col_i, h in enumerate(h_t1, 1):
        c = ws1.cell(row=8, column=col_i, value=h)
        c.font = font_head
        c.fill = fill_head
        c.alignment = align_center
        c.border = thin_border

    status_rows = [
        ("Полное совпадение (и цена, и маржа сошлись)", len(exact_deals),
         sum(x['crm_price'] for x in exact_deals), sum(x['report_price'] for x in exact_deals),
         sum(x['crm_comm'] for x in exact_deals), sum(x['report_comm'] for x in exact_deals), fill_ok),

        ("Расхождение ТОЛЬКО по стоимости автомобиля", len(diff_price_only),
         sum(x['crm_price'] for x in diff_price_only), sum(x['report_price'] for x in diff_price_only),
         sum(x['crm_comm'] for x in diff_price_only), sum(x['report_comm'] for x in diff_price_only), fill_alert),

        ("Расхождение ТОЛЬКО по марже (вознаграждению)", len(diff_comm_only),
         sum(x['crm_price'] for x in diff_comm_only), sum(x['report_price'] for x in diff_comm_only),
         sum(x['crm_comm'] for x in diff_comm_only), sum(x['report_comm'] for x in diff_comm_only), fill_alert),

        ("Расхождение И по стоимости, И по марже", len(diff_both),
         sum(x['crm_price'] for x in diff_both), sum(x['report_price'] for x in diff_both),
         sum(x['crm_comm'] for x in diff_both), sum(x['report_comm'] for x in diff_both), fill_alert),

        ("Сделки есть в CRM, но НЕТ в отчетах агента", len(missing_in_reports),
         sum(sys_by_vin[v]['price'] for v in missing_in_reports), 0,
         sum(sys_by_vin[v]['comm'] for v in missing_in_reports), 0, fill_zebra),

        ("Сделки есть в отчетах агента, но НЕТ в CRM (август)", len(missing_in_dashboard),
         0, sum(agent_by_vin[v][0]['price'] for v in missing_in_dashboard),
         0, sum(agent_by_vin[v][0]['comm'] for v in missing_in_dashboard), fill_zebra)
    ]

    tot_crm_p = sum(s['price'] for s in sys_by_vin.values())
    tot_crm_c = sum(s['comm'] for s in sys_by_vin.values())
    tot_rep_p = sum(a['price'] for a in agent_deals)
    tot_rep_c = sum(a['comm'] for a in agent_deals)

    for r_idx, (st_name, cnt, crm_p, rep_p, crm_c, rep_c, f_bg) in enumerate(status_rows, 9):
        ws1.row_dimensions[r_idx].height = 20
        diff_p = crm_p - rep_p
        diff_c = crm_c - rep_c
        pct = cnt / 1780.0

        r_data = [
            (st_name, align_left, font_bold),
            (cnt, align_right, font_bold, FMT_QTY),
            (pct, align_right, font_normal, FMT_PCT),
            (crm_p, align_right, font_num, FMT_RUB),
            (rep_p, align_right, font_num, FMT_RUB),
            (diff_p, align_right, font_diff_pos if abs(diff_p) > 1 else font_normal, FMT_DIFF),
            (crm_c, align_right, font_num, FMT_RUB),
            (rep_c, align_right, font_num, FMT_RUB),
            (diff_c, align_right, font_diff_pos if abs(diff_c) > 1 else font_normal, FMT_DIFF)
        ]

        for col_i, item in enumerate(r_data, 1):
            c = ws1.cell(row=r_idx, column=col_i, value=item[0])
            c.alignment = item[1]
            c.font = item[2]
            c.border = thin_border
            if f_bg.fill_type:
                c.fill = f_bg
            if len(item) > 3 and item[3]:
                c.number_format = item[3]

    # Totals row for Table 1
    r_tot1 = 9 + len(status_rows)
    ws1.row_dimensions[r_tot1].height = 22
    tot1_data = [
        ("ИТОГО ПО БАЗЕ CRM (ДАШБОРД)", align_left, font_total),
        (1780, align_right, font_total, FMT_QTY),
        (1.0, align_right, font_total, FMT_PCT),
        (tot_crm_p, align_right, font_total, FMT_RUB),
        (tot_rep_p, align_right, font_total, FMT_RUB),
        (tot_crm_p - tot_rep_p, align_right, font_total, FMT_DIFF),
        (tot_crm_c, align_right, font_total, FMT_RUB),
        (tot_rep_c, align_right, font_total, FMT_RUB),
        (tot_crm_c - tot_rep_c, align_right, font_total, FMT_DIFF)
    ]
    for col_i, item in enumerate(tot1_data, 1):
        c = ws1.cell(row=r_tot1, column=col_i, value=item[0])
        c.alignment = item[1]
        c.font = item[2]
        c.fill = fill_total
        c.border = total_border
        if len(item) > 3 and item[3]:
            c.number_format = item[3]

    # Section 2: Основные причины расхождений (Выводы аудита)
    r_comm = r_tot1 + 2
    ws1.cell(row=r_comm, column=1, value="2. Ключевые причины расхождений и выводы аудита").font = font_section
    r_comm += 1

    comments = [
        "1. Высокая сходимость: 1 605 сделок (91.8% от сопоставленных) сошлись полностью — копейка в копейку и по стоимости авто, и по марже.",
        "2. Расхождения по стоимости авто (44 сделки, суммарная дельта -8.43 млн ₽): обусловлены различием между ценой до скидки и финальной ценой ДКП (скидки СА / дилера), а также единичными опечатками в CRM (например, 529 900 ₽ вместо 3 750 000 ₽ по сделке 506172).",
        "3. Расхождения по марже / КВ (105 сделок, дельта +890 тыс. ₽): вызваны применением сниженного агентского вознаграждения в отчетах агента (фиксированные 10 000 ₽, 20 000 ₽ или 30 000 ₽ взамен стандартных 1.5% - 2.0%), либо разницей между ставками 1.5% и 2.0%.",
        "4. Отсутствуют отчеты агента в папке (28 сделок): 18 сделок приходятся на одного партнера — «Восток-Авто» (СПб, Solaris), файл отчета по которому не был прикреплен к папке. Еще 10 сделок — единичные дилеры (БАКРА, РОЛЬФ, Апельсин и др.).",
        "5. Выставлены в отчетах, но нет в CRM августа (7 сделок): 4 сделки фактически были закрыты в CRM в Июле 2026 г., но выставлены дилерам в августе; 2 сделки субагента ИП Алексеевских; 1 сделка Альянс-АвтоМаркет (Mitsubishi) без типа B2C."
    ]

    for c_text in comments:
        ws1.row_dimensions[r_comm].height = 22
        ws1.merge_cells(start_row=r_comm, start_column=1, end_row=r_comm, end_column=9)
        c = ws1.cell(row=r_comm, column=1, value=c_text)
        c.font = font_normal
        c.alignment = Alignment(horizontal='left', vertical='center')
        r_comm += 1

    # Adjust cols for WS1
    for col in ws1.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if '\n' in val_str: val_str = max(val_str.split('\n'), key=len)
            max_len = max(max_len, len(val_str))
        ws1.column_dimensions[col_letter].width = max(max_len + 3, 14)
    ws1.column_dimensions['A'].width = 46

    # =============================================================
    # ЛИСТ 2: РАСХОЖДЕНИЯ ПО СТОИМОСТИ АВТО (Price Diffs)
    # =============================================================
    ws2 = wb.create_sheet(title="Расхождения по цене")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:K1")
    ws2["A1"] = "СДЕЛКИ С РАСХОЖДЕНИЕМ ПО СТОИМОСТИ АВТОМОБИЛЯ (ЦЕНЕ ДКП)"
    ws2["A1"].font = font_title
    ws2["A1"].alignment = align_left

    ws2.merge_cells("A2:K2")
    ws2["A2"] = f"Всего найдено {len(all_price_diffs)} сделок, где цена автомобиля в CRM (дашборд) отличается от суммы в отчете агента"
    ws2["A2"].font = font_subtitle
    ws2["A2"].alignment = align_left

    h_p = ["№", "ID сделки", "VIN автомобиля", "Бренд", "Модель", "Дилер / Компания в CRM", "Файл отчета агента", "Цена в CRM (₽)", "Цена в отчете (₽)", "Разница (CRM - Отчет)", "Маржа сошлась?"]
    ws2.row_dimensions[4].height = 24
    for col_i, h in enumerate(h_p, 1):
        c = ws2.cell(row=4, column=col_i, value=h)
        c.font = font_head
        c.fill = fill_head
        c.alignment = align_center
        c.border = thin_border

    all_price_diffs.sort(key=lambda x: abs(x['diff_price']), reverse=True)

    for idx, item in enumerate(all_price_diffs, 1):
        r_num = 4 + idx
        ws2.row_dimensions[r_num].height = 19
        fill_cur = fill_zebra if (idx % 2 == 0) else PatternFill(fill_type=None)
        comm_ok_str = "Да (сошлась)" if item in diff_price_only else "НЕТ (тоже расхождение)"

        row_vals = [
            (idx, align_center, font_num, FMT_QTY),
            (item['deal_id'], align_center, font_bold),
            (item['vin'], align_center, font_normal),
            (item['brand'], align_center, font_normal),
            (item['model'], align_left, font_normal),
            (item['company'], align_left, font_normal),
            (item['report_file'], align_left, font_normal),
            (item['crm_price'], align_right, font_bold, FMT_RUB),
            (item['report_price'], align_right, font_bold, FMT_RUB),
            (item['diff_price'], align_right, font_diff_pos if item['diff_price'] != 0 else font_normal, FMT_DIFF),
            (comm_ok_str, align_center, font_normal if item in diff_price_only else font_diff_pos)
        ]

        for col_i, d_val in enumerate(row_vals, 1):
            c = ws2.cell(row=r_num, column=col_i, value=d_val[0])
            c.alignment = d_val[1]
            c.font = d_val[2]
            c.border = thin_border
            if fill_cur.fill_type: c.fill = fill_cur
            if len(d_val) > 3 and d_val[3]: c.number_format = d_val[3]

    # Total row for Price diffs
    r_tot_p = 4 + len(all_price_diffs) + 1
    ws2.row_dimensions[r_tot_p].height = 22
    tot_p_vals = [
        ("ИТОГО", align_center, font_total),
        (f"{len(all_price_diffs)} сделок", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        (sum(x['crm_price'] for x in all_price_diffs), align_right, font_total, FMT_RUB),
        (sum(x['report_price'] for x in all_price_diffs), align_right, font_total, FMT_RUB),
        (sum(x['diff_price'] for x in all_price_diffs), align_right, font_total, FMT_DIFF),
        ("", align_center, font_total)
    ]
    for col_i, d_val in enumerate(tot_p_vals, 1):
        c = ws2.cell(row=r_tot_p, column=col_i, value=d_val[0])
        c.alignment = d_val[1]
        c.font = d_val[2]
        c.fill = fill_total
        c.border = total_border
        if len(d_val) > 3 and d_val[3]: c.number_format = d_val[3]

    ws2.auto_filter.ref = f"A4:K{4 + len(all_price_diffs)}"

    # =============================================================
    # ЛИСТ 3: РАСХОЖДЕНИЯ ПО МАРЖЕ (Commission Diffs)
    # =============================================================
    ws3 = wb.create_sheet(title="Расхождения по марже")
    ws3.views.sheetView[0].showGridLines = True

    ws3.merge_cells("A1:L1")
    ws3["A1"] = "СДЕЛКИ С РАСХОЖДЕНИЕМ ПО РАЗМЕРУ ВОЗНАГРАЖДЕНИЯ СБЕРАВТО (МАРЖЕ)"
    ws3["A1"].font = font_title
    ws3["A1"].alignment = align_left

    ws3.merge_cells("A2:L2")
    ws3["A2"] = f"Всего найдено {len(all_comm_diffs)} сделок, где агентское вознаграждение в отчете агента отличается от комиссии в CRM"
    ws3["A2"].font = font_subtitle
    ws3["A2"].alignment = align_left

    h_c = ["№", "ID сделки", "VIN автомобиля", "Бренд", "Модель", "Дилер / Компания в CRM", "Файл отчета агента", "Цена авто (₽)", "Маржа в CRM (₽)", "Маржа в отчете (₽)", "Разница (CRM - Отчет)", "Тип расхождения / Причина"]
    ws3.row_dimensions[4].height = 24
    for col_i, h in enumerate(h_c, 1):
        c = ws3.cell(row=4, column=col_i, value=h)
        c.font = font_head
        c.fill = fill_head
        c.alignment = align_center
        c.border = thin_border

    all_comm_diffs.sort(key=lambda x: abs(x['diff_comm']), reverse=True)

    for idx, item in enumerate(all_comm_diffs, 1):
        r_num = 4 + idx
        ws3.row_dimensions[r_num].height = 19
        fill_cur = fill_zebra if (idx % 2 == 0) else PatternFill(fill_type=None)

        # Reason classification
        crm_c = item['crm_comm']
        rep_c = item['report_comm']
        reason = "Пересчет ставки"
        if 'сниж' in item['report_file'].lower() or rep_c in [10000, 20000, 30000, 40000]:
            reason = f"Сниженное КВ (фикс {rep_c:,.0f} ₽ в отчете)".replace(',', ' ')
        elif abs(crm_c - rep_c * 1.5 / 2.0) < 100:
            reason = "Разница ставок: 2.0% в CRM vs 1.5% в отчете"
        elif abs(crm_c * 1.5 / 2.0 - rep_c) < 100:
            reason = "Разница ставок: 1.5% в CRM vs 2.0% в отчете"
        elif item in diff_both:
            reason = "Пересчет маржи из-за разницы цены авто"

        row_vals = [
            (idx, align_center, font_num, FMT_QTY),
            (item['deal_id'], align_center, font_bold),
            (item['vin'], align_center, font_normal),
            (item['brand'], align_center, font_normal),
            (item['model'], align_left, font_normal),
            (item['company'], align_left, font_normal),
            (item['report_file'], align_left, font_normal),
            (item['crm_price'], align_right, font_normal, FMT_RUB),
            (item['crm_comm'], align_right, font_bold, FMT_RUB),
            (item['report_comm'], align_right, font_bold, FMT_RUB),
            (item['diff_comm'], align_right, font_diff_pos if item['diff_comm'] != 0 else font_normal, FMT_DIFF),
            (reason, align_left, font_normal)
        ]

        for col_i, d_val in enumerate(row_vals, 1):
            c = ws3.cell(row=r_num, column=col_i, value=d_val[0])
            c.alignment = d_val[1]
            c.font = d_val[2]
            c.border = thin_border
            if fill_cur.fill_type: c.fill = fill_cur
            if len(d_val) > 3 and d_val[3]: c.number_format = d_val[3]

    # Total row for Comm diffs
    r_tot_c = 4 + len(all_comm_diffs) + 1
    ws3.row_dimensions[r_tot_c].height = 22
    tot_c_vals = [
        ("ИТОГО", align_center, font_total),
        (f"{len(all_comm_diffs)} сделок", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        (sum(x['crm_price'] for x in all_comm_diffs), align_right, font_total, FMT_RUB),
        (sum(x['crm_comm'] for x in all_comm_diffs), align_right, font_total, FMT_RUB),
        (sum(x['report_comm'] for x in all_comm_diffs), align_right, font_total, FMT_RUB),
        (sum(x['diff_comm'] for x in all_comm_diffs), align_right, font_total, FMT_DIFF),
        ("", align_center, font_total)
    ]
    for col_i, d_val in enumerate(tot_c_vals, 1):
        c = ws3.cell(row=r_tot_c, column=col_i, value=d_val[0])
        c.alignment = d_val[1]
        c.font = d_val[2]
        c.fill = fill_total
        c.border = total_border
        if len(d_val) > 3 and d_val[3]: c.number_format = d_val[3]

    ws3.auto_filter.ref = f"A4:L{4 + len(all_comm_diffs)}"

    # =============================================================
    # ЛИСТ 4: ЕСТЬ В CRM, НЕТ В ОТЧЕТАХ (Missing in reports)
    # =============================================================
    ws4 = wb.create_sheet(title="Есть в CRM, нет в отчетах")
    ws4.views.sheetView[0].showGridLines = True

    ws4.merge_cells("A1:I1")
    ws4["A1"] = "СДЕЛКИ В CRM (ДАШБОРДЕ), ПО КОТОРЫМ НЕ НАЙДЕНО ОТЧЕТОВ В ПАПКЕ"
    ws4["A1"].font = font_title
    ws4["A1"].alignment = align_left

    ws4.merge_cells("A2:I2")
    ws4["A2"] = f"Всего {len(missing_in_reports)} сделок (из них 18 приходятся на «Восток-Авто», чей файл отчета отсутствует в предоставленной папке)"
    ws4["A2"].font = font_subtitle
    ws4["A2"].alignment = align_left

    h_m1 = ["№", "ID сделки", "VIN автомобиля", "Бренд", "Модель", "Дилер / Компания в CRM", "Стоимость авто (₽)", "Комиссия СА (₽)", "Комментарий / Причина отсутствия"]
    ws4.row_dimensions[4].height = 24
    for col_i, h in enumerate(h_m1, 1):
        c = ws4.cell(row=4, column=col_i, value=h)
        c.font = font_head
        c.fill = fill_head
        c.alignment = align_center
        c.border = thin_border

    for idx, v in enumerate(missing_in_reports, 1):
        s = sys_by_vin[v]
        r_num = 4 + idx
        ws4.row_dimensions[r_num].height = 19
        fill_cur = fill_zebra if (idx % 2 == 0) else PatternFill(fill_type=None)

        comp = s['company']
        if 'восток-авто' in comp.lower():
            comment = "Файл отчета «Восток-Авто» отсутствует в предоставленной папке"
        else:
            comment = "Отчет по дилеру не найден в папке или закрыт другим документом"

        row_vals = [
            (idx, align_center, font_num, FMT_QTY),
            (s['deal_id'], align_center, font_bold),
            (s['vin'], align_center, font_normal),
            (s['brand'], align_center, font_normal),
            (s['model'], align_left, font_normal),
            (comp, align_left, font_normal),
            (s['price'], align_right, font_bold, FMT_RUB),
            (s['comm'], align_right, font_bold, FMT_RUB),
            (comment, align_left, font_normal)
        ]

        for col_i, d_val in enumerate(row_vals, 1):
            c = ws4.cell(row=r_num, column=col_i, value=d_val[0])
            c.alignment = d_val[1]
            c.font = d_val[2]
            c.border = thin_border
            if fill_cur.fill_type: c.fill = fill_cur
            if len(d_val) > 3 and d_val[3]: c.number_format = d_val[3]

    r_tot_m1 = 4 + len(missing_in_reports) + 1
    ws4.row_dimensions[r_tot_m1].height = 22
    tot_m1_vals = [
        ("ИТОГО", align_center, font_total),
        (f"{len(missing_in_reports)} сделок", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        (sum(sys_by_vin[v]['price'] for v in missing_in_reports), align_right, font_total, FMT_RUB),
        (sum(sys_by_vin[v]['comm'] for v in missing_in_reports), align_right, font_total, FMT_RUB),
        ("", align_center, font_total)
    ]
    for col_i, d_val in enumerate(tot_m1_vals, 1):
        c = ws4.cell(row=r_tot_m1, column=col_i, value=d_val[0])
        c.alignment = d_val[1]
        c.font = d_val[2]
        c.fill = fill_total
        c.border = total_border
        if len(d_val) > 3 and d_val[3]: c.number_format = d_val[3]

    ws4.auto_filter.ref = f"A4:I{4 + len(missing_in_reports)}"

    # =============================================================
    # ЛИСТ 5: ЕСТЬ В ОТЧЕТАХ, НЕТ В CRM (Missing in CRM)
    # =============================================================
    ws5 = wb.create_sheet(title="Есть в отчетах, нет в CRM")
    ws5.views.sheetView[0].showGridLines = True

    ws5.merge_cells("A1:H1")
    ws5["A1"] = "СДЕЛКИ В ОТЧЕТАХ АГЕНТА, КОТОРЫХ НЕТ В ПРОДАЖАХ АВГУСТА В ДАШБОРДЕ"
    ws5["A1"].font = font_title
    ws5["A1"].alignment = align_left

    ws5.merge_cells("A2:H2")
    ws5["A2"] = f"Всего {len(missing_in_dashboard)} сделок (переходящие из июля, субагенты, неквалифицированные сделки)"
    ws5["A2"].font = font_subtitle
    ws5["A2"].alignment = align_left

    h_m2 = ["№", "VIN автомобиля", "Марка / Модель", "Файл отчета агента", "Стоимость авто (₽)", "Вознаграждение (₽)", "Номер и дата ДКП", "Причина отсутствия в августе"]
    ws5.row_dimensions[4].height = 24
    for col_i, h in enumerate(h_m2, 1):
        c = ws5.cell(row=4, column=col_i, value=h)
        c.font = font_head
        c.fill = fill_head
        c.alignment = align_center
        c.border = thin_border

    # Analyze reasons for missing_in_dashboard
    july_vins = {
        'XTA219040T1244965': 'Продажа закрыта в CRM в Июле 2026 (DID 496872), выставлена дилеру в августе',
        'EC37LUSM6TC007211': 'Продажа закрыта в CRM в Июле 2026 (DID 484526), выставлена дилеру в августе',
        'XTA219040T1256279': 'Продажа закрыта в CRM в Июле 2026 (DID 475470), выставлена дилеру в августе',
        'EC37LUSM7TC005001': 'Продажа закрыта в CRM в Июле 2026 (DID 504820), выставлена дилеру в августе',
        'JMBXTGA2WDE715698': 'Сделка DID 504672 (Mitsubishi ASX, Альянс) — без типа B2C в CRM',
        'EC3DCUFD3TC013545': 'Тестовая / пустая строка в отчете Радар-Центр (Цена 0, Вознаграждение 0)'
    }

    for idx, v in enumerate(missing_in_dashboard, 1):
        a = agent_by_vin[v][0]
        r_num = 4 + idx
        ws5.row_dimensions[r_num].height = 19
        fill_cur = fill_zebra if (idx % 2 == 0) else PatternFill(fill_type=None)

        expl = july_vins.get(v, "Сделка субагента / не заведена в сделки CRM")

        row_vals = [
            (idx, align_center, font_num, FMT_QTY),
            (v, align_center, font_normal),
            (f"{a['brand']} {a['model']}".strip(), align_left, font_normal),
            (a['source'], align_left, font_normal),
            (a['price'], align_right, font_bold, FMT_RUB),
            (a['comm'], align_right, font_bold, FMT_RUB),
            (f"{a['dkp_num']} от {a['dkp_date']}".strip(), align_center, font_normal),
            (expl, align_left, font_normal)
        ]

        for col_i, d_val in enumerate(row_vals, 1):
            c = ws5.cell(row=r_num, column=col_i, value=d_val[0])
            c.alignment = d_val[1]
            c.font = d_val[2]
            c.border = thin_border
            if fill_cur.fill_type: c.fill = fill_cur
            if len(d_val) > 3 and d_val[3]: c.number_format = d_val[3]

    r_tot_m2 = 4 + len(missing_in_dashboard) + 1
    ws5.row_dimensions[r_tot_m2].height = 22
    tot_m2_vals = [
        ("ИТОГО", align_center, font_total),
        (f"{len(missing_in_dashboard)} сделок", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        (sum(agent_by_vin[v][0]['price'] for v in missing_in_dashboard), align_right, font_total, FMT_RUB),
        (sum(agent_by_vin[v][0]['comm'] for v in missing_in_dashboard), align_right, font_total, FMT_RUB),
        ("", align_center, font_total),
        ("", align_center, font_total)
    ]
    for col_i, d_val in enumerate(tot_m2_vals, 1):
        c = ws5.cell(row=r_tot_m2, column=col_i, value=d_val[0])
        c.alignment = d_val[1]
        c.font = d_val[2]
        c.fill = fill_total
        c.border = total_border
        if len(d_val) > 3 and d_val[3]: c.number_format = d_val[3]

    ws5.auto_filter.ref = f"A4:H{4 + len(missing_in_dashboard)}"

    # Adjust column widths for all sheets
    for ws in [ws2, ws3, ws4, ws5]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                max_len = max(max_len, len(val_str))
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
        ws.freeze_panes = "A5"

    ws2.column_dimensions['A'].width = 6
    ws2.column_dimensions['B'].width = 12
    ws2.column_dimensions['C'].width = 22
    ws2.column_dimensions['F'].width = 32
    ws2.column_dimensions['G'].width = 38

    ws3.column_dimensions['A'].width = 6
    ws3.column_dimensions['B'].width = 12
    ws3.column_dimensions['C'].width = 22
    ws3.column_dimensions['F'].width = 32
    ws3.column_dimensions['G'].width = 38
    ws3.column_dimensions['L'].width = 38

    ws4.column_dimensions['A'].width = 6
    ws4.column_dimensions['B'].width = 12
    ws4.column_dimensions['C'].width = 22
    ws4.column_dimensions['F'].width = 35
    ws4.column_dimensions['I'].width = 45

    ws5.column_dimensions['A'].width = 6
    ws5.column_dimensions['B'].width = 22
    ws5.column_dimensions['D'].width = 35
    ws5.column_dimensions['H'].width = 50

    # Save to Downloads & reports
    fname = "Сверка_отчетов_агента_и_дашборда_Август_2026.xlsx"
    path_dl = os.path.expanduser(f"~/Downloads/{fname}")
    path_rep = os.path.join(PROJECT_ROOT, 'reports', fname)
    path_root = os.path.join(PROJECT_ROOT, fname)

    wb.save(path_dl)
    wb.save(path_rep)
    wb.save(path_root)

    print(f"[+] Файл успешно сохранен в Загрузки: {path_dl}")
    print(f"[+] Файл успешно сохранен в reports: {path_rep}")

if __name__ == '__main__':
    main()
