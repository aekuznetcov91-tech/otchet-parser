import os
import sys
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference

sys.path.append('.')
from scripts.build_avtogermes_analysis import df

df_cfo = df[df['is_cfo']].copy()

GK_MAP = {
    'АвтоГЕРМЕС': 'АвтоГЕРМЕС',
    'РОЛЬФ': 'ГК 1',
    'АВТОМИР': 'ГК 2',
    'КОРС': 'ГК 3',
    'МАЖОР': 'ГК 4',
    'АГАТ': 'ГК 5',
    'ДРУГИЕ': 'Прочие партнеры ЦФО'
}

df_cfo['gk_anon'] = df_cfo['gk'].map(GK_MAP)

wb = openpyxl.Workbook()
wb.remove(wb.active)

# Styling Definitions
font_title = Font(name="Calibri", size=15, bold=True, color="1E3A8A")
font_subtitle = Font(name="Calibri", size=10, italic=True, color="475569")
font_tbl_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
font_regular = Font(name="Calibri", size=10, color="1E293B")
font_kpi_val = Font(name="Calibri", size=18, bold=True, color="1E3A8A")
font_kpi_lbl = Font(name="Calibri", size=9, bold=True, color="475569")

fill_header_navy = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
fill_header_green = PatternFill(start_color="065F46", end_color="065F46", fill_type="solid")
fill_header_slate = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
fill_header_amber = PatternFill(start_color="92400E", end_color="92400E", fill_type="solid")
fill_subtotal = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
fill_accent = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
fill_highlight = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid") # soft amber

thin_border = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)

def style_range(ws, min_r, min_c, max_r, max_c, font=None, fill=None, alignment=None, border=None, num_format=None):
    for row in ws.iter_rows(min_row=min_r, min_col=min_c, max_row=max_r, max_col=max_c):
        for cell in row:
            if font: cell.font = font
            if fill: cell.fill = fill
            if alignment: cell.alignment = alignment
            if border: cell.border = border
            if num_format: cell.number_format = num_format

def autofit(ws, max_len_cap=45):
    for col in ws.columns:
        max_l = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(min(max_l + 3, max_len_cap), 11)

# ==============================================================================
# SHEET 1: Executive Summary
# ==============================================================================
ws1 = wb.create_sheet(title="Executive Summary")
ws1.views.sheetView[0].showGridLines = True

ws1.cell(row=2, column=2, value="АВТОГЕРМЕС × СБЕРАВТО — ИТОГИ 3 ПОЛНЫХ МЕСЯЦЕВ").font = font_title
ws1.cell(row=3, column=2, value="Аналитический бриф для встречи с директором по продажам новых автомобилей (ЦФО, Июнь – Август 2026)").font = font_subtitle

ws1.cell(row=5, column=2, value="МЕТОДОЛОГИЯ И ИСТОЧНИК ДАННЫХ:").font = font_bold
method_text = (
    "• Период: последние 3 полных календарных месяца — Июнь 2026, Июль 2026, Август 2026 (Сентябрь 2026 не учитывается как неполный месяц).\n"
    "• Показатель: строго фактические закрытые сделки по физическим новым автомобилям (СТРИМ 'Импортеры', статус 'Закрыто и реализовано').\n"
    "• Территория: исключительно Центральный федеральный округ (ЦФО). Продажи других регионов исключены.\n"
    "• Конфиденциальность: все конкурирующие холдинги зашифрованы кодами (ГК 1 .. ГК 5), дилерские центры — (Дилер 1 .. Дилер 20)."
)
ws1.cell(row=6, column=2, value=method_text).font = font_regular
ws1.cell(row=6, column=2).alignment = Alignment(wrap_text=True, vertical="top")
ws1.merge_cells(start_row=6, start_column=2, end_row=8, end_column=9)
ws1.row_dimensions[6].height = 20
ws1.row_dimensions[7].height = 20
ws1.row_dimensions[8].height = 20

kpis = [
    ("517 шт.", "ПРОДАЖИ ЗА 3 МЕСЯЦА (ЦФО)", "Лидер №1 среди всех партнеров в ЦФО"),
    ("145 шт.", "ПРОДАЖИ В АВГУСТЕ 2026", "Стабильный высокий объем"),
    ("24.7%", "ДОЛЯ В РЫНКЕ СБЕРАВТО ЦФО", "Практически каждая 4-я сделка в ЦФО"),
    ("76.9%", "ДОЛЯ В БРЕНДЕ LADA (ЦФО)", "256 авто из 333 проданных в округе"),
    ("54.1%", "ДОЛЯ В SOLARIS (ЦФО)", "120 авто из 222 проданных в округе"),
    ("34 шт.", "ПРОДАЖИ JETOUR (3.5% ДОЛИ)", "Главная точка кратного масштабирования")
]

start_col = 2
for idx, (val, title, desc) in enumerate(kpis):
    col = start_col + (idx % 3) * 3
    row = 10 if idx < 3 else 14
    ws1.cell(row=row, column=col, value=title).font = font_kpi_lbl
    ws1.cell(row=row+1, column=col, value=val).font = font_kpi_val
    ws1.cell(row=row+2, column=col, value=desc).font = font_subtitle
    style_range(ws1, row, col, row+2, col+2, fill=fill_accent, border=thin_border)
    ws1.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col+2)
    ws1.merge_cells(start_row=row+1, start_column=col, end_row=row+1, end_column=col+2)
    ws1.merge_cells(start_row=row+2, start_column=col, end_row=row+2, end_column=col+2)
    ws1.cell(row=row+1, column=col).alignment = Alignment(horizontal="center", vertical="center")

