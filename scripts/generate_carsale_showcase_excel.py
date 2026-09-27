import os
import re
import json
from collections import defaultdict, OrderedDict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# 1. Paths
html_path = '/Users/vaceslavgamaunov/Downloads/Новые авто.html'
data_json_path = '/Users/vaceslavgamaunov/Desktop/Dashboard_usualy/otchet-parser/data.json'
output_desktop = '/Users/vaceslavgamaunov/Desktop/Ранжирование_автомобилей_витрины_СберАвто_Carsale.xlsx'
output_downloads = '/Users/vaceslavgamaunov/Downloads/Ранжирование_автомобилей_витрины_СберАвто_Carsale.xlsx'

print("[*] 1. Парсинг живой витрины https://appsb.sberauto.com/carsale ...")
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

pattern = re.compile(r'<a[^>]+data-testid=[\"\']CarsPage\.List\.MiniAutoCard\.([^\"\']+)[\"\'][^>]*href=[\"\']([^\"\']+)[\"\'][^>]*>(.*?)</a>', re.DOTALL)
matches = pattern.findall(html)
print(f"[*] Найдено карточек на витрине: {len(matches)}")

all_cards = []
for idx, (testid, href, inner) in enumerate(matches, 1):
    clean = re.sub(r'<[^>]+>', '\n', inner)
    lines = [l.strip().replace('&nbsp;', ' ') for l in clean.split('\n') if l.strip()]
    m_name = testid.rsplit('.', 1)[0]
    
    price = None
    price_str = ''
    discount = ''
    dealers = ''
    specs = ''
    for l in lines:
        if 'Скидка' in l: 
            discount = l
        elif '₽' in l and not price:
            p_clean = re.sub(r'[^\d]', '', l)
            if p_clean and int(p_clean) > 500000:
                price = int(p_clean)
                price_str = l
        elif 'авто от' in l: 
            dealers = l
        elif any(k in l for k in ['л,', 'кВт,', 'Механика', 'Автомат', 'Робот', 'Вариатор']): 
            specs = l
            
    all_cards.append({
        'pos': idx,
        'name': m_name,
        'testid': testid,
        'href': href,
        'price': price,
        'price_str': price_str,
        'discount': discount,
        'dealers': dealers,
        'specs': specs
    })

# 2. Family categorizer function
def get_card_family(name):
    n = name.upper()
    if 'GRANTA' in n: return 'LADA Granta'
    if 'VESTA' in n: return 'LADA Vesta'
    if 'NIVA TRAVEL' in n: return 'LADA Niva Travel'
    if 'NIVA LEGEND' in n: return 'LADA Niva Legend'
    if 'NIVA' in n: return 'LADA Niva (Legend / Travel)'
    if 'LARGUS' in n: return 'LADA Largus'
    if 'ISKRA' in n: return 'LADA Iskra'
    if 'AURA' in n: return 'LADA Aura'
    if 'DASHING' in n: return 'Jetour Dashing'
    if 'X70' in n: return 'Jetour X70 PLUS'
    if 'X90' in n: return 'Jetour X90 PLUS'
    if 'T1' in n or 'Т1' in n: return 'Jetour T1'
    if 'T2' in n or 'Т2' in n: return 'Jetour T2'
    if 'SOUEAST S06' in n or 'S06' in n: return 'Soueast S06'
    if 'SOUEAST S07' in n or 'S07' in n: return 'Soueast S07'
    if 'GS8' in n: return 'GAC GS8'
    if 'GS4' in n: return 'GAC GS4'
    if 'GS3' in n: return 'GAC GS3'
    if 'EMPOW' in n: return 'GAC Empow'
    if 'AION' in n: return 'GAC Aion V'
    if 'M8' in n: return 'GAC M8'
    if 'S7' in n: return 'GAC S7'
    if 'S9' in n: return 'GAC S9'
    if 'JOLION' in n: return 'Haval Jolion'
    if 'M6' in n: return 'Haval M6'
    if 'H3' in n: return 'Haval H3'
    if 'H5' in n: return 'Haval H5'
    if 'H7' in n: return 'Haval H7'
    if 'H9' in n: return 'Haval H9'
    if 'F7X' in n: return 'Haval F7x'
    if 'F7' in n: return 'Haval F7'
    if 'DARGO' in n: return 'Haval Dargo'
    if 'SOLARIS HC' in n: return 'Solaris HC'
    if 'SOLARIS KRX' in n: return 'Solaris KRX'
    if 'SOLARIS KRS' in n: return 'Solaris KRS'
    if 'MONJARO' in n: return 'Geely Monjaro'
    if 'COOLRAY' in n: return 'Geely Coolray'
    if 'CITYRAY' in n: return 'Geely Cityray'
    if 'ATLAS' in n: return 'Geely Atlas'
    if 'PREFACE' in n: return 'Geely Preface'
    if 'OKAVANGO' in n: return 'Geely Okavango'
    if 'EX5' in n: return 'Geely EX5'
    if 'BELGEE X50' in n or 'X50+' in n: return 'Belgee X50+'
    if 'BELGEE X70' in n or 'Х70' in n: return 'Belgee X70'
    if 'BELGEE S50' in n or 'S50' in n: return 'Belgee S50'
    if 'TENET T4L' in n: return 'Tenet T4L'
    if 'TENET T4' in n: return 'Tenet T4'
    if 'TENET T7' in n: return 'Tenet T7'
    if 'TENET T8' in n: return 'Tenet T8'
    if 'TENET T9' in n: return 'Tenet T9'
    if 'TENET A8' in n: return 'Tenet A8'
    if 'JELAND J6' in n: return 'Jeland J6'
    if 'JELAND J7' in n: return 'Jeland J7'
    if 'JAECOO J6' in n: return 'Jaecoo J6'
    if 'JAECOO J7' in n: return 'Jaecoo J7'
    if 'JAECOO J8' in n: return 'Jaecoo J8'
    if 'OMODA C5' in n: return 'Omoda C5'
    if 'OMODA C7' in n: return 'Omoda C7'
    if 'UNI-S' in n: return 'Changan UNI-S'
    if 'UNI-V' in n: return 'Changan UNI-V'
    if 'UNI-K' in n: return 'Changan UNI-K'
    if 'UNI-T' in n: return 'Changan UNI-T'
    if 'CS35' in n: return 'Changan CS35PLUS / CS35MAX'
    if 'CS75' in n: return 'Changan CS75PLUS / CS75PRO'
    if 'CS95' in n: return 'Changan CS95'
    if 'ALSVIN' in n: return 'Changan Alsvin'
    if 'EADO' in n: return 'Changan Eado Plus'
    if 'HUNTER' in n: return 'Changan Hunter Plus'
    if 'DEEPAL' in n or 'G318' in n: return 'Changan Deepal G318'
    if 'МОСКВИЧ 3' in n: return 'Москвич 3'
    if 'МОСКВИЧ 8' in n: return 'Москвич 8'
    if 'М70' in n: return 'Москвич М70'
    if 'М90' in n: return 'Москвич М90'
    if 'MAZDA' in n: return 'Mazda CX-5'
    if 'TOYOTA' in n or 'CAMRY' in n: return 'Toyota Camry'
    if 'SANTA FE' in n or 'HYUNDAI' in n: return 'Hyundai Santa Fe'
    return name

