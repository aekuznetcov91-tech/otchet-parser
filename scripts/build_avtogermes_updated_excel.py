import os
import sys
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.path.append('.')
from scripts.build_avtogermes_analysis import df

# Strictly Central Federal District
df_cfo = df[df['is_cfo']].copy()

wb = openpyxl.Workbook()
wb.remove(wb.active) # Remove default sheet

# Typography & Color Palette
font_title = Font(name="Calibri", size=14, bold=True, color="1E3A8A")
font_subtitle = Font(name="Calibri", size=9.5, italic=True, color="475569")
font_section_hdr = Font(name="Calibri", size=11, bold=True, color="1E3A8A")
font_tbl_header = Font(name="Calibri", size=9.5, bold=True, color="FFFFFF")
font_bold = Font(name="Calibri", size=9.5, bold=True, color="0F172A")
font_regular = Font(name="Calibri", size=9.5, color="1E293B")
font_muted = Font(name="Calibri", size=8.5, italic=True, color="64748B")

font_kpi_val = Font(name="Calibri", size=17, bold=True, color="1E3A8A")
font_kpi_lbl = Font(name="Calibri", size=8.5, bold=True, color="475569")
font_kpi_sub = Font(name="Calibri", size=8.0, italic=True, color="64748B")

fill_header_navy = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
fill_header_green = PatternFill(start_color="065F46", end_color="065F46", fill_type="solid")
fill_header_slate = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
fill_subtotal = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
fill_accent = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
fill_highlight = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
fill_card = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
fill_green_light = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid")

thin_border = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)

double_bottom_border = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='double', color='0F172A')
)

def style_range(ws, min_r, min_c, max_r, max_c, font=None, fill=None, alignment=None, border=None, num_format=None):
    for row in ws.iter_rows(min_row=min_r, min_col=min_c, max_row=max_r, max_col=max_c):
        for cell in row:
            if font: cell.font = font
            if fill: cell.fill = fill
            if alignment: cell.alignment = alignment
            if border: cell.border = border
            if num_format: cell.number_format = num_format

def autofit(ws, max_len_cap=55):
    for col in ws.columns:
        max_l = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(min(max_l + 3, max_len_cap), 11)


# ==============================================================================
# SHEET 1: Executive Summary
# ==============================================================================
ws1 = wb.create_sheet(title="Executive Summary")
ws1.views.sheetView[0].showGridLines = True

ws1.cell(row=2, column=2, value="АВТОГЕРМЕС × СБЕРАВТО — ИТОГИ 3 МЕСЯЦЕВ").font = font_title
ws1.cell(row=3, column=2, value="Аналитический отчет для встречи с директором по продажам новых автомобилей (ЦФО, Июнь – Август 2026)").font = font_subtitle

# Methodology block
ws1.cell(row=5, column=2, value="МЕТОДОЛОГИЯ И ПАРАМЕТРЫ АНАЛИЗА:").font = font_bold
ws1.cell(row=6, column=2, value=(
    "• Период: последние 3 полных календарных месяца — Июнь 2026, Июль 2026, Август 2026 (Сентябрь 2026 не учитывается как текущий/неполный месяц).\n"
    "• Показатель: строго фактические закрытые сделки по физическим новым автомобилям (СТРИМ 'Импортеры', статус 'Закрыто и реализовано').\n"
    "• Территория: исключительно Центральный федеральный округ (ЦФО). Продажи других регионов РФ исключены.\n"
    "• Конфиденциальность: все конкурирующие холдинги зашифрованы кодами (ГК 1 .. ГК 5), дилерские центры — (Дилер 1 .. Дилер 20)."
)).font = font_regular
ws1.cell(row=6, column=2).alignment = Alignment(wrap_text=True, vertical="top")
ws1.merge_cells(start_row=6, start_column=2, end_row=8, end_column=9)
style_range(ws1, 6, 2, 8, 9, fill=fill_card, border=thin_border)
ws1.row_dimensions[6].height = 20
ws1.row_dimensions[7].height = 20
ws1.row_dimensions[8].height = 20

# KPI Metric Cards (6 cards)
kpis = [
    ("517 шт.", "ПРОДАЖИ ЗА 3 МЕСЯЦА (ЦФО)", "Лидер №1 среди всех партнеров СберАвто в ЦФО"),
    ("145 шт.", "ПРОДАЖИ ПОСЛЕДНЕГО МЕСЯЦА", "Август 2026: стабильный высокий объем"),
    ("24.7%", "ДОЛЯ В РЫНКЕ СБЕРАВТО ЦФО", "Практически каждая 4-я закрытая сделка округа"),
    ("7 активных", "КЛЮЧЕВЫХ БРЕНДОВ В ПОРТФЕЛЕ", "LADA, SOLARIS, Geely, JETOUR, SOUEAST, Changan, Chery"),
    ("LADA (256 шт.)", "КЛЮЧЕВОЙ БРЕНД ПО ОБЪЕМУ", "Доля в ЦФО 76.9% (256 из 333 авто округа)"),
    ("JETOUR (34 шт.)", "БРЕНД С МАКС. ЕМКОСТЬЮ", "Рынок ЦФО 985 шт. — главная точка масштабирования")
]

card_coords = [
    (10, 2, 12, 4),
    (10, 5, 12, 6),
    (10, 7, 12, 9),
    (14, 2, 16, 4),
    (14, 5, 16, 6),
    (14, 7, 16, 9)
]

for (val, lbl, sub), (r1, c1, r2, c2) in zip(kpis, card_coords):
    ws1.merge_cells(start_row=r1, start_column=c1, end_row=r2, end_column=c2)
    style_range(ws1, r1, c1, r2, c2, fill=fill_card, border=thin_border)
    top_c = ws1.cell(row=r1, column=c1)
    top_c.value = f"{val}\n{lbl}\n{sub}"
    top_c.font = font_bold
    top_c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    ws1.row_dimensions[r1].height = 22
    ws1.row_dimensions[r1+1].height = 20
    ws1.row_dimensions[r1+2].height = 20

# Key Takeaways & 3 Growth Points
ws1.cell(row=18, column=2, value="ГЛАВНЫЙ ПОСЫЛ И 3 ГЛАВНЫЕ ТОЧКИ РОСТА:").font = font_section_hdr

summary_rows = [
    ("🏆 Текущий статус партнера:", "АвтоГЕРМЕС — безоговорочный партнер №1 для СберАвто в ЦФО по объему сделок (517 авто за 3 мес). Ближайший федеральный конкурент (ГК 1) реализовал 319 авто. Доля АвтоГЕРМЕСА в продажах СберАвто по ЦФО составляет 24.7%."),
    ("🚀 Точка роста 1: JETOUR", "Крупнейший бренд на платформе СберАвто в ЦФО (985 проданных авто за 3 месяца). Доля АвтоГЕРМЕСА составляет 3.5% (34 авто). Партнер занимает 11-е место в ТОП-20 дилеров. Увеличение доли всего до 8.5% (+5 п.п.) даст АвтоГЕРМЕСУ дополнительно +41 сделку за 2 месяца (+20 авто/мес)."),
    ("📈 Точка роста 2: Geely & Belgee", "Рынок Geely & Belgee в ЦФО вырос в 2.3 раза (с 46 авто в июне до 108 в августе). Продажи АвтоГЕРМЕСА при этом снизились с 30 до 17 авто, а доля сократилась с 65.2% до 15.7%. Синхронизация складских остатков и цен позволит вернуть долю к 30-40% (+15..20 сделок/мес)."),
    ("✨ Точка роста 3: SOUEAST и расширение GAC", "SOUEAST показал успешный старт: рост с 0 до 8 авто в месяц (доля 14.7%). В сегменте GAC рынок ЦФО стремительно вырос (с 0 до 79 авто/мес), где АвтоГЕРМЕС пока не представлен в СберАвто. Подключение площадок GAC холдинга обеспечит моментальный прирост сделок.")
]

