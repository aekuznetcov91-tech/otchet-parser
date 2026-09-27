import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_document():
    doc = Document()

    # Page margins: 0.8 in (~2 cm)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Color Palette
    c_primary = RGBColor(0, 139, 142)    # SberAuto Teal #008B8E
    c_dark = RGBColor(15, 23, 42)        # Slate 900 #0F172A
    c_muted = RGBColor(100, 116, 139)    # Slate 500 #64748B
    c_emerald = RGBColor(5, 150, 105)    # Emerald 600 #059669

    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'''
            <w:tcMar {nsdecls("w")}>
                <w:top w:w="{top}" w:type="dxa"/>
                <w:bottom w:w="{bottom}" w:type="dxa"/>
                <w:left w:w="{left}" w:type="dxa"/>
                <w:right w:w="{right}" w:type="dxa"/>
            </w:tcMar>
        ''')
        tcPr.append(tcMar)

    def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:left w:val="none"/>
                <w:right w:val="none"/>
                <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:insideV w:val="none"/>
            </w:tblBorders>
        ''')
        tblPr.append(borders)

    # 1. Header & Title Block
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_after = Pt(4)
    run_pre = p_pre.add_run("СБЕРАВТО × АВТОГИД — НОВОЕ ПРОСТРАНСТВО ДЛЯ АВТОЛЮБИТЕЛЕЙ")
    run_pre.font.name = "Calibri"
    run_pre.font.size = Pt(9.5)
    run_pre.font.bold = True
    run_pre.font.color.rgb = c_primary

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_after = Pt(6)
    run_title = p_title.add_run("ТЕКСТОВЫЙ БРИФ ДЛЯ КАРТОЧЕК ВИТРИНЫ (ВАРИАНТ №2)")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = c_dark

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(14)
    run_sub = p_sub.add_run("Спецификация полей, цен, модификаций и скидок для 28 карточек по 10 брендам (LADA, JETOUR, SOUEAST, TENET, JELAND, CHANGAN, GAC, TENET PLUS, HONGQI, BELGEE). Все параметры актуализированы и строго синхронизированы с официальным калькулятором СберАвто (OEM 22.09 / git autocalculator).")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(10.5)
    run_sub.font.italic = True
    run_sub.font.color.rgb = c_muted

    # Callout box (Meta)
    t_meta = doc.add_table(rows=1, cols=1)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_meta = t_meta.rows[0].cells[0]
    set_cell_background(cell_meta, "F0FDFA") # Light teal
    set_cell_margins(cell_meta, top=160, bottom=160, left=200, right=200)

    tcPr = cell_meta._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:color="00A3A6"/>
            <w:bottom w:val="single" w:sz="6" w:color="00A3A6"/>
            <w:left w:val="single" w:sz="24" w:color="00A3A6"/>
            <w:right w:val="single" w:sz="6" w:color="00A3A6"/>
        </w:tcBorders>
    ''')
    tcPr.append(tcBorders)

    p_meta = cell_meta.paragraphs[0]
    p_meta.paragraph_format.space_after = Pt(0)
    r_m1 = p_meta.add_run("ПАРАМЕТРЫ ШАБЛОНА И СТАНДАРТ ЗАПОЛНЕНИЯ (ВАРИАНТ №2):\n")
    r_m1.bold = True
    r_m1.font.size = Pt(10)
    r_m1.font.color.rgb = c_primary

    r_m2 = p_meta.add_run(
        "• Чистая цена: крупная стартовая стоимость «от X ₽» без зачеркиваний, сформированная с учетом скидки на базовую версию (для брендов со скидками: РРЦ базовой версии минус официальная скидка) либо от официальной РРЦ базовой версии (для линеек без спецскидок: TENET PLUS, HONGQI).\n"
        "• Информационные плашки: две плашки с указанием выгоды/оснащения (базовая комплектация + топовая версия с бейджем [Хит]). Плашки не кликабельны.\n"
        "• Карточки без спецскидок (TENET PLUS, HONGQI): на плашках выводятся ключевые характеристики оснащения комплектаций и официальная РРЦ производителя, а цена «от» точно соответствует стартовой РРЦ.\n"
        "• Кнопка перехода: единственным активным элементом является кнопка «Купить», ведущая напрямую на форму оформления сделки в СберАвто.\n"
        "• Источник актуальных данных: репозиторий калькулятора СберАвто (git autocalculator / OEM СберАвто финал 22.09 / project_data.json)."
    )
    r_m2.font.size = Pt(9.5)
    r_m2.font.color.rgb = c_dark

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(14)
    p_space.paragraph_format.space_after = Pt(6)
    r_s_title = p_space.add_run("СВОДНАЯ ТАБЛИЦА ВСЕХ 28 КАРТОЧЕК ВИТРИНЫ (10 БРЕНДОВ)")
    r_s_title.bold = True
    r_s_title.font.size = Pt(12)
    r_s_title.font.color.rgb = c_dark

    # 2. Summary Table
    cards_summary = [
        ("1", "LADA", "Granta", "1.6 MT (90 / 106 л.с.)", "Стандарт Плюс", "Club'24 [Хит]", "от 820 000 ₽", "до 35 000 ₽"),
        ("2", "LADA", "Vesta NG", "1.6 MT / 1.8 AT", "Комфорт", "Техно [Хит]", "от 1 581 000 ₽", "до 55 000 ₽"),
        ("3", "LADA", "Niva Travel", "1.7 4WD / 1.8 4WD", "Классик'24", "КХЛ'24 [Хит]", "от 1 298 000 ₽", "до 45 000 ₽"),
        ("4", "JETOUR", "Dashing", "1.5T 2WD / 1.6T 2WD", "Комфорт", "Престиж [Хит]", "от 2 140 000 ₽", "до 619 900 ₽"),
        ("5", "JETOUR", "T1", "1.5T 2WD / 2.0T 4WD", "Престиж", "Премиум [Хит]", "от 3 470 000 ₽", "до 529 900 ₽"),
        ("6", "JETOUR", "T2", "2.0T 4WD (245 л.с.)", "Люкс", "Престиж [Хит]", "от 3 400 000 ₽", "до 759 000 ₽"),
        ("7", "SOUEAST", "S06", "1.5T 2WD / 1.6T 4WD", "Престиж 2WD", "Престиж 4WD [Хит]", "от 2 220 000 ₽", "до 929 900 ₽"),
        ("8", "SOUEAST", "S07", "1.6T 2WD / 1.6T 4WD", "Престиж 2WD", "Премиум 4WD [Хит]", "от 2 700 000 ₽", "до 749 000 ₽"),
        ("9", "TENET", "T7", "1.6 2WD / 1.6 AWD", "Active", "Prime [Хит]", "от 2 396 000 ₽", "до 401 000 ₽"),
        ("10", "TENET", "T4L", "1.5T 2WD (147 л.с.) / 6DCT", "Active", "Prime [Хит]", "от 2 213 000 ₽", "до 148 000 ₽"),
        ("11", "TENET", "T8", "1.6T 2WD / 2.0T AWD", "Active", "Prime [Хит]", "от 2 821 000 ₽", "до 466 000 ₽"),
        ("12", "JELAND", "J6", "1.5T 2WD / 1.5T AWD", "Active", "Comfort [Хит]", "от 2 119 000 ₽", "до 345 000 ₽"),
        ("13", "JELAND", "J7", "1.6T 2WD / 1.6T AWD", "Comfort", "Prestige 4WD [Хит]", "от 2 430 000 ₽", "до 462 000 ₽"),
        ("14", "JELAND", "J8", "2.0T AWD (249 л.с.)", "Comfort", "Prestige+ [Хит]", "от 3 874 000 ₽", "до 515 000 ₽"),
        ("15", "CHANGAN", "Uni-S", "1.5T 2WD / 1.5T 4WD", "Техно", "Техно+ [Хит]", "от 2 979 900 ₽", "до 200 000 ₽"),
        ("16", "CHANGAN", "CS35 Plus", "1.4T 2WD (150 л.с.)", "Комфорт", "Техно [Хит]", "от 2 374 900 ₽", "до 405 000 ₽"),
        ("17", "CHANGAN", "CS75 Plus", "1.5T 2WD / 2.0T 4WD", "Комфорт", "Люкс [Хит]", "от 3 634 900 ₽", "до 185 000 ₽"),
        ("18", "GAC", "GS8 II", "2.0T 4WD (248 л.с.)", "GL 4WD", "GX Premium [Хит]", "от 4 094 100 ₽", "до 534 900 ₽"),
        ("19", "GAC", "GS4 Max", "1.5T 2WD / 1.5T 4WD", "GB 2WD", "GL 4WD [Хит]", "от 2 969 100 ₽", "до 394 900 ₽"),
        ("20", "GAC", "M8", "2.0T 2WD (231 л.с.)", "GL", "GX Premium [Хит]", "от 4 949 999 ₽", "до 675 000 ₽"),
        # TENET PLUS:
        ("21", "TENET PLUS", "L4", "1.5T 2WD (147 л.с.)", "Стайл", "Элегант [Хит]", "от 2 540 000 ₽", "РРЦ (без скидки)"),
        ("22", "TENET PLUS", "L6", "1.5T 2WD / 1.6T 4WD", "Элегант", "Ультра [Хит]", "от 2 890 000 ₽", "РРЦ (без скидки)"),
        # HONGQI:
        ("23", "HONGQI", "HS3", "1.5T 2WD / 2.0T 4WD", "Comfort", "Deluxe 4WD [Хит]", "от 2 990 000 ₽", "РРЦ (без скидки)"),
        ("24", "HONGQI", "H5", "1.5T 2WD / 2.0T 2WD", "Comfort", "Deluxe [Хит]", "от 3 590 000 ₽", "РРЦ (без скидки)"),
        ("25", "HONGQI", "HS5 NEW", "2.0T 4WD (245 л.с.)", "Comfort 4WD", "Deluxe 4WD [Хит]", "от 4 190 000 ₽", "РРЦ (без скидки)"),
        # BELGEE:
        ("26", "BELGEE", "X50+", "1.5T 2WD (150 л.с.)", "Active 7DCT", "Style [Хит]", "от 2 229 990 ₽", "до 90 000 ₽"),
        ("27", "BELGEE", "X70", "1.5T 2WD / 1.5T 4WD", "Active 6AT", "Prestige+ 4WD [Хит]", "от 2 330 990 ₽", "до 594 000 ₽"),
        ("28", "BELGEE", "S50", "1.5 MT / 1.5 6AT", "Active MT", "Prestige AT [Хит]", "от 1 749 990 ₽", "до 180 000 ₽")
    ]

    t_sum = doc.add_table(rows=len(cards_summary) + 1, cols=8)
    t_sum.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_sum)

    sum_headers = ["№", "Бренд", "Модель", "Модификации", "Компл. 1", "Компл. 2", "Цена «от»", "Скидка / Статус"]
    hdr_row = t_sum.rows[0]
    for idx, name in enumerate(sum_headers):
        c = hdr_row.cells[idx]
        set_cell_background(c, "F1F5F9")
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(name)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = c_dark
        if idx in [0, 6, 7]:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    for r_idx, row_data in enumerate(cards_summary, start=1):
        row = t_sum.rows[r_idx]
        bg = "FFFFFF" if r_idx % 2 == 1 else "F8FAFC"
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=90, right=90)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8)
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r.font.color.rgb = c_muted
            elif c_idx == 1:
                r.bold = True
                r.font.color.rgb = c_primary
            elif c_idx == 2:
                r.bold = True
                r.font.color.rgb = c_dark
            elif c_idx == 6:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                r.bold = True
                r.font.color.rgb = c_dark
            elif c_idx == 7:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r.bold = True
                if "без скидки" in val:
                    r.font.color.rgb = c_muted
                else:
                    r.font.color.rgb = c_emerald
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    doc.add_page_break()

    # 3. Detailed Cards Section by Brand
    detailed_cards = [
        # --- LADA ---
        {
            "brand": "LADA",
            "desc": "Лидер массового сегмента рынка РФ. Обеспечивает максимальный органический охват и самый доступный порог входа.",
            "cards": [
                {
                    "title": "LADA Granta, 2026",
                    "badge": "Хит продаж",
                    "mods": "1.6 MT (90 л.с.) • 1.6 MT (106 л.с.)",
                    "c1_name": "Стандарт Плюс", "c1_disc": "скидка 30 000 ₽", "c1_rrc": "850 000 ₽",
                    "c2_name": "#КЛУБ ММС [Хит]", "c2_disc": "скидка 30 000 ₽", "c2_rrc": "1 290 000 ₽",
                    "price_from": "от 820 000 ₽",
                    "price_note": "цена указана за Стандарт Плюс (850 000 − 30 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/lada/granta"
                },
                {
                    "title": "LADA Vesta NG, 2026",
                    "badge": "Новый",
                    "mods": "1.6 MT (106 л.с.) • 1.8 AT (122 л.с.)",
                    "c1_name": "Комфорт (АТ)", "c1_disc": "скидка 50 000 ₽", "c1_rrc": "1 631 000 ₽",
                    "c2_name": "Техно [Хит]", "c2_disc": "скидка 50 000 ₽", "c2_rrc": "2 110 000 ₽",
                    "price_from": "от 1 581 000 ₽",
                    "price_note": "цена указана за Комфорт АТ (1 631 000 − 50 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/lada/vesta"
                },
                {
                    "title": "LADA Niva Travel, 2026",
                    "badge": "4WD",
                    "mods": "1.7 4WD (83 л.с.) • 1.8 4WD (90 л.с.)",
                    "c1_name": "Классик'24", "c1_disc": "скидка 45 000 ₽", "c1_rrc": "1 343 000 ₽",
                    "c2_name": "КХЛ'24 [Хит]", "c2_disc": "скидка 45 000 ₽", "c2_rrc": "1 668 000 ₽",
                    "price_from": "от 1 298 000 ₽",
                    "price_note": "цена указана за Классик'24 (1 343 000 − 45 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/lada/niva-travel"
                }
            ]
        },
        # --- JETOUR ---
        {
            "brand": "JETOUR",
            "desc": "Бренд №1 по объёму сделок на платформе СберАвто. Фокус на стильные кроссоверы и брутальные внедорожники серии T.",
            "cards": [
                {
                    "title": "Jetour Dashing, 2026",
                    "badge": "Новый",
                    "mods": "1.5T 2WD (147 л.с.) • 1.6T 2WD (190 л.с.)",
                    "c1_name": "Комфорт 1.5T 6DCT", "c1_disc": "скидка 619 900 ₽", "c1_rrc": "2 759 900 ₽",
                    "c2_name": "Престиж 1.5T 6DCT [Хит]", "c2_disc": "скидка 589 900 ₽", "c2_rrc": "3 029 900 ₽",
                    "price_from": "от 2 140 000 ₽",
                    "price_note": "цена указана за Комфорт (2 759 900 − 619 900 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/jetour/dashing"
                },
                {
                    "title": "Jetour T1, 2026",
                    "badge": "Новинка",
                    "mods": "1.5T 2WD • 2.0T 4WD (245 л.с.)",
                    "c1_name": "Престиж 2.0 8AT", "c1_disc": "скидка 529 900 ₽", "c1_rrc": "3 999 900 ₽",
                    "c2_name": "Премиум 2.0 8AT [Хит]", "c2_disc": "скидка 529 900 ₽", "c2_rrc": "4 199 900 ₽",
                    "price_from": "от 3 470 000 ₽",
                    "price_note": "цена указана за Престиж (3 999 900 − 529 900 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/jetour/t1"
                },
                {
                    "title": "Jetour T2, 2026",
                    "badge": "Лучшее",
                    "mods": "2.0T 4WD (245 л.с.) • 7DCT 4x4 / 8AT",
                    "c1_name": "Люкс 2.0 7DCT", "c1_disc": "скидка 759 000 ₽", "c1_rrc": "4 159 000 ₽",
                    "c2_name": "Престиж 2.0 7DCT [Хит]", "c2_disc": "скидка 759 000 ₽", "c2_rrc": "4 449 000 ₽",
                    "price_from": "от 3 400 000 ₽",
                    "price_note": "цена указана за Люкс (4 159 000 − 759 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/jetour/t2"
                }
            ]
        },
        # --- SOUEAST ---
        {
            "brand": "SOUEAST",
            "desc": "Новый стратегический бренд платформы СберАвто на проверенной технологической базе. Представлен моделями S06 и S07.",
            "cards": [
                {
                    "title": "SOUEAST S06, 2026",
                    "badge": "Новый",
                    "mods": "1.5T 2WD • 1.6T 4WD",
                    "c1_name": "Престиж 1.5T 2WD", "c1_disc": "скидка 879 000 ₽", "c1_rrc": "3 099 000 ₽",
                    "c2_name": "Престиж 1.6T 4WD [Хит]", "c2_disc": "скидка 929 900 ₽", "c2_rrc": "3 479 900 ₽",
                    "price_from": "от 2 220 000 ₽",
                    "price_note": "цена указана за Престиж 2WD (3 099 000 − 879 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/soueast/s06"
                },
                {
                    "title": "SOUEAST S07, 2026",
                    "badge": "Флагман",
                    "mods": "1.5T 2WD • 1.6T 4WD",
                    "c1_name": "Престиж 1.5T 2WD", "c1_disc": "скидка 699 000 ₽", "c1_rrc": "3 399 000 ₽",
                    "c2_name": "Премиум 1.6T 4WD [Хит]", "c2_disc": "скидка 749 000 ₽", "c2_rrc": "3 549 000 ₽",
                    "price_from": "от 2 700 000 ₽",
                    "price_note": "цена указана за Престиж 2WD (3 399 000 − 699 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/soueast/s07"
                }
            ]
        },
        # --- TENET ---
        {
            "brand": "TENET",
            "desc": "Современная городская линейка бренда TENET. Оптимальный баланс технологичности, динамики и прозрачного выбора комплектаций.",
            "cards": [
                {
                    "title": "Tenet T7, 2026",
                    "badge": "Новый",
                    "mods": "1.6 2WD • 1.6 AWD",
                    "c1_name": "Active 1.6T DCT7", "c1_disc": "скидка 389 000 ₽", "c1_rrc": "2 785 000 ₽",
                    "c2_name": "Prime 1.6T DCT7 [Хит]", "c2_disc": "скидка 388 000 ₽", "c2_rrc": "2 985 000 ₽",
                    "price_from": "от 2 396 000 ₽",
                    "price_note": "цена указана за Active (2 785 000 − 389 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/tenet/t7"
                },
                {
                    "title": "Tenet T4L, 2026",
                    "badge": "Хит",
                    "mods": "1.5T 2WD (147 л.с.) • 6DCT",
                    "c1_name": "Active 1.5T DCT6", "c1_disc": "скидка 116 000 ₽", "c1_rrc": "2 329 000 ₽",
                    "c2_name": "Prime 1.5T DCT6 [Хит]", "c2_disc": "скидка 148 000 ₽", "c2_rrc": "2 479 000 ₽",
                    "price_from": "от 2 213 000 ₽",
                    "price_note": "цена указана за Active (2 329 000 − 116 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/tenet/t4l"
                },
                {
                    "title": "Tenet T8, 2026",
                    "badge": "Флагман",
                    "mods": "1.6T 2WD • 2.0T AWD",
                    "c1_name": "Active 1.6T DCT7", "c1_disc": "скидка 278 000 ₽", "c1_rrc": "3 099 000 ₽",
                    "c2_name": "Prime 1.6T DCT7 [Хит]", "c2_disc": "скидка 395 000 ₽", "c2_rrc": "3 299 000 ₽",
                    "price_from": "от 2 821 000 ₽",
                    "price_note": "цена указана за Active (3 099 000 − 278 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/tenet/t8"
                }
            ]
        },
        # --- JELAND ---
        {
            "brand": "JELAND",
            "desc": "Инновационный технологичный суббренд. Включает стильные кроссоверы и полноприводные внедорожники серий J6, J7 и J8.",
            "cards": [
                {
                    "title": "Jeland J6, 2026",
                    "badge": "Электро / 4x4",
                    "mods": "1.5T 2WD • 1.5T AWD",
                    "c1_name": "Active 1.5T DCT6", "c1_disc": "скидка 231 000 ₽", "c1_rrc": "2 350 000 ₽",
                    "c2_name": "Comfort 1.5T DCT6 [Хит]", "c2_disc": "скидка 301 000 ₽", "c2_rrc": "2 549 000 ₽",
                    "price_from": "от 2 119 000 ₽",
                    "price_note": "цена указана за Active (2 350 000 − 231 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/jeland/j6"
                },
                {
                    "title": "Jeland J7, 2026",
                    "badge": "Новый",
                    "mods": "1.6T 2WD • 1.6T AWD",
                    "c1_name": "Comfort (Active) 1.6T", "c1_disc": "скидка 419 000 ₽", "c1_rrc": "2 849 000 ₽",
                    "c2_name": "Prestige 4WD [Хит]", "c2_disc": "скидка 462 000 ₽", "c2_rrc": "3 409 000 ₽",
                    "price_from": "от 2 430 000 ₽",
                    "price_note": "цена указана за Comfort (2 849 000 − 419 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/jeland/j7"
                },
                {
                    "title": "Jeland J8, 2026",
                    "badge": "Премиум",
                    "mods": "2.0T AWD (249 л.с.) • 8AT 4x4 / 7DCT",
                    "c1_name": "Comfort BL 4WD", "c1_disc": "скидка 456 000 ₽", "c1_rrc": "4 330 000 ₽",
                    "c2_name": "Prestige+ BL 4WD [Хит]", "c2_disc": "скидка 515 000 ₽", "c2_rrc": "4 845 000 ₽",
                    "price_from": "от 3 874 000 ₽",
                    "price_note": "цена указана за Comfort 4WD (4 330 000 − 456 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/jeland/j8"
                }
            ]
        },
        # --- CHANGAN ---
        {
            "brand": "CHANGAN",
            "desc": "Один из наиболее востребованных брендов с широким модельным рядом и динамичным дизайном серии UNI.",
            "cards": [
                {
                    "title": "Changan Uni-S, 2026",
                    "badge": "Новый",
                    "mods": "1.5T 2WD • 1.5T 4WD",
                    "c1_name": "Техно DCT 4x2", "c1_disc": "скидка 200 000 ₽", "c1_rrc": "3 179 900 ₽",
                    "c2_name": "Техно+ DCT 4x2 [Хит]", "c2_disc": "скидка 200 000 ₽", "c2_rrc": "3 209 900 ₽",
                    "price_from": "от 2 979 900 ₽",
                    "price_note": "цена указана за Техно (3 179 900 − 200 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/changan/uni-s"
                },
                {
                    "title": "Changan CS35 Plus, 2026",
                    "badge": "Хит",
                    "mods": "1.4T 2WD (150 л.с.) • 7DCT",
                    "c1_name": "Комфорт DCT 4x2", "c1_disc": "скидка 405 000 ₽", "c1_rrc": "2 779 900 ₽",
                    "c2_name": "Техно DCT 4x2 [Хит]", "c2_disc": "скидка 325 000 ₽", "c2_rrc": "2 839 900 ₽",
                    "price_from": "от 2 374 900 ₽",
                    "price_note": "цена указана за Комфорт (2 779 900 − 405 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/changan/cs35plus"
                },
                {
                    "title": "Changan CS75 Plus, 2026",
                    "badge": "Семейный",
                    "mods": "1.5T 2WD • 2.0T 4WD",
                    "c1_name": "Комфорт AT 4x2", "c1_disc": "скидка 185 000 ₽", "c1_rrc": "3 819 900 ₽",
                    "c2_name": "Люкс AT 4x2 [Хит]", "c2_disc": "скидка 185 000 ₽", "c2_rrc": "4 019 900 ₽",
                    "price_from": "от 3 634 900 ₽",
                    "price_note": "цена указана за Комфорт (3 819 900 − 185 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/changan/cs75plus"
                }
            ]
        },
        # --- GAC ---
        {
            "brand": "GAC",
            "desc": "Премиальный сегмент китайского рынка. Лидер по качеству сборки, флагманские 7-местные внедорожники и представительские минивэны.",
            "cards": [
                {
                    "title": "GAC GS8 II, 2026",
                    "badge": "Флагман",
                    "mods": "2.0T 4WD (248 л.с.) • 8AT 4x4",
                    "c1_name": "GL 4WD (5 мест)", "c1_disc": "скидка 454 900 ₽", "c1_rrc": "4 549 000 ₽",
                    "c2_name": "GX Premium 4WD [Хит]", "c2_disc": "скидка 534 900 ₽", "c2_rrc": "5 349 000 ₽",
                    "price_from": "от 4 094 100 ₽",
                    "price_note": "цена указана за GL 4WD (4 549 000 − 454 900 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/gac/gs8"
                },
                {
                    "title": "GAC GS4 Max, 2026",
                    "badge": "Новый",
                    "mods": "1.5T 2WD (177 л.с.) • 1.5T 4WD",
                    "c1_name": "GB 2WD", "c1_disc": "скидка 329 900 ₽", "c1_rrc": "3 299 000 ₽",
                    "c2_name": "GL 4WD [Хит]", "c2_disc": "скидка 394 900 ₽", "c2_rrc": "3 949 000 ₽",
                    "price_from": "от 2 969 100 ₽",
                    "price_note": "цена указана за GB 2WD (3 299 000 − 329 900 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/gac/gs4"
                },
                {
                    "title": "GAC M8, 2026",
                    "badge": "Бизнес-класс",
                    "mods": "2.0T 2WD (231 л.с.) • 8AT",
                    "c1_name": "GL 2WD", "c1_disc": "скидка 550 000 ₽", "c1_rrc": "5 499 999 ₽",
                    "c2_name": "GX Premium [Хит]", "c2_disc": "скидка 675 000 ₽", "c2_rrc": "6 749 999 ₽",
                    "price_from": "от 4 949 999 ₽",
                    "price_note": "цена указана за GL (5 499 999 − 550 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/gac/m8"
                }
            ]
        },
        # --- TENET PLUS ---
        {
            "brand": "TENET PLUS",
            "desc": "Инновационная технологичная линейка бренда TENET (L-серия). Расширенное интеллектуальное оснащение, динамичные силовые установки и субсидированные кредитные программы Сбера.",
            "cards": [
                {
                    "title": "TENET PLUS L4, 2026",
                    "badge": "Новый",
                    "mods": "1.5T 2WD (147 л.с.) • 6DCT",
                    "c1_name": "Стайл", "c1_disc": "1.5T 147 л.с. • LED-оптика • Цифровая панель", "c1_rrc": "2 540 000 ₽",
                    "c2_name": "Элегант [Хит]", "c2_disc": "Камеры 360° • Панорама • Тёплые опции", "c2_rrc": "2 690 000 ₽",
                    "price_from": "от 2 540 000 ₽",
                    "price_note": "официальная РРЦ за комплектацию Стайл (без спецскидки)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/tenet/plus-l4"
                },
                {
                    "title": "TENET PLUS L6, 2026",
                    "badge": "Хит линейки",
                    "mods": "1.5T 2WD (147 л.с.) • 1.6T AWD 4x4",
                    "c1_name": "Элегант", "c1_disc": "1.5T 147 л.с. • 2-зонный климат • 10.25' мультимедиа", "c1_rrc": "2 890 000 ₽",
                    "c2_name": "Ультра [Хит]", "c2_disc": "Интеллектуальный комплекс ADAS • Панорама", "c2_rrc": "3 040 000 ₽",
                    "price_from": "от 2 890 000 ₽",
                    "price_note": "официальная РРЦ за комплектацию Элегант (без спецскидки)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/tenet/plus-l6"
                }
            ]
        },
        # --- HONGQI ---
        {
            "brand": "HONGQI",
            "desc": "Официальный премиальный государственный автомобильный бренд Китая (FAW Hongqi). Высочайшее качество отделки, передовой акустический комфорт и представительский статус.",
            "cards": [
                {
                    "title": "Hongqi HS3, 2026",
                    "badge": "Новинка",
                    "mods": "1.5T 2WD (156 л.с.) • 2.0T AWD (252 л.с.) • 8AT",
                    "c1_name": "Comfort", "c1_disc": "1.5T 156 л.с. • Двойные стёкла • Цифровой кокпит", "c1_rrc": "2 990 000 ₽",
                    "c2_name": "Deluxe 4WD [Хит]", "c2_disc": "2.0T 252 л.с. AWD • Панорамная крыша • ADAS", "c2_rrc": "3 490 000 ₽",
                    "price_from": "от 2 990 000 ₽",
                    "price_note": "официальная РРЦ за комплектацию Comfort (без спецскидки)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/hongqi/hs3"
                },
                {
                    "title": "Hongqi H5, 2026",
                    "badge": "Бизнес-седан",
                    "mods": "1.5T 2WD (156 л.с.) • 2.0T 2WD (218 л.с.) • 8AT",
                    "c1_name": "Comfort", "c1_disc": "1.5T 156 л.с. • Натуральная кожа • Шумоизоляция", "c1_rrc": "3 590 000 ₽",
                    "c2_name": "Deluxe [Хит]", "c2_disc": "2.0T 218 л.с. 8AT • Вентиляция кресел • Аудио Dynaudio", "c2_rrc": "4 250 000 ₽",
                    "price_from": "от 3 590 000 ₽",
                    "price_note": "официальная РРЦ за комплектацию Comfort (без спецскидки)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/hongqi/h5"
                },
                {
                    "title": "Hongqi HS5 NEW, 2026",
                    "badge": "Флагман",
                    "mods": "2.0T 4WD (245 л.с.) • 8AT 4x4",
                    "c1_name": "Comfort 4WD", "c1_disc": "2.0T 245 л.с. 4WD • Кожа Nappa • Премиум Bose Audio", "c1_rrc": "4 190 000 ₽",
                    "c2_name": "Deluxe 4WD [Хит]", "c2_disc": "Адаптивная подвеска CDC • Проекция HUD • Массаж", "c2_rrc": "4 990 000 ₽",
                    "price_from": "от 4 190 000 ₽",
                    "price_note": "официальная РРЦ за комплектацию Comfort 4WD (без спецскидки)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/hongqi/hs5"
                }
            ]
        },
        # --- BELGEE ---
        {
            "brand": "BELGEE",
            "desc": "Один из лидеров продаж в масс-маркет и кроссоверном сегменте РФ. Высокая надёжность проверенной платформы Geely, локализованная сборка и максимальная субсидированная поддержка СберАвто.",
            "cards": [
                {
                    "title": "Belgee X50+, 2026",
                    "badge": "Хит продаж",
                    "mods": "1.5T 2WD (150 л.с.) • 7DCT",
                    "c1_name": "Active 1.5 7DCT", "c1_disc": "скидка 90 000 ₽", "c1_rrc": "2 319 990 ₽",
                    "c2_name": "Style 1.5 7DCT [Хит]", "c2_disc": "скидка 90 000 ₽", "c2_rrc": "2 509 990 ₽",
                    "price_from": "от 2 229 990 ₽",
                    "price_note": "цена указана за Active 1.5 7DCT (2 319 990 − 90 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/belgee/x50-plus"
                },
                {
                    "title": "Belgee X70, 2026",
                    "badge": "Семейный / 4WD",
                    "mods": "1.5T 2WD (6AT) • 1.5T 4WD (7DCT)",
                    "c1_name": "Active 1.5 6AT 2WD", "c1_disc": "скидка 495 000 ₽", "c1_rrc": "2 825 990 ₽",
                    "c2_name": "Prestige+ 1.5 7DCT 4WD [Хит]", "c2_disc": "скидка 594 000 ₽", "c2_rrc": "3 426 190 ₽",
                    "price_from": "от 2 330 990 ₽",
                    "price_note": "цена указана за Active 1.5 6AT 2WD (2 825 990 − 495 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/belgee/x70"
                },
                {
                    "title": "Belgee S50, 2026",
                    "badge": "Седан",
                    "mods": "1.5 MT (122 л.с.) • 1.5 6AT",
                    "c1_name": "Active MT", "c1_disc": "скидка 180 000 ₽", "c1_rrc": "1 929 990 ₽",
                    "c2_name": "Prestige AT [Хит]", "c2_disc": "скидка 108 000 ₽", "c2_rrc": "2 345 990 ₽",
                    "price_from": "от 1 749 990 ₽",
                    "price_note": "цена указана за Active MT (1 929 990 − 180 000 ₽)",
                    "cta": "Купить", "link": "https://sberauto.com/cars/belgee/s50"
                }
            ]
        }
    ]

    for b_idx, b_data in enumerate(detailed_cards, start=1):
        brand_name = b_data["brand"]

        p_b_hdr = doc.add_paragraph()
        p_b_hdr.paragraph_format.space_before = Pt(14)
        p_b_hdr.paragraph_format.space_after = Pt(4)
        r_b = p_b_hdr.add_run(f"РАЗДЕЛ {b_idx}. БРЕНД {brand_name}")
        r_b.bold = True
        r_b.font.size = Pt(14)
        r_b.font.color.rgb = c_primary

        p_b_desc = doc.add_paragraph()
        p_b_desc.paragraph_format.space_after = Pt(10)
        r_d = p_b_desc.add_run(b_data["desc"])
        r_d.italic = True
        r_d.font.size = Pt(9.5)
        r_d.font.color.rgb = c_muted

        for c_idx, c in enumerate(b_data["cards"], start=1):
            t_card = doc.add_table(rows=8, cols=2)
            t_card.alignment = WD_TABLE_ALIGNMENT.CENTER
            set_table_borders(t_card, color="E2E8F0", sz="4")

            # Card Header row (spanning 2 columns)
            hdr_cell = t_card.rows[0].cells[0]
            hdr_cell.merge(t_card.rows[0].cells[1])
            set_cell_background(hdr_cell, "F1F5F9")
            set_cell_margins(hdr_cell, top=100, bottom=100, left=140, right=140)
            p_c_hdr = hdr_cell.paragraphs[0]
            p_c_hdr.paragraph_format.space_after = Pt(0)
            r_c_t = p_c_hdr.add_run(f"Карточка {b_idx}.{c_idx}: {c['title']}  ")
            r_c_t.bold = True
            r_c_t.font.size = Pt(11)
            r_c_t.font.color.rgb = c_dark

            r_c_badge = p_c_hdr.add_run(f"[{c['badge']}]")
            r_c_badge.bold = True
            r_c_badge.font.size = Pt(9.5)
            r_c_badge.font.color.rgb = c_primary

            fields = [
                ("Модификации (теги):", c['mods']),
                ("Комплектация 1 (базовая):", f"{c['c1_name']}  —  {c['c1_disc']} (РРЦ {c['c1_rrc']})"),
                ("Комплектация 2 (топовая):", f"{c['c2_name']}  —  {c['c2_disc']} (РРЦ {c['c2_rrc']})"),
                ("Цена входа «от»:", c['price_from']),
                ("Подпись под ценой:", c['price_note']),
                ("Кнопка действия (CTA):", f"{c['cta']}  [Единственная активная кнопка]"),
                ("Ссылка перехода:", c['link'])
            ]

            for row_idx, (f_name, f_val) in enumerate(fields, start=1):
                row = t_card.rows[row_idx]

                # Left cell (Label)
                c_lbl = row.cells[0]
                set_cell_background(c_lbl, "FAFAFA")
                set_cell_margins(c_lbl, top=70, bottom=70, left=140, right=100)
                p_l = c_lbl.paragraphs[0]
                p_l.paragraph_format.space_after = Pt(0)
                r_l = p_l.add_run(f_name)
                r_l.bold = True
                r_l.font.size = Pt(9)
                r_l.font.color.rgb = c_muted

                # Right cell (Value)
                c_val = row.cells[1]
                set_cell_background(c_val, "FFFFFF")
                set_cell_margins(c_val, top=70, bottom=70, left=140, right=140)
                p_v = c_val.paragraphs[0]
                p_v.paragraph_format.space_after = Pt(0)
                r_v = p_v.add_run(f_val)
                r_v.font.size = Pt(9.5)

                if f_name.startswith("Цена"):
                    r_v.bold = True
                    r_v.font.size = Pt(11)
                    r_v.font.color.rgb = c_dark
                elif "скидка" in f_val.lower() or "ррц" in f_val.lower():
                    r_v.bold = True
                elif f_name.startswith("Кнопка"):
                    r_v.bold = True
                    r_v.font.color.rgb = c_primary

            doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Save to all designated locations
    out_paths = [
        "/Users/vaceslavgamaunov/Downloads/Текстовый_бриф_карточки_витрины_Вариант_2_1 (1).docx",
        "/Users/vaceslavgamaunov/Downloads/Текстовый_бриф_карточки_витрины_Вариант_2_1.docx",
        "/Users/vaceslavgamaunov/Downloads/Текстовый_бриф_карточки_витрины_Вариант_2.docx",
        "/Users/vaceslavgamaunov/Downloads/Текстовый_бриф_карточки_витрины_Вариант_2 (1).docx",
        "/Users/vaceslavgamaunov/Downloads/СберАвто_Редизайн_Вариант_2/Текстовый_бриф_карточки_витрины_Вариант_2.docx",
        "/Users/vaceslavgamaunov/Desktop/Текстовый_бриф_карточки_витрины_Вариант_2_1 (1).docx"
    ]

    for p in out_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        doc.save(p)
        print(f"Successfully saved: {p}")

if __name__ == "__main__":
    create_document()