for c in all_cards:
    c['family'] = get_card_family(c['name'])

# 3. Load sales DB
print("[*] 2. Загрузка базы сделок data.json...")
with open(data_json_path, 'r', encoding='utf-8') as f:
    d = json.load(f)
sys_db = d['sys_db']
retail_b2c = {'ФДЦ', 'ФДЦ+ГП', 'Online', 'Передача лида'}

def match_deal(b_raw, m_raw):
    b = str(b_raw).strip().upper()
    m = str(m_raw).strip().upper()
    
    if 'JETOUR' in b:
        if 'DASH' in m: return 'Jetour Dashing'
        if any(x in m for x in ['T1', 'Т1', 'T-1', 'TI']): return 'Jetour T1'
        if any(x in m for x in ['T2', 'Т2', 'T-2']): return 'Jetour T2'
        if any(x in m for x in ['X70', 'Х70', '70+', '70 +']): return 'Jetour X70 PLUS'
        if any(x in m for x in ['X90', 'Х90']): return 'Jetour X90 PLUS'
        return 'Jetour Другое'
        
    if 'LADA' in b or 'ВАЗ' in b:
        if 'GRANT' in m or 'GANT' in m: return 'LADA Granta'
        if 'VEST' in m or 'GFL' in m: return 'LADA Vesta'
        if 'TRAVEL' in m or 'TREVEL' in m: return 'LADA Niva Travel'
        if 'LEGEND' in m: return 'LADA Niva Legend'
        if any(x in m for x in ['NIVA', 'НИВА', '4X4']): return 'LADA Niva Legend'
        if 'LARG' in m: return 'LADA Largus'
        if 'ISKR' in m: return 'LADA Iskra'
        if 'AURA' in m: return 'LADA Aura'
        return 'LADA Другое'

    if 'SOUEAST' in b or 'SOUEAS' in b:
        if '06' in m: return 'Soueast S06'
        if '07' in m or 'С07' in m: return 'Soueast S07'
        return 'Soueast Другое'

    if 'GAC' in b:
        if 'GS8' in m or 'GS 8' in m or 'CS8' in m: return 'GAC GS8'
        if 'GS4' in m or 'GS 4' in m or 'CS4' in m: return 'GAC GS4'
        if 'M8' in m or 'М8' in m: return 'GAC M8'
        if 'S7' in m: return 'GAC S7'
        if 'S9' in m or 'GS9' in m: return 'GAC S9'
        if 'GS3' in m: return 'GAC GS3'
        if 'EMPOW' in m: return 'GAC Empow'
        if 'AION' in m: return 'GAC Aion V'
        return 'GAC Другое'

    if 'HAVAL' in b or 'ХАВЕЙЛ' in b or 'ХАВАЛ' in b:
        if 'JOLION' in m or 'ДЖОЛИОН' in m: return 'Haval Jolion'
        if 'M6' in m or 'М6' in m: return 'Haval M6'
        if 'F7X' in m: return 'Haval F7x'
        if 'F7' in m: return 'Haval F7'
        if 'DARGO' in m or 'ДАРГО' in m: return 'Haval Dargo'
        if 'H3' in m: return 'Haval H3'
        if 'H5' in m: return 'Haval H5'
        if 'H7' in m: return 'Haval H7'
        if 'H9' in m: return 'Haval H9'
        return 'Haval Другое'

    if 'GEELY' in b or 'ДЖИЛИ' in b:
        if 'MONJARO' in m or 'МАНДЖАРО' in m: return 'Geely Monjaro'
        if 'CITYRAY' in m or 'СИТИРЕЙ' in m: return 'Geely Cityray'
        if 'COOLRAY' in m or 'КУЛРЕЙ' in m: return 'Geely Coolray'
        if 'ATLAS' in m or 'АТЛАС' in m: return 'Geely Atlas'
        if 'PREFACE' in m or 'ПРЕФЕЙС' in m: return 'Geely Preface'
        if 'OKAVANGO' in m or 'ОКАВАНГО' in m: return 'Geely Okavango'
        if 'EX5' in m: return 'Geely EX5'
        return 'Geely Другое'

    if 'BELGEE' in b or 'БЕЛДЖИ' in b:
        if '50' in m and 'S50' not in m: return 'Belgee X50+'
        if '70' in m: return 'Belgee X70'
        if 'S50' in m: return 'Belgee S50'
        return 'Belgee Другое'

    if 'SOLARIS' in b or 'СОЛЯРИС' in b:
        if 'HC' in m or 'НС' in m: return 'Solaris HC'
        if 'KRX' in m: return 'Solaris KRX'
        if 'KRS' in m: return 'Solaris KRS'
        return 'Solaris Другое'

    if 'CHANGAN' in b or 'ЧАНГАН' in b:
        if 'UNI-S' in m or 'UNI S' in m or 'CS55' in m: return 'Changan UNI-S'
        if 'UNI-V' in m or 'UNI V' in m: return 'Changan UNI-V'
        if 'UNI-K' in m or 'UNI K' in m: return 'Changan UNI-K'
        if 'UNI-T' in m: return 'Changan UNI-T'
        if '35' in m: return 'Changan CS35PLUS / CS35MAX'
        if '75' in m: return 'Changan CS75PLUS / CS75PRO'
        if '95' in m: return 'Changan CS95'
        if 'ALSVIN' in m or 'АЛСВИН' in m: return 'Changan Alsvin'
        if 'EADO' in m or 'ИДО' in m: return 'Changan Eado Plus'
        if 'HUNTER' in m or 'ХАНТЕР' in m: return 'Changan Hunter Plus'
        if 'DEEPAL' in m or 'G318' in m: return 'Changan Deepal G318'
        return 'Changan Другое'

    if 'TENET' in b:
        if 'T4L' in m or 'Т4L' in m or 'T4 L' in m: return 'Tenet T4L'
        if 'T4' in m or 'Т4' in m: return 'Tenet T4'
        if 'T7' in m or 'Т7' in m: return 'Tenet T7'
        if 'T8' in m or 'Т8' in m: return 'Tenet T8'
        if 'T9' in m or 'Т9' in m: return 'Tenet T9'
        if 'A8' in m or 'А8' in m: return 'Tenet A8'
        return 'Tenet Другое'

    if 'JELAND' in b:
        if 'J6' in m: return 'Jeland J6'
        if 'J7' in m: return 'Jeland J7'
        return 'Jeland Другое'
    if 'JAECOO' in b:
        if 'J6' in m: return 'Jaecoo J6'
        if 'J7' in m: return 'Jaecoo J7'
        if 'J8' in m: return 'Jaecoo J8'
        return 'Jaecoo Другое'

    if 'OMODA' in b:
        if 'C5' in m: return 'Omoda C5'
        if 'C7' in m: return 'Omoda C7'
        return 'Omoda Другое'

    if 'МОСКВИЧ' in b or 'MOSKVICH' in b:
        if '3' in m: return 'Москвич 3'
        if '8' in m: return 'Москвич 8'
        if '70' in m or 'М70' in m: return 'Москвич М70'
        if '90' in m or 'М90' in m: return 'Москвич М90'
        return 'Москвич Другое'

    if 'TOYOTA' in b or 'ТОЙОТА' in b: return 'Toyota Camry'
    if 'MAZDA' in b or 'МАЗДА' in b: return 'Mazda CX-5'
    if 'HYUNDAI' in b or 'ХЕНДЭ' in b or 'ХЮНДАЙ' in b: return 'Hyundai Santa Fe'

    return 'Прочее'

