"""Sources stage of the dashboard ETL."""
from .config import DATA_DIR
from .config import PROJECT_ROOT
from .config import RAW_DATA_DIR
from .config import SITE_DIR
from .normalization import get_exact_val
from .normalization import parse_custom_date
from .tabular import identify_data_type
from .tabular import read_tabular_file
from .tabular import safe_open_rb
import hashlib
import os
import re
import sys

def load_sources():
    # 0. Sync OEM dealers & benchmarks if an OEM file exists in raw_data or root
    try:
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
        from scripts.sync_oem_registry import sync_oem_to_registry
        sync_oem_to_registry()
    except Exception as e:
        print(f"[!] OEM sync check skipped/warning: {e}")

    try:
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
        from scripts.sync_inn_dealers import sync_inn_dealers
        sync_inn_dealers()
    except Exception as e:
        print(f"[!] INN dealers sync check skipped/warning: {e}")

    try:
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
        from scripts.enrich_september_bi_oem import run_enrichment
        run_enrichment()
    except Exception as e:
        print(f"[!] September BI + OEM enrichment skipped/warning: {e}")

    try:
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
        from scripts.sync_kam_to_registry import sync_kam_to_registry
        sync_kam_to_registry()
    except Exception as e:
        print(f"[!] OEM KAM sync to registry skipped/warning: {e}")

    try:
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
        from scripts.merge_partner_splits import apply_merges_to_file
        for rp in [
            os.path.join(PROJECT_ROOT, 'partners_registry.json'),
            os.path.join(SITE_DIR, 'partners_registry.json'),
            os.path.join(DATA_DIR, 'partners_registry.json')
        ]:
            apply_merges_to_file(rp)
    except Exception as e:
        print(f"[!] Partner splits merger skipped/warning: {e}")

    # 1. Collect files from raw_data or root with MD5 hash deduplication
    search_dirs = [RAW_DATA_DIR, PROJECT_ROOT]
    deals_candidates = []
    leads_candidates = []
    directory_candidates = []
    all_leads_data = []
    seen_file_hashes = set()

    # Automatically identify latest Bitrix DEAL file
    all_deal_files = [f for sdir in search_dirs if os.path.exists(sdir) for f in os.listdir(sdir) if f.startswith('DEAL_') and f.lower().endswith('.xls')]
    latest_deal_file = max(all_deal_files) if all_deal_files else ''

    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        for fname in sorted(os.listdir(sdir), reverse=True):
            if fname.startswith('~$') or fname.startswith('.'):
                continue
            if fname.lower().endswith(('.xlsx', '.xlsm', '.csv', '.xls')):
                fpath = os.path.join(sdir, fname)

                # Read all tabular files; deduplicate identical files by MD5 content hash

                try:
                    with safe_open_rb(fpath) as fp:
                        fhash = hashlib.md5(fp.read(1024 * 1024)).hexdigest()
                except Exception:
                    fhash = fname

                if fhash in seen_file_hashes:
                    print(f"[*] Файл: {fname} -> ПРОПУСК (дубликат по хэшу)")
                    continue
                seen_file_hashes.add(fhash)

                datasets = read_tabular_file(fpath)
                for sname, rows in datasets:
                    dtype = identify_data_type(rows)
                    print(f"[*] Файл: {fname} [{sname}] -> Тип: '{dtype.upper()}' ({len(rows)} строк)")

                    if dtype == "deals":
                        deals_candidates.append((fname, fpath, rows))
                    elif dtype == "leads":
                        leads_candidates.append((fname, rows))
                    elif dtype == "directory":
                        directory_candidates.append((fname, rows))

    if not deals_candidates:
        print("[!] Ошибка: Файл сделок не найден!")
        sys.exit(1)

    # Filter strictly to Bitrix DEAL_*.xls exports if any exist
    bitrix_deals = [c for c in deals_candidates if c[0].startswith('DEAL_')]
    if bitrix_deals:
        deals_candidates = bitrix_deals

    # Filter strictly to dedicated data (*).xlsx leads files if any exist
    data_leads = [c for c in leads_candidates if c[0].startswith('data (')]

    # Classify lead files into Partner Transfers (has 'ПАРТНЕР' / 'СУММА ID') and General CRM Leads
    partner_lead_files = []
    crm_lead_files = []

    for fname, rows in data_leads:
        has_partner = 1 if rows and any(get_exact_val(r, 'ПАРТНЕР', 'BI') for r in rows[:50]) else 0
        num_match = re.search(r'data \((\d+)\)', fname)
        lead_num = int(num_match.group(1)) if num_match else 0
        if has_partner:
            partner_lead_files.append((lead_num, fname, rows))
        else:
            crm_lead_files.append((lead_num, fname, rows))

    partner_lead_files.sort(key=lambda x: x[0], reverse=True) # newest lead_num first
    crm_lead_files.sort(key=lambda x: x[0], reverse=True)     # newest lead_num first

    # 1. Build Merged Partner Transfers Dataset (leads_data)
    # If the newest file only covers the current month (e.g. September), backfill August & earlier from historical files
    if partner_lead_files:
        latest_partner_num, latest_partner_name, latest_partner_rows = partner_lead_files[0]
        # Check months in the newest partner file
        p_months = set()
        for r in latest_partner_rows[:200]:
            p_dt = parse_custom_date(get_exact_val(r, 'ДАТА', 'ДАТАСОБЫТИЯ'))
            if p_dt:
                p_months.add(p_dt.strftime('%Y-%m'))

        # If latest partner file is only current month (e.g. '2026-09') and lacks previous months, merge with historical files
        if len(p_months) == 1 and '2026-09' in p_months and len(partner_lead_files) > 1:
            print(f"[*] Файл партнерских лидов {latest_partner_name} содержит только 2026-09. Дополняем историей (август и ранее)...")
            historical_rows = []
            added_sources = []
            for _, prev_name, prev_rows in partner_lead_files[1:]:
                added_from_file = 0
                for r in prev_rows:
                    dt = parse_custom_date(get_exact_val(r, 'ДАТА', 'ДАТАСОБЫТИЯ'))
                    m_str = dt.strftime('%Y-%m') if dt else '2026-08'
                    if m_str != '2026-09':
                        historical_rows.append(r)
                        added_from_file += 1
                if added_from_file > 0:
                    added_sources.append(prev_name)
                    print(f"[*] Добавлено {added_from_file} исторических записей из {prev_name}")
            leads_data = historical_rows + latest_partner_rows
            leads_file_name = f"{latest_partner_name} + {' + '.join(added_sources)} (merged multi-month)"
        else:
            leads_data = latest_partner_rows
            leads_file_name = latest_partner_name
        print(f"[*] Сформирован датасет партнерских лидов: {len(leads_data)} записей ({leads_file_name})")
    else:
        leads_data = []
        leads_file_name = "None"

    # 2. Build Merged General CRM Leads Dataset
    if crm_lead_files:
        latest_crm_num, latest_crm_name, latest_crm_rows = crm_lead_files[0]
        c_months = set()
        for r in latest_crm_rows[:200]:
            c_dt = parse_custom_date(get_exact_val(r, 'ДАТАСОБЫТИЯ', 'ДАТАПЕРВОГОСОБЫТИЯ', 'ДАТА'))
            if c_dt:
                c_months.add(c_dt.strftime('%Y-%m'))

        if len(c_months) == 1 and '2026-09' in c_months:
            print(f"[*] Файл общих лидов CRM {latest_crm_name} содержит только 2026-09. Дополняем историей (август и ранее)...")
            historical_crm_rows = []
            for _, prev_crm_name, prev_crm_rows in crm_lead_files[1:]:
                added_now = 0
                for r in prev_crm_rows:
                    dt = parse_custom_date(get_exact_val(r, 'ДАТАСОБЫТИЯ', 'ДАТАПЕРВОГОСОБЫТИЯ', 'ДАТА'))
                    m_str = dt.strftime('%Y-%m') if dt else '2026-08'
                    if m_str != '2026-09':
                        historical_crm_rows.append(r)
                        added_now += 1
                if added_now > 0:
                    print(f"[*] Добавлено {added_now} исторических записей CRM из {prev_crm_name}")
                    break

            # If previous CRM files lacked older months, check partner_lead_files (e.g. data (39).xlsx)
            if not historical_crm_rows and partner_lead_files:
                for _, p_name, p_rows in partner_lead_files:
                    added_p = 0
                    for r in p_rows:
                        dt = parse_custom_date(get_exact_val(r, 'ДАТА', 'ДАТАСОБЫТИЯ'))
                        m_str = dt.strftime('%Y-%m') if dt else '2026-08'
                        if m_str != '2026-09':
                            historical_crm_rows.append(r)
                            added_p += 1
                    if added_p > 0:
                        print(f"[*] Добавлено {added_p} исторических записей лидов из {p_name}")
                        break
            crm_leads_data = historical_crm_rows + latest_crm_rows
        else:
            crm_leads_data = latest_crm_rows
        print(f"[*] Сформирован датасет CRM лидов: {len(crm_leads_data)} записей")
    else:
        crm_leads_data = []

    # Combined all_leads_data for cross-analytics
    all_leads_data = crm_leads_data + leads_data
    print(f"[*] Общий массив всех лидов: {len(all_leads_data)} записей")

    directory_data = directory_candidates[0][1] if directory_candidates else []
    return deals_candidates, directory_data, leads_data, all_leads_data, leads_file_name
