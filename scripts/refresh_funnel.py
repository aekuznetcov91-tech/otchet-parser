"""Rebuild only funnel analytics, preserving every transaction and other payload field."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.etl.config import OUTPUT_JSON_SITE, OUTPUT_JSON_ROOT
from scripts.etl.funnel import calculate_brand_funnel
from scripts.etl.sources import load_sources
from scripts.etl.export import safe_save_json


def main():
    payload = json.loads(Path(OUTPUT_JSON_SITE).read_text())
    _, _, _, leads, _ = load_sources(sync_catalogs=False, leads_only=True)
    payload['brand_funnel'] = calculate_brand_funnel(payload['sys_db'], leads, partners=payload['sys_db_partners'])
    for target in (OUTPUT_JSON_SITE, OUTPUT_JSON_ROOT):
        safe_save_json(payload, target)
    print('Refreshed funnel only; transaction arrays and sales metadata preserved.')


if __name__ == '__main__':
    main()