fam_stats = defaultdict(lambda: {
    'aug_tot': 0, 'aug_ret': 0, 
    'sep_tot': 0, 'sep_ret': 0, 
    'rev': 0.0, 'prices': []
})

for r in sys_db:
    if r.get('SaleQty', 0) != 1: continue
    m = r.get('SaleMonth')
    if m not in ('2026-08', '2026-09'): continue
    b = str(r.get('Brand') or '').strip()
    md = str(r.get('Model') or '').strip()
    p = r.get('Price', 0) or 0
    rev = r.get('Revenue', 0) or 0
    is_ret = r.get('B2C') in retail_b2c
    
    fam = match_deal(b, md)
    if m == '2026-08':
        fam_stats[fam]['aug_tot'] += 1
        if is_ret: fam_stats[fam]['aug_ret'] += 1
    else:
        fam_stats[fam]['sep_tot'] += 1
        if is_ret: fam_stats[fam]['sep_ret'] += 1
    fam_stats[fam]['rev'] += rev
    if p > 0: fam_stats[fam]['prices'].append(p)

# All unique families present on showcase
showcase_families_set = sorted(list(set(c['family'] for c in all_cards)))

family_ranking = []
for fam in showcase_families_set:
    s = fam_stats[fam]
    tot = s['aug_tot'] + s['sep_tot']
    ret = s['aug_ret'] + s['sep_ret']
    rev = s['rev']
    avg_price = sum(s['prices']) / len(s['prices']) if s['prices'] else 0
    
    # get min showcase price for this family
    showcase_prices = [c['price'] for c in all_cards if c['family'] == fam and c['price']]
    min_showcase_price = min(showcase_prices) if showcase_prices else avg_price
    
    # Tier classification
    if tot >= 100:
        tier = "Tier 1: Суперхиты (Топ витрины)"
        tier_code = 1
    elif tot >= 20:
        tier = "Tier 2: Высокий спрос (2-й эшелон)"
        tier_code = 2
    elif tot >= 5:
        tier = "Tier 3: Средний темп продаж"
        tier_code = 3
    elif tot >= 1:
        tier = "Tier 4: Единичные продажи"
        tier_code = 4
    else:
        tier = "Tier 5: 0 продаж (Самый низ витрины)"
        tier_code = 5
        
    family_ranking.append({
        'family': fam,
        'tier': tier,
        'tier_code': tier_code,
        'aug_tot': s['aug_tot'],
        'aug_ret': s['aug_ret'],
        'sep_tot': s['sep_tot'],
        'sep_ret': s['sep_ret'],
        'tot': tot,
        'ret': ret,
        'ret_share': (ret / tot) if tot > 0 else 0.0,
        'min_showcase_price': min_showcase_price,
        'avg_price': avg_price,
        'rev': rev,
        'cards_count': sum(1 for c in all_cards if c['family'] == fam)
    })

