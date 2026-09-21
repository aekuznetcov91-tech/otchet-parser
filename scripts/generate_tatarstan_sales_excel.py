# -*- coding: utf-8 -*-
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import json
import os
import sys
import datetime
import pandas as pd

sys.path.insert(0, 'otchet-parser/scripts')
from parser_engine import read_tabular_file, get_exact_val, parse_custom_date, normalize_brand

# 1. Загрузка данных из data.json и DEAL_...
d = json.load(open('otchet-parser/site/data.json'))
aug_sales_db = [r for r in d['sys_db'] if r.get('SaleQty') == 1 and r.get('SaleMonth') == '2026-08']

deal_file = 'raw_data/DEAL_20260904_c9102cd3_6a9a5fa93d07b.xls'
if not os.path.exists(deal_file):
    deal_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'raw_data', 'DEAL_20260904_c9102cd3_6a9a5fa93d07b.xls')
datasets = read_tabular_file(deal_file)
deals_by_id = {str(get_exact_val(r, 'ID', 'IDСДЕЛКИ') or '').strip(): r for r in datasets[0][1]}

tatar_cities = ['казань', 'челны', 'нижнекамск', 'альметьевск', 'бугульм', 'елабуг', 'зеленодольск', 'лениногорск', 'чистополь', 'заинск']

master_tatar = []
for s in aug_sales_db:
    did = str(s.get('DealId') or '').strip()
    raw_r = deals_by_id.get(did, {})
    c = str(get_exact_val(raw_r, 'ГОРОДB2C', 'ГОРОД') or '').strip()
    comp = str(get_exact_val(raw_r, 'КОМПАНИЯ', 'НАЗВАНИЕКОМПАНИИ') or '').strip()
    c_low = c.lower()
    
    city_norm = None
    if 'казань' in c_low or (c_low == 'ка' and 'барс' in comp.lower()): city_norm = 'Казань'
    elif 'челны' in c_low: city_norm = 'Набережные Челны'
    elif 'альметьевск' in c_low: city_norm = 'Альметьевск'
    elif 'нижнекамск' in c_low: city_norm = 'Нижнекамск'
    elif 'бугульм' in c_low: city_norm = 'Бугульма'
        
    if city_norm:
        deal_serial = s.get('DealDate')
        if deal_serial and isinstance(deal_serial, (int, float)):
            py_date = datetime.date(1899, 12, 30) + datetime.timedelta(days=int(deal_serial))
            date_str = py_date.strftime('%d.%m.%Y')
        else:
            date_str = str(get_exact_val(raw_r, 'ПРЕДПОЛАГАЕМАЯДАТАЗАКРЫТИЯ') or '')[:10]
            
        # Нормализация холдинга дилера
        comp_low = comp.lower()
        if 'диалог' in comp_low:
            holding = 'ГК «Диалог Авто»'
        elif 'барс' in comp_low:
            holding = 'АО «Барс Авто»'
        elif 'апельсин' in comp_low or 'челны-авто' in comp_low or 'автосеть' in comp_low or 'спектр' in comp_low:
            holding = 'ГК «Апельсин» / «Автосеть.РФ»'
        elif 'кан авто' in comp_low:
            holding = 'ГК «КАН АВТО»'
        elif 'армада' in comp_low:
            holding = 'ТД «Армада-Авто»'
        elif 'парус' in comp_low:
            holding = 'ООО «Парус»'
        else:
            holding = comp
            
        master_tatar.append({
            'DealId': did,
            'Date': date_str,
            'City': city_norm,
            'Brand': s.get('Brand') or 'ДРУГИЕ',
            'Model': s.get('Model') or '',
            'VIN': s.get('VIN') or '',
            'Holding': holding,
            'Company': comp,
            'B2C': s.get('B2C') or '',
            'Price': float(s.get('Price', 0)),
            'Comm': float(s.get('Comm', 0)),
            'Revenue': float(s.get('Revenue', 0)),
            'Manager': s.get('Manager') or '',
            'SeniorManager': s.get('SeniorManager') or ''
        })

df_tatar = pd.DataFrame(master_tatar)

# 2. Создание красивой книги openpyxl
wb = openpyxl.Workbook()
wb.remove(wb.active)

