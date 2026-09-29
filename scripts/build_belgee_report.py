# -*- coding: utf-8 -*-
"""
Belgee Comprehensive Analytics & Dashboard Generator
Extracts all August and September 2026 data for BELGEE:
- Transferred leads & deals
- Funnel metrics (Vitrina -> CRM -> Deals)
- Partner, Holding & KAM allocation
- Model lineup (X50, X70, S50) pricing & discounts
- Full searchable/sortable registries
Outputs:
- data/belgee_analytics.json
- belgee_dashboard.html
- site/belgee_dashboard.html
"""

import os
import sys
import json
from collections import defaultdict, Counter
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_JSON_PATH = os.path.join(PROJECT_ROOT, 'data.json')
CLEAN_FUNNELS_PATH = os.path.join(PROJECT_ROOT, 'raw_data', 'brand_funnels_clean.json')

def excel_date_to_str(val):
    if not val:
        return ""
    if isinstance(val, (int, float)):
        try:
            # Excel base date 1899-12-30
            dt = datetime(1899, 12, 30) + timedelta(days=float(val))
            return dt.strftime("%d.%m.%Y")
        except Exception:
            return str(val)
    return str(val)

def normalize_model(m):
    m_up = str(m or '').upper().strip()
    if 'X50' in m_up or 'Х50' in m_up:
        return 'BELGEE X50'
    elif 'X70' in m_up or 'Х70' in m_up or 'Х-70' in m_up:
        return 'BELGEE X70'
    elif 'S50' in m_up or 'С50' in m_up:
        return 'BELGEE S50'
    return m or 'BELGEE Другие'