family_ranking.sort(key=lambda x: (x['tot'], x['ret'], x['rev']), reverse=True)

# Assign recommended rank
for idx, item in enumerate(family_ranking, 1):
    item['rank'] = idx

# Map rank back to cards
family_to_rank = {item['family']: item['rank'] for item in family_ranking}
for c in all_cards:
    c['rec_rank'] = family_to_rank.get(c['family'], 999)

print(f"[*] Сформирован рейтинг из {len(family_ranking)} модельных семейств.")

# 4. Create Excel Workbook
print("[*] 3. Генерация профессиональной Excel книги...")
wb = openpyxl.Workbook()

# Style Palette
font_name = 'Arial'
font_title = Font(name=font_name, size=15, bold=True, color='1E4620')
font_subtitle = Font(name=font_name, size=9.5, italic=True, color='555555')
font_sec_hdr = Font(name=font_name, size=11, bold=True, color='1E4620')
font_tbl_hdr = Font(name=font_name, size=9.5, bold=True, color='FFFFFF')
font_bold = Font(name=font_name, size=9.5, bold=True)
font_regular = Font(name=font_name, size=9)
font_kpi_num = Font(name=font_name, size=14, bold=True, color='1E4620')

fill_dark_green = PatternFill(start_color='1E4620', end_color='1E4620', fill_type='solid')
fill_med_green = PatternFill(start_color='2E6930', end_color='2E6930', fill_type='solid')
fill_light_green = PatternFill(start_color='EAF5EA', end_color='EAF5EA', fill_type='solid')
fill_tier1 = PatternFill(start_color='E2F0D9', end_color='E2F0D9', fill_type='solid')
fill_tier2 = PatternFill(start_color='EAF2F8', end_color='EAF2F8', fill_type='solid')
fill_tier3 = PatternFill(start_color='FFF9E6', end_color='FFF9E6', fill_type='solid')
fill_tier4 = PatternFill(start_color='FDF2E9', end_color='FDF2E9', fill_type='solid')
fill_tier5 = PatternFill(start_color='F9EBEA', end_color='F9EBEA', fill_type='solid')
fill_total = PatternFill(start_color='DCEBDC', end_color='DCEBDC', fill_type='solid')
fill_zebra = PatternFill(start_color='FBFDFB', end_color='FBFDFB', fill_type='solid')