# Стили оформления
fill_navy = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
fill_emerald = PatternFill(start_color="1B4D3E", end_color="1B4D3E", fill_type="solid")
fill_slate = PatternFill(start_color="2D3748", end_color="2D3748", fill_type="solid")
fill_card = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
fill_total = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")

font_title = Font(name="Calibri", size=14, bold=True, color="1A365D")
font_section = Font(name="Calibri", size=12, bold=True, color="1A365D")
font_card_num = Font(name="Calibri", size=15, bold=True, color="1A365D")
font_card_lbl = Font(name="Calibri", size=9, bold=True, color="64748B")
font_th = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
font_bold = Font(name="Calibri", size=10, bold=True, color="000000")
font_normal = Font(name="Calibri", size=10, color="000000")

border_thin = Border(left=Side(style='thin', color='CBD5E1'), right=Side(style='thin', color='CBD5E1'),
                     top=Side(style='thin', color='CBD5E1'), bottom=Side(style='thin', color='CBD5E1'))
border_tot = Border(top=Side(style='thin', color='1E293B'), bottom=Side(style='double', color='1E293B'))

align_c = Alignment(horizontal='center', vertical='center')
align_l = Alignment(horizontal='left', vertical='center')
align_r = Alignment(horizontal='right', vertical='center')

# =============================================================
# ЛИСТ 1: Сводка Города и Бренды
# =============================================================
ws1 = wb.create_sheet(title="Сводка Города и Бренды")
ws1.views.sheetView[0].showGridLines = True

# Title
ws1.merge_cells("A1:I1")
ws1["A1"] = "ПРОДАЖИ ЧЕРЕЗ СБЕРАВТО В РЕСПУБЛИКЕ ТАТАРСТАН — АВГУСТ 2026 ГОДА"
ws1["A1"].font = font_title
ws1["A1"].alignment = align_l

# KPI Cards (Row 3-4)
cards = [
    ("B3:C3", "B4:C4", "129 шт.", "ВСЕГО ПРОДАЖ (АВТО)"),
    ("D3:E3", "D4:E4", f"{df_tatar['Price'].sum():,.0f} ₽".replace(',', ' '), "ОБЪЕМ ПРОДАЖ (GMV)"),
    ("F3:G3", "F4:G4", f"{df_tatar['Price'].mean():,.0f} ₽".replace(',', ' '), "СРЕДНИЙ ЧЕК АВТОМОБИЛЯ"),
    ("H3:I3", "H4:I4", f"{df_tatar['Revenue'].sum():,.0f} ₽".replace(',', ' '), "ВЫРУЧКА СБЕРАВТО (БЕЗ НДС)")
]

for rng_val, rng_lbl, val, lbl in cards:
    ws1.merge_cells(rng_val)
    ws1.merge_cells(rng_lbl)
    top_c = ws1[rng_val.split(':')[0]]
    lbl_c = ws1[rng_lbl.split(':')[0]]
    top_c.value = val
    top_c.font = font_card_num
    top_c.alignment = align_c
    top_c.fill = fill_card
    lbl_c.value = lbl
    lbl_c.font = font_card_lbl
    lbl_c.alignment = align_c
    lbl_c.fill = fill_card

# Section 1: Матрица Города x Бренды
ws1["A6"] = "1. Матрица продаж: Города × Бренды (шт.)"
ws1["A6"].font = font_section

brands_list = ['JETOUR', 'SOLARIS', 'GAC', 'Geely & Belgee', 'CHERY & TENET', 'SOUEAST', 'LADA', 'OMODA & JAECOO', 'MINI']
cities_list = ['Казань', 'Набережные Челны', 'Альметьевск', 'Нижнекамск', 'Бугульма']

headers_mat = ["Город"] + brands_list + ["ИТОГО", "Доля города, %"]
ws1.append([]) # row 7
ws1.append(headers_mat) # row 8

for c_idx in range(1, len(headers_mat) + 1):
    c = ws1.cell(8, c_idx)
    c.fill = fill_navy
    c.font = font_th
    c.alignment = align_c

