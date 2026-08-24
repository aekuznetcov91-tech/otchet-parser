import os
import sys
import re
import csv
import json
import datetime
from html.parser import HTMLParser

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'raw_data')
SITE_DIR = os.path.join(PROJECT_ROOT, 'site')
OUTPUT_JSON_SITE = os.path.join(SITE_DIR, 'data.json')
OUTPUT_JSON_ROOT = os.path.join(PROJECT_ROOT, 'data.json')

def clean_key(k):
    if k is None:
        return ""
    return re.sub(r'[^A-ZА-Я0-9]', '', str(k).upper())

def get_exact_val(row, *search_keys):
    row_cleaned = {clean_key(k): v for k, v in row.items()}
    for sk in search_keys:
        c_sk = clean_key(sk)
        if c_sk in row_cleaned:
            return row_cleaned[c_sk]
    return ""

def normalize_brand(tovar_str):
    t = str(tovar_str or "").upper()
    if "DASHING" in t or "X70 PLUS" in t or "JETOUR" in t:
        return "JETOUR"
    if "LADA" in t or "ЛАДА" in t:
        return "LADA"
    if "HAVAL" in t:
        return "HAVAL"
    if "SOLARIS" in t:
        return "SOLARIS"
    if "CHANGAN" in t:
        return "CHANGAN"
    if "G B K" in t or "GEELY" in t or "BELGEE" in t or "KNEWSTAR" in t:
        return "G B K"
    if "SOUEAST" in t:
        return "SOUEAST"
    if "GAC" in t:
        return "GAC"
    if "TENET" in t or "CHERY" in t:
        return "TENET"
    if "HONGQI" in t:
        return "HONGQI"
    if "XCITE" in t:
        return "XCITE"
    if "МОСКВИЧ" in t:
        return "МОСКВИЧ"
    if "OMODA" in t:
        return "OMODA"
    if "KIA" in t:
        return "KIA"
    
    words = re.split(r'[\s,/-]+', t.strip())
    return words[0] if words and words[0] else "НЕИЗВЕСТНЫЙ БРЕНД"

def parse_custom_date(date_value):
    if date_value is None or date_value == "":
        return None
    if isinstance(date_value, (datetime.date, datetime.datetime)):
        return date_value
    
    try:
        num = float(date_value)
        return datetime.date(1899, 12, 30) + datetime.timedelta(days=int(num))
    except (ValueError, TypeError):
        pass

    ds = str(date_value).strip()
    if not ds:
        return None

    date_part = ds.split('T')[0].split(' ')[0]
    
    if '/' in date_part:
        parts = date_part.split('/')
        if len(parts) == 3:
            try:
                m, d, y = int(parts[0]), int(parts[1]), int(parts[2])
                if y < 100: y += 2000
                if m > 12: return datetime.date(y, m, d)
                return datetime.date(y, m, d)
            except ValueError:
                pass

    if '.' in date_part or '-' in date_part:
        sep = '.' if '.' in date_part else '-'
        parts = date_part.split(sep)
        if len(parts) == 3:
            try:
                if len(parts[0]) == 4:
                    return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                y = int(parts[2])
                if y < 100: y += 2000
                return datetime.date(y, int(parts[1]), int(parts[0]))
            except ValueError:
                pass

    try:
        return datetime.datetime.fromisoformat(ds).date()
    except Exception:
        return None

def date_to_excel_serial(d_date):
    if not d_date:
        return 0
    if isinstance(d_date, datetime.datetime):
        d_date = d_date.date()
    return (d_date - datetime.date(1899, 12, 30)).days

class HtmlTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.current_row = []
        self.current_cell = []
        self.in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag in ('td', 'th'):
            self.in_cell = True
            self.current_cell = []
        elif tag == 'tr':
            self.current_row = []

    def handle_endtag(self, tag):
        if tag in ('td', 'th'):
            self.in_cell = False
            self.current_row.append("".join(self.current_cell).strip())
        elif tag == 'tr':
            if any(self.current_row):
                self.rows.append(self.current_row)

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell.append(data)