border_thin = Border(
    left=Side(style='thin', color='DDDDDD'), right=Side(style='thin', color='DDDDDD'),
    top=Side(style='thin', color='DDDDDD'), bottom=Side(style='thin', color='DDDDDD')
)
border_hdr = Border(
    left=Side(style='thin', color='1E4620'), right=Side(style='thin', color='1E4620'),
    top=Side(style='thin', color='1E4620'), bottom=Side(style='medium', color='0F2A12')
)
border_total = Border(
    left=Side(style='thin', color='999999'), right=Side(style='thin', color='999999'),
    top=Side(style='medium', color='1E4620'), bottom=Side(style='double', color='1E4620')
)

align_center = Alignment(vertical='center', horizontal='center')
align_left = Alignment(vertical='center', horizontal='left')
align_right = Alignment(vertical='center', horizontal='right')
align_hdr = Alignment(vertical='center', horizontal='center', wrap_text=True)

# ==============================================================================
# SHEET 1: Ранжирование витрины Carsale
# ==============================================================================
ws1 = wb.active
ws1.title = "Ранжирование витрины Carsale"
ws1.views.sheetView[0].showGridLines = True

# Title block
ws1.merge_cells("A1:N1")
ws1["A1"] = "СберАвто Carsale: Ранжирование автомобилей витрины по фактическим продажам"
ws1["A1"].font = font_title
ws1["A1"].alignment = align_left
ws1.row_dimensions[1].height = 32

ws1.merge_cells("A2:N2")
ws1["A2"] = "База сделок: Август и Сентябрь 2026 года (срез на 23.09.2026) | Живой каталог витрины: https://appsb.sberauto.com/carsale (148 карточек, 75 линеек)"
ws1["A2"].font = font_subtitle
ws1["A2"].alignment = align_left
ws1.row_dimensions[2].height = 20

# KPI Summary block
ws1.merge_cells("A4:C4")
ws1["A4"] = "Всего продаж на платформе:"
ws1["A4"].font = font_regular
ws1.merge_cells("A5:C5")
ws1["A5"] = "2 592 шт."
ws1["A5"].font = font_kpi_num

ws1.merge_cells("E4:G4")
ws1["E4"] = "Чистая розница B2C:"
ws1["E4"].font = font_regular
ws1.merge_cells("E5:G5")
ws1["E5"] = "563 шт. (21.7%)"
ws1["E5"].font = font_kpi_num

ws1.merge_cells("I4:K4")
ws1["I4"] = "Карточек в каталоге:"
ws1["I4"].font = font_regular
ws1.merge_cells("I5:K5")
ws1["I5"] = "148 предложений"
ws1["I5"].font = font_kpi_num

ws1.merge_cells("M4:N4")
ws1["M4"] = "Моделей без продаж:"
ws1["M4"].font = font_regular
ws1.merge_cells("M5:N5")
ws1["M5"] = "22 модели (29.3%)"
ws1["M5"].font = font_kpi_num

ws1.row_dimensions[4].height = 18
ws1.row_dimensions[5].height = 26

# Table Headers
headers_s1 = [
    "Ранг (Витрина)",
    "Марка и модель (Семейство)",
    "Блок ранжирования (Тир)",
    "Карточек в каталоге",
    "Август (Все)",
    "Август (Розница)",
    "Сентябрь (Все)",
    "Сентябрь (Розница)",
    "ИТОГО Продаж",
    "ИТОГО Розница",
    "Доля розницы",
    "Стартовая цена на витрине",
    "Ср. цена авто в сделках",
    "Выручка (КВ без НДС)"
]

row_start = 7
ws1.row_dimensions[row_start].height = 36

for col_idx, h_text in enumerate(headers_s1, 1):
    cell = ws1.cell(row=row_start, column=col_idx)
    cell.value = h_text
    cell.font = font_tbl_hdr
    cell.fill = fill_dark_green
    cell.alignment = align_hdr
    cell.border = border_hdr