curr_r = 20
for title_lbl, desc_lbl in summary_rows:
    ws1.cell(row=curr_r, column=2, value=title_lbl).font = font_bold
    ws1.cell(row=curr_r, column=2).alignment = Alignment(vertical="top")
    ws1.cell(row=curr_r, column=3, value=desc_lbl).font = font_regular
    ws1.cell(row=curr_r, column=3).alignment = Alignment(wrap_text=True, vertical="top")
    ws1.merge_cells(start_row=curr_r, start_column=3, end_row=curr_r, end_column=9)
    style_range(ws1, curr_r, 2, curr_r, 9, border=thin_border)
    ws1.row_dimensions[curr_r].height = 42
    curr_r += 1

autofit(ws1)


# ==============================================================================
# SHEET 2: АвтоГЕРМЕС ЦФО
# ==============================================================================
ws2 = wb.create_sheet(title="АвтоГЕРМЕС ЦФО")
ws2.views.sheetView[0].showGridLines = True

ws2.cell(row=2, column=2, value="ОБЩИЕ РЕЗУЛЬТАТЫ АВТОГЕРМЕСА В ЦФО (3 ПОЛНЫХ МЕСЯЦА)").font = font_title

headers_s2 = ['Показатель', 'Июнь 2026', 'Июль 2026', 'Август 2026', 'Итого за 3 мес', 'Динамика Июль vs Июнь', 'Динамика Авг vs Июль']
for c_idx, h in enumerate(headers_s2, start=2):
    cell = ws2.cell(row=4, column=c_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_header_navy
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws2.row_dimensions[4].height = 26

rows_s2 = [
    ('Продажи АвтоГЕРМЕС (шт.)', 206, 166, 145, 517, '-40 (-19.4%)', '-21 (-12.7%)'),
    ('Продажи всего рынка ЦФО (шт.)', 489, 763, 844, 2096, '+274 (+56.0%)', '+81 (+10.6%)'),
    ('Доля АвтоГЕРМЕС в ЦФО (%)', 0.4213, 0.2176, 0.1718, 0.2467, '-20.37 п.п.', '-4.58 п.п.')
]

for r_offset, r_data in enumerate(rows_s2):
    r_idx = 5 + r_offset
    ws2.row_dimensions[r_idx].height = 22
    for c_offset, val in enumerate(r_data):
        c_idx = 2 + c_offset
        cell = ws2.cell(row=r_idx, column=c_idx, value=val)
        cell.border = thin_border
        if c_offset == 0:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="left", vertical="center")
        elif c_offset in (1, 2, 3, 4):
            if r_offset in (0, 1):
                cell.font = font_bold if c_offset == 4 else font_regular
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = "#,##0"
            else:
                cell.font = font_bold
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = "0.00%"
                cell.fill = fill_highlight if c_offset == 4 else fill_accent
        else:
            cell.font = font_regular
            cell.alignment = Alignment(horizontal="center", vertical="center")

# Bottom explanatory notes
ws2.cell(row=9, column=2, value="АНАЛИТИЧЕСКИЕ ВЫВОДЫ ПО ДИНАМИКЕ ОБЪЕМА И ДОЛИ:").font = font_section_hdr
notes_s2 = [
    "1. АвтоГЕРМЕС обеспечил 517 закрытых сделок за 3 месяца — это абсолютное 1-е место в ЦФО с долей 24.67%.",
    "2. В июне доля составляла 42.13% (фактически каждая вторая сделка в ЦФО проходила через АвтоГЕРМЕС).",
    "3. В июле и августе общий рынок платформы в ЦФО стремительно вырос (+56% в июле и еще +11% в августе) в основном за счет брендов JETOUR и GAC.",
    "4. Снижение доли АвтоГЕРМЕСА до 17.18% в августе обусловлено не потерей позиций по ключевым брендам (LADA и SOLARIS держат лидерство), а взрывным ростом продаж JETOUR у других партнеров. Подключение потенциала JETOUR и GAC вернет долю АвтоГЕРМЕСА к 30%+."
]
for idx, n in enumerate(notes_s2, start=10):
    ws2.cell(row=idx, column=2, value=n).font = font_regular
    ws2.merge_cells(start_row=idx, start_column=2, end_row=idx, end_column=8)
    ws2.row_dimensions[idx].height = 18

autofit(ws2)


# ==============================================================================
# SHEET 3: Доля по брендам
# ==============================================================================
ws3 = wb.create_sheet(title="Доля по брендам")
ws3.views.sheetView[0].showGridLines = True

ws3.cell(row=2, column=2, value="РЕЗУЛЬТАТЫ АВТОГЕРМЕСА И ЕГО ДОЛЯ ПО БРЕНДАМ В ЦФО").font = font_title
ws3.cell(row=3, column=2, value="Сравнение продаж АвтоГЕРМЕСА с общей емкостью каждого бренда в ЦФО (3 полных месяца)").font = font_subtitle

headers_s3 = [
    'Бренд', 'Продажи АГ (Июн)', 'Продажи АГ (Июл)', 'Продажи АГ (Авг)', 'Продажи АГ (3 мес)',
    'Рынок ЦФО (Июн)', 'Рынок ЦФО (Июл)', 'Рынок ЦФО (Авг)', 'Рынок ЦФО (3 мес)',
    'Доля АГ в Июне', 'Доля АГ в Июле', 'Доля АГ в Августе', 'Доля АГ за 3 мес'
]

for c_idx, h in enumerate(headers_s3, start=2):
    cell = ws3.cell(row=5, column=c_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_header_navy
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws3.row_dimensions[5].height = 28

brands_s3 = [
    ('JETOUR', 6, 17, 11, 34, 170, 451, 364, 985, 0.035, 0.038, 0.030, 0.035),
    ('LADA', 105, 73, 78, 256, 138, 93, 102, 333, 0.761, 0.785, 0.765, 0.769),
    ('GEELY', 12, 19, 10, 41, 18, 50, 70, 138, 0.667, 0.380, 0.143, 0.297),
    ('BELGEE', 18, 5, 7, 30, 28, 29, 38, 95, 0.643, 0.172, 0.184, 0.316),
    ('SOLARIS', 50, 41, 29, 120, 87, 72, 63, 222, 0.575, 0.569, 0.460, 0.541),
    ('SOUEAST', 0, 7, 8, 15, 0, 28, 74, 102, 0.0, 0.250, 0.108, 0.147),
    ('GAC', 0, 0, 0, 0, 0, 11, 79, 90, 0.0, 0.0, 0.0, 0.0),
    ('CHANGAN', 9, 1, 0, 10, 23, 5, 21, 49, 0.391, 0.200, 0.0, 0.204),
    ('CHERY & TENET', 3, 0, 0, 3, 9, 8, 11, 28, 0.333, 0.0, 0.0, 0.107),
    ('Прочие бренды', 3, 3, 2, 8, 16, 16, 22, 54, 0.188, 0.188, 0.091, 0.148)
]

for r_offset, b_data in enumerate(brands_s3):
    r_idx = 6 + r_offset
    ws3.row_dimensions[r_idx].height = 20
    for c_offset, val in enumerate(b_data):
        c_idx = 2 + c_offset
        cell = ws3.cell(row=r_idx, column=c_idx, value=val)
        cell.border = thin_border
        if c_offset == 0:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="left", vertical="center")
        elif c_offset in range(1, 9):
            cell.font = font_bold if c_offset in (4, 8) else font_regular
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "#,##0"
            if c_offset == 4:
                cell.fill = fill_accent
        else:
            cell.font = font_bold if c_offset == 12 else font_regular
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "0.0%"
            if c_offset == 12:
                cell.fill = fill_highlight