pivot_data = pd.crosstab(df_tatar['City'], df_tatar['Brand'])
r_cur = 9
for city in cities_list:
    ws1.cell(r_cur, 1, city).alignment = align_l
    for b_idx, b in enumerate(brands_list, start=2):
        val = int(pivot_data.loc[city, b]) if (city in pivot_data.index and b in pivot_data.columns) else 0
        cell = ws1.cell(r_cur, b_idx, val)
        cell.alignment = align_r
        cell.number_format = '#,##0'
        if val > 0: cell.font = font_bold
    # Total formula
    ws1.cell(r_cur, 11, f"=SUM(B{r_cur}:J{r_cur})").alignment = align_r
    ws1.cell(r_cur, 11).number_format = '#,##0'
    ws1.cell(r_cur, 11).font = font_bold
    # Pct formula
    pct_c = ws1.cell(r_cur, 12, f"=K{r_cur}/$K$14")
    pct_c.alignment = align_r
    pct_c.number_format = '0.0%'
    
    for c in range(1, 13):
        ws1.cell(r_cur, c).border = border_thin
        if r_cur % 2 == 1: ws1.cell(r_cur, c).fill = fill_zebra
    r_cur += 1

# Total Row in Matrix
ws1.cell(14, 1, "ИТОГО ПО РЕГИОНУ").alignment = align_l
for b_idx in range(2, 11):
    col_let = get_column_letter(b_idx)
    cell = ws1.cell(14, b_idx, f"=SUM({col_let}9:{col_let}13)")
    cell.alignment = align_r
    cell.number_format = '#,##0'

ws1.cell(14, 11, "=SUM(K9:K13)").alignment = align_r
ws1.cell(14, 11).number_format = '#,##0'
ws1.cell(14, 12, "=SUM(L9:L13)").alignment = align_r
ws1.cell(14, 12).number_format = '0.0%'

for c in range(1, 13):
    cell = ws1.cell(14, c)
    cell.font = font_bold
    cell.fill = fill_total
    cell.border = border_tot

# Section 2: Финансовые показатели по городам
r_sec2 = 16
ws1.cell(r_sec2, 1, "2. Финансовые показатели продаж по городам Татарстана").font = font_section
headers_fin = ["Город", "Продажи, шт.", "Доля продаж, %", "Объем продаж (GMV, ₽)", "Средний чек (₽)", "Комиссия СберАвто (₽)", "Выручка без НДС (₽)", "Топ-бренд города"]
ws1.cell(r_sec2+1, 1).value = ""
for c_idx, h in enumerate(headers_fin, start=1):
    c = ws1.cell(r_sec2+1, c_idx, h)
    c.fill = fill_emerald
    c.font = font_th
    c.alignment = align_c

city_summary = df_tatar.groupby('City').agg(
    sales=('Price', 'count'),
    gmv=('Price', 'sum'),
    avg_price=('Price', 'mean'),
    comm=('Comm', 'sum'),
    rev=('Revenue', 'sum')
).reindex(cities_list).reset_index()

top_brands_by_city = {
    'Казань': 'JETOUR (45 шт., 74%)',
    'Набережные Челны': 'JETOUR (26 шт., 57%)',
    'Альметьевск': 'SOLARIS (14 шт., 88%)',
    'Нижнекамск': 'JETOUR (3 шт., 60%)',
    'Бугульма': 'JETOUR (1 шт., 100%)'
}

r_cur2 = r_sec2 + 2
for idx, r in city_summary.iterrows():
    ws1.cell(r_cur2, 1, r['City']).alignment = align_l
    ws1.cell(r_cur2, 2, r['sales']).alignment = align_r
    ws1.cell(r_cur2, 2).number_format = '#,##0'
    ws1.cell(r_cur2, 3, f"=B{r_cur2}/$B${r_sec2+7}").alignment = align_r
    ws1.cell(r_cur2, 3).number_format = '0.0%'
    ws1.cell(r_cur2, 4, r['gmv']).alignment = align_r
    ws1.cell(r_cur2, 4).number_format = '#,##0 ₽'
    ws1.cell(r_cur2, 5, r['avg_price']).alignment = align_r
    ws1.cell(r_cur2, 5).number_format = '#,##0 ₽'
    ws1.cell(r_cur2, 6, r['comm']).alignment = align_r
    ws1.cell(r_cur2, 6).number_format = '#,##0.00 ₽'
    ws1.cell(r_cur2, 7, r['rev']).alignment = align_r
    ws1.cell(r_cur2, 7).number_format = '#,##0.00 ₽'
    ws1.cell(r_cur2, 8, top_brands_by_city.get(r['City'], '')).alignment = align_l
    
    for c in range(1, 9):
        cell = ws1.cell(r_cur2, c)
        cell.font = font_normal
        cell.border = border_thin
        if r_cur2 % 2 == 1: cell.fill = fill_zebra
    r_cur2 += 1

