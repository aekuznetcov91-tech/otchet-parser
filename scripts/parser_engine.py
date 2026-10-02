"""CLI and compatibility exports for the modular dashboard ETL."""
import os
import sys

if __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.etl.normalization import (clean_key, get_exact_val, normalize_brand, parse_custom_date, date_to_excel_serial, normalize_vin_str)
from scripts.etl.tabular import (HtmlTableParser, extract_rows_from_matrix, safe_open_rb, read_xlsx_xml, read_tabular_file, identify_data_type)
from scripts.etl.funnel import (parse_funnel_image_or_config, calculate_brand_funnel)
from scripts.etl.analytics import (calculate_geo_match_analytics, calculate_city_expansion_potential, calculate_competitor_benchmarks, calculate_discount_analytics)
from scripts.etl.partners import (load_master_partners_registry, apply_canonical_kam_mapping)
from scripts.etl.lead_geo import (normalize_region_clean, resolve_sberauto_lead_partner, calculate_lead_geo_dealers_analytics)
from scripts.etl.config import PROJECT_ROOT, RAW_DATA_DIR, SITE_DIR, DATA_DIR, OUTPUT_JSON_SITE, OUTPUT_JSON_ROOT
from scripts.etl.sources import load_sources
from scripts.etl.history import merge_deal_history
from scripts.etl.transactions import build_transactions
from scripts.etl.payload import build_payload
from scripts.etl.export import export_payload


def run_pipeline():
    """Read sources, preserve history, aggregate transactions and export JSON."""
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    candidates, directory, leads, all_leads, leads_name = load_sources()
    deals, latest_file = merge_deal_history(candidates)
    if not deals:
        raise RuntimeError('No deals found')
    sales, partners, debtors, registry = build_transactions(deals, leads, all_leads, directory)
    payload, geo_clients, banking_deals = build_payload(
        sales, partners, debtors, registry, deals, leads, all_leads, latest_file, leads_name)
    export_payload(payload, geo_clients, banking_deals)
    print('ETL complete: {} sales, {:.2f} revenue, {} prepays'.format(
        payload['metadata']['total_sales'], payload['metadata']['total_revenue'],
        payload['metadata']['total_prepays']))


if __name__ == '__main__':
    run_pipeline()
