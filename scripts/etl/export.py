"""Export stage of the dashboard ETL."""
from .config import OUTPUT_JSON_ROOT
from .config import OUTPUT_JSON_SITE
from .config import PROJECT_ROOT
from .config import SITE_DIR
import json
import os

def safe_save_json(payload, target_path):
    """Replace JSON atomically, keeping the previous file on write failure."""
    target_path = os.fspath(target_path)
    temp_path = target_path + '.tmp'
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))
        os.replace(temp_path, target_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def export_payload(output_payload, lead_geo_dealers_full, banking_deals_payload):
    os.makedirs(SITE_DIR, exist_ok=True)
    safe_save_json(output_payload, OUTPUT_JSON_SITE)
    safe_save_json(output_payload, OUTPUT_JSON_ROOT)

    # 6.1. Save lazy-loaded satellite JSON files for performance
    geo_clients_path = os.path.join(SITE_DIR, 'geo_clients.json')
    safe_save_json(lead_geo_dealers_full, geo_clients_path)
    print(f"💾 geo_clients.json: {os.path.getsize(geo_clients_path)/(1024*1024):.2f} MB (lazy-loaded drilldown)")

    if banking_deals_payload:
        banking_deals_path = os.path.join(SITE_DIR, 'banking_deals.json')
        safe_save_json(banking_deals_payload, banking_deals_path)
        print(f"💾 banking_deals.json: {os.path.getsize(banking_deals_path)/(1024*1024):.2f} MB (lazy-loaded)")

    parent_root_json = os.path.join(os.path.dirname(PROJECT_ROOT), 'data.json')
    if os.path.exists(parent_root_json):
        try:
            safe_save_json(output_payload, parent_root_json)
        except Exception:
            pass