row_curr = row_start + 1
for r_item in family_ranking:
    ws1.row_dimensions[row_curr].height = 22
    
    # Fill based on tier
    t_code = r_item['tier_code']
    t_fill = fill_tier1 if t_code == 1 else (fill_tier2 if t_code == 2 else (fill_tier3 if t_code == 3 else (fill_tier4 if t_code == 4 else fill_tier5)))
    
    vals = [
        r_item['rank'],
        r_item['family'],
        r_item['tier'],
        r_item['cards_count'],
        r_item['aug_tot'],
        r_item['aug_ret'],
        r_item['sep_tot'],
        r_item['sep_ret'],
        r_item['tot'],
        r_item['ret'],
        r_item['ret_share'],
        r_item['min_showcase_price'] if r_item['min_showcase_price'] > 0 else "-",
        r_item['avg_price'] if r_item['avg_price'] > 0 else "-",
        r_item['rev']
    ]
    
    for col_idx, val in enumerate(vals, 1):
        cell = ws1.cell(row=row_curr, column=col_idx)
        cell.value = val
        cell.border = border_thin
        
        # formatting
        if col_idx == 1:
            cell.alignment = align_center
            cell.font = font_bold
            cell.fill = t_fill
        elif col_idx == 2:
            cell.alignment = align_left
            cell.font = font_bold if t_code in (1, 2) else font_regular
        elif col_idx == 3:
            cell.alignment = align_left
            cell.font = font_regular
            cell.fill = t_fill
        elif col_idx == 4:
            cell.alignment = align_center
            cell.font = font_regular
            cell.number_format = '#,##0'
        elif 5 <= col_idx <= 10:
            cell.alignment = align_right
            cell.font = font_bold if col_idx in (9, 10) else font_regular
            cell.number_format = '#,##0'
        elif col_idx == 11:
            cell.alignment = align_center
            cell.font = font_bold if r_item['ret_share'] > 0.5 else font_regular
            cell.number_format = '0.0%'
        elif col_idx in (12, 13, 14):
            cell.alignment = align_right
            cell.font = font_regular
            if isinstance(val, (int, float)):
                cell.number_format = '#,##0 "₽"'
                
    row_curr += 1

# Total Row
ws1.row_dimensions[row_curr].height = 26
ws1.cell(row=row_curr, column=1).value = ""
ws1.cell(row=row_curr, column=2).value = "ИТОГО ПО ВСЕМ МОДЕЛЯМ"
ws1.cell(row=row_curr, column=2).font = font_bold
ws1.cell(row=row_curr, column=3).value = f"75 моделей ({len(all_cards)} карточек)"
ws1.cell(row=row_curr, column=3).font = font_regular

ws1.cell(row=row_curr, column=4).value = f"=SUM(D{row_start+1}:D{row_curr-1})"
ws1.cell(row=row_curr, column=5).value = f"=SUM(E{row_start+1}:E{row_curr-1})"
ws1.cell(row=row_curr, column=6).value = f"=SUM(F{row_start+1}:F{row_curr-1})"
ws1.cell(row=row_curr, column=7).value = f"=SUM(G{row_start+1}:G{row_curr-1})"
ws1.cell(row=row_curr, column=8).value = f"=SUM(H{row_start+1}:H{row_curr-1})"
ws1.cell(row=row_curr, column=9).value = f"=SUM(I{row_start+1}:I{row_curr-1})"
ws1.cell(row=row_curr, column=10).value = f"=SUM(J{row_start+1}:J{row_curr-1})"
ws1.cell(row=row_curr, column=11).value = f"=J{row_curr}/I{row_curr}"
ws1.cell(row=row_curr, column=12).value = "-"
ws1.cell(row=row_curr, column=13).value = "-"
ws1.cell(row=row_curr, column=14).value = f"=SUM(N{row_start+1}:N{row_curr-1})"

for c_idx in range(1, 15):
    c_cell = ws1.cell(row=row_curr, column=c_idx)
    c_cell.font = font_bold
    c_cell.fill = fill_total
    c_cell.border = border_total
    if 4 <= c_idx <= 10:
        c_cell.alignment = align_right
        c_cell.number_format = '#,##0'
    elif c_idx == 11:
        c_cell.alignment = align_center
        c_cell.number_format = '0.0%'
    elif c_idx == 14:
        c_cell.alignment = align_right
        c_cell.number_format = '#,##0 "₽"'

ws1.freeze_panes = "A8"

# ==============================================================================
# SHEET 2: Все 148 карточек каталога
# ==============================================================================
ws2 = wb.create_sheet(title="Все 148 карточек каталога")
ws2.views.sheetView[0].showGridLines = True

ws2.merge_cells("A1:K1")
ws2["A1"] = "СберАвто Carsale: Полная спецификация всех 148 карточек каталога и рекомендованная позиция"
ws2["A1"].font = font_title
ws2["A1"].alignment = align_left
ws2.row_dimensions[1].height = 32

ws2.merge_cells("A2:K2")
ws2["A2"] = "Сравнение текущего порядка карточек на сайте с рекомендуемым рангом по продажам за август-сентябрь 2026"
ws2["A2"].font = font_subtitle
ws2["A2"].alignment = align_left
ws2.row_dimensions[2].height = 20

