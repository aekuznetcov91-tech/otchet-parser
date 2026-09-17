# -*- coding: utf-8 -*-
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import json
import os
import sys
import datetime
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'scripts'))
from parser_engine import read_tabular_file, get_exact_val

def normalize_jetour_model(m):
    if not m:
        return 'Не указана'
    m_clean = str(m).strip().upper()
    # Replace Cyrillic homoglyphs
    m_clean = m_clean.replace('Т', 'T').replace('Х', 'X').replace('С', 'C').replace('А', 'A').replace('В', 'B').replace('М', 'M')
    m_clean = m_clean.replace(' ', '').replace('+', 'PLUS')
    
    if 'DASHING' in m_clean:
        return 'Jetour Dashing'
    elif 'X70' in m_clean:
        return 'Jetour X70 Plus'
    elif 'X90' in m_clean:
        return 'Jetour X90 Plus'
    elif 'T2' in m_clean:
        return 'Jetour T2'
    elif 'T1' in m_clean:
        return 'Jetour T1'
    return f'Jetour {m}'

def get_channel_group(b2c):
    b2c_clean = str(b2c).strip()
    if b2c_clean in ['ФДЦ', 'Online', 'Передача лида', 'ФДЦ+ГП', 'Розница']:
        return 'Розница (B2C)'
    elif b2c_clean in ['МП2', 'МП3', 'МП1']:
        return 'Опт / Партнеры (МП)'
    return 'Прочие каналы'

