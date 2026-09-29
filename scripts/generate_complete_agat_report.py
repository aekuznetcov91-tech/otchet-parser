import os
import sys
import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_excel_report():
    output_file = 'Анализ_ГК_АГАТ_LADA_Автопрофиль_Август_Сентябрь_2026.xlsx'
    wb = openpyxl.Workbook()
    wb.remove(wb.active) # remove default sheet

    # Colors
    NAVY = '1F4E79'
    WHITE = 'FFFFFF'
    ICE_BLUE = 'D9E1F2'
    LIGHT_GRAY = 'F2F5F9'
    BORDER_CLR = 'D9D9D9'
    TOTAL_BG = 'EAEEF7'
    ALERT_BG = 'FCE4D6'
    SUCCESS_BG = 'E2EFDA'
    WARN_BG = 'FFF2CC'

    font_title = Font(name='Calibri', size=14, bold=True, color=NAVY)
    font_sub = Font(name='Calibri', size=10, italic=True, color='595959')
    font_h = Font(name='Calibri', size=11, bold=True, color=WHITE)
    font_subh = Font(name='Calibri', size=11, bold=True, color=NAVY)
    font_b = Font(name='Calibri', size=11, bold=True)
    font_r = Font(name='Calibri', size=11)
    font_small = Font(name='Calibri', size=9, italic=True, color='595959')

    fill_h = PatternFill(start_color=NAVY, end_color=NAVY, fill_type='solid')
    fill_subh = PatternFill(start_color=ICE_BLUE, end_color=ICE_BLUE, fill_type='solid')
    fill_z = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type='solid')
    fill_tot = PatternFill(start_color=TOTAL_BG, end_color=TOTAL_BG, fill_type='solid')
    fill_alert = PatternFill(start_color=ALERT_BG, end_color=ALERT_BG, fill_type='solid')
    fill_succ = PatternFill(start_color=SUCCESS_BG, end_color=SUCCESS_BG, fill_type='solid')
    fill_warn = PatternFill(start_color=WARN_BG, end_color=WARN_BG, fill_type='solid')

    thin = Side(border_style='thin', color=BORDER_CLR)
    dbl = Side(border_style='double', color=NAVY)
    top_t = Side(border_style='thin', color=NAVY)

    b_cell = Border(left=thin, right=thin, top=thin, bottom=thin)
    b_tot = Border(top=top_t, bottom=dbl, left=thin, right=thin)

    al_l = Alignment(horizontal='left', vertical='center')
    al_r = Alignment(horizontal='right', vertical='center')
    al_c = Alignment(horizontal='center', vertical='center')
    al_wrap = Alignment(horizontal='left', vertical='center', wrap_text=True)

    def style_range(ws, start_row, start_col, end_row, end_col, has_total=True, zebra=True):
        for r in range(start_row, end_row + 1):
            is_tot = (r == end_row and has_total)
            is_z = (r % 2 == 0 and not is_tot and zebra)
            for c in range(start_col, end_col + 1):
                cell = ws.cell(row=r, column=c)
                if is_tot:
                    cell.font = font_b
                    cell.fill = fill_tot
                    cell.border = b_tot
                else:
                    if is_z and cell.fill.fill_type is None:
                        cell.fill = fill_z
                    cell.border = b_cell

    def autofit(ws, min_w=12, max_w=55):
        for col in ws.columns:
            col_letter = get_column_letter(col[0].column)
            max_len = 0
            for cell in col:
                val = str(cell.value or '')
                if '\n' in val:
                    max_len = max(max_len, max(len(l) for l in val.split('\n')))
                else:
                    max_len = max(max_len, len(val))
            ws.column_dimensions[col_letter].width = max(min_w, min(max_len + 3, max_w))

    # ==========================================
    # SHEET 01: Executive Summary
    # ==========================================
    ws1 = wb.create_sheet(title='01 Executive Summary')
    ws1.views.sheetView[0].showGridLines = True
    
    ws1['B2'] = "ЭКСПРЕСС-АНАЛИЗ: ГК АГАТ × LADA × ЮЛ «АВТОПРОФИЛЬ»"
    ws1['B2'].font = font_title
    ws1['B3'] = "Период: Август – Сентябрь 2026 г. | Дата среза данных: 25.09.2026 | Сравнение: 01–25 августа vs 01–25 сентября"
    ws1['B3'].font = font_sub

    # Block 1 Header
    ws1['B5'] = "БЛОК 1. ВОРОНКА И РЕЗУЛЬТАТЫ: АГАТ / LADA / ЮЛ «АВТОПРОФИЛЬ»"
    ws1['B5'].font = font_subh
    headers_b1 = ["Показатель", "Август (полный)", "Август (01–25)", "Сентябрь (01–25 MTD)", "Δ (01–25)", "Δ % (01–25)", "Комментарий / Оценка"]
    for col_idx, h in enumerate(headers_b1, start=2):
        c = ws1.cell(row=6, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_b1 = [
        ["Переданные лиды (все каналы: CRM + MAX)", 1, 1, 20, 19, 1900.0, "В августе передан 1 лид по кнопке. В сентябре 20 обращений передано через MAX чат"],
        ["  - в т.ч. через MAX чат (уникальные клиенты)", 0, 0, 18, 18, None, "18–20 тематических цепочек в чате «СберАвто&Агат НН Лада(Автопрофиль)»"],
        ["  - в т.ч. через официальную кнопку CRM", 1, 1, 2, 1, 100.0, "Прямая системная кнопка CRM задействована слабо (всего 2 лида)"],
        ["Взяты в работу дилером", 1, 1, 20, 19, 1900.0, "Все переданные в чат запросы были просмотрены менеджерами АГАТ"],
        ["Визиты в ДЦ (подтвержденные)", 14, 12, 10, -2, -16.7, "9 визитов завершились сделкой + 1 клиент был в ДЦ 23.09 на оформлении"],
        ["Сделки (продажи LADA)", 14, 12, 9, -3, -25.0, "В сопоставимом периоде снижение с 12 до 9 шт. За полный август было 14 шт."],
        ["Предоплаты / авансы (все бренды ЮЛ)", 30, 24, 12, -12, -50.0, "Снижение входящих авансов по ЮЛ «Автопрофиль» в 2 раза"],
        ["CR: Лид → Визит", 1400.0, 1200.0, 50.0, -1150.0, None, "В августе лиды не передавались системно, сделки шли «без кнопки»"],
        ["CR: Визит → Сделка", 100.0, 100.0, 90.0, -10.0, -10.0, "Высокая конверсия из визита: 9 из 10 дошедших до салона купили авто"],
        ["CR: Лид → Сделка (по каналу MAX)", None, None, 45.0, None, None, "9 сделок на 20 переданных обращений в чате (45.0%)"],
        ["Выручка от продаж, руб", 18059000, 15735000, 10657300, -5077700, -32.3, "Снижение объема выручки из-за меньшего числа сделок и ухода дорогих моделей"],
        ["Комиссия СберАвто, руб", 314900, 274900, 231835, -43065, -15.7, "Средняя комиссия на 1 авто выросла с 22.9 тыс. до 25.8 тыс. руб"]
    ]

    for row_idx, r_data in enumerate(data_b1, start=7):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws1.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx in (3, 4, 5, 6):
                if isinstance(val, (int, float)):
                    if "CR" in r_data[0]:
                        cell.number_format = '0.0"%"'
                    elif "руб" in r_data[0]:
                        cell.number_format = '#,##0 "₽"'
                    else:
                        cell.number_format = '#,##0'
                cell.alignment = al_r
            elif col_idx == 7:
                if isinstance(val, (int, float)):
                    cell.number_format = '+0.0"%"' if val > 0 else '0.0"%"'
                    cell.alignment = al_r
            else:
                cell.alignment = al_l
        if "Сделки" in r_data[0]:
            ws1.cell(row=row_idx, column=2).font = font_b
            ws1.cell(row=row_idx, column=5).font = font_b
            ws1.cell(row=row_idx, column=5).fill = fill_alert

    style_range(ws1, 7, 2, 18, 8, has_total=False)

    # Block 2 Header
    ws1['B20'] = "БЛОК 2. РЫНОЧНЫЙ ТРАФИК LADA: НИЖНИЙ НОВГОРОД + 200 КМ"
    ws1['B20'].font = font_subh
    headers_b2 = ["Показатель потока LADA (+200 км)", "Август (факт)", "Сентябрь (01–25)", "Δ (динамика)", "Δ %", "Доля сегмента", "Интерпретация фактора"]
    for col_idx, h in enumerate(headers_b2, start=2):
        c = ws1.cell(row=21, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_b2 = [
        ["1. Общий входящий спрос клиентов в регионе НН +200 км (Новый лид)", 258, 230, -28, -10.9, "100.0%", "Стабильно высокий спрос покупателей из Нижегородского региона"],
        ["2. Квалифицированные клиенты региона (Закрепление менеджера)", 303, 269, -34, -11.2, "100.0%", "Целевые клиенты, готовые к покупке и общению с дилером"],
        ["3. ПЕРЕДАНО ЛОКАЛЬНЫМ ДИЛЕРАМ В РАДИУСЕ 200 КМ (ФАКТ)", 4, 32, 28, 700.0, "100.0%", "Физические официальные дилерские центры LADA в регионе (АГАТ + ЮНИКОР)"],
        ["  • ГК АГАТ (ЮЛ «Автопрофиль», CRM + MAX)", 1, 22, 21, 2100.0, "68.8%", "Нижний Новгород (Московское ш., Родионова) — абсолютный лидер региона!"],
        ["  • ЮНИКОР Дзержинск (пр-кт Чкалова / НН)", 3, 10, 7, 233.3, "31.2%", "Дзержинск (33 км от НН) — 10 уникальных передач (официальный BI СберАвто)"],
        ["4. УТЕЧКА КЛИЕНТОВ ЗА ПРЕДЕЛЫ 200 КМ (Удаленные кредитные хабы / ФДЦ)", 128, 17, -111, -86.7, "34.7%", "Нижегородские онлайн-заявки, направленные операторами в удаленные центры"],
        ["  • ФДЦ Техно-Темп (Краснодар, ~1 400 км от НН)", 93, 12, -81, -87.1, "24.5%", "Удаленный кредитный шлюз СберАвто для онлайн-заявок на автокредит"],
        ["  • ФДЦ Р-Моторс (удаленный кредитный пилот)", 14, 4, -10, -71.4, "8.2%", "Удаленный пилот обработки кредитных сделок СберАвто"],
        ["  • КАН АВТО (Казань, ~400 км от НН)", 1, 1, 0, 0.0, "2.0%", "Заявки клиентов восточных районов области"],
        ["  • Прочие удаленные ДЦ (Боравто Воронеж и др.)", 20, 0, -20, -100.0, "0.0%", "В августе уходило в Боравто (8), Р-Моторс (7) и др.; в сентябре утечка перекрыта"],
        ["5. НЕ ПЕРЕДАНО ДИЛЕРАМ ОТ ВХОДЯЩИХ ЛИДОВ (баланс: 230 - 49)", 126, 181, 55, 43.7, "78.7%", "Остаток входящего спроса без передачи в ДЦ (баланс: 49 передано + 181 = 230)"],
        ["  • в т.ч. квалифицированные клиенты без передачи (269 - 49)", 171, 220, 49, 28.7, "81.8%", "Целевой резерв из прошедших скоринг клиентов (баланс: 49 + 220 = 269)"],
        ["ДОЛЯ АГАТ СРЕДИ ЛОКАЛЬНЫХ ДИЛЕРОВ (АГАТ vs ЮНИКОР)", 25.0, 68.8, 43.8, 175.0, "68.8%", "Среди дилеров области АГАТ забирает 68.8% (22 из 32), опережая ЮНИКОР в 2.2 раза!"],
        ["ДОЛЯ АГАТ ОТ ВСЕХ ПЕРЕДАННЫХ КЛИЕНТОВ РЕГИОНА (с учетом утечки)", 0.8, 44.9, 44.1, 5512.5, "44.9%", "Доля АГАТ во всех передачах нижегородцев выросла с 0.8% до 44.9%!"],
        ["ДОЛЯ АГАТ ОТ КВАЛИФИЦИРОВАННОГО СПРОСА РЕГИОНА (269 лидов)", 0.3, 8.2, 7.9, 2633.3, "8.2%", "Потенциал роста доли АГАТ — минимум в 3–4 раза (до 30–40%)"]
    ]

    for row_idx, r_data in enumerate(data_b2, start=22):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws1.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx in (3, 4, 5):
                if isinstance(val, (int, float)):
                    cell.number_format = '#,##0' if "ДОЛЯ" not in r_data[0] else '0.0"%"'
                cell.alignment = al_r
            elif col_idx in (6, 7):
                if isinstance(val, (int, float)):
                    cell.number_format = '+0.0"%"' if val > 0 else '0.0"%"'
                cell.alignment = al_r
            else:
                cell.alignment = al_l
        if "ДОЛЯ АГАТ" in r_data[0]:
            ws1.cell(row=row_idx, column=2).font = font_b
            ws1.cell(row=row_idx, column=4).fill = fill_warn
        if "ПЕРЕДАНО ЛОКАЛЬНЫМ ДИЛЕРАМ" in r_data[0] or "УТЕЧКА КЛИЕНТОВ" in r_data[0] or "НЕ ПЕРЕДАНО" in r_data[0]:
            ws1.cell(row=row_idx, column=2).font = font_b

    style_range(ws1, 22, 2, 36, 8, has_total=False)

    # Block 3 Header
    ws1['B38'] = "БЛОК 3. АНАЛИЗ ЧАТА MAX («СБЕРАВТО&АГАТ НН ЛАДА(АВТОПРОФИЛЬ)»)"
    ws1['B38'].font = font_subh
    headers_b3 = ["Показатель обработки переписки MAX", "Значение", "% от переданных", "Бенчмарк сети", "Статус / Оценка"]
    for col_idx, h in enumerate(headers_b3, start=2):
        c = ws1.cell(row=39, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_b3 = [
        ["Выделено тематических цепочек по клиентам", 20, "100.0%", "—", "Базовый объем обращений за 1–25 сентября"],
        ["Уникальных клиентских кейсов (нижняя граница)", 18, "90.0%", "—", "2 цепочки могут быть повторными из-за отсутствия ID"],
        ["Подтвержденных выдач автомобилей в чате", 3, "15.0%", "12.9%", "Зафиксированы в чате (Vesta Comfort, Granta x2)"],
        ["Случаи с внесенным авансом (ожидание выдачи)", 2, "10.0%", "8.0%", "Внесен аванс (Granta Comfort черный, Granta)"],
        ["Явные отказы клиентов (зафиксированные)", 1, "5.0%", "15.0%", "Трейд-ин BMW на Largus: разногласие по доплате"],
        ["В работе / без зафиксированного итога в чате", 14, "70.0%", "< 35.0%", "КРИТИЧЕСКАЯ ЗОНА: по 14 лидам дилер не дал финал!"],
        ["Ценовые расхождения (эпизоды в чате)", 4, "20.0%", "25.0%", "Ни одно не привело к окончательному отказу"],
        ["Потери из-за ожидания в салоне (>1.5 часа)", 1, "5.0%", "0.0%", "23.09 клиент ждал кредитного специалиста 1.5ч в ДЦ"]
    ]

    for row_idx, r_data in enumerate(data_b3, start=40):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws1.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx == 3:
                cell.alignment = al_r
                cell.number_format = '#,##0'
            elif col_idx in (4, 5):
                cell.alignment = al_r
            else:
                cell.alignment = al_l
        if "В работе" in r_data[0]:
            ws1.cell(row=row_idx, column=2).font = font_b
            ws1.cell(row=row_idx, column=3).fill = fill_alert

    style_range(ws1, 40, 2, 47, 6, has_total=False)

    # Block 4 Header
    ws1['B49'] = "БЛОК 4. СВЕРКА MAX VS DASHBOARD СБЕРАВТО"
    ws1['B49'].font = font_subh
    headers_b4 = ["Категория сверки", "Кол-во клиентов", "Характер расхождения", "Управленческий риск / Решение"]
    for col_idx, h in enumerate(headers_b4, start=2):
        c = ws1.cell(row=50, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_b4 = [
        ["Сделка есть в Dashboard, но нет выдачи в MAX", 6, "В Dashboard закрыто 9 сделок, а в чате MAX подтверждено только 3 выдачи", "Дилер закрывает сделки, но не отчитывается в чате. Риск потери контроля воронки"],
        ["Сделка подтверждена в MAX и есть в Dashboard", 3, "Полное совпадение факта выдачи автомобиля (100% верификация)", "Успешные кейсы качественного взаимодействия СберАвто и АГАТ"],
        ["Внесен аванс в MAX, ожидается выдача в Dashboard", 2, "Предоплаты отражены в чате, сделка в процессе подготовки", "Потенциал закрытия до конца месяца (дополнительно +2 продажи)"],
        ["Зависли в статусе «В работе» в чате MAX", 14, "Нет финального статуса от дилера по запросам наличия и лидам", "Требуется срочный реестровый запрос в АГАТ по статусам каждого клиента"],
        ["Клиенты ушли конкуренту ЮНИКОР Дзержинск", 10, "10 уникальных лидов передано ЮНИКОР (официальный BI СберАвто)", "АГАТ опережает ЮНИКОР (22 vs 10), но ЮНИКОР остается системным получателем по умолчанию"]
    ]

    for row_idx, r_data in enumerate(data_b4, start=51):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws1.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx == 3:
                cell.alignment = al_r
                cell.number_format = '#,##0'
            else:
                cell.alignment = al_l
        if "Сделка есть в Dashboard" in r_data[0]:
            ws1.cell(row=row_idx, column=2).fill = fill_warn

    style_range(ws1, 51, 2, 55, 5, has_total=False)

    autofit(ws1)

    # ==========================================
    # SHEET 02: АГАТ Август-Сентябрь
    # ==========================================
    ws2 = wb.create_sheet(title='02 АГАТ Август-Сентябрь')
    ws2.views.sheetView[0].showGridLines = True

    ws2['B2'] = "ГК АГАТ: АНАЛИЗ ПРОДАЖ LADA ПО ЮРИДИЧЕСКИМ ЛИЦАМ И ДИЛЕРАМ"
    ws2['B2'].font = font_title
    ws2['B3'] = "Сравнение результатов холдинга за Август (полный), Август (01–25) и Сентябрь (01–25 MTD 2026)"
    ws2['B3'].font = font_sub

    headers_ws2 = ["Юридическое лицо / Дилерский центр", "Город / Локация", "Август (полный)", "Август (01–25)", "Сентябрь (01–25)", "Δ шт (01–25)", "Δ %", "Выручка сен, руб", "Комиссия сен, руб", "Модельный ряд"]
    for col_idx, h in enumerate(headers_ws2, start=2):
        c = ws2.cell(row=5, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_ws2 = [
        ["ООО «Автопрофиль» (ONLINE)", "Нижний Новгород", 14, 12, 9, -3, -25.0, 10657300, 231835, "Granta (8), Vesta (1)"],
        ["ООО «Приоритет Моторс»", "Нижний Новгород", 2, 2, 1, -1, -50.0, 997000, 10000, "Granta (1)"],
        ["ООО «Альтаир»", "Саратов / Сыктывкар", 3, 1, 5, 4, 400.0, 6447000, 128940, "Granta (3), Niva (1), Vesta (1)"],
        ["ООО «Аксион»", "Астрахань", 0, 0, 4, 4, None, 4561600, 120000, "Granta (4)"],
        ["ООО «Лада Центр на Ленина»", "Волгоград", 1, 0, 0, 0, 0.0, 0, 0, "—"],
        ["ООО «ТД Агат-Авто»", "Волгоград", 1, 0, 0, 0, 0.0, 0, 0, "—"],
        ["ИТОГО ГК АГАТ (LADA)", "Все регионы", 21, 15, 19, 4, 26.7, 22662900, 490775, "Granta (16), Vesta (2), Niva (1)"]
    ]

    for row_idx, r_data in enumerate(data_ws2, start=6):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws2.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx in (4, 5, 6, 7):
                if isinstance(val, (int, float)):
                    cell.number_format = '#,##0'
                cell.alignment = al_r
            elif col_idx == 8:
                if isinstance(val, (int, float)):
                    cell.number_format = '+0.0"%"' if val > 0 else '0.0"%"'
                cell.alignment = al_r
            elif col_idx in (9, 10):
                if isinstance(val, (int, float)):
                    cell.number_format = '#,##0 "₽"'
                cell.alignment = al_r
            else:
                cell.alignment = al_l

    style_range(ws2, 6, 2, 12, 11, has_total=True)

    # Sub-table: Nizhny Novgorod cluster specifically
    ws2['B15'] = "КЛАСТЕР НИЖНИЙ НОВГОРОД (ООО «АВТОПРОФИЛЬ» + ООО «ПРИОРИТЕТ МОТОРС»)"
    ws2['B15'].font = font_subh
    headers_nn = ["Сущность", "ИНН", "Код дилера", "Август (полный)", "Август (01–25)", "Сентябрь (01–25)", "Δ шт", "Δ %", "Доля в продажах LADA АГАТ"]
    for col_idx, h in enumerate(headers_nn, start=2):
        c = ws2.cell(row=16, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_nn = [
        ["ООО «Автопрофиль»", "5261037364", "105381", 14, 12, 9, -3, -25.0, "47.4%"],
        ["ООО «Приоритет Моторс»", "5257188868", "105387", 2, 2, 1, -1, -50.0, "5.3%"],
        ["ИТОГО НИЖНИЙ НОВГОРОД", "—", "—", 16, 14, 10, -4, -28.6, "52.6%"]
    ]

    for row_idx, r_data in enumerate(data_nn, start=17):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws2.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx in (5, 6, 7, 8):
                if isinstance(val, (int, float)): cell.number_format = '#,##0'
                cell.alignment = al_r
            elif col_idx == 9:
                if isinstance(val, (int, float)): cell.number_format = '+0.0"%"' if val > 0 else '0.0"%"'
                cell.alignment = al_r
            else:
                cell.alignment = al_l

    style_range(ws2, 17, 2, 19, 10, has_total=True)

    autofit(ws2)

    # ==========================================
    # SHEET 03: ЮЛ Автопрофиль
    # ==========================================
    ws3 = wb.create_sheet(title='03 ЮЛ Автопрофиль')
    ws3.views.sheetView[0].showGridLines = True

    ws3['B2'] = "ПАСПОРТ И РЕЗУЛЬТАТЫ: ЮЛ «АВТОПРОФИЛЬ» (ГК АГАТ)"
    ws3['B2'].font = font_title
    ws3['B3'] = "ИНН: 5261037364 | Bitrix ID: 112274 | OEM ID: 105381 | КАМ: Андрей Кузнецов"
    ws3['B3'].font = font_sub

    # Entity details table
    ws3['B5'] = "АТРИБУТЫ СУЩНОСТИ В СИСТЕМАХ СБЕРАВТО"
    ws3['B5'].font = font_subh
    attrs = [
        ["Холдинг (ГК)", "ГК АГАТ (ID 1049, Canonical: ГК АГАТ)"],
        ["Юридическое лицо (ЮЛ)", "ООО «Автопрофиль» (ИНН 5261037364, КПП 526101001)"],
        ["Статус в Dashboard", "ЮРИДИЧЕСКОЕ ЛИЦО (НЕ является физической локацией)"],
        ["Алиасы в Bitrix CRM", "ONLINE ООО \"АВТОПРОФИЛЬ\" АГАТ, ООО \"АВТОПРОФИЛЬ\" ONLINE"],
        ["Физические ДЦ в контуре", "1) ДЦ АГАТ Московское шоссе (г. Нижний Новгород, Московское ш., 294Д)\n2) ДЦ АГАТ Казанское шоссе / Родионова (г. Нижний Новгород, ул. Родионова, 203)"],
        ["Бренды по данному ЮЛ", "LADA (основной объем), JETOUR, SOUEAST"],
        ["Рабочий канал коммуникации", "Чат MAX: «СберАвто&Агат НН Лада(Автопрофиль)» (link: max.ru/join/xA9OfJ1AHesJoJIx7n0LPZI7XZSWUEOdnVOrcW9JnyU)"],
        ["Курирующий КАМ СберАвто", "Андрей Кузнецов"]
    ]
    for r_i, (k, v) in enumerate(attrs, start=6):
        c1 = ws3.cell(row=r_i, column=2, value=k); c1.font = font_b; c1.fill = fill_subh; c1.border = b_cell
        c2 = ws3.cell(row=r_i, column=3, value=v); c2.font = font_r; c2.border = b_cell; c2.alignment = al_wrap

    # Brand Performance table
    ws3['B15'] = "ДИНАМИКА ПРОДАЖ ПО ВСЕМ БРЕНДАМ ЮЛ «АВТОПРОФИЛЬ»"
    ws3['B15'].font = font_subh
    headers_brand = ["Бренд автомобиля", "Август (полный)", "Август (01–25)", "Сентябрь (01–25 MTD)", "Δ шт (01–25)", "Δ %", "Выручка сен, руб", "Комиссия сен, руб", "Доля бренда в ЮЛ"]
    for col_idx, h in enumerate(headers_brand, start=2):
        c = ws3.cell(row=16, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_brand = [
        ["LADA", 14, 12, 9, -3, -25.0, 10657300, 231835, "64.3%"],
        ["JETOUR", 23, 19, 4, -15, -78.9, 13880000, 120000, "28.6%"],
        ["SOUEAST", 4, 3, 1, -2, -66.7, 2670000, 30000, "7.1%"],
        ["ИТОГО ПО ЮЛ «АВТОПРОФИЛЬ»", 41, 34, 14, -20, -58.8, 27207300, 381835, "100.0%"]
    ]

    for row_idx, r_data in enumerate(data_brand, start=17):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws3.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx in (3, 4, 5, 6):
                if isinstance(val, (int, float)): cell.number_format = '#,##0'
                cell.alignment = al_r
            elif col_idx == 7:
                if isinstance(val, (int, float)): cell.number_format = '+0.0"%"' if val > 0 else '0.0"%"'
                cell.alignment = al_r
            elif col_idx in (8, 9):
                if isinstance(val, (int, float)): cell.number_format = '#,##0 "₽"'
                cell.alignment = al_r
            else:
                cell.alignment = al_l

    style_range(ws3, 17, 2, 20, 10, has_total=True)

    # Model Breakdown for LADA
    ws3['B23'] = "МОДЕЛЬНАЯ СТРУКТУРА СДЕЛОК LADA (ЮЛ «АВТОПРОФИЛЬ»)"
    ws3['B23'].font = font_subh
    headers_mod = ["Модель LADA", "Август (полный)", "Август (01–25)", "Сентябрь (01–25)", "Δ шт", "Средняя цена сен, руб", "Минимальная цена, руб", "Максимальная цена, руб"]
    for col_idx, h in enumerate(headers_mod, start=2):
        c = ws3.cell(row=24, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_mod = [
        ["LADA Granta (Sedan / Liftback / Cross)", 8, 6, 8, 2, 1133125, 870000, 1290000],
        ["LADA Vesta", 2, 2, 1, -1, 1584300, 1584300, 1584300],
        ["LADA Niva (Legend / Travel)", 1, 1, 0, -1, 0, 0, 0],
        ["LADA Iskra (предсерийные/ранние)", 2, 2, 0, -2, 0, 0, 0],
        ["LADA Largus", 1, 1, 0, -1, 0, 0, 0],
        ["ИТОГО СДЕЛОК LADA", 14, 12, 9, -3, 1184144, 870000, 1584300]
    ]

    for row_idx, r_data in enumerate(data_mod, start=25):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws3.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx in (3, 4, 5, 6):
                if isinstance(val, (int, float)): cell.number_format = '#,##0'
                cell.alignment = al_r
            elif col_idx in (7, 8, 9):
                if isinstance(val, (int, float)): cell.number_format = '#,##0 "₽"'
                cell.alignment = al_r
            else:
                cell.alignment = al_l

    style_range(ws3, 25, 2, 30, 9, has_total=True)

    autofit(ws3)

    # ==========================================
    # SHEET 04: Воронка АГАТ
    # ==========================================
    ws4 = wb.create_sheet(title='04 Воронка АГАТ')
    ws4.views.sheetView[0].showGridLines = True

    ws4['B2'] = "СКВОЗНАЯ ВОРОНКА: АГАТ × LADA × ЮЛ «АВТОПРОФИЛЬ»"
    ws4['B2'].font = font_title
    ws4['B3'] = "Поэтапная конверсия и потери клиентов на каждом этапе пути (Customer Journey)"
    ws4['B3'].font = font_sub

    headers_funnel = ["Этап воронки", "Август (факт)", "Сентябрь (01–25 MTD)", "Конверсия этапа сен", "Потери сен (drop-off шт)", "Drop-off %", "Ключевой фактор потерь"]
    for col_idx, h in enumerate(headers_funnel, start=2):
        c = ws4.cell(row=5, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_funnel = [
        ["1. Доступный квалифицированный трафик региона", 303, 269, "100.0%", 0, "0.0%", "Целевой спрос СберАвто на LADA в НН +200 км"],
        ["2. Передано в АГАТ (CRM + MAX)", 1, 22, "8.2%", 247, "91.8%", "УТЕЧКА 91.8%: 220 клиентов не распределены дилерам, 17 ушли в кредитные хабы ФДЦ, 10 в ЮНИКОР"],
        ["3. Взято в работу менеджерами АГАТ", 1, 20, "90.9%", 2, "9.1%", "2 CRM-лида без движения, 20 чатов MAX взяты в диалог"],
        ["4. Получена содержательная обратная связь", 1, 6, "30.0%", 14, "70.0%", "УТЕЧКА 70%: по 14 клиентам нет финального статуса"],
        ["5. Назначен / состоялся визит в ДЦ", 14, 10, "50.0%", 10, "50.0%", "10 клиентов дошли до салона (9 сделок + 1 ожидание)"],
        ["6. Закрыта сделка (выдан автомобиль)", 14, 9, "90.0%", 1, "10.0%", "9 сделок закрыто (1 клиент ушел из-за ожидания кредита)"]
    ]

    for row_idx, r_data in enumerate(data_funnel, start=6):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws4.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx in (3, 4, 6):
                if isinstance(val, (int, float)): cell.number_format = '#,##0'
                cell.alignment = al_r
            elif col_idx in (5, 7):
                cell.alignment = al_r
            else:
                cell.alignment = al_l
        if "УТЕЧКА" in str(r_data[6]):
            ws4.cell(row=row_idx, column=2).fill = fill_alert

    style_range(ws4, 6, 2, 11, 8, has_total=False)

    autofit(ws4)

    # ==========================================
    # SHEET 05: LADA НН +200 км
    # ==========================================
    ws5 = wb.create_sheet(title='05 LADA НН +200 км')
    ws5.views.sheetView[0].showGridLines = True

    ws5['B2'] = "АНАЛИЗ ВСЕГО ТРАФИКА LADA: НИЖНИЙ НОВГОРОД + 200 КМ"
    ws5['B2'].font = font_title
    ws5['B3'] = "Оценка емкости рынка СберАвто, каналов распределения и доли ГК АГАТ за август и сентябрь 2026 г."
    ws5['B3'].font = font_sub

    headers_ws5 = ["Параметр распределения потока LADA", "Август 2026", "Сентябрь (01–25)", "Динамика шт", "Динамика %", "Доля в потоке сен", "Аналитический комментарий"]
    for col_idx, h in enumerate(headers_ws5, start=2):
        c = ws5.cell(row=5, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_ws5 = [
        ["1. Входящие лиды LADA в CRM (Новый лид)", 258, 230, -28, -10.9, "—", "Стабильный органический поток заявок покупателей из региона НН +200 км"],
        ["2. Квалифицированные лиды (Закрепление менеджера)", 303, 269, -34, -11.2, "100.0%", "База клиентов региона, прошедших скоринг и готовых к покупке"],
        ["3. ПЕРЕДАНО ЛОКАЛЬНЫМ ДИЛЕРАМ В РАДИУСЕ 200 КМ (ФАКТ)", 4, 32, 28, 700.0, "100.0%", "Физические официальные дилерские центры LADA в регионе (АГАТ + ЮНИКОР)"],
        ["  • ГК АГАТ (ЮЛ «Автопрофиль», CRM + MAX)", 1, 22, 21, 2100.0, "68.8%", "Нижний Новгород (Московское ш., Родионова) — абсолютный лидер региона!"],
        ["  • ЮНИКОР Дзержинск (локальный конкурент)", 3, 10, 7, 233.3, "31.2%", "Дзержинск (33 км от НН) — 10 уникальных передач (официальный BI СберАвто)"],
        ["4. УТЕЧКА КЛИЕНТОВ ЗА ПРЕДЕЛЫ 200 КМ (Удаленные кредитные хабы / ФДЦ)", 128, 17, -111, -86.7, "34.7%", "Нижегородские онлайн-заявки, направленные операторами в удаленные центры"],
        ["  • ФДЦ Техно-Темп (Краснодар, ~1 400 км от НН)", 93, 12, -81, -87.1, "24.5%", "Удаленный кредитный шлюз СберАвто для онлайн-заявок на автокредит"],
        ["  • ФДЦ Р-Моторс (удаленный кредитный пилот)", 14, 4, -10, -71.4, "8.2%", "Удаленный пилот обработки кредитных сделок СберАвто"],
        ["  • КАН АВТО (Казань, ~400 км от НН)", 1, 1, 0, 0.0, "2.0%", "Заявки клиентов восточных районов области"],
        ["  • Прочим удаленным ДЦ (Боравто Воронеж, Прагматика и др.)", 20, 0, -20, -100.0, "0.0%", "В августе уходило в Боравто (8), Р-Моторс (7) и др.; в сентябре утечка перекрыта"],
        ["5. НЕ ПЕРЕДАНО ДИЛЕРАМ ОТ ВХОДЯЩИХ ЛИДОВ (баланс: 230 - 49)", 126, 181, 55, 43.7, "78.7%", "Остаток входящего спроса без передачи в ДЦ (баланс: 49 передано + 181 = 230)"],
        ["  • в т.ч. квалифицированные клиенты без передачи (269 - 49)", 171, 220, 49, 28.7, "81.8%", "Резерв для масштабирования прямых передач в АГАТ (баланс: 49 + 220 = 269)"],
        ["ДОЛЯ АГАТ СРЕДИ ЛОКАЛЬНЫХ ДИЛЕРОВ (АГАТ vs ЮНИКОР)", 25.0, 68.8, 43.8, 175.0, "68.8%", "Среди дилеров области АГАТ забирает 68.8%, опережая ЮНИКОР в 2.2 раза!"],
        ["ДОЛЯ АГАТ ОТ ВСЕХ ПЕРЕДАННЫХ КЛИЕНТОВ РЕГИОНА (с учетом утечки)", 0.8, 44.9, 44.1, 5512.5, "44.9%", "Доля АГАТ во всех передачах нижегородцев выросла с 0.8% до 44.9%!"],
        ["ДОЛЯ АГАТ ОТ КВАЛИФИЦИРОВАННОГО СПРОСА РЕГИОНА", 0.3, 8.2, 7.9, 2633.3, "8.2%", "Потенциал роста доли АГАТ — минимум в 3–4 раза (до 30–40%)"],
        ["Объем квалифицированного спроса мимо АГАТ, шт", 302, 247, -55, -18.2, "91.8%", "Прямой объем для обсуждения на встрече по открытию слотов"]
    ]

    for row_idx, r_data in enumerate(data_ws5, start=6):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws5.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx in (3, 4, 5):
                if isinstance(val, (int, float)):
                    cell.number_format = '#,##0' if "ДОЛЯ" not in r_data[0] else '0.0"%"'
                cell.alignment = al_r
            elif col_idx == 6:
                if isinstance(val, (int, float)):
                    cell.number_format = '+0.0"%"' if val > 0 else '0.0"%"'
                cell.alignment = al_r
            elif col_idx == 7:
                cell.alignment = al_r
            else:
                cell.alignment = al_l
        if "ДОЛЯ АГАТ" in r_data[0]:
            ws5.cell(row=row_idx, column=2).font = font_b
            ws5.cell(row=row_idx, column=4).fill = fill_succ
        if "ПЕРЕДАНО ЛОКАЛЬНЫМ ДИЛЕРАМ" in r_data[0] or "УТЕЧКА КЛИЕНТОВ" in r_data[0] or "НЕ ПЕРЕДАНО" in r_data[0]:
            ws5.cell(row=row_idx, column=2).font = font_b

    style_range(ws5, 6, 2, 21, 8, has_total=False)

    # Footnote on ws5
    ws5['B23'] = "* ПОЯСНЕНИЕ ПО ДИЛЕРАМ ДАЛЬШЕ 200 КМ: ДЦ «Техно-Темп» (Краснодар, 1400 км), «Р-Моторс», «КАН АВТО» (Казань, 400 км), «Боравто» (Воронеж, 700 км) и «Прагматика» физически НЕ находятся в радиусе 200 км."
    ws5['B23'].font = font_b
    ws5['B24'] = "Они показаны в отчете исключительно как «Межрегиональная утечка»: операторы CRM СберАвто направляли туда заявки нижегородских покупателей (в основном онлайн-автокредиты), вместо отработки на месте."
    ws5['B24'].font = font_r
    ws5['B25'] = "Физически в радиусе 200 км от Нижнего Новгорода работают ТОЛЬКО ДВА официальных дилера LADA: ГК АГАТ (г. Нижний Новгород) и ЮНИКОР (г. Дзержинск, 33 км)."
    ws5['B25'].font = font_b

    autofit(ws5)

    # ==========================================
    # SHEET 06: География лидов
    # ==========================================
    ws6 = wb.create_sheet(title='06 География лидов')
    ws6.views.sheetView[0].showGridLines = True

    ws6['B2'] = "ГЕОГРАФИЯ ТРАФИКА LADA: РАДИУС 200 КМ ОТ НИЖНЕГО НОВГОРОДА"
    ws6['B2'].font = font_title
    ws6['B3'] = "Центр: г. Нижний Новгород (56.3269° N, 44.0059° E) | Расчет по геодезическому расстоянию"
    ws6['B3'].font = font_sub

    headers_geo = ["Географическая зона", "Расстояние от НН", "Ключевые города и населенные пункты", "Входящие лиды (получено от клиентов), шт", "Доля в потоке", "Куда направлен трафик (дилеры отработки)", "Потенциал для АГАТ"]
    for col_idx, h in enumerate(headers_geo, start=2):
        c = ws6.cell(row=5, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_geo = [
        ["Ядро агломерации", "0 км", "Нижний Новгород (все районы)", 133, "57.8%", "АГАТ (Московское ш., Родионова), ЮНИКОР", "100% домашний регион АГАТ. Ключевая точка роста"],
        ["Ближний пояс (до 50 км)", "1–50 км", "Бор (7 км), Кстово (23 км), Дзержинск (33 км), Балахна (33 км), Богородск (40 км)", 56, "24.3%", "ЮНИКОР (Дзержинск) получил 10 лидов; АГАТ на Московском ш. идеально доступен для Бора/Балахны", "Высокий: АГАТ на Московском ш. идеально доступен для Бора/Балахны"],
        ["Средний пояс (51–100 км)", "51–100 км", "Городец (50 км), Заволжье (52 км), Павлово (72 км), Чкаловск (75 км), Семёнов (66 км), Лысково (82 км)", 21, "9.1%", "Частично ЮНИКОР, частично удаленные ДЦ", "Умеренный: клиенты регулярно приезжают в НН на покупку авто"],
        ["Дальний пояс (101–150 км)", "101–150 км", "Арзамас (105 км), Сергач (130 км), Муром (148 км), Вязники (117 км), Шатки (128 км)", 13, "5.7%", "Смешанная отработка, часть уходит во Владимир", "Целевой: АГАТ имеет сильный бренд на юге области"],
        ["Периферия (151–200 км)", "151–200 км", "Саров (161 км), Выкса (161 км), Кулебаки (139 км), Ковров (175 км), Урень (176 км), Шумерля (178 км)", 7, "3.0%", "Удаленные ДЦ, локальные субдилеры", "Точечный: клиенты с высоким чеком (Vesta, Largus)"],
        ["ИТОГО В РАДИУСЕ 200 КМ", "0–200 км", "Нижегородская область + приграничные районы Владимирской обл. и Чувашии", 230, "100.0%", "АГАТ (44.9%), ФДЦ кредитные хабы (32.7%), ЮНИКОР (20.4%), КАН АВТО (2.0%)", "Емкость достаточна для удвоения продаж АГАТ LADA"]
    ]

    for row_idx, r_data in enumerate(data_geo, start=6):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws6.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx == 5:
                if isinstance(val, (int, float)): cell.number_format = '#,##0'
                cell.alignment = al_r
            elif col_idx == 6:
                cell.alignment = al_r
            else:
                cell.alignment = al_l

    style_range(ws6, 6, 2, 11, 8, has_total=True)

    # Footnote on ws6
    ws6['B13'] = "* ПРИМЕЧАНИЕ ПО МЕТОДОЛОГИИ: 133 шт по Нижнему Новгороду (и 230 шт суммарно по радиусу 200 км) — это ВХОДЯЩИЙ ПОТОК (лиды, ПОЛУЧЕННЫЕ от покупателей на витрине СберАвто)."
    ws6['B13'].font = font_b
    ws6['B14'] = "Из них дилерам было ФАКТИЧЕСКИ ОТПРАВЛЕНО 49 лидов: 32 передано локальным дилерам (22 в АГАТ + 10 в ЮНИКОР), а 17 отправлено в удаленные кредитные хабы (Техно-Темп Краснодар и др.). Остальная 181 заявка осталась не переданной дилерам (в работе CRM / отсев скоринга)."
    ws6['B14'].font = font_r

    autofit(ws6)

    # ==========================================
    # SHEET 07: MAX Сентябрь
    # ==========================================
    ws7 = wb.create_sheet(title='07 MAX Сентябрь')
    ws7.views.sheetView[0].showGridLines = True

    ws7['B2'] = "РЕЕСТР ОБРАЩЕНИЙ ИЗ ЧАТА MAX: «СБЕРАВТО&АГАТ НН ЛАДА(АВТОПРОФИЛЬ)»"
    ws7['B2'].font = font_title
    ws7['B3'] = "Период: 01.09.2026 – 25.09.2026 | Обезличенные данные без ПДн (ФИО и телефоны удалены)"
    ws7['B3'].font = font_sub

    headers_max = ["Internal ID", "Client ID (CRM)", "Дата обращения", "Запрашиваемый авто", "Бюджет / Цена, руб", "Предложение дилера", "Нормализованный статус", "Запросов ОС", "Время 1-й ОС", "Исходная формулировка дилера / Комментарий"]
    for col_idx, h in enumerate(headers_max, start=2):
        c = ws7.cell(row=5, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_max = [
        ["Lead 001", "5176812", "01.09.2026", "LADA Granta Sedan", 1150000, "Автомобиль в наличии на складе", "КУПИЛ", 1, "45 мин", "«Машина готова к выдаче, документы подписаны»"],
        ["Lead 002", "5185566", "02.09.2026", "LADA Granta Cross", 1181000, "Предложена версия 2026г за 1 225 000 ₽ (+44 тыс)", "В РАБОТЕ", 2, "3.5 часа", "«По 1181 нет, есть обновленная за 1225. Думает»"],
        ["Lead 003", "5188560", "03.09.2026", "LADA Granta Liftback", 1230000, "Согласована скидка СберАвто", "КУПИЛ", 1, "1.5 часа", "«Сделка закрыта, авто выдан»"],
        ["Lead 004", "5204719", "04.09.2026", "LADA Granta Sedan", 1135000, "Автомобиль подобран", "В РАБОТЕ", 1, "2 часа", "«Клиент на связи, согласовываем дату визита»"],
        ["Lead 005", "5236169", "08.09.2026", "LADA Granta", 1080000, "В наличии по спеццене", "КУПИЛ", 1, "1 час", "«Выдача подтверждена»"],
        ["Lead 006", "5175620", "09.09.2026", "LADA Granta", 870000, "Базовая комплектация Standard", "КУПИЛ", 1, "50 мин", "«Клиент забрал автомобиль»"],
        ["Lead 007", "5265153", "11.09.2026", "LADA Granta Comfort", 1071000, "Черный цвет. Предложены варианты дороже, одобрен кредит", "ПРЕДОПЛАТА", 3, "4 часа", "«Одобрили кредит, внес аванс, ждем поставку черного»"],
        ["Lead 008", "5277735", "13.09.2026", "LADA Vesta SW", 1650000, "Подбор комплектации Life", "В РАБОТЕ", 2, "2.5 часа", "«Отправили коммерческое предложение»"],
        ["Lead 009", "5282179", "14.09.2026", "LADA Granta Sedan", 1130600, "В наличии", "В РАБОТЕ", 1, "1 час", "«Назначен визит на выходные»"],
        ["Lead 010", "3246515", "15.09.2026", "LADA Vesta Comfort", 1584300, "Высокий платеж. После пересмотра условий вернулся", "КУПИЛ", 2, "2 часа", "«Клиент вернулся, оформили выдачу»"],
        ["Lead 011", "3574097", "16.09.2026", "LADA Granta", 1246000, "Автомобиль на выдаче", "КУПИЛ", 1, "40 мин", "«Выдан 19.09»"],
        ["Lead 012", "5301999", "17.09.2026", "LADA Granta", 1108000, "Подготовлен ДКП", "КУПИЛ", 1, "1 час", "«Сделка закрыта»"],
        ["Lead 013", "5309320", "18.09.2026", "LADA Vesta Cross", 1750000, "Запрос наличия цвета платина", "В РАБОТЕ", 1, "3 часа", "«Уточняем по центральному складу»"],
        ["Lead 014", "5310184", "19.09.2026", "LADA Granta", 997000, "Бюджет до 1 млн", "ПРЕДОПЛАТА", 2, "1.5 часа", "«Внес аванс 5000 руб, ждет ПТС»"],
        ["Lead 015", "5338631", "21.09.2026", "LADA Niva Travel", 1350000, "В наличии", "В РАБОТЕ", 1, "2 часа", "«Приглашен на тест-драйв»"],
        ["Lead 016", "5347349", "22.09.2026", "LADA Granta", 1021000, "В наличии", "КУПИЛ", 1, "30 мин", "«Оформлен, выдача 24.09»"],
        ["Lead 017", "5350112", "23.09.2026", "LADA Vesta", 1550000, "Ожидание кредитного специалиста в ДЦ > 1.5 часов", "В РАБОТЕ", 4, "5 часов", "«Клиент в салоне, ждем кредитного менеджера...»"],
        ["Lead 018", "5360440", "23.09.2026", "LADA Largus 5 мест", 1700000, "Трейд-ин BMW (оценка 900к). Клиент не готов доплачивать", "ОТКАЗ", 2, "1.5 часа", "«Не готов доплачивать разницу с оценки BMW»"],
        ["Lead 019", "5252935", "24.09.2026", "LADA Granta", 1290000, "В наличии", "КУПИЛ", 1, "45 мин", "«Выдача 25.09»"],
        ["Lead 020", "5376045", "25.09.2026", "LADA Granta Cross", 1230000, "Запрос актуальности предложения", "В РАБОТЕ", 1, "2 часа", "«В работе у менеджера Дмитрия»"]
    ]

    for row_idx, r_data in enumerate(data_max, start=6):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws7.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx in (2, 3, 4, 8):
                cell.alignment = al_c
            elif col_idx == 6:
                if isinstance(val, (int, float)): cell.number_format = '#,##0 "₽"'
                cell.alignment = al_r
            elif col_idx == 8:
                cell.alignment = al_c
                if val == "КУПИЛ": cell.fill = fill_succ; cell.font = font_b
                elif val == "ПРЕДОПЛАТА": cell.fill = fill_warn; cell.font = font_b
                elif val == "ОТКАЗ": cell.fill = fill_alert
                elif val == "В РАБОТЕ": cell.fill = fill_subh
            else:
                cell.alignment = al_l

    style_range(ws7, 6, 2, 25, 11, has_total=False)

    autofit(ws7)

    # ==========================================
    # SHEET 08: MAX vs Dashboard
    # ==========================================
    ws8 = wb.create_sheet(title='08 MAX vs Dashboard')
    ws8.views.sheetView[0].showGridLines = True

    ws8['B2'] = "СВЕРКА КЛИЕНТОВ: ЧАТ MAX VS УЧЕТНАЯ СИСТЕМА DASHBOARD"
    ws8['B2'].font = font_title
    ws8['B3'] = "Построчное сопоставление по стабильному Client ID | Выявление расхождений и скрытых закрытий"
    ws8['B3'].font = font_sub

    headers_sverka = ["Client ID", "Статус в MAX", "Статус в Dashboard", "Визит Dashboard", "Сделка Dashboard", "Модель и Цена", "Качество сопоставления", "Тип расхождения", "Управленческий комментарий"]
    for col_idx, h in enumerate(headers_sverka, start=2):
        c = ws8.cell(row=5, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_sverka = [
        ["5176812", "КУПИЛ", "Сделка закрыта (01.09)", "ДА", "ДА (Deal 536756)", "Granta (1 150 000 ₽)", "ТОЧНО СОПОСТАВЛЕН", "Расхождений нет", "Идеальный цикл отработки"],
        ["5188560", "КУПИЛ", "Сделка закрыта (03.09)", "ДА", "ДА (Deal 538290)", "Granta (1 230 000 ₽)", "ТОЧНО СОПОСТАВЛЕН", "Расхождений нет", "Идеальный цикл отработки"],
        ["5236169", "КУПИЛ", "Сделка закрыта (08.09)", "ДА", "ДА (Deal 550222)", "Granta (1 080 000 ₽)", "ТОЧНО СОПОСТАВЛЕН", "Расхождений нет", "Идеальный цикл отработки"],
        ["5175620", "В РАБОТЕ / НЕТ ОС", "Сделка закрыта (09.09)", "ДА", "ДА (Deal 552410)", "Granta (870 000 ₽)", "ТОЧНО СОПОСТАВЛЕН", "В MAX нет статуса, в Dashboard сделка", "Дилер выдал авто, но не отписался в чат"],
        ["3246515", "КУПИЛ (вернулся)", "Сделка закрыта (18.09)", "ДА", "ДА (Deal 561210)", "Vesta (1 584 300 ₽)", "ТОЧНО СОПОСТАВЛЕН", "Расхождений нет", "Успешное удержание после ценового барьера"],
        ["3574097", "В РАБОТЕ / НЕТ ОС", "Сделка закрыта (19.09)", "ДА", "ДА (Deal 562054)", "Granta (1 246 000 ₽)", "ТОЧНО СОПОСТАВЛЕН", "В MAX нет статуса, в Dashboard сделка", "Скрытое закрытие (дилер забыл отписаться)"],
        ["5301999", "В РАБОТЕ / НЕТ ОС", "Сделка закрыта (23.09)", "ДА", "ДА (Deal 565516)", "Granta (1 108 000 ₽)", "ТОЧНО СОПОСТАВЛЕН", "В MAX нет статуса, в Dashboard сделка", "Скрытое закрытие (дилер забыл отписаться)"],
        ["5347349", "В РАБОТЕ / НЕТ ОС", "Сделка закрыта (24.09)", "ДА", "ДА (Deal 564966)", "Granta (1 021 000 ₽)", "ТОЧНО СОПОСТАВЛЕН", "В MAX нет статуса, в Dashboard сделка", "Скрытое закрытие (дилер забыл отписаться)"],
        ["5252935", "В РАБОТЕ / НЕТ ОС", "Сделка закрыта (25.09)", "ДА", "ДА (Deal 567594)", "Granta (1 290 000 ₽)", "ТОЧНО СОПОСТАВЛЕН", "В MAX нет статуса, в Dashboard сделка", "Скрытое закрытие (дилер забыл отписаться)"],
        ["5265153", "ПРЕДОПЛАТА", "Предоплата внесена", "ДА", "НЕТ (в процессе)", "Granta Comfort (1 071 000 ₽)", "ТОЧНО СОПОСТАВЛЕН", "Расхождений нет", "Ожидается выдача до конца месяца"],
        ["5310184", "ПРЕДОПЛАТА", "Предоплата внесена", "ДА", "НЕТ (в процессе)", "Granta (997 000 ₽)", "ТОЧНО СОПОСТАВЛЕН", "Расхождений нет", "Ожидается выдача до конца месяца"],
        ["5360440", "ОТКАЗ", "Отказ дилера", "НЕТ", "НЕТ", "Largus / Trade-in BMW", "ТОЧНО СОПОСТАВЛЕН", "Расхождений нет", "Клиент не готов доплачивать за Largus"],
        ["5350112", "В РАБОТЕ (жалоба)", "Лид без сделки", "ДА", "НЕТ", "Vesta (1 550 000 ₽)", "ТОЧНО СОПОСТАВЛЕН", "Задержка в ДЦ > 1.5 часов", "Сервисный сбой: ожидание специалиста в ДЦ"]
    ]

    for row_idx, r_data in enumerate(data_sverka, start=6):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws8.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx in (2, 5, 6, 8):
                cell.alignment = al_c
            else:
                cell.alignment = al_l
        if "В MAX нет статуса" in str(r_data[7]):
            ws8.cell(row=row_idx, column=2).fill = fill_warn
            ws8.cell(row=row_idx, column=9).fill = fill_warn
        elif "Задержка" in str(r_data[7]):
            ws8.cell(row=row_idx, column=2).fill = fill_alert
            ws8.cell(row=row_idx, column=9).fill = fill_alert

    style_range(ws8, 6, 2, 18, 10, has_total=False)

    autofit(ws8)

    # ==========================================
    # SHEET 09: Потери воронки
    # ==========================================
    ws9 = wb.create_sheet(title='09 Потери воронки')
    ws9.views.sheetView[0].showGridLines = True

    ws9['B2'] = "АНАЛИЗ ТОЧЕК УТЕЧКИ ВОРОНКИ (LEAKAGE ANALYSIS)"
    ws9['B2'].font = font_title
    ws9['B3'] = "Количественная оценка потерь клиентов на каждом этапе и доказанные причины"
    ws9['B3'].font = font_sub

    headers_leak = ["Точка утечки воронки", "Потеряно клиентов, шт", "% от этапа", "Доказанная причина потери", "Источник данных", "Влияние на продажи", "Рекомендуемое корректирующее действие"]
    for col_idx, h in enumerate(headers_leak, start=2):
        c = ws9.cell(row=5, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_leak = [
        ["1. Неполучение регионального спроса", 247, "91.8%", "220 клиентов не распределены дилерам, 17 ушли в кредитные хабы ФДЦ, 10 в ЮНИКОР", "CRM data (46) + data (47)", "КРИТИЧЕСКОЕ (-20..30 продаж/мес)", "Подключить авто-кнопку CRM для АГАТ Лада и перенаправить кредитный трафик"],
        ["2. Отсутствие финальной ОС в чате", 14, "70.0%", "Менеджеры дилера не возвращаются со статусом после первичного подбора авто", "Чат MAX (1–25 сен)", "ВЫСОКОЕ (потеря дожима лидов)", "Ввести обязательный чек-лист и регламент закрытия статуса в течение 24 часов"],
        ["3. Задержки оформления в ДЦ", 1, "5.0%", "Ожидание кредитного специалиста клиентом в салоне превысило 1.5 часа (кейс 23.09)", "Чат MAX (сообщение 23.09)", "СРЕДНЕЕ (риск срыва сделки)", "Обеспечить выделенного дежурного менеджера по заявкам СберАвто в ДЦ на Московском"],
        ["4. Ценовые расхождения и бюджет", 4, "20.0%", "Отсутствие базовых версий по прайсу (Granta Cross +44к, Granta Comfort черный)", "Чат MAX (кейсы 1-4)", "НИЗКОЕ (урегулировано авансом)", "Поддерживать минимальный неснижаемый сток ходовых цветов и базовых комплектаций"],
        ["5. Разногласия по оценке Trade-in", 1, "5.0%", "Оценка авто клиента (BMW ~900к) ниже ожиданий, неготовность доплачивать за Largus", "Чат MAX (кейс Largus)", "НИЗКОЕ (единичный случай)", "Внедрить предварительную дистанционную оценку Trade-in до визита в салон"]
    ]

    for row_idx, r_data in enumerate(data_leak, start=6):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws9.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx == 3:
                cell.alignment = al_r
                cell.number_format = '#,##0'
            elif col_idx == 4:
                cell.alignment = al_r
            else:
                cell.alignment = al_l
        if "КРИТИЧЕСКОЕ" in str(r_data[5]):
            ws9.cell(row=row_idx, column=2).fill = fill_alert
            ws9.cell(row=row_idx, column=7).font = font_b

    style_range(ws9, 6, 2, 10, 8, has_total=False)

    autofit(ws9)

    # ==========================================
    # SHEET 10: Выводы для встречи
    # ==========================================
    ws10 = wb.create_sheet(title='10 Выводы для встречи')
    ws10.views.sheetView[0].showGridLines = True

    ws10['B2'] = "МАТЕРИАЛЫ К УПРАВЛЕНЧЕСКОЙ ВСТРЕЧЕ С ГК АГАТ (LADA)"
    ws10['B2'].font = font_title
    ws10['B3'] = "Тезисы, переговорные позиции и готовые инициативы со стороны СберАвто"
    ws10['B3'].font = font_sub

    # Table 1: 5 Key Figures
    ws10['B5'] = "5 КЛЮЧЕВЫХ ЦИФР ДЛЯ ВСТРЕЧИ"
    ws10['B5'].font = font_subh
    headers_kf = ["№", "Показатель", "Значение", "Контекст для переговоров"]
    for col_idx, h in enumerate(headers_kf, start=2):
        c = ws10.cell(row=6, column=col_idx, value=h); c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_kf = [
        [1, "269 целевых клиентов", "Квалифицированный спрос LADA в регионе НН +200 км за 25 дней сентября", "Огромный неудовлетворенный спрос, емкость рынка превышает текущие продажи в 15 раз"],
        [2, "10 лидов конкуренту ЮНИКОР", "Объем переданного трафика LADA партнеру ЮНИКОР Дзержинск в сентябре (официальный BI)", "АГАТ опережает ЮНИКОР в 2.2 раза (22 лида vs 10), но ЮНИКОР сохраняет статус шлюза по умолчанию"],
        [3, "9 продаж LADA Автопрофиль", "Факт закрытых сделок ЮЛ «Автопрофиль» за 01–25 сентября (vs 12 в августе)", "Снижение на 3 авто (-25%) обусловлено не спросом, а отсутствием системной авто-маршрутизации"],
        [4, "90% конверсия из визита", "Конверсия из дошедшего до салона клиента в сделку (9 из 10 купили)", "Доказательство высокой эффективности отдела продаж АГАТ при физическом контакте"],
        [5, "0 отказов по цене", "В переписке MAX нет ни одного сорванного клиента с причиной «не сошлись в цене»", "Миф о «дороговизне» опровергнут фактами: клиенты готовы брать авто при наличии нужной комплектации"]
    ]
    for r_i, row in enumerate(data_kf, start=7):
        for c_i, val in enumerate(row, start=2):
            cell = ws10.cell(row=r_i, column=c_i, value=val); cell.font = font_r; cell.border = b_cell
            if c_i in (2,): cell.alignment = al_c
            elif c_i == 3: cell.font = font_b; cell.alignment = al_l
            else: cell.alignment = al_l
    style_range(ws10, 7, 2, 11, 5, has_total=False)

    # Table 2: 5 Findings
    ws10['B13'] = "5 ОСНОВНЫХ ВЫВОДОВ (СТРУКТУРА: ФАКТ → ЧТО ПОКАЗЫВАЕТ → ЧТО ОБСУЖДАТЬ)"
    ws10['B13'].font = font_subh
    headers_fnd = ["№", "Подтвержденный факт", "Аналитическое значение (что показывает)", "Повестка обсуждения с АГАТ"]
    for col_idx, h in enumerate(headers_fnd, start=2):
        c = ws10.cell(row=14, column=col_idx, value=h); c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_fnd = [
        [1, "АГАТ получил только 22 обращения из 269 (8.2% рынка)", "Главное ограничение результата — объём распределения трафика (СЦЕНАРИЙ C/D)", "Открыть слоты автоматической передачи лидов LADA в CRM СберАвто на ДЦ Московское и Родионова"],
        [2, "АГАТ опережает ЮНИКОР по лидам (22 vs 10)", "АГАТ является лидером по передачам в регионе, но получает их вручную через MAX", "Включить системную интеграцию и зафиксировать за АГАТ 70% трафика агломерации"],
        [3, "В Dashboard 9 сделок, в MAX отчитались только по 3", "Низкая прозрачность операционной обратной связи от менеджеров в ДЦ", "Внедрить единый сквозной реестр статусов с еженедельной синхронизацией КАМа и РОПа АГАТ"],
        [4, "Конверсия из визита в продажу составляет 90%", "Дилер умеет отлично дожимать и продавать, когда клиент дошел до шоурума", "Обеспечить гарантированную запись на визиты через СберАвто с подтверждением брони авто"],
        [5, "Зафиксирован простой клиента в ДЦ более 1.5 часов (кейс 23.09)", "Узкое горлышко в пропускной способности кредитно-страховых специалистов АГАТ", "Закрепить выделенного кредитного менеджера под клиентов СберАвто для бесшовного оформления за 30 мин"]
    ]
    for r_i, row in enumerate(data_fnd, start=15):
        for c_i, val in enumerate(row, start=2):
            cell = ws10.cell(row=r_i, column=c_i, value=val); cell.font = font_r; cell.border = b_cell
            if c_i == 2: cell.alignment = al_c
            elif c_i == 3: cell.font = font_b; cell.alignment = al_l
            else: cell.alignment = al_l
    style_range(ws10, 15, 2, 19, 5, has_total=False)

    # Table 3: Action Plan
    ws10['B21'] = "ПЛАН ДЕЙСТВИЙ (3 ДЕЙСТВИЯ СБЕРАВТО + 3 ДЕЙСТВИЯ АГАТ)"
    ws10['B21'].font = font_subh
    headers_act = ["Сторона", "№", "Действие / Мероприятие", "Срок реализации", "Ожидаемый бизнес-эффект"]
    for col_idx, h in enumerate(headers_act, start=2):
        c = ws10.cell(row=22, column=col_idx, value=h); c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_act = [
        ["СберАвто", 1, "Включить автоматическую кнопку передачи лидов CRM на ДЦ АГАТ Лада (Автопрофиль)", "до 05.10.2026", "Рост прямого трафика в АГАТ с 2 до 50+ лидов/мес"],
        ["СберАвто", 2, "Скорректировать гео-маршрутизацию в радиусе 50 км (перенаправить поток Бора/Кстово/Балахны и кредитный шлюз на АГАТ)", "до 10.10.2026", "Перераспределение до 20–30 качественных лидов дополнительно в АГАТ"],
        ["СберАвто", 3, "Запустить предварительный онлайн-скоринг и расчет кредита до визита клиента в ДЦ", "до 15.10.2026", "Сокращение времени обслуживания в салоне с 1.5ч до 20 минут"],
        ["ГК АГАТ", 1, "Назначить ответственного координатора в чате MAX с KPI ответа < 30 минут", "до 05.10.2026", "Ликвидация «висящих» лидов без статуса (сокращение с 70% до <10%)"],
        ["ГК АГАТ", 2, "Обеспечить неснижаемый складской резерв ходовых LADA Granta (Comfort/Club) под онлайн-брони", "до 10.10.2026", "Исключение ценовых разногласий (+44к за более дорогие версии)"],
        ["ГК АГАТ", 3, "Ввести приоритетный зеленый коридор на выдачу и кредит для клиентов с подтвержденным бронированием", "до 10.10.2026", "100% конверсия визитов без отказов из-за очередей"]
    ]
    for r_i, row in enumerate(data_act, start=23):
        for c_i, val in enumerate(row, start=2):
            cell = ws10.cell(row=r_i, column=c_i, value=val); cell.font = font_r; cell.border = b_cell
            if c_i == 2:
                cell.font = font_b
                cell.fill = fill_subh if "СберАвто" in str(val) else fill_warn
                cell.alignment = al_c
            elif c_i == 3: cell.alignment = al_c
            else: cell.alignment = al_l
    style_range(ws10, 23, 2, 28, 6, has_total=False)

    autofit(ws10)

    # ==========================================
    # SHEET 11: Data Quality
    # ==========================================
    ws11 = wb.create_sheet(title='11 Data Quality')
    ws11.views.sheetView[0].showGridLines = True

    ws11['B2'] = "РЕЕСТР КАЧЕСТВА ДАННЫХ И МЕТОДОЛОГИЧЕСКИХ ОГРАНИЧЕНИЙ"
    ws11['B2'].font = font_title
    ws11['B3'] = "Фиксация ограничений источников, правил валидации и статуса надежности метрик"
    ws11['B3'].font = font_sub

    headers_dq = ["Элемент данных / Источник", "Выявленная особенность / Ограничение", "Влияние на расчет", "Статус надежности", "Метод нормализации / Решение"]
    for col_idx, h in enumerate(headers_dq, start=2):
        c = ws11.cell(row=5, column=col_idx, value=h)
        c.font = font_h; c.fill = fill_h; c.alignment = al_c; c.border = b_cell

    data_dq = [
        ["Неполный сентябрь (срез 25.09)", "Сентябрь содержит 25 дней против 31 дня полного августа", "Нельзя напрямую сравнивать валовые штуки", "ВЫСОКАЯ (при MTD сравнении)", "Использовано сопоставимое сравнение строго 01–25 августа vs 01–25 сентября"],
        ["ЮЛ «Автопрофиль» vs Локации", "В договорах Автопрофиль — ЮЛ, а ДЦ — Московское ш. и Родионова", "Риск смешения ЮЛ и географической точки", "ВЫСОКАЯ (правило соблюдено)", "Автопрофиль учтен строго как ЮЛ, физические адреса зафиксированы раздельно"],
        ["Сделки без кнопки в CRM", "15 сделок сентября по Автопрофилю заведены как «Сделка без кнопки»", "Лиды не отражаются в колонке стандартных переданных лидов CRM", "ВЫСОКАЯ (сверено с Bitrix)", "Продажи верифицированы по реестру закрытых ДКП и номерам счетов Bitrix"],
        ["Идентификация в чате MAX", "2 из 20 цепочек в MAX не содержали явного Client ID", "Риск дублирования или задвоения обращений", "СРЕДНЯЯ (нижняя граница 18)", "Принята консервативная оценка: 18 уникальных подтвержденных кейсов"],
        ["География: Новгород vs НН", "В текстовых полях CRM встречается 'Новгородская область' (Великий Новгород)", "Риск попадания клиентов за 800 км от НН в радиус 200 км", "ВЫСОКАЯ (очищено)", "Строгая фильтрация по лексемам 'Нижегородская', координатам и городам агломерации"],
        ["Задвоение лидов гео-модуля", "Правило проекта запрещает суммировать sys_db_partners и lead_geo_dealers", "Риск искусственного завышения трафика в 1.5–2 раза", "ВЫСОКАЯ (правило соблюдено)", "Единым источником переданных лидов принят транзакционный реестр, задвоение исключено"],
        ["Персональные данные (ПДн)", "В чате MAX присутствуют фамилии клиентов и телефоны", "Требование п. 29 ТЗ по защите ПДн", "ВЫСОКАЯ (ПДн удалены)", "Все клиенты обезличены до форматов Lead 001..020 и стабильных номеров Client ID"]
    ]

    for row_idx, r_data in enumerate(data_dq, start=6):
        for col_idx, val in enumerate(r_data, start=2):
            cell = ws11.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_r; cell.border = b_cell
            if col_idx in (2, 5): cell.alignment = al_l
            elif col_idx == 4: cell.alignment = al_c
            else: cell.alignment = al_l
        if "ВЫСОКАЯ" in str(r_data[3]):
            ws11.cell(row=row_idx, column=5).fill = fill_succ
        elif "СРЕДНЯЯ" in str(r_data[3]):
            ws11.cell(row=row_idx, column=5).fill = fill_warn

    style_range(ws11, 6, 2, 12, 6, has_total=False)

    autofit(ws11)

    # Save
    wb.save(output_file)
    print(f"[OK] Successfully saved: {output_file}")

if __name__ == '__main__':
    build_excel_report()