def extract_rows_from_matrix(matrix):
    if not matrix:
        return []
    header_idx = -1
    for i, row in enumerate(matrix[:25]):
        row_str = clean_key("".join(str(c) for c in row))
        if (
            'ПРЕДПОЛАГАЕМАЯДАТАЗАКРЫТИЯ' in row_str or 
            'EVENTNAME' in row_str or 
            ('БИТРИКС' in row_str and 'ПОЧТА' in row_str) or
            ('СТАДИЯСДЕЛКИ' in row_str and 'ТОВАР' in row_str) or
            ('БИТРИКС' in row_str and 'КАМ' in row_str) or
            ('ДАТА' in row_str and 'ЦЕНААВТО' in row_str) or
            ('CLIENTID' in row_str and 'ПАРТНЕР' in row_str) or
            ('SALEMONTH' in row_str and 'PREPAYMONTH' in row_str)
        ):
            header_idx = i
            break

    if header_idx == -1:
        header_idx = 0

    headers = [str(c).strip() for c in matrix[header_idx]]
    result = []
    for row in matrix[header_idx + 1:]:
        row_dict = {}
        for h_i, h_name in enumerate(headers):
            if h_name:
                val = row[h_i] if h_i < len(row) else ""
                row_dict[h_name] = val if val is not None else ""
        if any(v != "" for v in row_dict.values()):
            result.append(row_dict)
    return result

def read_tabular_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    datasets = []

    if ext in ('.xlsx', '.xlsm'):
        try:
            import openpyxl
            wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
            for sname in wb.sheetnames:
                ws = wb[sname]
                matrix = []
                for row in ws.iter_rows(values_only=True):
                    if any(cell is not None for cell in row):
                        matrix.append(list(row))
                if matrix:
                    parsed_rows = extract_rows_from_matrix(matrix)
                    if parsed_rows:
                        datasets.append((sname, parsed_rows))
            wb.close()
        except Exception as e:
            print(f"[!] Warning reading {filepath} with openpyxl: {e}")
    else:
        with open(filepath, 'rb') as f:
            raw_bytes = f.read()

        encoding = 'windows-1251'
        if raw_bytes.startswith(b'\xef\xbb\xbf'):
            encoding = 'utf-8-sig'
        elif b'charset=utf-8' in raw_bytes[:500].lower() or b'charset="utf-8"' in raw_bytes[:500].lower():
            encoding = 'utf-8'

        try:
            text = raw_bytes.decode(encoding)
        except Exception:
            text = raw_bytes.decode('windows-1251', errors='ignore')

        if '<table' in text.lower() or '<tr' in text.lower():
            p = HtmlTableParser()
            p.feed(text)
            parsed_rows = extract_rows_from_matrix(p.rows)
            if parsed_rows:
                datasets.append(('main', parsed_rows))
        else:
            sample = text[:2048]
            delimiter = ';' if sample.count(';') > sample.count(',') else ','
            reader = csv.reader(text.splitlines(), delimiter=delimiter)
            matrix = [r for r in reader if any(r)]
            parsed_rows = extract_rows_from_matrix(matrix)
            if parsed_rows:
                datasets.append(('main', parsed_rows))

    return datasets

def identify_data_type(rows):
    if not rows:
        return "unknown"
    headers_str = clean_key("".join(str(k) for k in rows[0].keys()))
    
    if ('СТАДИЯСДЕЛКИ' in headers_str and ('ПРЕДПОЛАГАЕМАЯДАТАЗАКРЫТИЯ' in headers_str or 'ТОВАР' in headers_str or 'КОМИССИЯСДЕЛКИРУБ' in headers_str)) or ('SALEMONTH' in headers_str and 'PREPAYMONTH' in headers_str):
        return "deals"
    if 'EVENTNAME' in headers_str or ('ДАТА' in headers_str and 'ЦЕНААВТО' in headers_str) or ('CLIENTID' in headers_str and ('ПАРТНЕР' in headers_str or 'BI' in headers_str)):
        return "leads"
    if 'БИТРИКС' in headers_str or ('КАМ' in headers_str and 'BI' in headers_str):
        return "directory"
    
    return "unknown"

