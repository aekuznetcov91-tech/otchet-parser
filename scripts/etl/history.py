"""History stage of the dashboard ETL."""
from .config import DATA_DIR
from .normalization import get_exact_val
from .normalization import parse_custom_date
import json
import os
import re

def merge_deal_history(deals_candidates):
    HISTORICAL_DEALS_CACHE_PATH = os.path.join(DATA_DIR, 'historical_deals_cache.json')

    def file_rank_deals(item):
        fname, fpath, rows = item
        m = re.search(r'DEAL_(\d{8})', fname)
        if m:
            return (0, m.group(1), fname)
        mtime = os.path.getmtime(fpath) if os.path.exists(fpath) else 0
        return (1, str(mtime), fname)

    # Merge deal candidates in ascending order of file date/mtime (older first, newer overwrites)
    # This preserves multi-month history (January - August) while updating fresh September deals.
    deals_candidates.sort(key=file_rank_deals)

    merged_deals_dict = {}

    # 1. Load persistent historical deals cache if present (guarantees past months can never be lost)
    if os.path.exists(HISTORICAL_DEALS_CACHE_PATH):
        try:
            with open(HISTORICAL_DEALS_CACHE_PATH, 'r', encoding='utf-8') as f:
                hist_deals = json.load(f)
                for r in hist_deals:
                    did = str(get_exact_val(r, 'ID', 'IDСДЕЛКИ') or '').strip()
                    tovar = str(get_exact_val(r, 'ТОВАР') or '').strip()
                    vin = str(get_exact_val(r, 'VIN') or '').strip()
                    key = f"{did}::{tovar}" if (did and tovar) else (f"{did}::{vin}" if (did and vin) else f"{did}::{len(merged_deals_dict)}")
                    merged_deals_dict[key] = r
                print(f"[*] Загружен постоянный кэш исторических сделок: {len(merged_deals_dict)} записей")
        except Exception as e:
            print(f"[!] Предупреждение при загрузке historical_deals_cache: {e}")

    # 2. Merge all discovered deal candidate files (older to newer)
    for d_fname, d_fpath, d_rows in deals_candidates:
        file_added = 0
        file_updated = 0
        for r in d_rows:
            stream = str(get_exact_val(r, 'СТРИМ') or '').strip()
            if stream and stream != 'Импортеры':
                continue
            did = str(get_exact_val(r, 'ID', 'IDСДЕЛКИ') or '').strip()
            tovar = str(get_exact_val(r, 'ТОВАР') or '').strip()
            vin = str(get_exact_val(r, 'VIN') or '').strip()
            key = f"{did}::{tovar}" if (did and tovar) else (f"{did}::{vin}" if (did and vin) else f"{did}::{len(merged_deals_dict)}")
            if key in merged_deals_dict:
                file_updated += 1
            else:
                file_added += 1
            merged_deals_dict[key] = r
        print(f"[*] Сделки из {d_fname}: {len(d_rows)} строк (новых: {file_added}, обновлено: {file_updated})")

    deals_data = list(merged_deals_dict.values())
    latest_deal_file = deals_candidates[-1][0] if deals_candidates else 'historical_cache'
    print(f"[*] Сформирован объединенный массив сделок: {len(deals_data)} записей (свежий файл: {latest_deal_file})")

    # 3. Save/update persistent historical deals cache for all closed past months (< active_month)
    all_deal_months = set()
    for r in deals_data:
        dt = parse_custom_date(get_exact_val(r, 'ПРЕДПОЛАГАЕМАЯДАТАЗАКРЫТИЯ'))
        if dt:
            all_deal_months.add(dt.strftime('%Y-%m'))
    active_month = max(all_deal_months) if all_deal_months else '2026-10'

    hist_to_cache = []
    for r in deals_data:
        dt = parse_custom_date(get_exact_val(r, 'ПРЕДПОЛАГАЕМАЯДАТАЗАКРЫТИЯ'))
        m_str = dt.strftime('%Y-%m') if dt else ''
        if m_str and m_str < active_month:
            hist_to_cache.append(r)

    if hist_to_cache:
        try:
            with open(HISTORICAL_DEALS_CACHE_PATH, 'w', encoding='utf-8') as f:
                json.dump(hist_to_cache, f, ensure_ascii=False)
            print(f"[*] Сохранен кэш историчности закрытых месяцев (< {active_month}): {len(hist_to_cache)} сделок")
        except Exception as e:
            print(f"[!] Ошибка сохранения historical_deals_cache: {e}")

    return deals_data, latest_deal_file