def run():
    print("[1/5] Loading data.json...")
    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Vitrina PostHog
    vitrina_stats = {
        '2026-08': {'page_view': 259301, 'car_card_show': 16599, 'car_card_click': 1280, 'offer_show': 1248, 'offer_click': 732, 'offer_success': 720},
        '2026-09': {'page_view': 206620, 'car_card_show': 10072, 'car_card_click': 745, 'offer_show': 726, 'offer_click': 432, 'offer_success': 422}
    }
    if os.path.exists(CLEAN_FUNNELS_PATH):
        try:
            with open(CLEAN_FUNNELS_PATH, 'r', encoding='utf-8') as f:
                c_data = json.load(f)
                for item in c_data:
                    if str(item.get('brand', '')).upper() == 'BELGEE':
                        m = item.get('month')
                        if m in ('2026-08', '2026-09'):
                            vitrina_stats[m] = {
                                'page_view': item.get('page_view', 0),
                                'car_card_show': item.get('car_card_show', 0),
                                'car_card_click': item.get('car_card_click', 0),
                                'offer_show': item.get('offer_show', 0),
                                'offer_click': item.get('offer_click', 0),
                                'offer_success': item.get('offer_success', 0)
                            }
        except Exception as e:
            print(f"Warning reading clean funnels: {e}")

    # 2. Extract Belgee partners records
    sys_db_partners = data.get('sys_db_partners', [])
    belgee_recs = [r for r in sys_db_partners if ('BELGEE' in str(r.get('Brand', '')).upper() or 'БЕЛДЖИ' in str(r.get('Brand', '')).upper()) and r.get('Month') in ('2026-08', '2026-09')]

    print(f"Found {len(belgee_recs)} Belgee records in sys_db_partners (Aug + Sep)")

    # 3. Process Deals & Leads
    deals_aug = []
    deals_sep = []
    leads_aug = []
    leads_sep = []

    for r in belgee_recs:
        item = dict(r)
        item['DateFormatted'] = excel_date_to_str(r.get('Date'))
        item['ModelClean'] = normalize_model(r.get('Model'))
        
        m = r.get('Month')
        t = r.get('Type')
        if t == 'Сделка':
            if m == '2026-08':
                deals_aug.append(item)
            else:
                deals_sep.append(item)
        else:
            if m == '2026-08':
                leads_aug.append(item)
            else:
                leads_sep.append(item)

    # Sort registries by date descending
    deals_aug.sort(key=lambda x: str(x.get('Date', '')), reverse=True)
    deals_sep.sort(key=lambda x: str(x.get('Date', '')), reverse=True)
    leads_aug.sort(key=lambda x: str(x.get('Date', '')), reverse=True)
    leads_sep.sort(key=lambda x: str(x.get('Date', '')), reverse=True)

    # 4. Aggregations
    def summarize_period(deals, leads):
        deal_count = len(deals)
        lead_count = len(leads)
        turnover = sum(d.get('Price', 0) for d in deals)
        revenue = sum(d.get('Comm', 0) for d in deals)
        avg_price = turnover / deal_count if deal_count else 0
        avg_comm = revenue / deal_count if deal_count else 0
        deal_cr = (deal_count / lead_count * 100) if lead_count else 0
        prepay_deals = sum(1 for d in deals if d.get('HasPrepay') == 1)
        prepay_pct = (prepay_deals / deal_count * 100) if deal_count else 0
        
        # Models
        model_stats = defaultdict(lambda: {'count': 0, 'turnover': 0.0, 'revenue': 0.0, 'exact_models': Counter()})
        for d in deals:
            mc = d['ModelClean']
            model_stats[mc]['count'] += 1
            model_stats[mc]['turnover'] += d.get('Price', 0)
            model_stats[mc]['revenue'] += d.get('Comm', 0)
            model_stats[mc]['exact_models'][d.get('Model', 'Не указана')] += 1

        # KAMs
        kam_stats = defaultdict(lambda: {'deals': 0, 'leads': 0, 'turnover': 0.0, 'revenue': 0.0, 'partners': set()})
        for d in deals:
            kam = d.get('KAM') or 'Не назначен'
            kam_stats[kam]['deals'] += 1
            kam_stats[kam]['turnover'] += d.get('Price', 0)
            kam_stats[kam]['revenue'] += d.get('Comm', 0)
            kam_stats[kam]['partners'].add(d.get('Partner') or 'Не указан')
        for l in leads:
            kam = l.get('KAM') or 'Не назначен'
            kam_stats[kam]['leads'] += 1
            kam_stats[kam]['partners'].add(l.get('Partner') or 'Не указан')

        # B2C Channels
        b2c_stats = Counter(d.get('B2C') or 'Не указан' for d in deals)

        return {
            'deal_count': deal_count,
            'lead_count': lead_count,
            'turnover': turnover,
            'revenue': revenue,
            'avg_price': avg_price,
            'avg_comm': avg_comm,
            'deal_cr': deal_cr,
            'prepay_deals': prepay_deals,
            'prepay_pct': prepay_pct,
            'models': {k: {
                'count': v['count'],
                'share': (v['count'] / deal_count * 100) if deal_count else 0,
                'turnover': v['turnover'],
                'revenue': v['revenue'],
                'avg_price': v['turnover'] / v['count'] if v['count'] else 0,
                'avg_comm': v['revenue'] / v['count'] if v['count'] else 0,
                'exact_models': dict(v['exact_models'])
            } for k, v in model_stats.items()},
            'kams': {k: {
                'deals': v['deals'],
                'leads': v['leads'],
                'turnover': v['turnover'],
                'revenue': v['revenue'],
                'partners_count': len(v['partners']),
                'partners_list': sorted(list(v['partners']))
            } for k, v in kam_stats.items()},
            'b2c_stats': dict(b2c_stats)
        }

    sum_aug = summarize_period(deals_aug, leads_aug)
    sum_sep = summarize_period(deals_sep, leads_sep)

    # 5. Combined Partners Matrix (Deals + Leads + CR + KAM)
    all_partners = set([d.get('Partner') for d in deals_aug + deals_sep + leads_aug + leads_sep if d.get('Partner')])
    partner_matrix = []
    for p in all_partners:
        p_d_aug = [d for d in deals_aug if d.get('Partner') == p]
        p_d_sep = [d for d in deals_sep if d.get('Partner') == p]
        p_l_aug = [l for l in leads_aug if l.get('Partner') == p]
        p_l_sep = [l for l in leads_sep if l.get('Partner') == p]

        kam_set = set([x.get('KAM') for x in p_d_aug + p_d_sep + p_l_aug + p_l_sep if x.get('KAM')])
        kam_str = ", ".join(sorted(kam_set)) if kam_set else "Не назначен"

        raw_set = set([x.get('RawPartner') for x in p_d_aug + p_d_sep + p_l_aug + p_l_sep if x.get('RawPartner')])
        raw_str = "; ".join(sorted(raw_set))

        # Financials
        rev_aug = sum(x.get('Comm', 0) for x in p_d_aug)
        rev_sep = sum(x.get('Comm', 0) for x in p_d_sep)
        turn_aug = sum(x.get('Price', 0) for x in p_d_aug)
        turn_sep = sum(x.get('Price', 0) for x in p_d_sep)

        d_cnt_aug = len(p_d_aug)
        d_cnt_sep = len(p_d_sep)
        l_cnt_aug = len(p_l_aug)
        l_cnt_sep = len(p_l_sep)

        cr_aug = (d_cnt_aug / l_cnt_aug * 100) if l_cnt_aug else (100.0 if d_cnt_aug > 0 else 0.0)
        cr_sep = (d_cnt_sep / l_cnt_sep * 100) if l_cnt_sep else (100.0 if d_cnt_sep > 0 else 0.0)

        partner_matrix.append({
            'partner': p,
            'kam': kam_str,
            'raw_names': raw_str,
            'leads_aug': l_cnt_aug,
            'leads_sep': l_cnt_sep,
            'leads_delta': l_cnt_sep - l_cnt_aug,
            'deals_aug': d_cnt_aug,
            'deals_sep': d_cnt_sep,
            'deals_delta': d_cnt_sep - d_cnt_aug,
            'turnover_aug': turn_aug,
            'turnover_sep': turn_sep,
            'revenue_aug': rev_aug,
            'revenue_sep': rev_sep,
            'revenue_delta': rev_sep - rev_aug,
            'cr_aug': cr_aug,
            'cr_sep': cr_sep
        })

    # Sort partners matrix by September deals desc, then September leads desc
    partner_matrix.sort(key=lambda x: (x['deals_sep'], x['deals_aug'], x['leads_sep']), reverse=True)

    # 6. Commercial & Discounts Enrichment
    discount_info = {
        'avg_rrc': 2739455.0,
        'avg_final': 2513631.0,
        'avg_discount_rub': 225824.0,
        'avg_discount_pct': 8.24,
        'avg_sa_discount': 78162.0,
        'avg_dc_discount': 147662.0,
        'sa_discount_share': 34.6,
        'dc_discount_share': 65.4
    }
    da_brands = data.get('discount_analytics', {}).get('brands', [])
    for b in da_brands:
        if 'BELGEE' in str(b.get('brand', '')).upper():
            avg_fin = b.get('avg_final', 2513631.0)
            avg_disc = b.get('avg_discount_rub', 225824.0)
            avg_rrc = avg_fin + avg_disc
            discount_info = {
                'avg_rrc': avg_rrc,
                'avg_final': avg_fin,
                'avg_discount_rub': avg_disc,
                'avg_discount_pct': round((avg_disc / avg_rrc * 100), 2) if avg_rrc else 8.24,
                'avg_sa_discount': b.get('avg_sa_discount', 78162.0),
                'avg_dc_discount': b.get('avg_dc_discount', 147662.0),
                'sa_discount_share': round(b.get('avg_sa_discount', 78162.0) / avg_disc * 100, 1) if avg_disc else 34.6,
                'dc_discount_share': round(b.get('avg_dc_discount', 147662.0) / avg_disc * 100, 1) if avg_disc else 65.4
            }
            break

    # 7. CRM Funnel comparison
    crm_funnel = {
        '2026-08': {
            'vitrina': vitrina_stats['2026-08'],
            'leads': 280,
            'qual': 118,
            'qual_cr': round(118 / 280 * 100, 1),
            'calc_total': 134,
            'calc_cr': round(134 / 280 * 100, 1),
            'dealer': 22,
            'dealer_cr': round(22 / 280 * 100, 1),
            'trans_leads_db': len(leads_aug),
            'fdc_app': 28,
            'fdc_appr': 15,
            'fdc_appr_cr': round(15 / 28 * 100, 1),
            'deals': len(deals_aug),
            'turnover': sum_aug['turnover'],
            'revenue': sum_aug['revenue']
        },
        '2026-09': {
            'vitrina': vitrina_stats['2026-09'],
            'leads': 426,
            'qual': 312,
            'qual_cr': round(312 / 426 * 100, 1),
            'calc_total': 204,
            'calc_cr': round(204 / 426 * 100, 1),
            'dealer': 38,
            'dealer_cr': round(38 / 426 * 100, 1),
            'trans_leads_db': len(leads_sep),
            'fdc_app': 41,
            'fdc_appr': 16,
            'fdc_appr_cr': round(16 / 41 * 100, 1),
            'deals': len(deals_sep),
            'turnover': sum_sep['turnover'],
            'revenue': sum_sep['revenue']
        }
    }

    # Consolidated output payload
    belgee_analytics = {
        'generated_at': datetime.now().strftime("%d.%m.%Y %H:%M"),
        'brand': 'BELGEE',
        'august': sum_aug,
        'september': sum_sep,
        'vitrina': vitrina_stats,
        'crm_funnel': crm_funnel,
        'partner_matrix': partner_matrix,
        'discount_info': discount_info,
        'deals_aug': deals_aug,
        'deals_sep': deals_sep,
        'leads_aug': leads_aug,
        'leads_sep': leads_sep
    }

    out_json = os.path.join(PROJECT_ROOT, 'data', 'belgee_analytics.json')
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(belgee_analytics, f, ensure_ascii=False, indent=2)
    print(f"[2/5] Saved aggregated JSON to {out_json}")

    return belgee_analytics

if __name__ == '__main__':
    run()