def parse_funnel_image_or_config(raw_dir):
    default_funnel = {
        "page_view": 191607,
        "sbol_car_card_show": 28919,
        "sbol_car_card_click": 3706,
        "sbol_offer_show": 3626,
        "sbol_offer_click": 2324,
        "sbol_offer_success_show": 2269
    }

    if not os.path.exists(raw_dir):
        return default_funnel

    for fname in os.listdir(raw_dir):
        fpath = os.path.join(raw_dir, fname)
        if fname.lower() in ('funnel.json', 'funnel_metrics.json', 'metrics.json'):
            try:
                with open(fpath, 'r', encoding='utf-8-sig') as f:
                    cfg = json.load(f)
                    print(f"[*] Считаны метрики воронки из {fname}")
                    return cfg
            except Exception as e:
                print(f"[!] Warning reading {fname}: {e}")

    for fname in os.listdir(raw_dir):
        if fname.lower().endswith(('.jpg', '.jpeg', '.png')) and not fname.startswith('.'):
            fpath = os.path.join(raw_dir, fname)
            try:
                from PIL import Image
                import pytesseract
                img = Image.open(fpath)
                text = pytesseract.image_to_string(img)
                numbers = [int(n) for n in re.findall(r'\b\d{2,7}\b', text)]
                if len(numbers) >= 6:
                    print(f"[*] Найдены этапы воронки на изображении {fname}: {numbers[:6]}")
                    return {
                        "page_view": numbers[0],
                        "sbol_car_card_show": numbers[1],
                        "sbol_car_card_click": numbers[2],
                        "sbol_offer_show": numbers[3],
                        "sbol_offer_click": numbers[4],
                        "sbol_offer_success_show": numbers[5]
                    }
            except Exception:
                pass

    return default_funnel