headers_s2 = [
    "Текущая позиция на сайте",
    "Рекомендуемая позиция (Ранг)",
    "Название карточки на сайте",
    "Семейство модели",
    "Тир витрины",
    "Стартовая цена на сайте",
    "Скидка на сайте",
    "Модификация / Двигатель",
    "Предложений от дилеров",
    "Продажи семейства (Всего)",
    "Продажи семейства (Розница)"
]

ws2.row_dimensions[4].height = 34
for col_idx, h_text in enumerate(headers_s2, 1):
    cell = ws2.cell(row=4, column=col_idx)
    cell.value = h_text
    cell.font = font_tbl_hdr
    cell.fill = fill_med_green
    cell.alignment = align_hdr
    cell.border = border_hdr

row_c = 5
for card in all_cards:
    ws2.row_dimensions[row_c].height = 21
    fam = card['family']
    f_info = next((item for item in family_ranking if item['family'] == fam), None)
    
    vals2 = [
        card['pos'],
        card['rec_rank'],
        card['name'],
        fam,
        f_info['tier'] if f_info else "-",
        card['price'] if card['price'] else card['price_str'],
        card['discount'] if card['discount'] else "Без спецскидки",
        card['specs'] if card['specs'] else "-",
        card['dealers'] if card['dealers'] else "1 авто",
        f_info['tot'] if f_info else 0,
        f_info['ret'] if f_info else 0
    ]
    
    t_code = f_info['tier_code'] if f_info else 5
    t_fill = fill_tier1 if t_code == 1 else (fill_tier2 if t_code == 2 else (fill_tier3 if t_code == 3 else (fill_tier4 if t_code == 4 else fill_tier5)))
    
    for col_idx, val in enumerate(vals2, 1):
        cell = ws2.cell(row=row_c, column=col_idx)
        cell.value = val
        cell.border = border_thin
        
        if col_idx in (1, 2):
            cell.alignment = align_center
            cell.font = font_bold
            if col_idx == 2: cell.fill = t_fill
        elif col_idx in (3, 4):
            cell.alignment = align_left
            cell.font = font_bold if col_idx == 4 else font_regular
        elif col_idx == 5:
            cell.alignment = align_left
            cell.font = font_regular
            cell.fill = t_fill
        elif col_idx == 6:
            cell.alignment = align_right
            if isinstance(val, (int, float)): cell.number_format = '#,##0 "₽"'
        elif col_idx in (7, 8, 9):
            cell.alignment = align_left
            cell.font = font_regular
        elif col_idx in (10, 11):
            cell.alignment = align_right
            cell.font = font_bold if col_idx == 10 else font_regular
            cell.number_format = '#,##0'
            
    row_c += 1

ws2.freeze_panes = "A5"

# ==============================================================================
# SHEET 3: Детализация всплеска розницы (22-23.09)
# ==============================================================================
ws3 = wb.create_sheet(title="Всплеск розницы (22.09)")
ws3.views.sheetView[0].showGridLines = True

ws3.merge_cells("A1:I1")
ws3["A1"] = "Детализация всплеска розничных сделок: 39 сделок (22–23 сентября 2026)"
ws3["A1"].font = font_title
ws3["A1"].alignment = align_left
ws3.row_dimensions[1].height = 32

ws3.merge_cells("A2:I2")
ws3["A2"] = "Пакетное закрытие сделок через федеральную партнерскую сеть дилеров СберАвто (Online / Сделка без кнопки)"
ws3["A2"].font = font_subtitle
ws3["A2"].alignment = align_left
ws3.row_dimensions[2].height = 20

headers_s3 = [
    "№",
    "ID клиента",
    "Марка",
    "Модель",
    "Партнер / Дилер",
    "Канал сделки",
    "Стоимость ТС",
    "Регион клиента",
    "Ответственный менеджер"
]

ws3.row_dimensions[4].height = 32
for col_idx, h_text in enumerate(headers_s3, 1):
    cell = ws3.cell(row=4, column=col_idx)
    cell.value = h_text
    cell.font = font_tbl_hdr
    cell.fill = fill_dark_green
    cell.alignment = align_hdr
    cell.border = border_hdr

# Load 39 deals
fpath38 = '/Users/vaceslavgamaunov/Desktop/Dashboard_usualy/otchet-parser/raw_data/data (38).xlsx'
fpath37 = '/Users/vaceslavgamaunov/Desktop/Dashboard_usualy/otchet-parser/raw_data/data (37).xlsx'
import pandas as pd
df38 = pd.read_excel(fpath38, skiprows=2)
df37 = pd.read_excel(fpath37, skiprows=2)