# Total Row Section 2
tot_r2 = r_cur2
ws1.cell(tot_r2, 1, "ИТОГО").alignment = align_l
ws1.cell(tot_r2, 2, f"=SUM(B{r_sec2+2}:B{tot_r2-1})").alignment = align_r
ws1.cell(tot_r2, 2).number_format = '#,##0'
ws1.cell(tot_r2, 3, f"=SUM(C{r_sec2+2}:C{tot_r2-1})").alignment = align_r
ws1.cell(tot_r2, 3).number_format = '0.0%'
ws1.cell(tot_r2, 4, f"=SUM(D{r_sec2+2}:D{tot_r2-1})").alignment = align_r
ws1.cell(tot_r2, 4).number_format = '#,##0 ₽'
ws1.cell(tot_r2, 5, f"=AVERAGE(E{r_sec2+2}:E{tot_r2-1})").alignment = align_r
ws1.cell(tot_r2, 5).number_format = '#,##0 ₽'
ws1.cell(tot_r2, 6, f"=SUM(F{r_sec2+2}:F{tot_r2-1})").alignment = align_r
ws1.cell(tot_r2, 6).number_format = '#,##0.00 ₽'
ws1.cell(tot_r2, 7, f"=SUM(G{r_sec2+2}:G{tot_r2-1})").alignment = align_r
ws1.cell(tot_r2, 7).number_format = '#,##0.00 ₽'
ws1.cell(tot_r2, 8, "Весь регион").alignment = align_l

for c in range(1, 9):
    cell = ws1.cell(tot_r2, c)
    cell.font = font_bold
    cell.fill = fill_total
    cell.border = border_tot

# Section 3: Рейтинг Брендов
r_sec3 = tot_r2 + 2
ws1.cell(r_sec3, 1, "3. Рейтинг брендов в Татарстане (Август 2026)").font = font_section
headers_br = ["Бренд", "Продажи, шт.", "Доля рынка, %", "Объем продаж (GMV, ₽)", "Средний чек (₽)", "Выручка СберАвто (₽)", "Популярные модели в регионе"]
for c_idx, h in enumerate(headers_br, start=1):
    c = ws1.cell(r_sec3+1, c_idx, h)
    c.fill = fill_slate
    c.font = font_th
    c.alignment = align_c

brand_summary = df_tatar.groupby('Brand').agg(
    sales=('Price', 'count'),
    gmv=('Price', 'sum'),
    avg_price=('Price', 'mean'),
    rev=('Revenue', 'sum')
).sort_values(by='sales', ascending=False).reset_index()

top_models_by_brand = {
    'JETOUR': 'Dashing (36), X70 Plus (21), T2 (5), X90 Plus (4)',
    'SOLARIS': 'Solaris HC (20), KRS / KRX (2)',
    'GAC': 'GS8 (9), GS4 (2), S7 (2), S9 (1)',
    'Geely & Belgee': 'Geely Monjaro (3), Cityray (2), Belgee X50 (1)',
    'CHERY & TENET': 'TENET T7 (3), TENET T4 (1)',
    'SOUEAST': 'Soueast S06 (3)',
    'LADA': 'Granta (2), Vesta (1)',
    'OMODA & JAECOO': 'Jaecoo J7 (1)',
    'MINI': 'Mini One (1)'
}

r_cur3 = r_sec3 + 2
for idx, r in brand_summary.iterrows():
    ws1.cell(r_cur3, 1, r['Brand']).alignment = align_l
    ws1.cell(r_cur3, 2, r['sales']).alignment = align_r
    ws1.cell(r_cur3, 2).number_format = '#,##0'
    ws1.cell(r_cur3, 3, f"=B{r_cur3}/$B${r_sec3 + len(brand_summary) + 2}").alignment = align_r
    ws1.cell(r_cur3, 3).number_format = '0.0%'
    ws1.cell(r_cur3, 4, r['gmv']).alignment = align_r
    ws1.cell(r_cur3, 4).number_format = '#,##0 ₽'
    ws1.cell(r_cur3, 5, r['avg_price']).alignment = align_r
    ws1.cell(r_cur3, 5).number_format = '#,##0 ₽'
    ws1.cell(r_cur3, 6, r['rev']).alignment = align_r
    ws1.cell(r_cur3, 6).number_format = '#,##0.00 ₽'
    ws1.cell(r_cur3, 7, top_models_by_brand.get(r['Brand'], '')).alignment = align_l
    
    for c in range(1, 8):
        cell = ws1.cell(r_cur3, c)
        cell.font = font_normal
        cell.border = border_thin
        if r_cur3 % 2 == 1: cell.fill = fill_zebra
    r_cur3 += 1

