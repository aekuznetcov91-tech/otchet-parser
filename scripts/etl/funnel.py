"""Funnel stage of the dashboard ETL."""
from .config import PROJECT_ROOT
from .config import RAW_DATA_DIR
from .normalization import clean_key
from .normalization import get_exact_val
from .normalization import normalize_brand
from .normalization import parse_custom_date
from collections import defaultdict
import json
from datetime import datetime, timedelta
import os
import re
from .calculator import load_calculator_snapshot, calculator_metrics, event_brand, client_id

def parse_funnel_image_or_config(raw_dir):
    """Extract funnel clickstream config from JSON or OCR images."""
    default_funnel = None  # No source means unavailable, never a hardcoded benchmark.

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


def crm_event_datetime(value):
    """Retain time-of-day when the CRM export provides it."""
    if isinstance(value, datetime):
        return value
    text = str(value or '').strip()
    try:
        return datetime(1899, 12, 30) + timedelta(days=float(text))
    except (ValueError, OverflowError):
        pass
    for fmt in ('%d.%m.%Y %H:%M:%S', '%d.%m.%Y, %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    day = parse_custom_date(value)
    return datetime.combine(day, datetime.min.time()) if day else None


def calculate_brand_funnel(sys_db, leads_data=None, calculator=None, partners=None):
    """
    Calculate observed multi-month brand metrics without estimates.
    Integrates PostHog clickstream vitrina data with CRM sales metrics and dynamic leads from data.xlsx.
    """
    vitrina_map = {}
    ocr_files = [
        os.path.join(RAW_DATA_DIR, 'brand_funnels_clean.json'),
        os.path.join(PROJECT_ROOT, 'Jetour', 'brand_funnels_clean.json'),
        os.path.join(PROJECT_ROOT, 'brand_funnels_clean.json')
    ]
    for ofile in ocr_files:
        if os.path.exists(ofile):
            try:
                with open(ofile, 'r', encoding='utf-8') as fp:
                    items = json.load(fp)
                    for item in items:
                        m = item.get('month', '')
                        b = item.get('brand', '')
                        if m and b:
                            vitrina_map[(m, b)] = item
                break
            except Exception:
                pass

    if calculator is None:
        calculator = load_calculator_snapshot()
    all_brands = ['JETOUR', 'LADA', 'TENET', 'CHERY', 'CHANGAN', 'GAC', 'SOLARIS', 'SOUEAST', 'BELGEE', 'GEELY', 'KNEWSTAR', 'HAVAL', 'JAECOO', 'OMODA', 'МОСКВИЧ', 'JELAND']
    crm = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    latest_dates = []
    normalized = []
    first_lead = {}
    for row in leads_data or []:
        cid = client_id(get_exact_val(row, 'client_id', 'CLIENTID', 'IDКЛИЕНТА'))
        dt = crm_event_datetime(get_exact_val(row, 'Дата события', 'ДАТАСОБЫТИЯ', 'ДАТА', 'Дата'))
        if not cid or not dt:
            continue
        month = dt.strftime('%Y-%m')
        ev = clean_key(get_exact_val(row, 'Событие', 'EVENTNAME', 'event_name'))
        brand = event_brand(str(get_exact_val(row, 'БРЕНД', 'Бренд')) + ' ' + str(get_exact_val(row, 'МОДЕЛЬ', 'Модель')), month)
        normalized.append((cid, dt, month, ev, brand))
        latest_dates.append(dt)
        if 'НОВЫЙЛИД' in ev:
            first_lead[cid] = min(first_lead.get(cid, dt), dt)
    for cid, dt, month, ev, brand in normalized:
        for period in (month, 'all'):
            for scope in (brand, 'ALL'):
                st = crm[period][scope]
                if 'НОВЫЙЛИД' in ev:
                    st['leads'].add(cid)
                if 'ЗАКРЕПЛЕНИЕМЕНЕДЖЕРА' in ev and cid in first_lead and dt >= first_lead[cid]:
                    st['qual'].add(cid)
                # Only explicit bank approval events, never application/credit keywords.
                if ev in ('КРЕДИТОДОБРЕН', 'ОДОБРЕНИЕБАНКА', 'ОДОБРЕНОБАНКОМ'):
                    st['fdc_appr'].add(cid)
    # Canonical transferred leads, never added to geo/CRM approximations.
    for row in partners or []:
        if row.get('Type') != 'Лид':
            continue
        cid = client_id(row.get('ClientId'))
        month = row.get('Month')
        if not cid or not month:
            continue
        brand = event_brand(str(row.get('Brand') or '') + ' ' + str(row.get('Model') or ''), month)
        for period in (month, 'all'):
            for scope in (brand, 'ALL'):
                crm[period][scope]['dealer'].add(cid)
    extra_brands = {b for st in crm.values() for b in st if b != 'ALL'}
    if calculator:
        extra_brands.update(b for st in calculator['by_month'].values() for b in st if b != 'ALL')
    all_brands += sorted(extra_brands - set(all_brands))
    month_keys = {m for m, _ in vitrina_map} | {r.get('SaleMonth') for r in sys_db if r.get('SaleQty') == 1}
    month_keys.update(m for m in crm if m != 'all')
    if calculator:
        month_keys.update(m for m in calculator['by_month'] if m != 'all')
    months = sorted((m for m in month_keys if m and re.fullmatch(r'\d{4}-\d{2}', m)), reverse=True) + ['all']

    by_month = {}

    def is_brand_match_for_funnel(r_brand, r_model, funnel_brand, m_str=None):
        m = (r_model or '').upper()
        b_up = (r_brand or '').upper()
        if m_str and m_str >= '2026-09' and funnel_brand in ('OMODA', 'JAECOO'):
            return False
        if b_up == funnel_brand:
            return True
        if funnel_brand == 'JELAND':
            if m_str and m_str >= '2026-09':
                return any(k in b_up or k in m for k in ('JELAND', 'ДЖЕЙЛЕНД', 'OMODA', 'JAECOO', 'ОМОДА', 'ДЖЕЙКУ')) or r_brand == 'OMODA & JAECOO'
            return 'JELAND' in b_up or 'JELAND' in m or 'ДЖЕЙЛЕНД' in m
        if funnel_brand == 'GEELY':
            return r_brand == 'Geely & Belgee' and not any(k in m for k in ('BELGEE', 'БЕЛДЖИ', 'X50', 'X70', 'S50', '001', 'KNEWSTAR'))
        if funnel_brand == 'BELGEE':
            return r_brand == 'Geely & Belgee' and any(k in m for k in ('BELGEE', 'БЕЛДЖИ', 'X50', 'X70', 'S50'))
        if funnel_brand == 'KNEWSTAR':
            return r_brand == 'Geely & Belgee' and (any(k in m for k in ('KNEWSTAR', 'КНЬЮСТАР', 'КНЮСТАР')) or '001' in m)
        if funnel_brand == 'OMODA':
            return r_brand == 'OMODA & JAECOO' and not any(k in m for k in ('JAECOO', 'ДЖЕЙКУ', 'J7', 'J8', 'JELAND', 'ДЖЕЙЛЕНД'))
        if funnel_brand == 'JAECOO':
            return r_brand == 'OMODA & JAECOO' and any(k in m for k in ('JAECOO', 'ДЖЕЙКУ', 'J7', 'J8')) and not any(k in m for k in ('JELAND', 'ДЖЕЙЛЕНД'))
        if funnel_brand == 'CHERY':
            return r_brand == 'CHERY & TENET' and 'TENET' not in m and 'ТЕНЕТ' not in m
        if funnel_brand == 'TENET':
            return r_brand == 'CHERY & TENET' and ('TENET' in m or 'ТЕНЕТ' in m)
        return False

    # Every sale belongs to exactly one brand, with unresolved cases visible.
    sales_by_brand = defaultdict(list)
    for row in sys_db:
        if row.get('SaleQty') != 1:
            continue
        brand = next((b for b in all_brands if is_brand_match_for_funnel(row.get('Brand'), row.get('Model'), b, row.get('SaleMonth'))), 'НЕ ОПРЕДЕЛЁН')
        sales_by_brand[brand].append(row)
    if 'НЕ ОПРЕДЕЛЁН' in sales_by_brand and 'НЕ ОПРЕДЕЛЁН' not in all_brands:
        all_brands.append('НЕ ОПРЕДЕЛЁН')

    for m in months:
        by_month[m] = {
            "month": m,
            "month_label": m if m != "all" else "Все периоды (Тотал)",
            "brands": {}
        }

        for b in all_brands:
            b_sales = [r for r in sales_by_brand[b] if m == 'all' or r.get('SaleMonth') == m]

            b_mp2 = [r for r in b_sales if 'МП2' in str(r.get('B2C') or '').upper()]
            b_no_mp2 = [r for r in b_sales if 'МП2' not in str(r.get('B2C') or '').upper()]

            deals_by_b2c = {}
            rev_by_b2c = {}
            for r in b_no_mp2:
                b2c_type = str(r.get('B2C') or 'Не указан').strip()
                rev = r.get('Revenue', 0)
                deals_by_b2c[b2c_type] = deals_by_b2c.get(b2c_type, 0) + 1
                rev_by_b2c[b2c_type] = round(rev_by_b2c.get(b2c_type, 0.0) + rev, 2)

            # Preserve observed PostHog metrics, with missing sources explicit.
            v_items = [v for (period, brand), v in vitrina_map.items() if brand == b and (m == 'all' or period == m)]
            v_keys = ('page_view', 'car_card_show', 'car_card_click', 'offer_show', 'offer_click', 'offer_success')
            v_stat = {key: sum(v.get(key, 0) for v in v_items) for key in v_keys} if v_items else None
            st = crm[m][b]
            logs = calculator_metrics(calculator, m, b)
            # No observed CRM event means unknown, not an inferred zero or percentage.
            leads_count = len(st['leads']) or None
            qual_count = len(st['qual']) or None
            dealer_count = len(st['dealer']) or None
            fdc_appr = len(st['fdc_appr']) or None
            calc_total = logs['calc']['events'] if logs else None
            offer_total = logs['offer']['events'] if logs else None
            fdc_app = None  # A completed calculator form is not a submitted bank application.

            tot_rev_no_mp2 = round(sum(r.get('Revenue', 0) for r in b_no_mp2), 2)
            tot_rev_mp2 = round(sum(r.get('Revenue', 0) for r in b_mp2), 2)
            tot_rev_all = round(tot_rev_no_mp2 + tot_rev_mp2, 2)

            by_month[m]["brands"][b] = {
                "brand": b,
                "vitrina": v_stat,
                "leads": leads_count,
                "qual": qual_count,
                "calc_total": calc_total,
                "calc_matched": None,
                "calculator": logs,
                "offer_total": offer_total,
                "offer_matched": None,
                "dealer": dealer_count,
                "fdc_app": fdc_app,
                "fdc_appr": fdc_appr,
                "deals_total_all": len(b_sales),
                "mp2_count": len(b_mp2),
                "mp2_rev": tot_rev_mp2,
                "deals_no_mp2": len(b_no_mp2),
                "rev_no_mp2": tot_rev_no_mp2,
                "deals_by_b2c": deals_by_b2c,
                "rev_by_b2c": rev_by_b2c,
                "arpu_no_mp2": round(tot_rev_no_mp2 / len(b_no_mp2), 2) if len(b_no_mp2) > 0 else 0,
                "arpu_total": round(tot_rev_all / len(b_sales), 2) if len(b_sales) > 0 else 0,
                "src_breakdown": None,
                "latest_lead_date": max(latest_dates).isoformat() if latest_dates else None
            }

    brand_funnel = {
        "OVERALL_LATEST_DATE": max(latest_dates).isoformat() if latest_dates else None,
        "calculator_source": {k: v for k, v in calculator.items() if k != "by_month"} if calculator else None,
        "months": months,
        "by_month": by_month
    }
    for m in months:
        by_month[m]['calculator'] = calculator_metrics(calculator, m, 'ALL')
        by_month[m]['crm_totals'] = {key: len(crm[m]['ALL'][key]) or None for key in ('leads', 'qual', 'dealer', 'fdc_appr')}
    for b in all_brands:
        brand_funnel[b] = by_month[months[0]]['brands'][b]

    return brand_funnel