df38['date_dt'] = pd.to_datetime(df38['Дата'], errors='coerce')
deals_38 = df38[(df38['date_dt'].dt.strftime('%Y-%m-%d') == '2026-09-22') & (df38['event_name'].str.contains('Сделка', na=False))].copy()
cids = [str(int(c)) for c in deals_38['client_id'].dropna()]
m37 = df37[df37['client_id'].astype(str).isin(cids)]
cid_info = {}
for cid, group in m37.groupby('client_id'):
    brands = [b for b in group['Бренд'].dropna().unique() if str(b).strip()]
    models = [m for m in group['Модель'].dropna().unique() if str(m).strip()]
    regions = [r for r in group['Регион клиента'].dropna().unique() if str(r).strip()]
    cid_info[str(cid)] = {
        'brand': brands[0] if brands else None,
        'model': models[0] if models else None,
        'region': regions[0] if regions else None
    }

row_3 = 5
for idx, (_, r) in enumerate(deals_38.iterrows(), 1):
    ws3.row_dimensions[row_3].height = 21
    cid_str = str(int(r['client_id'])) if pd.notna(r['client_id']) else ''
    info = cid_info.get(cid_str, {})
    brand = r['Бренд'] if pd.notna(r['Бренд']) else (info.get('brand') or 'Не указан')
    model = r['Модель'] if pd.notna(r['Модель']) else (info.get('model') or 'Не указана')
    reg = r['Регион клиента из sber_id'] if pd.notna(r['Регион клиента из sber_id']) else (info.get('region') or 'Не указан')
    partner = str(r['Партнер']) if pd.notna(r['Партнер']) else 'Online партнер'
    price = r['Цена авто'] if pd.notna(r['Цена авто']) else 0
    event = r['event_name']
    resp = r['Ответственный'] if pd.notna(r['Ответственный']) else 'Ответственный не назначен'
    
    vals3 = [
        idx,
        cid_str,
        brand,
        model,
        partner,
        event,
        price,
        reg,
        resp
    ]
    
    for col_idx, val in enumerate(vals3, 1):
        cell = ws3.cell(row=row_3, column=col_idx)
        cell.value = val
        cell.border = border_thin
        
        if col_idx == 1:
            cell.alignment = align_center
            cell.font = font_bold
        elif col_idx in (2, 3, 4):
            cell.alignment = align_center if col_idx == 2 else align_left
            cell.font = font_bold if col_idx == 3 else font_regular
        elif col_idx in (5, 6, 8, 9):
            cell.alignment = align_left
            cell.font = font_regular
        elif col_idx == 7:
            cell.alignment = align_right
            cell.font = font_bold
            cell.number_format = '#,##0 "₽"'
            
    row_3 += 1

# Total for sheet 3
ws3.row_dimensions[row_3].height = 24
ws3.cell(row=row_3, column=1).value = ""
ws3.cell(row=row_3, column=2).value = "ИТОГО"
ws3.cell(row=row_3, column=2).font = font_bold
ws3.cell(row=row_3, column=3).value = f"{len(deals_38)} сделок"
ws3.cell(row=row_3, column=7).value = f"=SUM(G5:G{row_3-1})"

for c_idx in range(1, 10):
    c_cell = ws3.cell(row=row_3, column=c_idx)
    c_cell.font = font_bold
    c_cell.fill = fill_total
    c_cell.border = border_total
    if c_idx == 7:
        c_cell.alignment = align_right
        c_cell.number_format = '#,##0 "₽"'

ws3.freeze_panes = "A5"

# Auto-adjust column widths for all sheets
for ws in [ws1, ws2, ws3]:
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if cell.number_format and '₽' in cell.number_format:
                val_str += '  ₽'
            # don't let merged header blow up width
            if cell.row in (1, 2, 4) and len(val_str) > 40:
                continue
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

# Specific tweaks
ws1.column_dimensions['A'].width = 16
ws1.column_dimensions['B'].width = 30
ws1.column_dimensions['C'].width = 32
ws1.column_dimensions['D'].width = 18
ws1.column_dimensions['K'].width = 14
ws1.column_dimensions['L'].width = 25
ws1.column_dimensions['M'].width = 24
ws1.column_dimensions['N'].width = 22

ws2.column_dimensions['A'].width = 22
ws2.column_dimensions['B'].width = 24
ws2.column_dimensions['C'].width = 34
ws2.column_dimensions['D'].width = 28
ws2.column_dimensions['E'].width = 32
ws2.column_dimensions['F'].width = 22
ws2.column_dimensions['G'].width = 20
ws2.column_dimensions['H'].width = 36

ws3.column_dimensions['A'].width = 8
ws3.column_dimensions['B'].width = 16
ws3.column_dimensions['C'].width = 16
ws3.column_dimensions['D'].width = 20
ws3.column_dimensions['E'].width = 38
ws3.column_dimensions['F'].width = 20
ws3.column_dimensions['G'].width = 20
ws3.column_dimensions['H'].width = 24
ws3.column_dimensions['I'].width = 28

# Save
wb.save(output_desktop)
wb.save(output_downloads)
print(f"[✓] Успешно сохранен файл: {output_desktop}")
print(f"[✓] Успешно сохранен файл: {output_downloads}")
