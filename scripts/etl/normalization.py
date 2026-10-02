"""Normalization stage of the dashboard ETL."""
import datetime
import re

def clean_key(k):
    """Normalize string key by removing whitespace and non-alphanumerics."""
    if k is None:
        return ""
    return re.sub(r'[^A-ZА-Я0-9]', '', str(k).upper())


def get_exact_val(row, *search_keys):
    """
    Fetch value from row dictionary.
    Supports both pre-cleaned uppercase keys (O(1)) and fallback on raw keys.
    """
    if not isinstance(row, dict):
        return ""
    for sk in search_keys:
        # Fast path: exact key or clean key in row
        if sk in row and row[sk] != "":
            return row[sk]
        c_sk = clean_key(sk)
        if c_sk in row and row[c_sk] != "":
            return row[c_sk]
    return ""


def normalize_brand(tovar_str, month=None):
    """Normalize vehicle brand name from raw product/deal text."""
    t = str(tovar_str or "").upper().strip()
    aux_keywords = ("КРЕДИТ", "КАСКО", "ОСАГО", "ГАП", "СТРАХОВ", "СЕРТИФИКАТ", "ВНЕСЕНИЕ АВАНСА", "ВНЕСЕНИЕ", "АВАНС", "ОФОРМЛЕНИЕ", "ДОГОВОР", "УСЛУГА", "КОМИССИЯ", "ДОП", "БРОНИРОВАНИЕ", "БРОНЬ", "БРОНИР")
    if any(kw in t for kw in aux_keywords):
        return None

    # Strip VIN or 17-character alphanumeric tokens before matching model acronyms
    t_clean = re.sub(r'VIN\s*[:\s]*\s*[A-Z0-9]+', ' ', t)
    t_clean = re.sub(r'\b[A-HJ-NPR-Z0-9]{17}\b', ' ', t_clean)

    # Normalize visually identical Cyrillic homoglyphs to Latin (e.g. Cyrillic 'Т' in 'ТENET', 'О' in 'SОLARIS')
    cyr_to_lat = str.maketrans('АВЕКМНОРСТХ', 'ABEKMHOPCTX')
    t_latin = t_clean.translate(cyr_to_lat)

    # 1. Primary check: Full Brand Names (highest priority, avoids substring collisions)
    if any(k in t_clean or k in t_latin for k in ["KNEWSTAR", "КНЬЮСТАР", "КНЮСТАР"]) or (re.search(r'\b001\b', t_latin) and any(k in t_clean or k in t_latin for k in ["G B K", "GEELY", "KNEWSTAR", "TUGELLA"])):
        return "Knewstar"
    if any(k in t_clean or k in t_latin for k in ["BELGEE", "BEELGEE", "БЕЛДЖИ"]):
        return "Belgee"
    if any(k in t_clean or k in t_latin for k in ["GEELY", "ДЖИЛИ", "G B K", "GBK"]) and re.search(r'\b(X50|X70|S50|X-50|X-70)\b', t_latin) and not re.search(r'\bX70\s*PLUS\b', t_latin):
        return "Belgee"
    if any(k in t_clean or k in t_latin for k in ["GEELY", "ДЖИЛИ"]) or (any(k in t_clean or k in t_latin for k in ["G B K", "GBK"]) and re.search(r'\b(MONJARO|COOLRAY|ATLAS|PREFACE|EMGRAND|OKAVANGO|TUGELLA|TUGGELLA|CITYRAY|EX5|EX-5)\b', t_latin)):
        return "Geely"
    if any(k in t_clean or k in t_latin for k in ["HAVAL", "ХАВЕЙЛ"]):
        return "HAVAL"
    if any(k in t_clean or k in t_latin for k in ["JELAND", "ДЖЕЙЛЕНД"]):
        return "JELAND"
    if any(k in t_clean or k in t_latin for k in ["OMODA", "JAECOO", "ОМОДА", "ДЖЕЙКУ", "ДЖАКУ"]):
        if month and str(month) >= "2026-09":
            return "JELAND"
        return "OMODA & JAECOO"
    if any(k in t_clean or k in t_latin for k in ["TENET", "ТЕНЕТ", "CHERY", "ЧЕРИ"]):
        return "CHERY & TENET"
    if any(k in t_clean or k in t_latin for k in ["CHANGAN", "ЧАНГАН"]):
        return "CHANGAN"
    if any(k in t_clean or k in t_latin for k in ["JETOUR", "JETOR", "ДЖЕТУР"]):
        return "JETOUR"
    if any(k in t_clean or k in t_latin for k in ["LADA", "ЛАДА"]):
        return "LADA"
    if any(k in t_clean or k in t_latin for k in ["GAC", "ГАК"]):
        return "GAC"
    if any(k in t_clean or k in t_latin for k in ["TOYOTA", "ТОЙОТА"]):
        return "TOYOTA"
    if any(k in t_clean or k in t_latin for k in ["TANK", "ТАНК"]):
        return "TANK"
    if any(k in t_clean or k in t_latin for k in ["EXEED", "ЭКСИД"]):
        return "EXEED"
    if any(k in t_clean or k in t_latin for k in ["SOUEAST", "SOUEAS", "СОУИСТ"]):
        return "SOUEAST"
    if any(k in t_clean or k in t_latin for k in ["SOLARIS", "СОЛЯРИС"]):
        return "SOLARIS"
    if any(k in t_clean or k in t_latin for k in ["HONGQI", "ХОНЧИ"]):
        return "HONGQI"
    if any(k in t_clean or k in t_latin for k in ["XCITE", "X-CITE", "ИКСИТ"]):
        return "XCITE"
    if any(k in t_clean or k in t_latin for k in ["МОСКВИЧ", "MOSKVICH"]):
        return "МОСКВИЧ"
    if any(k in t_clean or k in t_latin for k in ["KIA", "КИА"]):
        return "KIA"
    if any(k in t_clean or k in t_latin for k in ["HYUNDAI", "ХЕНДЭ", "ХЕНДАЙ"]):
        return "HYUNDAI"
    if any(k in t_clean or k in t_latin for k in ["VOYAH", "ВОЯ"]):
        return "VOYAH"
    if any(k in t_clean or k in t_latin for k in ["G B K", "GBK"]):
        return "Geely & Belgee"

    # 2. Secondary check: Distinct vehicle models using regex word boundaries
    if re.search(r'\b(DASHING|X70\s*PLUS|T2|T1|X90\s*PLUS)\b', t_latin):
        return "JETOUR"
    if re.search(r'\b(JOLION|DARGO|H3|H9|M6|F7|F7X|H7)\b', t_latin):
        return "HAVAL"
    if re.search(r'\b(MONJARO|COOLRAY|ATLAS|PREFACE|EMGRAND|OKAVANGO|TUGELLA|TUGGELLA|CITYRAY|EX5|EX-5)\b', t_latin):
        return "Geely"
    if re.search(r'\b(X50|X70|S50|X-50|X-70)\b', t_latin):
        return "Belgee"
    if re.search(r'\b(UNI-V|UNI-K|UNI-T|UNI-S|CS35|CS55|CS75|CS95|HUNTER|LAMORE|EADO|ALSVIN)\b', t_latin):
        return "CHANGAN"
    if re.search(r'\b(GS3|GS8|M8)\b', t_latin):
        return "GAC"
    if re.search(r'\b(TIGGO|ARRIZO|T4L|T4|T7|T8)\b', t_latin):
        return "CHERY & TENET"
    if re.search(r'\b(C5|S5|J7|J8)\b', t_latin):
        if month and str(month) >= "2026-09":
            return "JELAND"
        return "OMODA & JAECOO"

    words = re.split(r'[\s,/-]+', t_clean.strip())
    first_word = words[0] if words and words[0] else ""
    first_word_lat = first_word.translate(cyr_to_lat)
    if first_word_lat in ("TENET", "CHERY"):
        return "CHERY & TENET"
    if first_word_lat in ("SOLARIS",):
        return "SOLARIS"
    if len(first_word) >= 2 and re.match(r'^[A-ZА-Я0-9]+$', first_word) and not any(kw in first_word for kw in aux_keywords):
        return first_word
    return None


def parse_custom_date(date_value):
    """Parse Excel serial, ISO format, or standard date strings into datetime.date."""
    if date_value is None or date_value == "":
        return None
    if isinstance(date_value, (datetime.date, datetime.datetime)):
        return date_value if isinstance(date_value, datetime.date) else date_value.date()

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
    """Convert datetime.date to Excel serial number integer."""
    if not d_date:
        return 0
    if isinstance(d_date, datetime.datetime):
        d_date = d_date.date()
    return (d_date - datetime.date(1899, 12, 30)).days


def normalize_vin_str(vin_val):
    """Normalize VIN: strip whitespace, map Cyrillic homoglyphs to Latin, standardize 1/I and 0/O for 17-char VINs."""
    if not vin_val:
        return ""
    v = str(vin_val).strip().upper()
    v = v.translate(str.maketrans('АВЕКМНОРСТХ', 'ABEKMHOPCTX'))
    v = re.sub(r'[^A-Z0-9]', '', v)
    if len(v) == 17:
        v = v.replace('I', '1').replace('O', '0')
    return v