# Total row 15
tot_r = 6 + len(brands_s3)
ws3.row_dimensions[tot_r].height = 22
tot_vals = ['ИТОГО ПО ВСЕМ БРЕНДАМ', 206, 166, 145, 517, 489, 763, 844, 2096, 0.421, 0.218, 0.172, 0.247]
for c_offset, val in enumerate(tot_vals):
    c_idx = 2 + c_offset
    cell = ws3.cell(row=tot_r, column=c_idx, value=val)
    cell.font = font_bold
    cell.border = double_bottom_border
    cell.fill = fill_subtotal
    if c_offset == 0:
        cell.alignment = Alignment(horizontal="left", vertical="center")
    elif c_offset in range(1, 9):
        cell.alignment = Alignment(horizontal="right", vertical="center")
        cell.number_format = "#,##0"
    else:
        cell.alignment = Alignment(horizontal="right", vertical="center")
        cell.number_format = "0.0%"

autofit(ws3)


# ==============================================================================

# ==============================================================================
# SHEET 3b: Позиция по 5 брендам в ЦФО
# ==============================================================================
ws_pos = wb.create_sheet(title="Позиция по 5 брендам")
ws_pos.views.sheetView[0].showGridLines = True

ws_pos.cell(row=2, column=2, value="ПОЗИЦИЯ АВТОГЕРМЕСА ПО КЛЮЧЕВЫМ БРЕНДАМ В ЦФО (Q3 2026)").font = font_title
ws_pos.cell(row=3, column=2, value="Детализированный срез по 5 ключевым брендам за последние 3 полных месяца (Июнь, Июль, Август 2026)").font = font_subtitle

# Block 1: Сводная таблица по 5 брендам
ws_pos.cell(row=5, column=2, value="СВОДНЫЕ РЕЗУЛЬТАТЫ АВТОГЕРМЕСА В ЦФО (3 ПОЛНЫХ МЕСЯЦА):").font = font_section_hdr

headers_pos = [
    'Бренд', 'Рынок ЦФО', 'Продажи АвтоГЕРМЕС', 'Доля АвтоГЕРМЕС', 'Позиция в ЦФО',
    'Месяц 1 (Июнь)', 'Месяц 2 (Июль)', 'Месяц 3 (Август)', 'Динамика продаж'
]

for c_idx, h in enumerate(headers_pos, start=2):
    cell = ws_pos.cell(row=7, column=c_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_header_navy
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws_pos.row_dimensions[7].height = 28

pos_data = [
    ('LADA', 333, 256, 0.769, '1-е место', '105 шт. (76.1%, 1-е)', '73 шт. (78.5%, 1-е)', '78 шт. (76.5%, 1-е)', '105 ➔ 73 (-30.5%) ➔ 78 (+6.8%)'),
    ('SOLARIS', 222, 120, 0.541, '1-е место', '50 шт. (57.5%, 1-е)', '41 шт. (56.9%, 1-е)', '29 шт. (46.0%, 1-е)', '50 ➔ 41 (-18.0%) ➔ 29 (-29.3%)'),
    ('BELGEE', 95, 30, 0.316, '2-е место', '18 шт. (64.3%, 1-е)', '5 шт. (17.2%, 3-е)', '7 шт. (18.4%, 2-е)', '18 ➔ 5 (-72.2%) ➔ 7 (+40.0%)'),
    ('GEELY', 138, 41, 0.297, '2-е место', '12 шт. (66.7%, 1-е)', '19 шт. (38.0%, 2-е)', '10 шт. (14.3%, 2-е*)', '12 ➔ 19 (+58.3%) ➔ 10 (-47.4%)'),
    ('CHANGAN', 49, 10, 0.204, '3-е место', '9 шт. (39.1%, 1-е)', '1 шт. (20.0%, 2-е)', '0 шт. (0.0%, -)', '9 ➔ 1 (-88.9%) ➔ 0 (-100.0%)')
]

for r_offset, p_row in enumerate(pos_data):
    r_idx = 8 + r_offset
    ws_pos.row_dimensions[r_idx].height = 22
    for c_offset, val in enumerate(p_row):
        c_idx = 2 + c_offset
        cell = ws_pos.cell(row=r_idx, column=c_idx, value=val)
        cell.border = thin_border
        if c_offset == 0:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="left", vertical="center")
        elif c_offset in (1, 2):
            cell.font = font_bold if c_offset == 2 else font_regular
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "#,##0"
            if c_offset == 2:
                cell.fill = fill_accent
        elif c_offset == 3:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "0.0%"
            cell.fill = fill_highlight
        elif c_offset == 4:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="center", vertical="center")
            if '1-е' in str(val):
                cell.fill = fill_green_light
        elif c_offset in (5, 6, 7):
            cell.font = font_regular
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="left", vertical="center")

# Total row
tot_pos_r = 8 + len(pos_data)
ws_pos.row_dimensions[tot_pos_r].height = 24
tot_pos_vals = ['ИТОГО ПО 5 БРЕНДАМ', 837, 457, 0.546, '1-е место', '194 шт. (66.0%)', '139 шт. (55.8%)', '124 шт. (42.2%)', '194 ➔ 139 ➔ 124 (-36.1%)']
for c_offset, val in enumerate(tot_pos_vals):
    c_idx = 2 + c_offset
    cell = ws_pos.cell(row=tot_pos_r, column=c_idx, value=val)
    cell.font = font_bold
    cell.border = double_bottom_border
    cell.fill = fill_subtotal
    if c_offset == 0:
        cell.alignment = Alignment(horizontal="left", vertical="center")
    elif c_offset in (1, 2):
        cell.alignment = Alignment(horizontal="right", vertical="center")
        cell.number_format = "#,##0"
    elif c_offset == 3:
        cell.alignment = Alignment(horizontal="right", vertical="center")
        cell.number_format = "0.0%"
    elif c_offset == 4:
        cell.alignment = Alignment(horizontal="center", vertical="center")
    else:
        cell.alignment = Alignment(horizontal="center" if c_offset < 8 else "left", vertical="center")

# Block 2: Конкурентное окружение и разрывы (Строго обезличено)
comp_start_r = tot_pos_r + 3
ws_pos.cell(row=comp_start_r, column=2, value="КОНКУРЕНТНОЕ ОКРУЖЕНИЕ И РАЗРЫВЫ ДО СМЕЖНЫХ ПОЗИЦИЙ В ЦФО:").font = font_section_hdr