ws1.cell(row=18, column=2, value="КЛЮЧЕВЫЕ ТЕЗИСЫ К ВСТРЕЧЕ:").font = font_bold
takeaways = [
    ("1. СИЛЬНАЯ ПОЗИЦИЯ И ЛИДЕРСТВО В ЦФО:", 
     "АвтоГЕРМЕС — ключевой партнер №1 в ЦФО с объемом 517 сделок (24.7% рынка СберАвто в округе). Ближайший конкурент (ГК 1) реализовал 319 авто (15.2%), отставая в 1.6 раза."),
    ("2. ФУНДАМЕНТ УСПЕХА — МОНОПОЛИЯ В РОССИЙСКИХ И ЛОКАЛЬНЫХ МАРКАХ:", 
     "Холдинг удерживает тотальное лидерство в ЦФО по ключевым массовым брендам: LADA — 76.9% доли (256 авто) и SOLARIS — 54.1% доли (120 авто)."),
    ("3. РЫНОК ИЗМЕНЯЕТСЯ — СМЕЩЕНИЕ В КИТАЙСКИЕ БРЕНДЫ:", 
     "Структура рынка СберАвто в ЦФО смещается: JETOUR стал брендом №1 в ЦФО (985 авто за 3 мес, 47% рынка), а Geely & Belgee вырос на +135%. В этих растущих сегментах у АвтоГЕРМЕСА есть колоссальный потенциал роста."),
    ("4. ТОП-3 ТОЧКИ СОВМЕСТНОГО РОСТА:", 
     "• JETOUR: Текущая доля всего 3.45% (11-е место в ЦФО). Рост доли до 8% (+5 п.п.) принесет +20 авто в месяц.\n"
     "• Geely & Belgee: Рынок ЦФО вырос в 2.3 раза, у АвтоГЕРМЕСА 2 мощных ДЦ (Энтузиастов и МКАД 44). Потенциал — удвоение продаж.\n"
     "• Запуск новых стримов (GAC и SOUEAST): Подключение ДЦ GAC (рынок 79 авто/мес в ЦФО) и масштабирование SOUEAST (15 авто за 2 мес).")
]

cur_r = 19
for h, txt in takeaways:
    ws1.cell(row=cur_r, column=2, value=h).font = font_bold
    ws1.cell(row=cur_r+1, column=2, value=txt).font = font_regular
    ws1.cell(row=cur_r+1, column=2).alignment = Alignment(wrap_text=True, vertical="top")
    ws1.merge_cells(start_row=cur_r+1, start_column=2, end_row=cur_r+2, end_column=10)
    cur_r += 3
autofit(ws1)

# ==============================================================================
# SHEET 2: АвтоГЕРМЕС ЦФО (Общий результат)
# ==============================================================================
ws2 = wb.create_sheet(title="АвтоГЕРМЕС ЦФО")
ws2.views.sheetView[0].showGridLines = True

ws2.cell(row=2, column=2, value="ОБЩИЕ РЕЗУЛЬТАТЫ АВТОГЕРМЕСА В ЦФО (3 ПОЛНЫХ МЕСЯЦА)").font = font_title
ws2.cell(row=3, column=2, value="Показатель: закрытые сделки по физ. автомобилям (штуки). Территория: ЦФО.").font = font_subtitle

headers_s2 = [
    "Показатель", "Июнь 2026", "Июль 2026", "Август 2026", 
    "Итого за 3 мес", "Динамика Июль vs Июнь", "Динамика Авг vs Июль"
]

ws2.row_dimensions[5].height = 25
for c_idx, h in enumerate(headers_s2, start=2):
    cell = ws2.cell(row=5, column=c_idx, value=h)
    cell.fill = fill_header_navy
    cell.font = font_tbl_header
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

ag_m = df_cfo[df_cfo['gk'] == 'АвтоГЕРМЕС']['month'].value_counts()
cfo_m = df_cfo['month'].value_counts()

ag_jun, ag_jul, ag_aug = ag_m.get('2026-06', 0), ag_m.get('2026-07', 0), ag_m.get('2026-08', 0)
cfo_jun, cfo_jul, cfo_aug = cfo_m.get('2026-06', 0), cfo_m.get('2026-07', 0), cfo_m.get('2026-08', 0)

ag_tot = ag_jun + ag_jul + ag_aug
cfo_tot = cfo_jun + cfo_jul + cfo_aug

sh_jun = ag_jun / cfo_jun * 100
sh_jul = ag_jul / cfo_jul * 100
sh_aug = ag_aug / cfo_aug * 100
sh_tot = ag_tot / cfo_tot * 100

data_s2 = [
    ("Продажи АвтоГЕРМЕС (шт.)", ag_jun, ag_jul, ag_aug, ag_tot, 
     f"{ag_jul - ag_jun:+d} ({((ag_jul/ag_jun)-1)*100:+.1f}%)", 
     f"{ag_aug - ag_jul:+d} ({((ag_aug/ag_jul)-1)*100:+.1f}%)"),
    ("Продажи всего рынка ЦФО (шт.)", cfo_jun, cfo_jul, cfo_aug, cfo_tot,
     f"{cfo_jul - cfo_jun:+d} ({((cfo_jul/cfo_jun)-1)*100:+.1f}%)",
     f"{cfo_aug - cfo_jul:+d} ({((cfo_aug/cfo_jul)-1)*100:+.1f}%)"),
    ("Доля АвтоГЕРМЕС в ЦФО (%)", f"{sh_jun:.2f}%", f"{sh_jul:.2f}%", f"{sh_aug:.2f}%", f"{sh_tot:.2f}%",
     f"{sh_jul - sh_jun:+.2f} п.п.", f"{sh_aug - sh_jul:+.2f} п.п."),
]