# Total Row Section 3
tot_r3 = r_cur3
ws1.cell(tot_r3, 1, "ИТОГО").alignment = align_l
ws1.cell(tot_r3, 2, f"=SUM(B{r_sec3+2}:B{tot_r3-1})").alignment = align_r
ws1.cell(tot_r3, 2).number_format = '#,##0'
ws1.cell(tot_r3, 3, f"=SUM(C{r_sec3+2}:C{tot_r3-1})").alignment = align_r
ws1.cell(tot_r3, 3).number_format = '0.0%'
ws1.cell(tot_r3, 4, f"=SUM(D{r_sec3+2}:D{tot_r3-1})").alignment = align_r
ws1.cell(tot_r3, 4).number_format = '#,##0 ₽'
ws1.cell(tot_r3, 5, f"=AVERAGE(E{r_sec3+2}:E{tot_r3-1})").alignment = align_r
ws1.cell(tot_r3, 5).number_format = '#,##0 ₽'
ws1.cell(tot_r3, 6, f"=SUM(F{r_sec3+2}:F{tot_r3-1})").alignment = align_r
ws1.cell(tot_r3, 6).number_format = '#,##0.00 ₽'
ws1.cell(tot_r3, 7, "9 брендов").alignment = align_l

for c in range(1, 8):
    cell = ws1.cell(tot_r3, c)
    cell.font = font_bold
    cell.fill = fill_total
    cell.border = border_tot


# =============================================================
# ЛИСТ 2: Дилеры и партнеры РТ
# =============================================================
ws2 = wb.create_sheet(title="Дилеры и партнеры РТ")
ws2.views.sheetView[0].showGridLines = True

headers_dealers = [
    "№", 
    "Дилерский холдинг / Сеть", 
    "Города присутствия", 
    "Продажи, шт.", 
    "Доля в регионе, %", 
    "Объем продаж (GMV, ₽)", 
    "Выручка СберАвто (₽)", 
    "Проданные бренды", 
    "Юридические лица / Названия в CRM"
]

ws2.append(headers_dealers)
for c_idx in range(1, len(headers_dealers) + 1):
    c = ws2.cell(1, c_idx)
    c.fill = fill_navy
    c.font = font_th
    c.alignment = align_c

dealer_stats = []
for h, g in df_tatar.groupby('Holding'):
    dealer_stats.append({
        'holding': h,
        'cities': ', '.join(sorted(g['City'].unique())),
        'sales': len(g),
        'gmv': g['Price'].sum(),
        'rev': g['Revenue'].sum(),
        'brands': ', '.join(sorted(g['Brand'].unique())),
        'comps': ' | '.join(sorted(g['Company'].unique()))
    })

df_ds = pd.DataFrame(dealer_stats).sort_values(by='sales', ascending=False).reset_index(drop=True)

r_cur_d = 2
for idx, r in df_ds.iterrows():
    ws2.cell(r_cur_d, 1, idx + 1).alignment = align_c
    ws2.cell(r_cur_d, 2, r['holding']).alignment = align_l
    ws2.cell(r_cur_d, 3, r['cities']).alignment = align_l
    ws2.cell(r_cur_d, 4, r['sales']).alignment = align_r
    ws2.cell(r_cur_d, 4).number_format = '#,##0'
    ws2.cell(r_cur_d, 5, f"=D{r_cur_d}/$D${len(df_ds)+2}").alignment = align_r
    ws2.cell(r_cur_d, 5).number_format = '0.0%'
    ws2.cell(r_cur_d, 6, r['gmv']).alignment = align_r
    ws2.cell(r_cur_d, 6).number_format = '#,##0 ₽'
    ws2.cell(r_cur_d, 7, r['rev']).alignment = align_r
    ws2.cell(r_cur_d, 7).number_format = '#,##0.00 ₽'
    ws2.cell(r_cur_d, 8, r['brands']).alignment = align_l
    ws2.cell(r_cur_d, 9, r['comps']).alignment = align_l
    
    for c in range(1, 10):
        cell = ws2.cell(r_cur_d, c)
        cell.font = font_normal
        cell.border = border_thin
        if r_cur_d % 2 == 1: cell.fill = fill_zebra
    r_cur_d += 1