headers_comp = [
    'Бренд', '1-е место в ЦФО', '2-е место в ЦФО', '3-е место в ЦФО', 'Позиция АвтоГЕРМЕС', 'Разрыв / Отрыв'
]
for c_idx, h in enumerate(headers_comp, start=2):
    cell = ws_pos.cell(row=comp_start_r + 2, column=c_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_header_slate
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws_pos.row_dimensions[comp_start_r + 2].height = 26

comp_rows = [
    ('LADA', 'АвтоГЕРМЕС: 256 шт. (76.9%)', 'ГК 1: 26 шт. (7.8%)', 'ГК 2: 15 шт. (4.5%)', '1-е место', 'Отрыв от 2-го места: +230 шт. (+69.1 п.п.)'),
    ('SOLARIS', 'АвтоГЕРМЕС: 120 шт. (54.1%)', 'ГК 1: 68 шт. (30.6%)', 'ГК 2: 20 шт. (9.0%)', '1-е место', 'Отрыв от 2-го места: +52 шт. (+23.5 п.п.)'),
    ('BELGEE', 'ГК 1: 39 шт. (41.1%)', 'АвтоГЕРМЕС: 30 шт. (31.6%)', 'ГК 2: 16 шт. (16.8%)', '2-е место', 'Разрыв до 1-го места: -9 шт.; отрыв от 3-го места: +14 шт.'),
    ('GEELY', 'ГК 1: 72 шт. (52.2%)', 'АвтоГЕРМЕС: 41 шт. (29.7%)', 'ГК 2: 10 шт. (7.2%)', '2-е место', 'Разрыв до 1-го места: -31 шт.; отрыв от 3-го места: +31 шт.'),
    ('CHANGAN', 'ГК 1: 23 шт. (46.9%)', 'ГК 2: 13 шт. (26.5%)', 'АвтоГЕРМЕС: 10 шт. (20.4%)', '3-е место', 'Разрыв до 2-го места: -3 шт.; до 1-го места: -13 шт.')
]

for r_offset, c_row in enumerate(comp_rows):
    r_idx = comp_start_r + 3 + r_offset
    ws_pos.row_dimensions[r_idx].height = 22
    for c_offset, val in enumerate(c_row):
        c_idx = 2 + c_offset
        cell = ws_pos.cell(row=r_idx, column=c_idx, value=val)
        cell.border = thin_border
        if c_offset == 0:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="left", vertical="center")
        elif c_offset in (1, 2, 3):
            cell.font = font_regular
            cell.alignment = Alignment(horizontal="left", vertical="center")
            if 'АвтоГЕРМЕС' in str(val):
                cell.font = font_bold
                cell.fill = fill_accent
        elif c_offset == 4:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="center", vertical="center")
            if '1-е' in str(val):
                cell.fill = fill_green_light
        else:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="left", vertical="center")

# Block 3: Стратегические выводы по 4 категориям
strat_start_r = comp_start_r + 3 + len(comp_rows) + 2
ws_pos.cell(row=strat_start_r, column=2, value="СТРАТЕГИЧЕСКИЕ АКЦЕНТЫ ПО 4 КАТЕГОРИЯМ:").font = font_section_hdr

strat_blocks = [
    ("1. Где АвтоГЕРМЕС уже занимает сильную позицию:", [
        "• LADA: 1-е место в ЦФО. Продажи составили 256 автомобилей (доля 76.9% рынка округа). Отрыв от ближайшего участника рынка составляет 230 автомобилей. Позиция стабильна: 1-е место во все 3 месяца (105 ➔ 73 ➔ 78 шт.).",
        "• SOLARIS: 1-е место в ЦФО. Реализовано 120 автомобилей (доля 54.1%). Отрыв от 2-го места составляет 52 автомобиля. Стабильное удержание 1-го места на протяжении всего 3-месячного периода (50 ➔ 41 ➔ 29 шт.)."
    ]),
    ("2. Где у АвтоГЕРМЕСА высокая доля рынка:", [
        "• LADA — 76.9% всех закрытых сделок округа за 3 месяца.",
        "• SOLARIS — 54.1% рынка ЦФО (более половины всех сделок округа).",
        "• BELGEE — 31.6% рынка ЦФО (практически каждый третий автомобиль марки).",
        "• GEELY — 29.7% рынка ЦФО (почти треть всех сделок марки в округе)."
    ]),
    ("3. Где объём рынка большой, но доля АвтоГЕРМЕСА относительно небольшая:", [
        "• GEELY: Емкость рынка ЦФО выросла в 3.9 раза — с 18 авто в июне до 70 авто в августе (суммарный объем 138 шт.). При этом доля АвтоГЕРМЕСА сократилась с 66.7% в июне до 14.3% в августе (продажи в августе составили 10 авто против 19 в июле).",
        "• CHANGAN: Емкость рынка ЦФО в августе восстановилась до 21 автомобиля (после 5 авто в июле), однако у АвтоГЕРМЕСА зафиксировано 0 продаж в августе (доля 0.0%)."
    ]),
    ("4. Где есть возможность увеличить позицию:", [
        "• BELGEE: АвтоГЕРМЕС занимает 2-е место с 30 автомобилями (доля 31.6%). Разрыв до 1-го места (ГК 1, 39 шт.) составляет всего 9 автомобилей за 3 месяца (в среднем 3 авто в месяц). Дополнительные 3-4 продажи в месяц обеспечат переход на 1-е место в ЦФО.",
        "• GEELY: АвтоГЕРМЕС занимает 2-е место (41 шт., 29.7%). Разрыв до 1-го места (ГК 1, 72 шт.) составляет 31 автомобиль за 3 месяца. Возврат к рыночной доле уровня июня (40-50%) позволит существенно сократить данный разрыв.",
        "• CHANGAN: АвтоГЕРМЕС занимает 3-е место с 10 автомобилями. Разрыв до 2-го места (ГК 2, 13 шт.) составляет всего 3 автомобиля. Активизация стока марки позволяет оперативно вернуть 2-е место."
    ])
]

curr_strat_r = strat_start_r + 2
for cat_title, bullets in strat_blocks:
    ws_pos.cell(row=curr_strat_r, column=2, value=cat_title).font = font_bold
    ws_pos.merge_cells(start_row=curr_strat_r, start_column=2, end_row=curr_strat_r, end_column=9)
    curr_strat_r += 1
    
    for b_text in bullets:
        ws_pos.cell(row=curr_strat_r, column=2, value=b_text).font = font_regular
        ws_pos.cell(row=curr_strat_r, column=2).alignment = Alignment(wrap_text=True, vertical="top")
        ws_pos.merge_cells(start_row=curr_strat_r, start_column=2, end_row=curr_strat_r, end_column=9)
        ws_pos.row_dimensions[curr_strat_r].height = 24
        curr_strat_r += 1
    curr_strat_r += 1

autofit(ws_pos)

# SHEET 4: Федеральные партнёры (STRICT CONFIDENTIALITY)
# ==============================================================================
ws4 = wb.create_sheet(title="Федеральные партнёры")
ws4.views.sheetView[0].showGridLines = True

ws4.cell(row=2, column=2, value="СРАВНЕНИЕ АВТОГЕРМЕСА С ФЕДЕРАЛЬНЫМИ ПАРТНЕРАМИ В ЦФО").font = font_title
ws4.cell(row=3, column=2, value="Конфиденциальность: все конкурирующие холдинги строго анонимизированы (ГК 1 .. ГК 5). Территория: ЦФО.").font = font_subtitle