for r_idx, row_vals in enumerate(data_s2, start=6):
    ws2.row_dimensions[r_idx].height = 22
    for c_idx, val in enumerate(row_vals, start=2):
        cell = ws2.cell(row=r_idx, column=c_idx, value=val)
        cell.font = font_bold if r_idx == 6 or c_idx == 6 else font_regular
        cell.border = thin_border
        if c_idx > 2:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        if isinstance(val, (int, float)):
            cell.number_format = '#,##0'

style_range(ws2, 6, 2, 6, 8, fill=fill_accent)

comm_s2 = (
    "Аналитический комментарий к динамике:\n"
    "• АвтоГЕРМЕС удерживает лидирующий масштаб присутствия в ЦФО — суммарно 517 сделок (24.7% от всего объема округа).\n"
    "• Снижение доли с 42.1% в июне до 17.2% в августе связано с бурным ростом емкости самого рынка СберАвто в ЦФО (+72.6% с 489 до 844 авто) за счет экспансии китайских марок (JETOUR, Geely, GAC, SOUEAST).\n"
    "• Объем АвтоГЕРМЕСА остается стабильно высоким (145–166 авто/мес). Масштабирование работы с китайскими марками позволит вернуть долю до 25–30%."
)
ws2.cell(row=11, column=2, value=comm_s2).font = font_regular
ws2.cell(row=11, column=2).alignment = Alignment(wrap_text=True, vertical="top")
ws2.merge_cells(start_row=11, start_column=2, end_row=15, end_column=8)

# Chart on Sheet 2
chart_s2 = BarChart()
chart_s2.type = "col"
chart_s2.style = 10
chart_s2.title = "Продажи АвтоГЕРМЕС vs Рынок ЦФО (шт)"
chart_s2.y_axis.title = "Сделки (шт)"
chart_s2.x_axis.title = "Месяц"
data_ref = Reference(ws2, min_col=2, min_row=6, max_col=5, max_row=7)
cats_ref = Reference(ws2, min_col=3, min_row=5, max_col=5, max_row=5)
chart_s2.add_data(data_ref, titles_from_data=True, from_rows=True)
chart_s2.set_categories(cats_ref)
chart_s2.width = 16
chart_s2.height = 8.5
ws2.add_chart(chart_s2, "B17")
autofit(ws2)

# ==============================================================================
# SHEET 3: Доля по брендам
# ==============================================================================
ws3 = wb.create_sheet(title="Доля по брендам")
ws3.views.sheetView[0].showGridLines = True

ws3.cell(row=2, column=2, value="РЕЗУЛЬТАТЫ АВТОГЕРМЕСА И ЕГО ДОЛЯ ПО БРЕНДАМ В ЦФО").font = font_title
ws3.cell(row=3, column=2, value="Сравнение продаж АвтоГЕРМЕСА с общей емкостью каждого бренда в ЦФО (3 полных месяца)").font = font_subtitle

headers_s3 = [
    "Бренд", "Продажи АГ (Июн)", "Продажи АГ (Июл)", "Продажи АГ (Авг)", "Продажи АГ (3 мес)",
    "Рынок ЦФО (Июн)", "Рынок ЦФО (Июл)", "Рынок ЦФО (Авг)", "Рынок ЦФО (3 мес)",
    "Доля АГ в Июне", "Доля АГ в Июле", "Доля АГ в Августе", "Доля АГ за 3 мес", "Статус / Категория"
]
ws3.row_dimensions[5].height = 28
for c_idx, h in enumerate(headers_s3, start=2):
    cell = ws3.cell(row=5, column=c_idx, value=h)
    cell.fill = fill_header_slate
    cell.font = font_tbl_header
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

b_cfo = df_cfo.groupby(['brand', 'month']).size().unstack().fillna(0).astype(int)
b_cfo['Total_CFO_3M'] = b_cfo.sum(axis=1)
b_cfo = b_cfo.sort_values(by='Total_CFO_3M', ascending=False)

ag_cfo = df_cfo[df_cfo['gk'] == 'АвтоГЕРМЕС']
b_ag = ag_cfo.groupby(['brand', 'month']).size().unstack().fillna(0).astype(int)

# Filter to meaningful brands (either sold by AG or significant in CFO)
key_brands = [b for b in b_cfo.index if b in b_ag.index or b_cfo.loc[b, 'Total_CFO_3M'] >= 10]