tot_d = r_cur_d
ws2.cell(tot_d, 1, "ИТОГО").alignment = align_c
ws2.cell(tot_d, 2, f"Всего сетей: {len(df_ds)}").alignment = align_l
ws2.cell(tot_d, 3, "Весь Татарстан").alignment = align_l
ws2.cell(tot_d, 4, f"=SUM(D2:D{tot_d-1})").alignment = align_r
ws2.cell(tot_d, 4).number_format = '#,##0'
ws2.cell(tot_d, 5, f"=SUM(E2:E{tot_d-1})").alignment = align_r
ws2.cell(tot_d, 5).number_format = '0.0%'
ws2.cell(tot_d, 6, f"=SUM(F2:F{tot_d-1})").alignment = align_r
ws2.cell(tot_d, 6).number_format = '#,##0 ₽'
ws2.cell(tot_d, 7, f"=SUM(G2:G{tot_d-1})").alignment = align_r
ws2.cell(tot_d, 7).number_format = '#,##0.00 ₽'
ws2.cell(tot_d, 8, "9 брендов").alignment = align_l
ws2.cell(tot_d, 9, "13 дилерских центров").alignment = align_l

for c in range(1, 10):
    cell = ws2.cell(tot_d, c)
    cell.font = font_bold
    cell.fill = fill_total
    cell.border = border_tot


# =============================================================
# ЛИСТ 3: Реестр всех 129 сделок
# =============================================================
ws3 = wb.create_sheet(title="Реестр сделок (129 авто)")
ws3.views.sheetView[0].showGridLines = True

headers_deals = [
    "№", 
    "ID сделки", 
    "Дата", 
    "Город продажи", 
    "Бренд", 
    "Модель автомобиля", 
    "VIN номер", 
    "Дилерский холдинг", 
    "Компания / Дилер в CRM", 
    "Тип сделки (B2C)", 
    "Стоимость авто (₽)", 
    "Комиссия СберАвто (₽)", 
    "Выручка без НДС (₽)", 
    "Менеджер сделки", 
    "Старший менеджер"
]

ws3.append(headers_deals)
for c_idx in range(1, len(headers_deals) + 1):
    c = ws3.cell(1, c_idx)
    c.fill = fill_slate
    c.font = font_th
    c.alignment = align_c

# Сортировка: Город -> Бренд -> Дата
df_tatar_sorted = df_tatar.sort_values(by=['City', 'Brand', 'Price'], ascending=[True, True, False]).reset_index(drop=True)

r_cur_reg = 2
for idx, r in df_tatar_sorted.iterrows():
    ws3.cell(r_cur_reg, 1, idx + 1).alignment = align_c
    ws3.cell(r_cur_reg, 2, r['DealId']).alignment = align_c
    ws3.cell(r_cur_reg, 3, r['Date']).alignment = align_c
    ws3.cell(r_cur_reg, 4, r['City']).alignment = align_l
    ws3.cell(r_cur_reg, 5, r['Brand']).alignment = align_l
    ws3.cell(r_cur_reg, 6, r['Model']).alignment = align_l
    ws3.cell(r_cur_reg, 7, r['VIN']).alignment = align_c
    ws3.cell(r_cur_reg, 8, r['Holding']).alignment = align_l
    ws3.cell(r_cur_reg, 9, r['Company']).alignment = align_l
    ws3.cell(r_cur_reg, 10, r['B2C']).alignment = align_l
    
    ws3.cell(r_cur_reg, 11, r['Price']).alignment = align_r
    ws3.cell(r_cur_reg, 11).number_format = '#,##0 ₽'
    
    ws3.cell(r_cur_reg, 12, r['Comm']).alignment = align_r
    ws3.cell(r_cur_reg, 12).number_format = '#,##0.00 ₽'
    
    ws3.cell(r_cur_reg, 13, r['Revenue']).alignment = align_r
    ws3.cell(r_cur_reg, 13).number_format = '#,##0.00 ₽'
    
    ws3.cell(r_cur_reg, 14, r['Manager']).alignment = align_l
    ws3.cell(r_cur_reg, 15, r['SeniorManager']).alignment = align_l
    
    for c in range(1, 16):
        cell = ws3.cell(r_cur_reg, c)
        cell.font = font_normal
        cell.border = border_thin
        if r_cur_reg % 2 == 1: cell.fill = fill_zebra
    r_cur_reg += 1

