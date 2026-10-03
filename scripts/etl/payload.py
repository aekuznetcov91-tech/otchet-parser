"""Payload stage of the dashboard ETL."""
from .analytics import calculate_city_expansion_potential
from .analytics import calculate_competitor_benchmarks
from .analytics import calculate_discount_analytics
from .analytics import calculate_geo_match_analytics
from .config import OUTPUT_JSON_ROOT
from .config import PROJECT_ROOT
from .config import RAW_DATA_DIR
from .funnel import calculate_brand_funnel
from .funnel import parse_funnel_image_or_config
from .lead_geo import calculate_lead_geo_dealers_analytics
import datetime
import json
import os

def build_payload(sys_db, sys_db_partners, debtors, reg_data, deals_data, leads_data, all_leads_data, latest_deal_file, leads_file_name):
    # 5. Funnel Data (Clickstream & Brand Funnel) & Analytics Modules
    funnel_metrics = parse_funnel_image_or_config(RAW_DATA_DIR if os.path.exists(RAW_DATA_DIR) else PROJECT_ROOT)
    brand_funnel = calculate_brand_funnel(sys_db, all_leads_data, partners=sys_db_partners)
    geo_analytics = calculate_geo_match_analytics(deals_data, leads_data, sys_db)
    city_expansion = calculate_city_expansion_potential(deals_data, leads_data)
    competitor_benchmarks = calculate_competitor_benchmarks(deals_data)
    discount_analytics = calculate_discount_analytics(deals_data)
    lead_geo_dealers, lead_geo_dealers_full = calculate_lead_geo_dealers_analytics(all_leads_data, deals_data)

    total_sales = sum(r['SaleQty'] for r in sys_db)
    total_prepays = sum(r['PrepayQty'] for r in sys_db)
    total_revenue = sum(r['Revenue'] for r in sys_db)
    now_iso = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")

    output_payload = {
        "metadata": {
            "updated_at": now_iso,
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "total_prepays": total_prepays,
            "latest_deal_file": latest_deal_file,
            "latest_leads_file": leads_file_name if 'leads_file_name' in locals() else ""
        },
        "sys_db": sys_db,
        "sys_db_partners": sys_db_partners,
        "funnel_metrics": funnel_metrics,
        "brand_funnel": brand_funnel,
        "debtors": debtors,
        "partners_registry": reg_data.get('partners', []),
        "unmatched_partners": reg_data.get('unmatched_queue', []),
        "geo_analytics": geo_analytics,
        "city_expansion": city_expansion,
        "competitor_benchmarks": competitor_benchmarks,
        "discount_analytics": discount_analytics,
        "lead_geo_dealers": lead_geo_dealers
    }

    # 5.1. Optional Banking Analytics (if enriched Bitrix file with 'Банк' column exists)
    try:
        from scripts.banking_dc_parser import parse_banking_analytics
        banking_analytics = parse_banking_analytics(PROJECT_ROOT)
    except Exception as e:
        print(f"[!] Banking analytics warning/skipped: {e}")
        banking_analytics = None

    if banking_analytics is None:
        if os.path.exists(OUTPUT_JSON_ROOT):
            try:
                with open(OUTPUT_JSON_ROOT, 'r', encoding='utf-8') as f_old:
                    old_data = json.load(f_old)
                    banking_analytics = old_data.get('banking_analytics')
            except Exception:
                pass

    banking_deals_payload = None
    if banking_analytics:
        # Performance split: extract heavy other_deals_db into a separate lazy-loaded file
        banking_deals_payload = None
        if 'other_deals_db' in banking_analytics:
            banking_deals_payload = banking_analytics['other_deals_db']
            banking_analytics_lite = {k: v for k, v in banking_analytics.items() if k != 'other_deals_db'}
            output_payload["banking_analytics"] = banking_analytics_lite
        else:
            output_payload["banking_analytics"] = banking_analytics

    return output_payload, lead_geo_dealers_full, banking_deals_payload