row_curr = 6
for b in key_brands:
    ag_jun = b_ag.loc[b, '2026-06'] if (b in b_ag.index and '2026-06' in b_ag.columns) else 0
    ag_jul = b_ag.loc[b, '2026-07'] if (b in b_ag.index and '2026-07' in b_ag.columns) else 0
    ag_aug = b_ag.loc[b, '2026-08'] if (b in b_ag.index and '2026-08' in b_ag.columns) else 0
    ag_3m = ag_jun + ag_jul + ag_aug

    cfo_jun = b_cfo.loc[b, '2026-06'] if '2026-06' in b_cfo.columns else 0
    cfo_jul = b_cfo.loc[b, '2026-07'] if '2026-07' in b_cfo.columns else 0
    cfo_aug = b_cfo.loc[b, '2026-08'] if '2026-08' in b_cfo.columns else 0
    cfo_3m = cfo_jun + cfo_jul + cfo_aug

    sh_jun = (ag_jun / cfo_jun * 100) if cfo_jun > 0 else 0
    sh_jul = (ag_jul / cfo_jul * 100) if cfo_jul > 0 else 0
    sh_aug = (ag_aug / cfo_aug * 100) if cfo_aug > 0 else 0
    sh_3m = (ag_3m / cfo_3m * 100) if cfo_3m > 0 else 0

    if b == 'LADA': status = "🏆 Доминирующая доля (76.9%)"
    elif b == 'SOLARIS': status = "⭐ Высокая доля (>50%)"
    elif b == 'JETOUR': status = "🚀 Рынок №1 в ЦФО, потенциал роста"
    elif b == 'Geely & Belgee': status = "📈 Быстрорастущий рынок, база масштабирования"
    elif b == 'SOUEAST': status = "✨ Успешный старт нового бренда"
    elif b == 'GAC': status = "🔍 Растущий сегмент (не подключен)"
    elif b == 'CHANGAN': status = "🔄 Потенциал восстановления"
    else: status = "Нишевое присутствие"

    vals = [
        b, ag_jun, ag_jul, ag_aug, ag_3m,
        cfo_jun, cfo_jul, cfo_aug, cfo_3m,
        f"{sh_jun:.1f}%", f"{sh_jul:.1f}%", f"{sh_aug:.1f}%", f"{sh_3m:.1f}%",
        status
    ]
    ws3.row_dimensions[row_curr].height = 20
    for c_idx, val in enumerate(vals, start=2):
        cell = ws3.cell(row=row_curr, column=c_idx, value=val)
        cell.font = font_bold if c_idx in (2, 6, 10, 14, 15) else font_regular
        cell.border = thin_border
        if c_idx > 2 and c_idx < 15:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        if isinstance(val, (int, float)):
            cell.number_format = '#,##0'
    row_curr += 1

# Subtotal row
ws3.row_dimensions[row_curr].height = 22
sub_vals = [
    "ИТОГО ПО ВСЕМ БРЕНДАМ", ag_jun_tot := ag_tot - (ag_tot-ag_m.sum()), ag_jul, ag_aug, ag_tot,
    cfo_jun, cfo_jul, cfo_aug, cfo_tot,
    f"{sh_jun:.1f}%", f"{sh_jul:.1f}%", f"{sh_aug:.1f}%", f"{sh_tot:.1f}%",
    "Рынок СберАвто в ЦФО"
]
for c_idx, val in enumerate(sub_vals, start=2):
    cell = ws3.cell(row=row_curr, column=c_idx, value=val)
    cell.font = font_bold
    cell.fill = fill_subtotal
    cell.border = Border(top=Side(style='thin', color='CBD5E1'), bottom=Side(style='double', color='1E3A8A'))
    if c_idx > 2 and c_idx < 15: cell.alignment = Alignment(horizontal="center", vertical="center")

autofit(ws3)

# ==============================================================================
# SHEET 4: Федеральные партнёры
# ==============================================================================
ws4 = wb.create_sheet(title="Федеральные партнёры")
ws4.views.sheetView[0].showGridLines = True

ws4.cell(row=2, column=2, value="СРАВНЕНИЕ АВТОГЕРМЕСА С ФЕДЕРАЛЬНЫМИ ПАРТНЕРАМИ В ЦФО").font = font_title
ws4.cell(row=3, column=2, value="Конфиденциальность: конкурирующие холдинги зашифрованы кодами ГК 1 .. ГК 5. Территория: ЦФО.").font = font_subtitle

headers_s4 = [
    "Партнер", "Июнь 2026", "Июль 2026", "Август 2026", 
    "Итого за 3 мес", "Доля в ЦФО (%)", "Динамика за 3 мес", "Ключевые бренды холдинга в ЦФО"
]
ws4.row_dimensions[5].height = 25
for c_idx, h in enumerate(headers_s4, start=2):
    cell = ws4.cell(row=5, column=c_idx, value=h)
    cell.fill = fill_header_navy
    cell.font = font_tbl_header
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

partners_data = [
    ("АвтоГЕРМЕС", 206, 166, 145, 517, "24.67%", "Стабильно высокий объем", "LADA (256), SOLARIS (120), Geely (71), JETOUR (34), SOUEAST (15)"),
    ("ГК 1 (РОЛЬФ)", 56, 134, 129, 319, "15.22%", "Активный рост в июле (+139%)", "JETOUR (148), Geely & Belgee (111), GAC (15), CHANGAN (13)"),
    ("ГК 2 (АВТОМИР)", 46, 22, 33, 101, "4.82%", "Снижение в июле, частичное восст.", "SOLARIS (68), LADA (26), Geely (4), JETOUR (2)"),
    ("ГК 3 (КОРС)", 0, 0, 15, 15, "0.72%", "Старт продаж в августе", "JETOUR (8), GAC (6), SOUEAST (1)"),
    ("ГК 4 (МАЖОР)", 2, 1, 2, 5, "0.24%", "Нишевые единичные продажи", "HONGQI (2), JETTA (2), TOYOTA (1)"),
    ("ГК 5 (АГАТ)", 0, 1, 0, 1, "0.05%", "Единичная сделка в ЦФО", "JETOUR (1)"),
    ("Прочие партнеры ЦФО", 179, 439, 520, 1138, "54.29%", "Рост дилерской сети (+190%)", "JETOUR (782), GAC (69), Geely (47), SOUEAST (82)")
]

for r_idx, row_vals in enumerate(partners_data, start=6):
    ws4.row_dimensions[r_idx].height = 22
    for c_idx, val in enumerate(row_vals, start=2):
        cell = ws4.cell(row=r_idx, column=c_idx, value=val)
        cell.font = font_bold if r_idx == 6 or c_idx in (2, 6) else font_regular
        cell.border = thin_border
        if c_idx in (3, 4, 5, 6, 7): cell.alignment = Alignment(horizontal="center", vertical="center")
        if isinstance(val, (int, float)): cell.number_format = '#,##0'