def run_pipeline():
    print("=" * 60)
    print("   AUTOMATED PARSER ENGINE: B2C Auto Analytics & Funnel")
    print("=" * 60)

    # 1. Collect files from raw_data or root
    search_dirs = [RAW_DATA_DIR, PROJECT_ROOT]
    deals_data = []
    leads_data = []
    directory_data = []

    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        for fname in sorted(os.listdir(sdir)):
            if fname.startswith('~$') or fname.startswith('.'):
                continue
            if fname.lower().endswith(('.xlsx', '.xlsm', '.csv', '.xls')):
                fpath = os.path.join(sdir, fname)
                datasets = read_tabular_file(fpath)
                for sname, rows in datasets:
                    dtype = identify_data_type(rows)
                    print(f"[*] Файл: {fname} [{sname}] -> Тип: '{dtype.upper()}' ({len(rows)} строк)")
                    
                    if dtype == "deals" and not deals_data:
                        deals_data = rows
                    elif dtype == "leads" and not leads_data:
                        leads_data = rows
                    elif dtype == "directory" and not directory_data:
                        directory_data = rows

    if not deals_data:
        print("[!] Ошибка: Файл сделок не найден!")
        sys.exit(1)

    # 2. Build KAM dictionaries
    kam_dict_bitrix = {}
    kam_dict_bi = {}
    kam_dict_sber = {}

    if directory_data:
        for r in directory_data:
            bitrix = str(get_exact_val(r, 'БИТРИКС') or "").strip()
            bi = str(get_exact_val(r, 'BI') or "").strip()
            kam = str(get_exact_val(r, 'КАМ') or "").strip()
            pochta = str(get_exact_val(r, 'ПОЧТА') or "").strip()

            if bitrix: kam_dict_bitrix[bitrix.lower()] = kam
            if bi: kam_dict_bi[bi.lower()] = kam
            if pochta: kam_dict_sber[pochta.lower()] = kam
        print(f"[*] Справочник загружен: {len(directory_data)} записей КАМов.")

    # 3. Process Deals -> sys_db & sys_db_partners
    sys_db = []
    sys_db_partners = []

    aux_keywords = ("КРЕДИТ", "КАСКО", "ОСАГО", "ГАП", "СТРАХОВ", "СЕРТИФИКАТ")

    for row in deals_data:
        tovar = str(get_exact_val(row, 'ТОВАР') or "").upper()
        if any(kw in tovar for kw in aux_keywords):
            continue

        b2c = str(get_exact_val(row, 'ТИПСДЕЛКИB2C') or "")
        try:
            price = float(str(get_exact_val(row, 'ФИНАЛЬНАЯЦЕНАB2C', 'ЦЕНА') or 0).replace(' ', '').replace('\xa0', '').replace(',', '.'))
        except ValueError:
            price = 0.0

        try:
            comm = float(str(get_exact_val(row, 'КОМИССИЯСДЕЛКИРУБ') or 0).replace(' ', '').replace('\xa0', '').replace(',', '.'))
        except ValueError:
            comm = 0.0

        manager = str(get_exact_val(row, 'МЕНЕДЖЕРСДЕЛКИ') or "Не указан")
        stage = str(get_exact_val(row, 'СТАДИЯСДЕЛКИ') or "").upper()

        vin = str(get_exact_val(row, 'VIN', 'VINНОМЕР') or "").strip()
        if not vin:
            words = tovar.split()
            if words and len(words[-1]) > 10 and bool(re.search(r'[A-Z0-9]', words[-1])):
                vin = words[-1]
            else:
                vin = str(get_exact_val(row, 'ID') or "")

        raw_deal_date = get_exact_val(row, 'ПРЕДПОЛАГАЕМАЯДАТАЗАКРЫТИЯ')
        raw_prepay_date = get_exact_val(row, 'ДАТАВНЕСЕНИЯПРЕДОПЛАТЫРОЗНИЦА', 'ДАТАПОЛУЧЕНИЯАВАНСА') or raw_deal_date

        is_prepay = "ВНЕСЕНИЕ АВАНСА" in tovar
        is_sale = ("ЗАКРЫТО И РЕАЛИЗОВАН" in stage) and not is_prepay
        is_wait = (not is_sale) and not is_prepay

        d_deal_date = parse_custom_date(raw_deal_date)
        d_prepay_date = parse_custom_date(raw_prepay_date)

        deal_month_str = f"{d_deal_date.year}-{str(d_deal_date.month).zfill(2)}" if d_deal_date else ""
        prepay_month_str = f"{d_prepay_date.year}-{str(d_prepay_date.month).zfill(2)}" if d_prepay_date else ""

        b2c_upper = b2c.upper().replace(' ', '')
        chart_group = "Новые авто"
        if any(k in b2c_upper for k in ("МП1", "МП2", "МП3", "ВХОДЯЩАЯЗАЯВКА", "PARTNER")):
            chart_group = "Partners"

        final_brand = normalize_brand(tovar)
        final_revenue = round(comm / 1.22, 2) if (is_sale and comm > 0) else 0.0

        sys_db.append({
            "SaleMonth": deal_month_str if is_sale else "",
            "PrepayMonth": prepay_month_str if is_prepay else "",
            "Brand": "ВНЕСЕНИЕ" if is_prepay else final_brand,
            "B2C": b2c,
            "SaleQty": 1 if is_sale else 0,
            "Price": price if is_sale else 0,
            "Comm": comm if is_sale else 0,
            "PrepayQty": 1 if is_prepay else 0,
            "WaitQty": 1 if is_wait else 0,
            "WaitMonth": deal_month_str if is_wait else "",
            "DealDate": date_to_excel_serial(d_deal_date),
            "Manager": manager,
            "SeniorManager": str(get_exact_val(row, 'ОТВЕТСТВЕННЫЙЗАСДЕЛКУСТАРШИЙ', 'СТАРШИЙ') or "Без старшего"),
            "PrepayDate": date_to_excel_serial(d_prepay_date),
            "Revenue": final_revenue,
            "VIN": vin,
            "ChartGroup": chart_group
        })

        partner = str(get_exact_val(row, 'КОМПАНИЯНАЗВАНИЕКОМПАНИИ', 'КОМПАНИЯ') or "").strip()
        if partner:
            kam_partner = kam_dict_bitrix.get(partner.lower(), "")
            if is_sale:
                sys_db_partners.append({"Month": deal_month_str, "Partner": partner, "KAM": kam_partner, "Type": "Сделка", "Qty": 1, "B2C": b2c, "Brand": final_brand})
            elif is_prepay:
                sys_db_partners.append({"Month": prepay_month_str, "Partner": partner, "KAM": kam_partner, "Type": "Предоплата", "Qty": 1})
            elif is_wait:
                sys_db_partners.append({"Month": deal_month_str, "Partner": partner, "KAM": kam_partner, "Type": "Без сделки", "Qty": 1})

    # 4. Process Leads
    if leads_data:
        seen_clients = set()
        for row in leads_data:
            event_name = str(get_exact_val(row, 'EVENTNAME', 'ИМЯСОБЫТИЯ') or "").strip()
            if event_name and event_name != "Отправка лида":
                continue

            client_id = str(get_exact_val(row, 'CLIENTID', 'IDКЛИЕНТА', 'ID') or "").strip()
            if client_id and client_id in seen_clients:
                continue
            if client_id:
                seen_clients.add(client_id)

            partner = str(get_exact_val(row, 'BI', 'ПАРТНЕР') or "").strip()
            if not partner:
                continue

            partner_lower = partner.lower()
            kam = ""
            if "сберавто" in partner_lower or "сбер авто" in partner_lower:
                contact_name = str(get_exact_val(row, 'НАЗВАНИЕКОНТАКТА', 'КОНТАКТ') or "").strip()
                if contact_name:
                    kam = kam_dict_sber.get(contact_name.lower(), "")
            else:
                kam = kam_dict_bi.get(partner_lower, "")

            d_lead_date = parse_custom_date(get_exact_val(row, 'ДАТА'))
            lead_month_str = f"{d_lead_date.year}-{str(d_lead_date.month).zfill(2)}" if d_lead_date else ""

            sys_db_partners.append({
                "Month": lead_month_str,
                "Partner": partner,
                "KAM": kam,
                "Type": "Лид",
                "Qty": 1
            })

    # 5. Funnel Data
    funnel_metrics = parse_funnel_image_or_config(RAW_DATA_DIR if os.path.exists(RAW_DATA_DIR) else PROJECT_ROOT)

    output_payload = {
        "sys_db": sys_db,
        "sys_db_partners": sys_db_partners,
        "funnel_metrics": funnel_metrics
    }

    # 6. Save JSON
    os.makedirs(SITE_DIR, exist_ok=True)
    with open(OUTPUT_JSON_SITE, 'w', encoding='utf-8') as f:
        json.dump(output_payload, f, ensure_ascii=False, indent=2)

    with open(OUTPUT_JSON_ROOT, 'w', encoding='utf-8') as f:
        json.dump(output_payload, f, ensure_ascii=False, indent=2)

    total_sales = sum(r['SaleQty'] for r in sys_db)
    total_prepays = sum(r['PrepayQty'] for r in sys_db)
    total_revenue = sum(r['Revenue'] for r in sys_db)

    print("-" * 60)
    print(f"✅ ПАРСИНГ УСПЕШНО ЗАВЕРШЕН!")
    print(f"📊 Итого сделок (SaleQty):    {total_sales:,}".replace(',', ' '))
    print(f"💰 Итого выручка (Revenue):   {total_revenue:,.2f} ₽".replace(',', ' '))
    print(f"📦 Итого авансов (PrepayQty): {total_prepays:,}".replace(',', ' '))
    print(f"💾 Файл сохранен в: {OUTPUT_JSON_SITE} ({os.path.getsize(OUTPUT_JSON_SITE)/(1024*1024):.2f} MB)")
    print("-" * 60)

if __name__ == '__main__':
    run_pipeline()