headers_s4 = ['Партнер', 'Июнь 2026', 'Июль 2026', 'Август 2026', 'Итого за 3 мес', 'Доля в ЦФО (%)']
for c_idx, h in enumerate(headers_s4, start=2):
    cell = ws4.cell(row=5, column=c_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_header_navy
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws4.row_dimensions[5].height = 26

partners_data = [
    ('АвтоГЕРМЕС', 206, 166, 145, 517, 0.2467, True),
    ('ГК 1', 56, 134, 129, 319, 0.1522, False),
    ('ГК 2', 46, 22, 33, 101, 0.0482, False),
    ('ГК 3', 0, 0, 15, 15, 0.0072, False),
    ('ГК 4', 2, 1, 2, 5, 0.0024, False),
    ('ГК 5', 0, 1, 0, 1, 0.0005, False),
    ('Прочие партнеры ЦФО', 179, 439, 520, 1138, 0.5429, False)
]

for r_offset, p_row in enumerate(partners_data):
    r_idx = 6 + r_offset
    p_name, m6, m7, m8, tot, sh, is_ag = p_row
    ws4.row_dimensions[r_idx].height = 20
    
    vals = [p_name, m6, m7, m8, tot, sh]
    for c_offset, val in enumerate(vals):
        c_idx = 2 + c_offset
        cell = ws4.cell(row=r_idx, column=c_idx, value=val)
        cell.border = thin_border
        if is_ag:
            cell.font = font_bold
            cell.fill = fill_highlight
        else:
            cell.font = font_regular
        
        if c_offset == 0:
            cell.alignment = Alignment(horizontal="left", vertical="center")
        elif c_offset in (1, 2, 3, 4):
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "#,##0"
            if c_offset == 4 and not is_ag:
                cell.font = font_bold
        else:
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "0.00%"
            if not is_ag:
                cell.font = font_bold

# Total row
tot_r_s4 = 6 + len(partners_data)
ws4.row_dimensions[tot_r_s4].height = 22
tot_vals_s4 = ['ИТОГО РЫНОК ЦФО', 489, 763, 844, 2096, 1.0000]
for c_offset, val in enumerate(tot_vals_s4):
    c_idx = 2 + c_offset
    cell = ws4.cell(row=tot_r_s4, column=c_idx, value=val)
    cell.font = font_bold
    cell.border = double_bottom_border
    cell.fill = fill_subtotal
    if c_offset == 0:
        cell.alignment = Alignment(horizontal="left", vertical="center")
    elif c_offset in (1, 2, 3, 4):
        cell.alignment = Alignment(horizontal="right", vertical="center")
        cell.number_format = "#,##0"
    else:
        cell.alignment = Alignment(horizontal="right", vertical="center")
        cell.number_format = "0.00%"

# Notes on federal partners
ws4.cell(row=15, column=2, value="КЛЮЧЕВЫЕ ВЫВОДЫ ПО ФЕДЕРАЛЬНЫМ ПАРТНЕРАМ:").font = font_section_hdr
notes_s4 = [
    "• АвтоГЕРМЕС — абсолютный лидер №1 среди всех федеральных групп компаний в ЦФО (517 авто vs 319 у ближайшего конкурента ГК 1).",
    "• Разрыв с ГК 1 составляет +198 проданных автомобилей за 3 месяца (+62% к объему конкурента).",
    "• Рост объема ГК 1 в июле-августе был обеспечен фокусом на JETOUR и Geely. Подключение этих брендов в АвтоГЕРМЕСЕ позволит ещё сильнее оторваться от конкурентов."
]
for idx, n in enumerate(notes_s4, start=16):
    ws4.cell(row=idx, column=2, value=n).font = font_regular
    ws4.merge_cells(start_row=idx, start_column=2, end_row=idx, end_column=7)
    ws4.row_dimensions[idx].height = 18

autofit(ws4)


# ==============================================================================
# SHEET 5: Динамика
# ==============================================================================
ws5 = wb.create_sheet(title="Динамика")
ws5.views.sheetView[0].showGridLines = True

ws5.cell(row=2, column=2, value="ДЕТАЛЬНАЯ ДИНАМИКА БРЕНДОВ АВТОГЕРМЕСА (МЕСЯЦ К МЕСЯЦУ)").font = font_title
ws5.cell(row=3, column=2, value="Классификация тренда: 🟢 рост, ⚪ стабильно, 🔴 снижение. Фактические данные за Июнь, Июль, Август 2026.").font = font_subtitle

headers_s5 = ['Бренд', 'Июнь 2026 (шт)', 'Июль 2026 (шт)', 'Август 2026 (шт)', 'Сумма (3 мес)', 'Июль к Июню', 'Август к Июлю', 'Классификация']
for c_idx, h in enumerate(headers_s5, start=2):
    cell = ws5.cell(row=4, column=c_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_header_navy
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws5.row_dimensions[4].height = 26

dyn_data = [
    ('LADA', 105, 73, 78, 256, '-32 шт. (-30.5%)', '+5 шт. (+6.8%)', '⚪ Стабильно'),
    ('SOLARIS', 50, 41, 29, 120, '-9 шт. (-18.0%)', '-12 шт. (-29.3%)', '🔴 Снижение'),
    ('Geely & Belgee', 30, 24, 17, 71, '-6 шт. (-20.0%)', '-7 шт. (-29.2%)', '🔴 Снижение'),
    ('JETOUR', 6, 17, 11, 34, '+11 шт. (+183.3%)', '-6 шт. (-35.3%)', '🟢 Рост к июню'),
    ('SOUEAST', 0, 7, 8, 15, '+7 шт. (Старт)', '+1 шт. (+14.3%)', '🟢 Рост'),
    ('CHANGAN', 9, 1, 0, 10, '-8 шт. (-88.9%)', '-1 шт. (-100%)', '🔴 Снижение'),
    ('CHERY & TENET', 3, 0, 0, 3, '-3 шт. (-100%)', '0 шт.', '🔴 Снижение'),
    ('Прочие бренды', 3, 3, 2, 8, '0 шт. (0.0%)', '-1 шт. (-33.3%)', '⚪ Стабильно')
]

for r_offset, d_row in enumerate(dyn_data):
    r_idx = 5 + r_offset
    ws5.row_dimensions[r_idx].height = 20
    for c_offset, val in enumerate(d_row):
        c_idx = 2 + c_offset
        cell = ws5.cell(row=r_idx, column=c_idx, value=val)
        cell.border = thin_border
        if c_offset == 0:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="left", vertical="center")
        elif c_offset in (1, 2, 3, 4):
            cell.font = font_bold if c_offset == 4 else font_regular
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "#,##0"
            if c_offset == 4:
                cell.fill = fill_accent
        elif c_offset in (5, 6):
            cell.font = font_regular
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="center", vertical="center")
            if '🟢' in str(val):
                cell.fill = fill_green_light
            elif '🔴' in str(val):
                cell.fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
            else:
                cell.fill = fill_subtotal

# Total Row
tot_dyn_r = 5 + len(dyn_data)
ws5.row_dimensions[tot_dyn_r].height = 22
tot_dyn_vals = ['ИТОГО АВТОГЕРМЕС', 206, 166, 145, 517, '-40 шт. (-19.4%)', '-21 шт. (-12.7%)', '⚪ Лидер ЦФО']
for c_offset, val in enumerate(tot_dyn_vals):
    c_idx = 2 + c_offset
    cell = ws5.cell(row=tot_dyn_r, column=c_idx, value=val)
    cell.font = font_bold
    cell.border = double_bottom_border
    cell.fill = fill_subtotal
    if c_offset == 0:
        cell.alignment = Alignment(horizontal="left", vertical="center")
    elif c_offset in (1, 2, 3, 4):
        cell.alignment = Alignment(horizontal="right", vertical="center")
        cell.number_format = "#,##0"
    else:
        cell.alignment = Alignment(horizontal="center", vertical="center")