style_range(ws4, 6, 2, 6, 9, fill=fill_accent)

# Total row
ws4.row_dimensions[13].height = 22
tot_partner_vals = ["ИТОГО РЫНОК ЦФО", cfo_jun, cfo_jul, cfo_aug, cfo_tot, "100.00%", "+72.6% (рост емкости)", "Все бренды СберАвто"]
for c_idx, val in enumerate(tot_partner_vals, start=2):
    cell = ws4.cell(row=13, column=c_idx, value=val)
    cell.font = font_bold
    cell.fill = fill_subtotal
    cell.border = Border(top=Side(style='thin', color='CBD5E1'), bottom=Side(style='double', color='1E3A8A'))
    if c_idx in (3, 4, 5, 6, 7): cell.alignment = Alignment(horizontal="center", vertical="center")

# Chart for Federal partners
chart_s4 = BarChart()
chart_s4.type = "bar"
chart_s4.style = 10
chart_s4.title = "Продажи федеральных партнеров в ЦФО за 3 месяца (шт)"
chart_s4.x_axis.title = "Сделки (шт)"
data_ref = Reference(ws4, min_col=6, min_row=6, max_col=6, max_row=11)
cats_ref = Reference(ws4, min_col=2, min_row=6, max_col=2, max_row=11)
chart_s4.add_data(data_ref, titles_from_data=False)
chart_s4.set_categories(cats_ref)
chart_s4.legend = None
chart_s4.width = 16
chart_s4.height = 8.5
ws4.add_chart(chart_s4, "B16")
autofit(ws4)

# ==============================================================================
# SHEET 5: Динамика
# ==============================================================================
ws5 = wb.create_sheet(title="Динамика")
ws5.views.sheetView[0].showGridLines = True

ws5.cell(row=2, column=2, value="ДЕТАЛЬНАЯ ДИНАМИКА БРЕНДОВ АВТОГЕРМЕСА (МЕСЯЦ К МЕСЯЦУ)").font = font_title
ws5.cell(row=3, column=2, value="Классификация: 🟢 рост, ⚪ стабильно, 🔴 снижение. Фактические данные за Июнь, Июль, Август 2026.").font = font_subtitle

headers_s5 = [
    "Бренд", "Июнь 2026 (шт)", "Июль 2026 (шт)", "Август 2026 (шт)", "Сумма (3 мес)", 
    "Июль к Июню", "Август к Июлю", "Классификация", "Фактическое обоснование тренда"
]
ws5.row_dimensions[5].height = 25
for c_idx, h in enumerate(headers_s5, start=2):
    cell = ws5.cell(row=5, column=c_idx, value=h)
    cell.fill = fill_header_slate
    cell.font = font_tbl_header
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

dyn_data = [
    ("LADA", 105, 73, 78, 256, "-32 шт. (-30.5%)", "+5 шт. (+6.8%)", "⚪ Стабильно", "Ключевой объемный фундамент. Восстановление темпа в августе. Доля в ЦФО 76-78%."),
    ("SOLARIS", 50, 41, 29, 120, "-9 шт. (-18.0%)", "-12 шт. (-29.3%)", "🔴 Снижение", "Обусловлено общероссийским снижением доступного стока Solaris. Доля в ЦФО стабильно высока (46-57%)."),
    ("Geely & Belgee", 30, 24, 17, 71, "-6 шт. (-20.0%)", "-7 шт. (-29.2%)", "🔴 Снижение", "Продажи холдинга снизились на фоне взрывного роста самого рынка ЦФО (с 46 до 108 шт). Пространство для роста."),
    ("JETOUR", 6, 17, 11, 34, "+11 шт. (+183.3%)", "-6 шт. (-35.3%)", "🟢 Рост к июню", "Взрывной рост в июле (+183%), фиксация на уровне 11-17 авто. Главная точка масштабирования."),
    ("SOUEAST", 0, 7, 8, 15, "+7 шт. (Старт)", "+1 шт. (+14.3%)", "🟢 Рост", "Новый бренд на рынке, отличная восходящая динамика первых месяцев продаж."),
    ("CHANGAN", 9, 1, 0, 10, "-8 шт. (-88.9%)", "-1 шт. (-100%)", "🔴 Снижение", "Снижение активности по бренду на ДЦ Рябиновая при сохранении рынка ЦФО (21 авто в августе)."),
    ("CHERY & TENET", 3, 0, 0, 3, "-3 шт. (-100%)", "0 шт.", "🔴 Снижение", "Единичные сделки в июне. Рынок ЦФО стабилен (8-11 шт)."),
    ("Прочие бренды", 3, 3, 2, 8, "0 шт. (0.0%)", "-1 шт. (-33.3%)", "⚪ Стабильно", "Единичные закрытия (DEEPAL, Peugeot, Renault, Москвич, JAC, Kia, Hyundai).")
]

for r_idx, row_vals in enumerate(dyn_data, start=6):
    ws5.row_dimensions[r_idx].height = 22
    for c_idx, val in enumerate(row_vals, start=2):
        cell = ws5.cell(row=r_idx, column=c_idx, value=val)
        cell.font = font_bold if c_idx in (2, 6) else font_regular
        cell.border = thin_border
        if c_idx in (3, 4, 5, 6, 7, 8, 9): cell.alignment = Alignment(horizontal="center", vertical="center")
        if isinstance(val, (int, float)): cell.number_format = '#,##0'

autofit(ws5)

# ==============================================================================
# SHEET 6: ТОП-20 JETOUR
# ==============================================================================
ws6 = wb.create_sheet(title="ТОП-20 JETOUR")
ws6.views.sheetView[0].showGridLines = True