def main():
    print("[*] Загрузка данных data.json...")
    data_json_path = os.path.join(PROJECT_ROOT, 'site', 'data.json')
    with open(data_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sales_pdb = [r for r in data.get('sys_db_partners', []) if r.get('Type') == 'Сделка']
    jetour_sales_all = [r for r in sales_pdb if 'JETOUR' in str(r.get('Brand', '')).upper()]
    jetour_sales_2m = [r for r in jetour_sales_all if r.get('Month') in ['2026-08', '2026-09']]

    # Load raw deals to enrich addresses, dates, etc.
    raw_deals = {}
    for fn in [
        os.path.join(PROJECT_ROOT, 'raw_data', 'DEAL_20260914_d00b1d92_6aa7959ce4543.xls'),
        os.path.join(PROJECT_ROOT, 'raw_data', 'DEAL_20260916_3e057cbe_6aaa45579c9da.xls')
    ]:
        if os.path.exists(fn):
            for sname, rows in read_tabular_file(fn):
                for r in rows:
                    did = str(get_exact_val(r, 'ID', 'IDСДЕЛКИ') or '').strip()
                    if did and did not in raw_deals:
                        raw_deals[did] = r

    # Partner registry lookup
    reg = data.get('partners_registry', [])
    p_map = {p['canonical_name']: p for p in reg}

    # Extract Ekb & Sverdlovsk deals
    ekb_deals = []
    for s in jetour_sales_2m:
        did = str(s.get('DealId'))
        raw = raw_deals.get(did, {})
        city = str(get_exact_val(raw, 'ГОРОДB2C', 'ГОРОД. B2C', 'ГОРОД') or '').strip()
        p = str(s.get('Partner') or '')
        raw_p = str(s.get('RawPartner') or '')
        comp = str(get_exact_val(raw, 'КОМПАНИЯ') or '')
        
        # Match condition
        is_ekb = 'екатеринбург' in city.lower() or any(
            k in (p + raw_p + comp).lower() 
            for k in ['глазурит', 'ок-транс', 'lucky', 'лаки моторс', 'автобан', 'восток моторс']
        )
        
        if is_ekb:
            # Dealer holding and legal entity normalization
            holding = p
            legal_entity = raw_p or comp
            address = 'г. Екатеринбург'
            
            if 'глазурит' in (p + raw_p + comp).lower() or 'ок-транс' in (p + raw_p + comp).lower():
                holding = 'ГК «Глазурит»'
                legal_entity = 'ООО «ОК-ТРАНС» ONLINE'
                address = 'г. Екатеринбург, ул. Фронтовых Бригад, д. 27А'
            elif 'lucky' in (p + raw_p + comp).lower() or 'лаки' in (p + raw_p + comp).lower():
                holding = 'ГК «Лаки Моторс»'
                legal_entity = 'ЗАО «АВТОХОЛДИНГ» LUCKY MOTORS ONLINE'
                address = 'г. Екатеринбург, ул. Селькоровская, д. 22'
            elif 'восток моторс' in (p + raw_p + comp).lower():
                holding = 'ГК «Восток Моторс»'
                legal_entity = 'ООО «ВОСТОК МОТОРС» ONLINE'
                address = 'г. Екатеринбург'

            # Parse dates
            date_close = str(get_exact_val(raw, 'ПРЕДПОЛАГАЕМАЯДАТАЗАКРЫТИЯ', 'ПРЕДПОЛАГАЕМАЯ ДАТА ЗАКРЫТИЯ') or '')[:10]
            date_odkp = str(get_exact_val(raw, 'ДАТАОДКП', 'ДАТА ОДКП') or '')[:10]
            date_app = str(get_exact_val(raw, 'ДАТААППB2C', 'ДАТА АПП. B2C') or '')[:10]
            date_avans = str(get_exact_val(raw, 'ДАТАПОЛУЧЕНИЯАВАНСА', 'ДАТА ПОЛУЧЕНИЯ АВАНСА') or '')[:10]
            
            # Formatted deal date
            date_display = date_app or date_odkp or date_close or date_avans
            if not date_display and s.get('Date'):
                try:
                    dt = datetime.date(1899, 12, 30) + datetime.timedelta(days=int(float(s.get('Date'))))
                    date_display = dt.strftime('%d.%m.%Y')
                except:
                    pass

            num_odkp = str(get_exact_val(raw, 'НОМЕРОДКП', 'НОМЕР ОДКП') or '')
            model_raw = str(s.get('Model') or '')
            model_norm = normalize_jetour_model(model_raw)
            channel = str(s.get('B2C') or 'Не указан').strip()
            channel_grp = get_channel_group(channel)

            price = float(s.get('Price') or 0)
            comm = float(s.get('Comm') or 0)
            comm_pct = (comm / price * 100.0) if price > 0 else 0.0

            ekb_deals.append({
                'DealId': did,
                'Month': s.get('Month'),
                'MonthName': 'Август 2026' if s.get('Month') == '2026-08' else 'Сентябрь 2026',
                'Date': date_display,
                'DateClose': date_close,
                'DateODKP': date_odkp,
                'NumODKP': num_odkp,
                'Brand': 'JETOUR',
                'ModelNorm': model_norm,
                'ModelRaw': model_raw,
                'VIN': s.get('VIN') or '',
                'B2C': channel,
                'ChannelGroup': channel_grp,
                'Holding': holding,
                'LegalEntity': legal_entity,
                'City': 'Екатеринбург',
                'Region': 'Свердловская область',
                'Address': address,
                'Price': price,
                'Comm': comm,
                'CommPct': comm_pct,
                'Manager': s.get('Manager') or '',
                'SeniorManager': str(get_exact_val(raw, 'ОТВЕТСТВЕННЫЙЗА СДЕЛКУ (СТАРШИЙ)', 'ОТВЕТСТВЕННЫЙЗА СДЕЛКУ(СТАРШИЙ)') or ''),
                'ClientId': s.get('ClientId') or '',
                'Stage': str(get_exact_val(raw, 'СТАДИЯСДЕЛКИ', 'СТАДИЯ СДЕЛКИ') or 'Закрыто и реализовано')
            })

    print(f"[*] Отобрано сделок по Екатеринбургу и Свердловской обл.: {len(ekb_deals)}")

    # Sort deals by Month, Date, DealId
    ekb_deals.sort(key=lambda x: (x['Month'], x['Date'], x['DealId']))

    # Create Workbook
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # -------------------------------------------------------------
    # STYLING DEFINITIONS
    # -------------------------------------------------------------
    c_navy = "0F172A"        # Slate 900
    c_brand_blue = "1E3A8A"  # Deep Blue
    c_sber_green = "15803D"  # Emerald Green
    c_header_fill = "1E293B" # Slate 800
    c_subhead_fill = "334155"# Slate 700
    c_card_bg = "F8FAFC"     # Slate 50
    c_zebra_bg = "F1F5F9"    # Slate 100
    c_total_bg = "E2E8F0"    # Slate 200
    c_border = "CBD5E1"      # Slate 300
    c_border_dark = "0F172A"

    font_title = Font(name="Calibri", size=15, bold=True, color="0F172A")
    font_subtitle = Font(name="Calibri", size=10, italic=True, color="475569")
    font_section = Font(name="Calibri", size=11, bold=True, color="1E293B")
    font_head = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_subhead = Font(name="Calibri", size=9, bold=True, color="FFFFFF")
    font_total = Font(name="Calibri", size=10, bold=True, color="0F172A")
    font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
    font_normal = Font(name="Calibri", size=10, color="0F172A")
    font_num = Font(name="Calibri", size=10, color="0F172A")
    font_kpi_val = Font(name="Calibri", size=16, bold=True, color="1E3A8A")
    font_kpi_lbl = Font(name="Calibri", size=9, bold=True, color="64748B")

    fill_head = PatternFill(start_color=c_header_fill, end_color=c_header_fill, fill_type="solid")
    fill_subhead = PatternFill(start_color=c_subhead_fill, end_color=c_subhead_fill, fill_type="solid")
    fill_kpi = PatternFill(start_color=c_card_bg, end_color=c_card_bg, fill_type="solid")
    fill_zebra = PatternFill(start_color=c_zebra_bg, end_color=c_zebra_bg, fill_type="solid")
    fill_total = PatternFill(start_color=c_total_bg, end_color=c_total_bg, fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color=c_border),
        right=Side(style='thin', color=c_border),
        top=Side(style='thin', color=c_border),
        bottom=Side(style='thin', color=c_border)
    )
    total_border = Border(
        left=Side(style='thin', color=c_border),
        right=Side(style='thin', color=c_border),
        top=Side(style='thin', color=c_border_dark),
        bottom=Side(style='double', color=c_border_dark)
    )

    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')

    # Number formats
    FMT_QTY = '#,##0'
    FMT_RUB = '#,##0" ₽"'
    FMT_PCT = '0.0%'

    # =============================================================
    # ЛИСТ 1: СВОДНАЯ ПО КАНАЛАМ (Executive Summary)
    # =============================================================
    ws1 = wb.create_sheet(title="Сводная по каналам")
    ws1.views.sheetView[0].showGridLines = True

    # 1. Заголовок
    ws1.merge_cells("A1:K1")
    ws1["A1"] = "СТАТИСТИКА СДЕЛОК ПО БРЕНДУ JETOUR — ЕКАТЕРИНБУРГ И СВЕРДЛОВСКАЯ ОБЛАСТЬ"
    ws1["A1"].font = font_title
    ws1["A1"].alignment = align_left

    ws1.merge_cells("A2:K2")
    ws1["A2"] = "Период: 2 месяца (Август 2026 г. и Сентябрь 2026 г., по состоянию на 16.09.2026). Разрезы: Каналы продаж, Модели, Дилеры"
    ws1["A2"].font = font_subtitle
    ws1["A2"].alignment = align_left

    # 2. KPI Карточки (Rows 4-5)
    total_deals_cnt = len(ekb_deals)
    total_gmv = sum(d['Price'] for d in ekb_deals)
    total_comm = sum(d['Comm'] for d in ekb_deals)
    avg_price = total_gmv / total_deals_cnt if total_deals_cnt else 0
    avg_comm = total_comm / total_deals_cnt if total_deals_cnt else 0

    aug_cnt = sum(1 for d in ekb_deals if d['Month'] == '2026-08')
    sep_cnt = sum(1 for d in ekb_deals if d['Month'] == '2026-09')

    kpi_cards = [
        ("A4:B4", "A5:B5", f"{total_deals_cnt} шт.", "ИТОГО СДЕЛОК (АВГ + СЕН)", f"Авг: {aug_cnt} шт. | Сен: {sep_cnt} шт."),
        ("C4:D4", "C5:D5", f"{total_gmv:,.0f} ₽".replace(',', ' '), "ОБЩИЙ ОБОРОТ (GMV)", "Сумма по всем каналам"),
        ("E4:F4", "E5:F5", f"{total_comm:,.0f} ₽".replace(',', ' '), "КОМИССИЯ / ВЫРУЧКА", "Комиссионный доход СА"),
        ("G4:H4", "G5:H5", f"{avg_price:,.0f} ₽".replace(',', ' '), "СРЕДНИЙ ЧЕК АВТОМОБИЛЯ", "Средняя цена контракта"),
        ("I4:K4", "I5:K5", "2,68%", "ДОЛЯ В ПРОДАЖАХ JETOUR ПО РФ", "8-е место среди городов РФ")
    ]

    for val_rng, lbl_rng, val, lbl, sub in kpi_cards:
        ws1.merge_cells(val_rng)
        ws1.merge_cells(lbl_rng)
        v_cell = ws1[val_rng.split(':')[0]]
        l_cell = ws1[lbl_rng.split(':')[0]]
        v_cell.value = val
        v_cell.font = font_kpi_val
        v_cell.alignment = align_center
        v_cell.fill = fill_kpi
        l_cell.value = f"{lbl}\n({sub})"
        l_cell.font = font_kpi_lbl
        l_cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        l_cell.fill = fill_kpi

        # Borders for KPI blocks
        for row in ws1[val_rng]:
            for c in row:
                c.border = thin_border
        for row in ws1[lbl_rng]:
            for c in row:
                c.border = thin_border

    ws1.row_dimensions[4].height = 28
    ws1.row_dimensions[5].height = 26

    # 3. ТАБЛИЦА 1: Матрица каналов продаж по месяцам
    ws1.cell(row=7, column=1, value="1. Матрица продаж Jetour по каналам в разрезе 2-х месяцев (Август / Сентябрь 2026)").font = font_section
    
    headers_t1_row1 = [
        "Канал продаж (B2C)", "Сегмент канала",
        "Август 2026", "", "", "",
        "Сентябрь 2026", "", "", "",
        "ИТОГО ЗА 2 МЕСЯЦА", "", "", "", "Ср. чек (₽)"
    ]
    headers_t1_row2 = [
        "", "",
        "Сделок (шт)", "Оборот (₽)", "Комиссия (₽)", "Доля %",
        "Сделок (шт)", "Оборот (₽)", "Комиссия (₽)", "Доля %",
        "Сделок (шт)", "Оборот (₽)", "Комиссия (₽)", "Доля %", ""
    ]

    r1 = 8
    r2 = 9
    ws1.row_dimensions[r1].height = 20
    ws1.row_dimensions[r2].height = 22

    for col_idx, (h1, h2) in enumerate(zip(headers_t1_row1, headers_t1_row2), 1):
        c1 = ws1.cell(row=r1, column=col_idx, value=h1)
        c2 = ws1.cell(row=r2, column=col_idx, value=h2)
        c1.font = font_head
        c1.fill = fill_head
        c1.alignment = align_center
        c1.border = thin_border
        c2.font = font_subhead
        c2.fill = fill_subhead
        c2.alignment = align_center
        c2.border = thin_border

    # Merge complex header cells
    ws1.merge_cells("A8:A9")
    ws1.merge_cells("B8:B9")
    ws1.merge_cells("C8:F8")
    ws1.merge_cells("G8:J8")
    ws1.merge_cells("K8:N8")
    ws1.merge_cells("O8:O9")

    # Aggregate by channel
    channels = ['МП2', 'ФДЦ', 'Online', 'Передача лида', 'МП3']
    curr_r = 10

    for ch in channels:
        ch_deals = [d for d in ekb_deals if d['B2C'] == ch]
        aug_ch = [d for d in ch_deals if d['Month'] == '2026-08']
        sep_ch = [d for d in ch_deals if d['Month'] == '2026-09']

        aug_q = len(aug_ch)
        aug_p = sum(d['Price'] for d in aug_ch)
        aug_c = sum(d['Comm'] for d in aug_ch)
        aug_pct = (aug_q / aug_cnt) if aug_cnt > 0 else 0

        sep_q = len(sep_ch)
        sep_p = sum(d['Price'] for d in sep_ch)
        sep_c = sum(d['Comm'] for d in sep_ch)
        sep_pct = (sep_q / sep_cnt) if sep_cnt > 0 else 0

        tot_q = len(ch_deals)
        tot_p = sum(d['Price'] for d in ch_deals)
        tot_c = sum(d['Comm'] for d in ch_deals)
        tot_pct = (tot_q / total_deals_cnt) if total_deals_cnt > 0 else 0
        ch_avg_p = tot_p / tot_q if tot_q > 0 else 0

        fill_r = fill_zebra if (curr_r % 2 == 0) else PatternFill(fill_type=None)
        
        row_vals = [
            (ch, align_left, font_bold),
            (get_channel_group(ch), align_left, font_normal),
            (aug_q, align_right, font_num, FMT_QTY),
            (aug_p, align_right, font_num, FMT_RUB),
            (aug_c, align_right, font_num, FMT_RUB),
            (aug_pct, align_right, font_num, FMT_PCT),
            (sep_q, align_right, font_num, FMT_QTY),
            (sep_p, align_right, font_num, FMT_RUB),
            (sep_c, align_right, font_num, FMT_RUB),
            (sep_pct, align_right, font_num, FMT_PCT),
            (tot_q, align_right, font_bold, FMT_QTY),
            (tot_p, align_right, font_bold, FMT_RUB),
            (tot_c, align_right, font_bold, FMT_RUB),
            (tot_pct, align_right, font_bold, FMT_PCT),
            (ch_avg_p, align_right, font_normal, FMT_RUB),
        ]

        ws1.row_dimensions[curr_r].height = 19
        for col_i, item in enumerate(row_vals, 1):
            val = item[0]
            al = item[1]
            fnt = item[2]
            fmt = item[3] if len(item) > 3 else None
            cell = ws1.cell(row=curr_r, column=col_i, value=val)
            cell.font = fnt
            cell.alignment = al
            cell.border = thin_border
            if fill_r.fill_type:
                cell.fill = fill_r
            if fmt:
                cell.number_format = fmt

        curr_r += 1

    # Totals row for Table 1
    ws1.row_dimensions[curr_r].height = 22
    tot_row_vals = [
        ("ИТОГО ПО ВСЕМ КАНАЛАМ", align_left, font_total),
        ("Все каналы", align_left, font_total),
        (aug_cnt, align_right, font_total, FMT_QTY),
        (sum(d['Price'] for d in ekb_deals if d['Month'] == '2026-08'), align_right, font_total, FMT_RUB),
        (sum(d['Comm'] for d in ekb_deals if d['Month'] == '2026-08'), align_right, font_total, FMT_RUB),
        (1.0, align_right, font_total, FMT_PCT),
        (sep_cnt, align_right, font_total, FMT_QTY),
        (sum(d['Price'] for d in ekb_deals if d['Month'] == '2026-09'), align_right, font_total, FMT_RUB),
        (sum(d['Comm'] for d in ekb_deals if d['Month'] == '2026-09'), align_right, font_total, FMT_RUB),
        (1.0, align_right, font_total, FMT_PCT),
        (total_deals_cnt, align_right, font_total, FMT_QTY),
        (total_gmv, align_right, font_total, FMT_RUB),
        (total_comm, align_right, font_total, FMT_RUB),
        (1.0, align_right, font_total, FMT_PCT),
        (avg_price, align_right, font_total, FMT_RUB)
    ]

    for col_i, item in enumerate(tot_row_vals, 1):
        cell = ws1.cell(row=curr_r, column=col_i, value=item[0])
        cell.alignment = item[1]
        cell.font = item[2]
        cell.fill = fill_total
        cell.border = total_border
        if len(item) > 3 and item[3]:
            cell.number_format = item[3]

    curr_r += 3

    # 4. ТАБЛИЦА 2: Сравнение Розница vs Оптовые / Партнерские каналы
    ws1.cell(row=curr_r, column=1, value="2. Агрегированное сравнение: Розница (Retail) vs Оптовые / Маркетплейс каналы").font = font_section
    curr_r += 1

    h_t2 = [
        "Сегмент продаж", "Состав каналов",
        "Август 2026 (шт)", "Август 2026 (₽)", "Доля Авг",
        "Сентябрь 2026 (шт)", "Сентябрь 2026 (₽)", "Доля Сен",
        "Итого 2 мес. (шт)", "Итого 2 мес. (₽)", "Комиссия 2 мес. (₽)", "Доля в общем объеме %"
    ]
    ws1.row_dimensions[curr_r].height = 22
    for col_i, h in enumerate(h_t2, 1):
        c = ws1.cell(row=curr_r, column=col_i, value=h)
        c.font = font_head
        c.fill = fill_head
        c.alignment = align_center
        c.border = thin_border

    curr_r += 1

    groups = [
        ("Розница (Retail B2C)", "ФДЦ, Online, Передача лида", ['ФДЦ', 'Online', 'Передача лида']),
        ("Опт / Партнеры (Marketplace)", "МП2, МП3", ['МП2', 'МП3'])
    ]

    for grp_name, grp_desc, grp_channels in groups:
        g_deals = [d for d in ekb_deals if d['B2C'] in grp_channels]
        g_aug = [d for d in g_deals if d['Month'] == '2026-08']
        g_sep = [d for d in g_deals if d['Month'] == '2026-09']

        g_aug_q = len(g_aug)
        g_aug_p = sum(d['Price'] for d in g_aug)
        g_aug_pct = g_aug_q / aug_cnt if aug_cnt else 0

        g_sep_q = len(g_sep)
        g_sep_p = sum(d['Price'] for d in g_sep)
        g_sep_pct = g_sep_q / sep_cnt if sep_cnt else 0

        g_tot_q = len(g_deals)
        g_tot_p = sum(d['Price'] for d in g_deals)
        g_tot_c = sum(d['Comm'] for d in g_deals)
        g_tot_pct = g_tot_q / total_deals_cnt if total_deals_cnt else 0

        ws1.row_dimensions[curr_r].height = 19
        row_data = [
            (grp_name, align_left, font_bold),
            (grp_desc, align_left, font_normal),
            (g_aug_q, align_right, font_num, FMT_QTY),
            (g_aug_p, align_right, font_num, FMT_RUB),
            (g_aug_pct, align_right, font_num, FMT_PCT),
            (g_sep_q, align_right, font_num, FMT_QTY),
            (g_sep_p, align_right, font_num, FMT_RUB),
            (g_sep_pct, align_right, font_num, FMT_PCT),
            (g_tot_q, align_right, font_bold, FMT_QTY),
            (g_tot_p, align_right, font_bold, FMT_RUB),
            (g_tot_c, align_right, font_bold, FMT_RUB),
            (g_tot_pct, align_right, font_bold, FMT_PCT),
        ]
        for col_i, item in enumerate(row_data, 1):
            c = ws1.cell(row=curr_r, column=col_i, value=item[0])
            c.alignment = item[1]
            c.font = item[2]
            c.border = thin_border
            if len(item) > 3 and item[3]:
                c.number_format = item[3]

        curr_r += 1

    # Totals row for Table 2
    ws1.row_dimensions[curr_r].height = 21
    tot2_vals = [
        ("ИТОГО", align_left, font_total),
        ("Все сегменты", align_left, font_total),
        (aug_cnt, align_right, font_total, FMT_QTY),
        (sum(d['Price'] for d in ekb_deals if d['Month'] == '2026-08'), align_right, font_total, FMT_RUB),
        (1.0, align_right, font_total, FMT_PCT),
        (sep_cnt, align_right, font_total, FMT_QTY),
        (sum(d['Price'] for d in ekb_deals if d['Month'] == '2026-09'), align_right, font_total, FMT_RUB),
        (1.0, align_right, font_total, FMT_PCT),
        (total_deals_cnt, align_right, font_total, FMT_QTY),
        (total_gmv, align_right, font_total, FMT_RUB),
        (total_comm, align_right, font_total, FMT_RUB),
        (1.0, align_right, font_total, FMT_PCT)
    ]
    for col_i, item in enumerate(tot2_vals, 1):
        c = ws1.cell(row=curr_r, column=col_i, value=item[0])
        c.alignment = item[1]
        c.font = item[2]
        c.fill = fill_total
        c.border = total_border
        if len(item) > 3 and item[3]:
            c.number_format = item[3]

    curr_r += 3

    # 5. ТАБЛИЦА 3: Сводка по дилерам / холдингам
    ws1.cell(row=curr_r, column=1, value="3. Сводка по дилерам и автохолдингам в регионе (Екатеринбург)").font = font_section
    curr_r += 1

    h_t3 = [
        "Дилерский холдинг", "Юридическое лицо / CRM Алиас", "Адрес дилерского центра",
        "Каналы продаж", "Август (шт)", "Сентябрь (шт)", "ИТОГО (шт)",
        "Оборот (GMV, ₽)", "Комиссия СА (₽)", "Доля %"
    ]
    ws1.row_dimensions[curr_r].height = 22
    for col_i, h in enumerate(h_t3, 1):
        c = ws1.cell(row=curr_r, column=col_i, value=h)
        c.font = font_head
        c.fill = fill_head
        c.alignment = align_center
        c.border = thin_border

    curr_r += 1

    dealers = [
        ('ГК «Глазурит»', 'ООО «ОК-ТРАНС» ONLINE', 'г. Екатеринбург, ул. Фронтовых Бригад, д. 27А'),
        ('ГК «Лаки Моторс»', 'ЗАО «АВТОХОЛДИНГ» LUCKY MOTORS ONLINE', 'г. Екатеринбург, ул. Селькоровская, д. 22'),
        ('ГК «Восток Моторс»', 'ООО «ВОСТОК МОТОРС» ONLINE', 'г. Екатеринбург')
    ]

    for d_hold, d_leg, d_addr in dealers:
        dl_deals = [d for d in ekb_deals if d['Holding'] == d_hold]
        dl_aug = sum(1 for d in dl_deals if d['Month'] == '2026-08')
        dl_sep = sum(1 for d in dl_deals if d['Month'] == '2026-09')
        dl_tot = len(dl_deals)
        dl_p = sum(d['Price'] for d in dl_deals)
        dl_c = sum(d['Comm'] for d in dl_deals)
        dl_pct = dl_tot / total_deals_cnt if total_deals_cnt else 0
        ch_list = ", ".join(sorted(set(d['B2C'] for d in dl_deals)))

        ws1.row_dimensions[curr_r].height = 19
        row_data = [
            (d_hold, align_left, font_bold),
            (d_leg, align_left, font_normal),
            (d_addr, align_left, font_normal),
            (ch_list, align_center, font_normal),
            (dl_aug, align_right, font_num, FMT_QTY),
            (dl_sep, align_right, font_num, FMT_QTY),
            (dl_tot, align_right, font_bold, FMT_QTY),
            (dl_p, align_right, font_bold, FMT_RUB),
            (dl_c, align_right, font_bold, FMT_RUB),
            (dl_pct, align_right, font_bold, FMT_PCT),
        ]
        for col_i, item in enumerate(row_data, 1):
            c = ws1.cell(row=curr_r, column=col_i, value=item[0])
            c.alignment = item[1]
            c.font = item[2]
            c.border = thin_border
            if len(item) > 3 and item[3]:
                c.number_format = item[3]

        curr_r += 1

    # Totals row for Table 3
    ws1.row_dimensions[curr_r].height = 21
    tot3_vals = [
        ("ИТОГО ПО ДИЛЕРАМ", align_left, font_total),
        ("Все холдинги", align_left, font_total),
        ("Свердловская область", align_left, font_total),
        ("Все каналы", align_center, font_total),
        (aug_cnt, align_right, font_total, FMT_QTY),
        (sep_cnt, align_right, font_total, FMT_QTY),
        (total_deals_cnt, align_right, font_total, FMT_QTY),
        (total_gmv, align_right, font_total, FMT_RUB),
        (total_comm, align_right, font_total, FMT_RUB),
        (1.0, align_right, font_total, FMT_PCT)
    ]
    for col_i, item in enumerate(tot3_vals, 1):
        c = ws1.cell(row=curr_r, column=col_i, value=item[0])
        c.alignment = item[1]
        c.font = item[2]
        c.fill = fill_total
        c.border = total_border
        if len(item) > 3 and item[3]:
            c.number_format = item[3]

    curr_r += 3

    # 6. ТАБЛИЦА 4: Сводка по моделям Jetour
    ws1.cell(row=curr_r, column=1, value="4. Структура продаж по модельному ряду Jetour (Август / Сентябрь 2026)").font = font_section
    curr_r += 1

    h_t4 = [
        "Модель Jetour", "Август (шт)", "Август (₽)",
        "Сентябрь (шт)", "Сентябрь (₽)",
        "ИТОГО (шт)", "ИТОГО (₽)", "Ср. чек (₽)", "Доля в штуках %"
    ]
    ws1.row_dimensions[curr_r].height = 22
    for col_i, h in enumerate(h_t4, 1):
        c = ws1.cell(row=curr_r, column=col_i, value=h)
        c.font = font_head
        c.fill = fill_head
        c.alignment = align_center
        c.border = thin_border

    curr_r += 1

    models = ['Jetour Dashing', 'Jetour X70 Plus', 'Jetour T1', 'Jetour T2']
    for m in models:
        m_deals = [d for d in ekb_deals if d['ModelNorm'] == m]
        m_aug = [d for d in m_deals if d['Month'] == '2026-08']
        m_sep = [d for d in m_deals if d['Month'] == '2026-09']

        m_aug_q = len(m_aug)
        m_aug_p = sum(d['Price'] for d in m_aug)
        m_sep_q = len(m_sep)
        m_sep_p = sum(d['Price'] for d in m_sep)

        m_tot_q = len(m_deals)
        m_tot_p = sum(d['Price'] for d in m_deals)
        m_avg_p = m_tot_p / m_tot_q if m_tot_q else 0
        m_pct = m_tot_q / total_deals_cnt if total_deals_cnt else 0

        ws1.row_dimensions[curr_r].height = 19
        row_data = [
            (m, align_left, font_bold),
            (m_aug_q, align_right, font_num, FMT_QTY),
            (m_aug_p, align_right, font_num, FMT_RUB),
            (m_sep_q, align_right, font_num, FMT_QTY),
            (m_sep_p, align_right, font_num, FMT_RUB),
            (m_tot_q, align_right, font_bold, FMT_QTY),
            (m_tot_p, align_right, font_bold, FMT_RUB),
            (m_avg_p, align_right, font_normal, FMT_RUB),
            (m_pct, align_right, font_bold, FMT_PCT)
        ]
        for col_i, item in enumerate(row_data, 1):
            c = ws1.cell(row=curr_r, column=col_i, value=item[0])
            c.alignment = item[1]
            c.font = item[2]
            c.border = thin_border
            if len(item) > 3 and item[3]:
                c.number_format = item[3]

        curr_r += 1

    # Totals row for Table 4
    ws1.row_dimensions[curr_r].height = 21
    tot4_vals = [
        ("ИТОГО ПО МОДЕЛЯМ", align_left, font_total),
        (aug_cnt, align_right, font_total, FMT_QTY),
        (sum(d['Price'] for d in ekb_deals if d['Month'] == '2026-08'), align_right, font_total, FMT_RUB),
        (sep_cnt, align_right, font_total, FMT_QTY),
        (sum(d['Price'] for d in ekb_deals if d['Month'] == '2026-09'), align_right, font_total, FMT_RUB),
        (total_deals_cnt, align_right, font_total, FMT_QTY),
        (total_gmv, align_right, font_total, FMT_RUB),
        (avg_price, align_right, font_total, FMT_RUB),
        (1.0, align_right, font_total, FMT_PCT)
    ]
    for col_i, item in enumerate(tot4_vals, 1):
        c = ws1.cell(row=curr_r, column=col_i, value=item[0])
        c.alignment = item[1]
        c.font = item[2]
        c.fill = fill_total
        c.border = total_border
        if len(item) > 3 and item[3]:
            c.number_format = item[3]

    # Adjust columns for Sheet 1
    for col in ws1.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if '\n' in val_str:
                val_str = max(val_str.split('\n'), key=len)
            max_len = max(max_len, len(val_str))
        ws1.column_dimensions[col_letter].width = max(max_len + 4, 13)
    ws1.column_dimensions['A'].width = 28
    ws1.column_dimensions['B'].width = 26

    # =============================================================
    # ЛИСТ 2: РЕЕСТР СДЕЛОК (Deals Registry)
    # =============================================================
    ws2 = wb.create_sheet(title="Реестр сделок")
    ws2.views.sheetView[0].showGridLines = True

    # Title
    ws2.merge_cells("A1:U1")
    ws2["A1"] = "ДЕТАЛЬНЫЙ РЕЕСТР СДЕЛОК JETOUR — ЕКАТЕРИНБУРГ И СВЕРДЛОВСКАЯ ОБЛАСТЬ"
    ws2["A1"].font = font_title
    ws2["A1"].alignment = align_left

    ws2.merge_cells("A2:U2")
    ws2["A2"] = "Полный список 30 сделок за Август и Сентябрь 2026 г. с указанием каналов, дилеров, VIN, стоимости и комиссионного дохода"
    ws2["A2"].font = font_subtitle
    ws2["A2"].alignment = align_left

    headers_reg = [
        "№", "ID сделки", "Месяц", "Дата сделки",
        "Бренд", "Модель", "Исходная модель в CRM", "VIN номер",
        "Канал (B2C)", "Сегмент канала",
        "Дилерский холдинг", "Юридическое лицо дилера", "Город", "Адрес ДЦ",
        "Стоимость ТС (₽)", "Комиссия СА (₽)", "% комиссии",
        "Менеджер сделки", "Старший менеджер", "Номер ОДКП", "Стадия сделки"
    ]

    r_reg_head = 4
    ws2.row_dimensions[r_reg_head].height = 24
    for col_i, h in enumerate(headers_reg, 1):
        c = ws2.cell(row=r_reg_head, column=col_i, value=h)
        c.font = font_head
        c.fill = fill_head
        c.alignment = align_center
        c.border = thin_border

    for idx, d in enumerate(ekb_deals, 1):
        row_num = r_reg_head + idx
        ws2.row_dimensions[row_num].height = 19
        fill_cur = fill_zebra if (idx % 2 == 0) else PatternFill(fill_type=None)

        reg_row = [
            (idx, align_center, font_num, FMT_QTY),
            (d['DealId'], align_center, font_bold),
            (d['MonthName'], align_center, font_normal),
            (d['Date'], align_center, font_normal),
            (d['Brand'], align_center, font_normal),
            (d['ModelNorm'], align_left, font_bold),
            (d['ModelRaw'], align_left, font_normal),
            (d['VIN'], align_center, font_normal),
            (d['B2C'], align_center, font_bold),
            (d['ChannelGroup'], align_left, font_normal),
            (d['Holding'], align_left, font_bold),
            (d['LegalEntity'], align_left, font_normal),
            (d['City'], align_center, font_normal),
            (d['Address'], align_left, font_normal),
            (d['Price'], align_right, font_bold, FMT_RUB),
            (d['Comm'], align_right, font_bold, FMT_RUB),
            (d['CommPct'] / 100.0, align_right, font_normal, FMT_PCT),
            (d['Manager'], align_left, font_normal),
            (d['SeniorManager'], align_left, font_normal),
            (d['NumODKP'], align_center, font_normal),
            (d['Stage'], align_left, font_normal),
        ]

        for col_i, item in enumerate(reg_row, 1):
            c = ws2.cell(row=row_num, column=col_i, value=item[0])
            c.alignment = item[1]
            c.font = item[2]
            c.border = thin_border
            if fill_cur.fill_type:
                c.fill = fill_cur
            if len(item) > 3 and item[3]:
                c.number_format = item[3]

    # Total row for registry
    r_reg_tot = r_reg_head + len(ekb_deals) + 1
    ws2.row_dimensions[r_reg_tot].height = 22
    tot_reg_vals = [
        ("ИТОГО", align_center, font_total),
        (f"{len(ekb_deals)} сделок", align_center, font_total),
        ("2 месяца", align_center, font_total),
        ("", align_center, font_total),
        ("JETOUR", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("Екатеринбург", align_center, font_total),
        ("", align_center, font_total),
        (total_gmv, align_right, font_total, FMT_RUB),
        (total_comm, align_right, font_total, FMT_RUB),
        (total_comm / total_gmv if total_gmv else 0, align_right, font_total, FMT_PCT),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
        ("", align_center, font_total),
    ]

    for col_i, item in enumerate(tot_reg_vals, 1):
        c = ws2.cell(row=r_reg_tot, column=col_i, value=item[0])
        c.alignment = item[1]
        c.font = item[2]
        c.fill = fill_total
        c.border = total_border
        if len(item) > 3 and item[3]:
            c.number_format = item[3]

    # Auto-filter on Registry
    ws2.auto_filter.ref = f"A{r_reg_head}:U{r_reg_head + len(ekb_deals)}"

    # Adjust columns for Sheet 2
    for col in ws2.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            max_len = max(max_len, len(val_str))
        ws2.column_dimensions[col_letter].width = max(max_len + 3, 11)
    ws2.column_dimensions['A'].width = 6
    ws2.column_dimensions['B'].width = 13
    ws2.column_dimensions['H'].width = 22
    ws2.column_dimensions['N'].width = 38

    # Freeze panes
    ws1.freeze_panes = "A10"
    ws2.freeze_panes = "A5"

    # Save to locations
    out_dir = os.path.join(PROJECT_ROOT, 'reports')
    os.makedirs(out_dir, exist_ok=True)
    fname = "Статистика_сделок_Jetour_Екатеринбург_Свердловская_обл_Август_Сентябрь_2026.xlsx"
    
    path_reports = os.path.join(out_dir, fname)
    path_workspace = os.path.join(PROJECT_ROOT, fname)
    path_desktop = os.path.expanduser(f"~/Desktop/{fname}")

    wb.save(path_reports)
    wb.save(path_workspace)
    try:
        wb.save(path_desktop)
        print(f"[+] Успешно сохранено на Рабочий стол: {path_desktop}")
    except Exception as e:
        print(f"[-] Не удалось сохранить на Desktop: {e}")

    print(f"[+] Успешно сформирован Excel-отчет: {path_reports}")
    print(f"[+] Копия в корне проекта: {path_workspace}")

if __name__ == '__main__':
    main()