tot_reg = r_cur_reg
ws3.cell(tot_reg, 1, "ИТОГО").alignment = align_c
ws3.cell(tot_reg, 2, f"129 сделок").alignment = align_c
ws3.cell(tot_reg, 11, f"=SUM(K2:K{tot_reg-1})").alignment = align_r
ws3.cell(tot_reg, 11).number_format = '#,##0 ₽'
ws3.cell(tot_reg, 12, f"=SUM(L2:L{tot_reg-1})").alignment = align_r
ws3.cell(tot_reg, 12).number_format = '#,##0.00 ₽'
ws3.cell(tot_reg, 13, f"=SUM(M2:M{tot_reg-1})").alignment = align_r
ws3.cell(tot_reg, 13).number_format = '#,##0.00 ₽'

for c in range(1, 16):
    cell = ws3.cell(tot_reg, c)
    cell.font = font_bold
    cell.fill = fill_total
    cell.border = border_tot


# Авто-подбор ширины столбцов и фильтры
ws1.column_dimensions['A'].width = 24
ws1.column_dimensions['B'].width = 16
ws1.column_dimensions['C'].width = 16
ws1.column_dimensions['D'].width = 16
ws1.column_dimensions['E'].width = 18
ws1.column_dimensions['F'].width = 18
ws1.column_dimensions['G'].width = 15
ws1.column_dimensions['H'].width = 15
ws1.column_dimensions['I'].width = 18
ws1.column_dimensions['J'].width = 15
ws1.column_dimensions['K'].width = 16
ws1.column_dimensions['L'].width = 16

ws2.column_dimensions['A'].width = 6
ws2.column_dimensions['B'].width = 30
ws2.column_dimensions['C'].width = 32
ws2.column_dimensions['D'].width = 16
ws2.column_dimensions['E'].width = 18
ws2.column_dimensions['F'].width = 24
ws2.column_dimensions['G'].width = 22
ws2.column_dimensions['H'].width = 32
ws2.column_dimensions['I'].width = 45

ws3.column_dimensions['A'].width = 6
ws3.column_dimensions['B'].width = 14
ws3.column_dimensions['C'].width = 14
ws3.column_dimensions['D'].width = 20
ws3.column_dimensions['E'].width = 18
ws3.column_dimensions['F'].width = 20
ws3.column_dimensions['G'].width = 22
ws3.column_dimensions['H'].width = 26
ws3.column_dimensions['I'].width = 35
ws3.column_dimensions['J'].width = 20
ws3.column_dimensions['K'].width = 20
ws3.column_dimensions['L'].width = 20
ws3.column_dimensions['M'].width = 20
ws3.column_dimensions['N'].width = 22
ws3.column_dimensions['O'].width = 22

# Закрепление областей
ws1.freeze_panes = 'A8'
ws2.freeze_panes = 'A2'
ws3.freeze_panes = 'A2'

# Автофильтры
ws2.auto_filter.ref = f"A1:I{len(df_ds)+1}"
ws3.auto_filter.ref = f"A1:O{len(df_tatar)+1}"

out_root = "Продажи_Татарстан_Август_2026_СберАвто.xlsx"
out_down = "/Users/vaceslavgamaunov/Downloads/Продажи_Татарстан_Август_2026_СберАвто.xlsx"
out_raw = "otchet-parser/raw_data/Продажи_Татарстан_Август_2026_СберАвто.xlsx"

wb.save(out_root)
wb.save(out_down)
wb.save(out_raw)

print(f"[+] Файл успешно сгенерирован и сохранен:")
print(f"    1. {out_root}")
print(f"    2. {out_down}")
print(f"    3. {out_raw}")