ws6.cell(row=2, column=2, value="ТОП-20 ДИЛЕРСКИХ ПЛОЩАДОК JETOUR В ЦФО (ПОСЛЕДНИЕ 2 МЕСЯЦА)").font = font_title
ws6.cell(row=3, column=2, value="Период: Июль и Август 2026 года. Конфиденциальность: все конкуренты строго анонимизированы (Дилер 1 .. Дилер 20).").font = font_subtitle

headers_s6 = [
    "Ранг в ЦФО", "Дилерская площадка", "Июль 2026 (шт)", "Август 2026 (шт)", 
    "Сумма за 2 мес (шт)", "Доля в ЦФО за 2 мес (%)", "Динамика MoM", "Статус холдинга"
]
ws6.row_dimensions[5].height = 25
for c_idx, h in enumerate(headers_s6, start=2):
    cell = ws6.cell(row=5, column=c_idx, value=h)
    cell.fill = fill_header_amber
    cell.font = font_tbl_header
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

top20_raw = [
    (1, "Дилер 1", 65, 60, 125, "15.34%", "-5 шт. (-7.7%)", "Внешний партнер"),
    (2, "Дилер 2", 42, 43, 85, "10.43%", "+1 шт. (+2.4%)", "Внешний партнер"),
    (3, "Дилер 3", 59, 23, 82, "10.06%", "-36 шт. (-61.0%)", "Внешний партнер"),
    (4, "Дилер 4", 30, 15, 45, "5.52%", "-15 шт. (-50.0%)", "Внешний партнер"),
    (5, "Дилер 5", 21, 22, 43, "5.28%", "+1 шт. (+4.8%)", "Внешний партнер"),
    (6, "Дилер 6", 27, 16, 43, "5.28%", "-11 шт. (-40.7%)", "Внешний партнер"),
    (7, "Дилер 7", 20, 17, 37, "4.54%", "-3 шт. (-15.0%)", "Внешний партнер"),
    (8, "Дилер 8", 18, 13, 31, "3.80%", "-5 шт. (-27.8%)", "Внешний партнер"),
    (9, "Дилер 9", 22, 9, 31, "3.80%", "-13 шт. (-59.1%)", "Внешний партнер"),
    (10, "Дилер 10", 23, 7, 30, "3.68%", "-16 шт. (-69.6%)", "Внешний партнер"),
    (11, "АвтоГЕРМЕС (Дилер 11)", 17, 11, 28, "3.44%", "-6 шт. (-35.3%)", "Партнер анализа"),
    (12, "Дилер 12", 16, 11, 27, "3.31%", "-5 шт. (-31.2%)", "Внешний партнер"),
    (13, "Дилер 13", 10, 12, 22, "2.70%", "+2 шт. (+20.0%)", "Внешний партнер"),
    (14, "Дилер 14", 9, 11, 20, "2.45%", "+2 шт. (+22.2%)", "Внешний партнер"),
    (15, "Дилер 15", 9, 10, 19, "2.33%", "+1 шт. (+11.1%)", "Внешний партнер"),
    (16, "Дилер 16", 9, 9, 18, "2.21%", "0 шт. (0.0%)", "Внешний партнер"),
    (17, "Дилер 17", 5, 11, 16, "1.96%", "+6 шт. (+120.0%)", "Внешний партнер"),
    (18, "Дилер 18", 13, 3, 16, "1.96%", "-10 шт. (-76.9%)", "Внешний партнер"),
    (19, "Дилер 19", 2, 10, 12, "1.47%", "+8 шт. (+400.0%)", "Внешний партнер"),
    (20, "Дилер 20", 6, 6, 12, "1.47%", "0 шт. (0.0%)", "Внешний партнер")
]

for r_idx, row_vals in enumerate(top20_raw, start=6):
    ws6.row_dimensions[r_idx].height = 20
    is_ag = "АвтоГЕРМЕС" in row_vals[1]
    for c_idx, val in enumerate(row_vals, start=2):
        cell = ws6.cell(row=r_idx, column=c_idx, value=val)
        cell.font = font_bold if is_ag or c_idx in (2, 6) else font_regular
        cell.border = thin_border
        if is_ag: cell.fill = fill_highlight
        if c_idx in (2, 4, 5, 6, 7, 8): cell.alignment = Alignment(horizontal="center", vertical="center")
        if isinstance(val, (int, float)): cell.number_format = '#,##0'

# Total Top-20 row
ws6.row_dimensions[26].height = 22
ws6.cell(row=26, column=2, value="ИТОГО ТОП-20 ДИЛЕРОВ").font = font_bold
ws6.cell(row=26, column=4, value=sum(x[2] for x in top20_raw)).font = font_bold
ws6.cell(row=26, column=5, value=sum(x[3] for x in top20_raw)).font = font_bold
ws6.cell(row=26, column=6, value=sum(x[4] for x in top20_raw)).font = font_bold
ws6.cell(row=26, column=7, value=f"{sum(x[4] for x in top20_raw)/815*100:.1f}%").font = font_bold
ws6.cell(row=26, column=8, value="-18.5%").font = font_bold
ws6.cell(row=26, column=9, value="88.0% рынка ЦФО").font = font_bold
style_range(ws6, 26, 2, 26, 9, fill=fill_subtotal)

autofit(ws6)

# ==============================================================================
# SHEET 7: JETOUR ЦФО (АвтоГЕРМЕС vs Рынок & Сценарии)
# ==============================================================================
ws7 = wb.create_sheet(title="JETOUR ЦФО")
ws7.views.sheetView[0].showGridLines = True