autofit(ws5)


# ==============================================================================
# SHEET 6: ТОП-20 JETOUR (STRICT CONFIDENTIALITY)
# ==============================================================================
ws6 = wb.create_sheet(title="ТОП-20 JETOUR")
ws6.views.sheetView[0].showGridLines = True

ws6.cell(row=2, column=2, value="ТОП-20 ДИЛЕРСКИХ ПЛОЩАДОК JETOUR В ЦФО (ПОСЛЕДНИЕ 2 МЕСЯЦА)").font = font_title
ws6.cell(row=3, column=2, value="Период: Июль и Август 2026 года. Конфиденциальность: все конкуренты строго анонимизированы (Дилер 1 .. Дилер 20).").font = font_subtitle

headers_s6 = ['Ранг в ЦФО', 'Дилерская площадка', 'Июль 2026 (шт)', 'Август 2026 (шт)', 'Сумма за 2 мес (шт)', 'Доля в ЦФО за 2 мес (%)', 'Динамика MoM (шт / %)']
for c_idx, h in enumerate(headers_s6, start=2):
    cell = ws6.cell(row=5, column=c_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_header_navy
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws6.row_dimensions[5].height = 26

jetour_dealers_data = [
    (1, 'Дилер 1', 65, 60, 125, 0.1534, '-5 шт. (-7.7%)', False),
    (2, 'Дилер 2', 42, 43, 85, 0.1043, '+1 шт. (+2.4%)', False),
    (3, 'Дилер 3', 59, 23, 82, 0.1006, '-36 шт. (-61.0%)', False),
    (4, 'Дилер 4', 30, 15, 45, 0.0552, '-15 шт. (-50.0%)', False),
    (5, 'Дилер 5', 21, 22, 43, 0.0528, '+1 шт. (+4.8%)', False),
    (6, 'Дилер 6', 27, 16, 43, 0.0528, '-11 шт. (-40.7%)', False),
    (7, 'Дилер 7', 20, 17, 37, 0.0454, '-3 шт. (-15.0%)', False),
    (8, 'Дилер 8', 18, 13, 31, 0.0380, '-5 шт. (-27.8%)', False),
    (9, 'Дилер 9', 22, 9, 31, 0.0380, '-13 шт. (-59.1%)', False),
    (10, 'Дилер 10', 23, 7, 30, 0.0368, '-16 шт. (-69.6%)', False),
    (11, 'АвтоГЕРМЕС', 17, 11, 28, 0.0344, '-6 шт. (-35.3%)', True),
    (12, 'Дилер 12', 16, 11, 27, 0.0331, '-5 шт. (-31.2%)', False),
    (13, 'Дилер 13', 10, 12, 22, 0.0270, '+2 шт. (+20.0%)', False),
    (14, 'Дилер 14', 9, 11, 20, 0.0245, '+2 шт. (+22.2%)', False),
    (15, 'Дилер 15', 9, 10, 19, 0.0233, '+1 шт. (+11.1%)', False),
    (16, 'Дилер 16', 9, 9, 18, 0.0221, '0 шт. (0.0%)', False),
    (17, 'Дилер 17', 5, 11, 16, 0.0196, '+6 шт. (+120.0%)', False),
    (18, 'Дилер 18', 13, 3, 16, 0.0196, '-10 шт. (-76.9%)', False),
    (19, 'Дилер 19', 2, 10, 12, 0.0147, '+8 шт. (+400.0%)', False),
    (20, 'Дилер 20', 6, 6, 12, 0.0147, '0 шт. (0.0%)', False)
]

for r_offset, d_entry in enumerate(jetour_dealers_data):
    r_idx = 6 + r_offset
    rank, name, m7, m8, tot, sh, mom, is_ag = d_entry
    ws6.row_dimensions[r_idx].height = 20
    
    vals = [rank, name, m7, m8, tot, sh, mom]
    for c_offset, val in enumerate(vals):
        c_idx = 2 + c_offset
        cell = ws6.cell(row=r_idx, column=c_idx, value=val)
        cell.border = thin_border
        
        if is_ag:
            cell.font = font_bold
            cell.fill = fill_highlight
        else:
            cell.font = font_regular
            
        if c_offset == 0:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif c_offset == 1:
            cell.alignment = Alignment(horizontal="left", vertical="center")
        elif c_offset in (2, 3, 4):
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "#,##0"
            if c_offset == 4 and not is_ag:
                cell.font = font_bold
        elif c_offset == 5:
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "0.00%"
            if not is_ag:
                cell.font = font_bold
        else:
            cell.alignment = Alignment(horizontal="center", vertical="center")

# Subtotal TOP-20 row 26
ws6.row_dimensions[26].height = 21
ws6.cell(row=26, column=2, value="ИТОГО ТОП-20 ДИЛЕРОВ").font = font_bold
ws6.cell(row=26, column=2).alignment = Alignment(horizontal="left", vertical="center")
ws6.merge_cells("B26:C26")
for c_idx in range(2, 9):
    ws6.cell(row=26, column=c_idx).border = thin_border
    ws6.cell(row=26, column=c_idx).fill = fill_subtotal

ws6.cell(row=26, column=4, value=423).number_format = "#,##0"
ws6.cell(row=26, column=4).font = font_bold
ws6.cell(row=26, column=4).alignment = Alignment(horizontal="right", vertical="center")

ws6.cell(row=26, column=5, value=319).number_format = "#,##0"
ws6.cell(row=26, column=5).font = font_bold
ws6.cell(row=26, column=5).alignment = Alignment(horizontal="right", vertical="center")

ws6.cell(row=26, column=6, value=742).number_format = "#,##0"
ws6.cell(row=26, column=6).font = font_bold
ws6.cell(row=26, column=6).alignment = Alignment(horizontal="right", vertical="center")

ws6.cell(row=26, column=7, value=0.9104).number_format = "0.00%"
ws6.cell(row=26, column=7).font = font_bold
ws6.cell(row=26, column=7).alignment = Alignment(horizontal="right", vertical="center")

ws6.cell(row=26, column=8, value='-104 шт. (-24.6%)').font = font_bold
ws6.cell(row=26, column=8).alignment = Alignment(horizontal="center", vertical="center")

# Total Market row 27
ws6.row_dimensions[27].height = 22
ws6.cell(row=27, column=2, value="ВСЕГО РЫНОК JETOUR В ЦФО").font = font_bold
ws6.cell(row=27, column=2).alignment = Alignment(horizontal="left", vertical="center")
ws6.merge_cells("B27:C27")
for c_idx in range(2, 9):
    ws6.cell(row=27, column=c_idx).border = double_bottom_border
    ws6.cell(row=27, column=c_idx).fill = fill_accent

ws6.cell(row=27, column=4, value=451).number_format = "#,##0"
ws6.cell(row=27, column=4).font = font_bold
ws6.cell(row=27, column=4).alignment = Alignment(horizontal="right", vertical="center")

ws6.cell(row=27, column=5, value=364).number_format = "#,##0"
ws6.cell(row=27, column=5).font = font_bold
ws6.cell(row=27, column=5).alignment = Alignment(horizontal="right", vertical="center")

ws6.cell(row=27, column=6, value=815).number_format = "#,##0"
ws6.cell(row=27, column=6).font = font_bold
ws6.cell(row=27, column=6).alignment = Alignment(horizontal="right", vertical="center")

ws6.cell(row=27, column=7, value=1.0000).number_format = "0.00%"
ws6.cell(row=27, column=7).font = font_bold
ws6.cell(row=27, column=7).alignment = Alignment(horizontal="right", vertical="center")

ws6.cell(row=27, column=8, value='-87 шт. (-19.3%)').font = font_bold
ws6.cell(row=27, column=8).alignment = Alignment(horizontal="center", vertical="center")

autofit(ws6)


# ==============================================================================
# SHEET 7: JETOUR ЦФО (Рынок vs АвтоГЕРМЕС и Сценарии роста)
# ==============================================================================
ws7 = wb.create_sheet(title="JETOUR ЦФО")
ws7.views.sheetView[0].showGridLines = True

ws7.cell(row=2, column=2, value="JETOUR — АВТОГЕРМЕС VS РЫНОК ЦФО И СЦЕНАРИИ РОСТА").font = font_title
ws7.cell(row=3, column=2, value="Анализ текущей позиции и моделирование расчетного потенциала увеличения продаж").font = font_subtitle

# Table 1: Market Position Overview
ws7.cell(row=5, column=2, value="1. ТЕКУЩАЯ ПОЗИЦИЯ АВТОГЕРМЕСА В СЕГМЕНТЕ JETOUR (ЦФО)").font = font_section_hdr

headers_s7_1 = ['Период', 'Рынок JETOUR в ЦФО (шт)', 'Продажи АвтоГЕРМЕС (шт)', 'Доля АвтоГЕРМЕС (%)', 'Позиция в ЦФО']
for c_idx, h in enumerate(headers_s7_1, start=2):
    cell = ws7.cell(row=6, column=c_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_header_navy
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws7.row_dimensions[6].height = 24

jet_summary_rows = [
    ('Июнь 2026', 170, 6, 0.0353, 'Вхождение в бренд'),
    ('Июль 2026', 451, 17, 0.0377, 'Топ-11 в округе'),
    ('Август 2026', 364, 11, 0.0302, 'Топ-11 в округе'),
    ('Итого за 2 полных мес (Июл+Авг)', 815, 28, 0.0344, '11-е место в ТОП-20 ЦФО'),
    ('Итого за 3 полных мес (Июн+Июл+Авг)', 985, 34, 0.0345, 'Топ-12 в ЦФО')
]

for r_offset, r_data in enumerate(jet_summary_rows):
    r_idx = 7 + r_offset
    ws7.row_dimensions[r_idx].height = 20
    is_tot = r_offset >= 3
    for c_offset, val in enumerate(r_data):
        c_idx = 2 + c_offset
        cell = ws7.cell(row=r_idx, column=c_idx, value=val)
        cell.border = double_bottom_border if r_offset == 4 else thin_border
        if is_tot:
            cell.font = font_bold
            cell.fill = fill_highlight if r_offset == 3 else fill_subtotal
        else:
            cell.font = font_regular
            
        if c_offset == 0:
            cell.alignment = Alignment(horizontal="left", vertical="center")
        elif c_offset in (1, 2):
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "#,##0"
        elif c_offset == 3:
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "0.00%"
        else:
            cell.alignment = Alignment(horizontal="center", vertical="center")

# Table 2: Growth Scenario Modeling
ws7.cell(row=14, column=2, value="2. МОДЕЛИРОВАНИЕ ДОПОЛНИТЕЛЬНОГО ОБЪЕМА ПРОДАЖ JETOUR В ЦФО").font = font_section_hdr

headers_s7_2 = [
    'Сценарий развития', 'Целевая доля в ЦФО', 'Расчетные продажи за 2 мес (шт)',
    'Прирост за 2 мес к факту (шт)', 'Среднемесячный прирост (шт/мес)', 'Ориентир на рынке ЦФО'
]

for c_idx, h in enumerate(headers_s7_2, start=2):
    cell = ws7.cell(row=15, column=c_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_header_slate
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws7.row_dimensions[15].height = 26

scenarios_data = [
    ('Факт (текущий базовый уровень)', 0.0344, 28, 0, 0.0, '11-е место (текущая позиция)'),
    ('Сценарий 1: Рост доли на +2.0 п.п.', 0.0544, 44, 16, 8.0, 'Уровень Дилера 4–6 (ТОП-5 в ЦФО)'),
    ('Сценарий 2: Рост доли на +5.0 п.п.', 0.0844, 69, 41, 20.5, 'Уровень Дилера 3 (ТОП-3 в ЦФО)'),
    ('Сценарий 3: Выход на уровень лидеров (10.0%)', 0.1000, 82, 54, 27.0, 'Уровень Дилера 2–3 (Борьба за ТОП-2)')
]

for r_offset, s_row in enumerate(scenarios_data):
    r_idx = 16 + r_offset
    ws7.row_dimensions[r_idx].height = 20
    is_base = (r_offset == 0)
    for c_offset, val in enumerate(s_row):
        c_idx = 2 + c_offset
        cell = ws7.cell(row=r_idx, column=c_idx, value=val)
        cell.border = thin_border
        if is_base:
            cell.font = font_bold
            cell.fill = fill_subtotal
        else:
            cell.font = font_bold if c_offset in (2, 3, 4) else font_regular
            if c_offset in (3, 4):
                cell.fill = fill_green_light
        
        if c_offset == 0:
            cell.alignment = Alignment(horizontal="left", vertical="center")
        elif c_offset == 1:
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "0.00%"
        elif c_offset in (2, 3):
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "#,##0"
        elif c_offset == 4:
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.number_format = "+#,##0.0" if not is_base else "0.0"
        else:
            cell.alignment = Alignment(horizontal="left", vertical="center")

# Note on calculations
ws7.cell(row=21, column=2, value=(
    "ВАЖНОЕ ПРИМЕЧАНИЕ: Расчётный потенциал носит сценарный характер, рассчитан на базе фактической емкости рынка JETOUR в ЦФО (815 авто за 2 мес) "
    "и НЕ является гарантированным результатом. Достижение показателей возможно при реализации совместного комплекса коммерческих и маркетинговых мер."
)).font = font_muted
ws7.cell(row=21, column=2).alignment = Alignment(wrap_text=True, vertical="top")
ws7.merge_cells(start_row=21, start_column=2, end_row=22, end_column=7)

autofit(ws7)


# ==============================================================================
# SHEET 8: Точки роста и предложения
# ==============================================================================
ws8 = wb.create_sheet(title="Точки роста и предложения")
ws8.views.sheetView[0].showGridLines = True

ws8.cell(row=2, column=2, value="СТРАТЕГИЧЕСКИЕ ТОЧКИ РОСТА И ПРЕДЛОЖЕНИЯ ДЛЯ АВТОГЕРМЕСА").font = font_title
ws8.cell(row=3, column=2, value="Конкретные направления масштабирования продаж на основе анализа емкости рынка ЦФО").font = font_subtitle

# Section 1: Growth Drivers Matrix
ws8.cell(row=5, column=2, value="1. МАТРИЦА ТОЧЕК РОСТА ПО БРЕНДАМ В ЦФО").font = font_section_hdr

headers_s8_1 = [
    'Бренд', 'Рынок ЦФО (3 мес)', 'Продажи АГ (3 мес)', 'Текущая доля АГ',
    'Динамика бренда', 'В чем возможность масштабирования', 'Конкретное действие со стороны СберАвто'
]

for c_idx, h in enumerate(headers_s8_1, start=2):
    cell = ws8.cell(row=6, column=c_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_header_navy
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws8.row_dimensions[6].height = 28

growth_matrix = [
    (
        'JETOUR', 985, 34, 0.0345, 'Рост емкости: июнь 170 -> июль 451 -> авг 364',
        'Крупнейший бренд на платформе в ЦФО. У АГ 11-е место (доля 3.5%). Подъем в ТОП-5 дилеров дает +20 авто/мес.',
        'Целевое направление онлайн-заявок СберАвто на ДЦ АвтоГЕРМЕС, приоритетная выдача в автокаталоге, субсидированная авторассрочка.'
    ),
    (
        'Geely & Belgee', 233, 71, 0.3047, 'Рынок вырос с 46 до 108 шт. Продажи АГ упали с 30 до 17 шт.',
        'Рынок вырос в 2.3 раза, но доля АГ упала с 65% до 16%. Возврат к доле 40% вернет продажи на уровень 40+ авто/мес.',
        'Аудит доступности складов, совместная маркетинговая кампания по Belgee X50/X70, специальные условия трейд-ин через СберАвто.'
    ),
    (
        'SOUEAST', 102, 15, 0.1471, 'Старт продаж: июль 7 шт., август 8 шт. Рынок вырос до 74 шт.',
        'Новый быстрорастущий бренд. АвтоГЕРМЕС успешно запустил продажи (доля 14.7%). Высокий интерес аудитории к кроссоверам S07/S09.',
        'Подключение 100% дилерских центров АвтоГЕРМЕС с брендом SOUEAST, баннерная поддержка на главной странице СберАвто.'
    ),
    (
        'SOLARIS', 222, 120, 0.5405, 'Продажи АГ: июнь 50 -> июль 41 -> авг 29. Рынок 63 шт.',
        'Флагманский бренд АвтоГЕРМЕСА с долей >50%. Важно защитить доминирование при активизации федеральных конкурентов (ГК 2).',
        'Программа "Гарантия лучшей цены" в экосистеме Сбера, интеграция спецпредложений в витрину СберБанк Онлайн.'
    ),
    (
        'GAC / CHANGAN', 139, 10, 0.0719, 'GAC взлетел с 11 до 79 шт. Changan упал у АГ с 9 до 0 шт.',
        'GAC — второй по темпам роста бренд в августе (79 авто в ЦФО). АвтоГЕРМЕС пока не продавал GAC в СберАвто.',
        'Пилотное подключение дилерских центров GAC и Changan АвтоГЕРМЕС к онлайн-бронированию СберАвто с нулевой комиссией на первые сделки.'
    )
]

for r_offset, g_row in enumerate(growth_matrix):
    r_idx = 7 + r_offset
    ws8.row_dimensions[r_idx].height = 44
    b_name, mkt, ag, sh, dyn, opp, act = g_row
    
    vals = [b_name, mkt, ag, sh, dyn, opp, act]
    for c_offset, val in enumerate(vals):
        c_idx = 2 + c_offset
        cell = ws8.cell(row=r_idx, column=c_idx, value=val)
        cell.border = thin_border
        
        if c_offset == 0:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="left", vertical="top")
        elif c_offset in (1, 2):
            cell.font = font_bold if c_offset == 2 else font_regular
            cell.alignment = Alignment(horizontal="right", vertical="top")
            cell.number_format = "#,##0"
        elif c_offset == 3:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="right", vertical="top")
            cell.number_format = "0.0%"
            cell.fill = fill_highlight if b_name == 'JETOUR' else fill_accent
        elif c_offset in (4, 5, 6):
            cell.font = font_regular
            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

# Section 2: Concrete Actionable Proposals
ws8.cell(row=13, column=2, value="2. ЧТО ПРЕДЛОЖИТЬ АВТОГЕРМЕСУ: ПАКЕТ ИЗ 4 СОВМЕСТНЫХ ИНИЦИАТИВ").font = font_section_hdr

headers_s8_2 = ['№', 'Инициатива', 'Суть предложения и механизм реализации', 'Ожидаемый бизнес-эффект для АвтоГЕРМЕС']
for c_idx, h in enumerate(headers_s8_2, start=2):
    cell = ws8.cell(row=14, column=c_idx, value=h)
    cell.font = font_tbl_header
    cell.fill = fill_header_green
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws8.row_dimensions[14].height = 24

proposals_data = [
    (
        1, 'Совместный спринт по JETOUR «ТОП-5 в ЦФО»',
        'СберАвто направляет целевой входящий трафик покупателей JETOUR на площадки АвтоГЕРМЕС в Москве и МО, предоставляет выделенного менеджера сопровождения сделок. АвтоГЕРМЕС обеспечивает оперативный отклик (<15 мин) и наличие ходовых комплектаций Dashing и X70 Plus.',
        '+15 .. +25 закрытых сделок JETOUR в месяц, выход на устойчивое место в ТОП-5 дилеров ЦФО.'
    ),
    (
        2, 'Программа восстановления темпов Geely & Belgee',
        'Интеграция складов новых авто Geely/Belgee в режиме реального времени. Запуск совместной промо-акции с кешбэком бонусами СберСпасибо при оформлении автокредита Сбера через СберАвто.',
        'Восстановление доли в ЦФО до 35-40%, дополнительно +15..20 сделок ежемесячно.'
    ),
    (
        3, 'Масштабирование SOUEAST на все площадки холдинга',
        'Подключение всех авторизованных ДЦ холдинга к витрине СберАвто, добавление новинок S07 и S09 в подборки «Премьеры сезона» с прямой ссылкой на автомобили в наличии у АвтоГЕРМЕС.',
        'Рост продаж бренда до 20-25 авто в месяц, закрепление за АвтоГЕРМЕСОМ статуса ключевого партнера марки в ЦФО.'
    ),
    (
        4, 'Пилотное подключение дилерских центров GAC холдинга',
        'Бесшовное подключение складских остатков GAC АвтоГЕРМЕС к платформе. СберАвто предлагает тестовый период: 0% комиссии на первые 10 реализованных автомобилей для быстрой оценки эффективности канала.',
        'Вход в самый динамично растущий сегмент ЦФО (79 авто в августе) без стартовых маркетинговых затрат.'
    )
]

for r_offset, p_row in enumerate(proposals_data):
    r_idx = 15 + r_offset
    ws8.row_dimensions[r_idx].height = 42
    p_num, p_title, p_desc, p_eff = p_row
    
    vals = [p_num, p_title, p_desc, p_eff]
    for c_offset, val in enumerate(vals):
        c_idx = 2 + c_offset
        cell = ws8.cell(row=r_idx, column=c_idx, value=val)
        cell.border = thin_border
        
        if c_offset == 0:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="center", vertical="top")
        elif c_offset == 1:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        elif c_offset == 2:
            cell.font = font_regular
            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        else:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            cell.fill = fill_green_light

autofit(ws8)

output_path = '/Users/vaceslavgamaunov/Downloads/Аналитический_разбор_АвтоГЕРМЕС_СберАвто_ЦФО_Q3_2026_актуализированный.xlsx'
wb.save(output_path)
print(f"Workbook successfully generated and saved to: {output_path}")