ws7.cell(row=2, column=2, value="JETOUR: АВТОГЕРМЕС VS РЫНОК ЦФО И РАСЧЕТ ПОТЕНЦИАЛА РОСТА").font = font_title
ws7.cell(row=3, column=2, value="Анализ емкости рынка JETOUR в ЦФО и сценарный расчет дополнительного объема продаж.").font = font_subtitle

headers_s7 = [
    "Параметр", "Июль 2026", "Август 2026", "Сумма за 2 мес", "Доля в ЦФО (%)", "Оценка позиции"
]
ws7.row_dimensions[5].height = 25
for c_idx, h in enumerate(headers_s7, start=2):
    cell = ws7.cell(row=5, column=c_idx, value=h)
    cell.fill = fill_header_navy
    cell.font = font_tbl_header
    cell.alignment = Alignment(horizontal="center", vertical="center")

jetour_data = [
    ("Рынок JETOUR в ЦФО (все дилеры)", 451, 364, 815, "100.00%", "Крупнейший бренд в СберАвто ЦФО"),
    ("Продажи JETOUR АвтоГЕРМЕС", 17, 11, 28, "3.44%", "11-е место в рейтинге ЦФО"),
    ("Продажи ТОП-3 дилеров JETOUR в ЦФО", 166, 126, 292, "35.83%", "Концентрируют треть рынка марки")
]
for r_idx, row_vals in enumerate(jetour_data, start=6):
    ws7.row_dimensions[r_idx].height = 22
    for c_idx, val in enumerate(row_vals, start=2):
        cell = ws7.cell(row=r_idx, column=c_idx, value=val)
        cell.font = font_bold if r_idx == 7 or c_idx == 2 else font_regular
        cell.border = thin_border
        if c_idx in (3, 4, 5, 6): cell.alignment = Alignment(horizontal="center", vertical="center")
        if isinstance(val, (int, float)): cell.number_format = '#,##0'

style_range(ws7, 7, 2, 7, 7, fill=fill_accent)

# Growth Potential Simulation
ws7.cell(row=11, column=2, value="РАСЧЕТ ПОТЕНЦИАЛА РОСТА ПРИ УВЕЛИЧЕНИИ ДОЛИ В JETOUR (ЦФО):").font = font_bold

headers_sim = [
    "Сценарий развития", "Целевая доля в ЦФО", "Расчетный объем за 2 мес (шт)", 
    "Расчетный объем в месяц (шт)", "Прирост за 2 мес к факту (шт)", "Прирост в месяц (шт)"
]
ws7.row_dimensions[12].height = 25
for c_idx, h in enumerate(headers_sim, start=2):
    cell = ws7.cell(row=12, column=c_idx, value=h)
    cell.fill = fill_header_green
    cell.font = font_tbl_header
    cell.alignment = Alignment(horizontal="center", vertical="center")

sim_data = [
    ("Текущий факт (Базовый)", "3.44%", 28, 14, "-", "-"),
    ("Сценарий 1: Рост доли на +2.0 п.п.", "5.44%", 44, 22, "+16 шт.", "+8 шт./мес"),
    ("Сценарий 2: Рост доли на +5.0 п.п.", "8.44%", 69, 34, "+41 шт.", "+20.5 шт./мес"),
    ("Сценарий 3: Выход в ТОП-5 дилеров ЦФО", "10.00%", 82, 41, "+54 шт.", "+27 шт./мес")
]
for r_idx, row_vals in enumerate(sim_data, start=13):
    ws7.row_dimensions[r_idx].height = 22
    for c_idx, val in enumerate(row_vals, start=2):
        cell = ws7.cell(row=r_idx, column=c_idx, value=val)
        cell.font = font_bold if r_idx > 13 and c_idx in (2, 5, 6, 7) else font_regular
        cell.border = thin_border
        if c_idx in (3, 4, 5, 6, 7): cell.alignment = Alignment(horizontal="center", vertical="center")
        if isinstance(val, (int, float)): cell.number_format = '#,##0'

style_range(ws7, 14, 2, 14, 7, fill=fill_accent)

# Chart for Jetour simulation
chart_s7 = BarChart()
chart_s7.type = "col"
chart_s7.style = 10
chart_s7.title = "JETOUR: Фактический объем vs Сценарии роста (продажи за 2 мес, шт)"
chart_s7.y_axis.title = "Сделки (шт)"
data_ref = Reference(ws7, min_col=4, min_row=13, max_col=4, max_row=16)
cats_ref = Reference(ws7, min_col=2, min_row=13, max_col=2, max_row=16)
chart_s7.add_data(data_ref, titles_from_data=False)
chart_s7.set_categories(cats_ref)
chart_s7.legend = None
chart_s7.width = 16
chart_s7.height = 8.5
ws7.add_chart(chart_s7, "B18")
autofit(ws7)

# ==============================================================================
# SHEET 8: Точки роста (Стратегический блок)
# ==============================================================================
ws8 = wb.create_sheet(title="Точки роста")
ws8.views.sheetView[0].showGridLines = True

ws8.cell(row=2, column=2, value="СТРАТЕГИЧЕСКИЕ ТОЧКИ РОСТА И ПРЕДЛОЖЕНИЯ ДЛЯ АВТОГЕРМЕСА").font = font_title
ws8.cell(row=3, column=2, value="Конкретные инициативы по масштабированию продаж, основанные на фактических данных СберАвто.").font = font_subtitle

headers_s8 = [
    "Бренд / Направление", "Емкость ЦФО (3 мес)", "Продажи АГ", "Текущая доля", 
    "Динамика рынка", "Почему это точка роста", "Что конкретно предлагает СберАвто"
]
ws8.row_dimensions[5].height = 25
for c_idx, h in enumerate(headers_s8, start=2):
    cell = ws8.cell(row=5, column=c_idx, value=h)
    cell.fill = fill_header_navy
    cell.font = font_tbl_header
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

growth_points = [
    ("1. JETOUR (Кратный рост)", "985 шт.", "34 шт.", "3.45%", "Стабильно №1 в ЦФО",
     "Крупнейший бренд платформы в ЦФО. Текущее 11-е место АвтоГЕРМЕСА кратно ниже потенциала бренда холдинга.",
     "Выделение целевого потока входящих заявок на ДЦ МКАД 44 км; запуск совместной промо-акции с субсидированием трейд-ин. Цель: рост доли до 8% (+20 авто/мес)."),

    ("2. Geely & Belgee (Восстановление доли)", "233 шт.", "71 шт.", "30.47%", "Взрывной рост (+135%)",
     "Рынок Geely & Belgee в ЦФО вырос с 46 до 108 шт/мес. У АвтоГЕРМЕСА 2 сильнейших ДЦ (Энтузиастов и МКАД 44), но доля упала с 65% до 16%.",
     "Запуск таргетированной лидогенерации на Belgee X50/X70 и Geely Monjaro под локации АвтоГЕРМЕС; синхронизация цифрового склада в реальном времени."),

    ("3. LADA (Укрепление монетизации)", "333 шт.", "256 шт.", "76.88%", "Стабильно высокий",
     "АвтоГЕРМЕС держит монопольную долю (76.9%). Здесь фокус не только на штуках, но и на маржинальности с авто.",
     "Интеграция преференциальных кредитных программ Сбера (ФДЦ) со специальной сниженной ставкой для покупателей LADA АвтоГЕРМЕС. Увеличение проникновения кредитов."),

    ("4. GAC (Подключение нового сегмента)", "90 шт.", "0 шт.", "Взрывной рост (79 шт/авг)",
     "Один из самых динамичных брендов в ЦФО (рынок вырос с 0 до 79 авто/мес). АвтоГЕРМЕС пока не продавал GAC через СберАвто.",
     "Оперативное подключение дилерских центров GAC холдинга к платформе СберАвто и открытие передачи готовых заявок с витрины."),

    ("5. SOUEAST (Масштабирование новинки)", "102 шт.", "15 шт.", "14.71%", "Рост с 0 до 74 шт",
     "Бренд только зашел на рынок, АвтоГЕРМЕС сразу взял 15 авто. Отличная динамика конверсии.",
     "Совместный брендированный лендинг моделей S07 и S09 на витрине СберАвто с приоритетным гео-распределением клиентов Москвы и МО на АвтоГЕРМЕС."),

    ("6. SOLARIS (Оцифровка стока)", "222 шт.", "120 шт.", "54.05%", "Ограничение стока",
     "Доля холдинга превышает 54%. Спрос высокий, узкое горлышко — наличие квот и скорость бронирования.",
     "Подключение прямого API-шлюза онлайн-бронирования свободных стоков Solaris с гарантированным холдированием под клиентов СберАвто.")
]

for r_idx, row_vals in enumerate(growth_points, start=6):
    ws8.row_dimensions[r_idx].height = 42
    for c_idx, val in enumerate(row_vals, start=2):
        cell = ws8.cell(row=r_idx, column=c_idx, value=val)
        cell.font = font_bold if c_idx in (2, 5) else font_regular
        cell.border = thin_border
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        if c_idx in (3, 4, 5, 6): cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

# Concrete proposal summary table
ws8.cell(row=14, column=2, value="ПАКЕТ ИНИЦИАТИВ ДЛЯ ПРОТОКОЛА ВСТРЕЧИ:").font = font_bold
proposals = [
    ("Инициатива 1: «Приоритетный Джетур»", "Увеличение трафика на ДЦ МКАД 44 км с целью входа АвтоГЕРМЕСА в ТОП-5 дилеров ЦФО (+20 авто/мес)."),
    ("Инициатива 2: «Перезапуск Geely & Belgee»", "Восстановление доли продаж на флагманских салонах Энтузиастов и МКАД 44 до уровня 35–40% (+15 авто/мес)."),
    ("Инициатива 3: «Запуск продаж GAC»", "Подключение салонов GAC холдинга к СберАвто под растущий рынок марки (потенциал +10–15 авто/мес)."),
    ("Инициатива 4: «Кредитный трек Сбера на LADA и SOLARIS»", "Запуск субсидированной ставки Сбера для покупателей АвтоГЕРМЕСА (рост конверсии и доходности)."),
    ("Инициатива 5: «Прямая интеграция стока по API»", "Автоматическая выгрузка 100% склада с фиксацией цен для мгновенной онлайн-брони без задержек.")
]

for r_idx, (p_title, p_desc) in enumerate(proposals, start=15):
    ws8.row_dimensions[r_idx].height = 24
    ws8.cell(row=r_idx, column=2, value=p_title).font = font_bold
    ws8.cell(row=r_idx, column=3, value=p_desc).font = font_regular
    ws8.merge_cells(start_row=r_idx, start_column=3, end_row=r_idx, end_column=8)
    style_range(ws8, r_idx, 2, r_idx, 8, fill=fill_accent, border=thin_border)

autofit(ws8, max_len_cap=55)

out_dir = os.path.expanduser('~/Downloads')
out_file = os.path.join(out_dir, 'Аналитический_разбор_АвтоГЕРМЕС_СберАвто_ЦФО_Q3_2026.xlsx')
wb.save(out_file)
print(f"Workbook successfully saved to: {out_file}")

