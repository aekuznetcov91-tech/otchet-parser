import pickle
import pandas as pd
from collections import defaultdict

with open('scratch/cross_brand_data.pkl', 'rb') as f:
    data = pickle.load(f)

deals_by_client = data['deals_by_client']
partner_leads_by_client = data['partner_leads_by_client']
crm_leads_by_client = data['crm_leads_by_client']

def is_jetour_soueast(brand_str):
    if not brand_str: return False
    b = str(brand_str).upper()
    return any(k in b for k in ('JETOUR', 'SOUEAST', 'SOUEAS', 'ДЖЕТУР', 'СОУИСТ', 'DASHING', 'X70', 'X90', 'T2', 'S07', 'S09'))

print("="*100)
print("DETAILS FOR CASE 2: TRANSFERRED JETOUR/SOUEAST LEAD -> BOUGHT DIFFERENT CAR")
print("="*100)

case2_records = []
for cid, dlist in deals_by_client.items():
    diff_deals = [d for d in dlist if not is_jetour_soueast(d.get('brand')) and d.get('brand')]
    if not diff_deals:
        continue
    c_part = partner_leads_by_client.get(cid, [])
    c_crm = crm_leads_by_client.get(cid, [])
    
    js_transfers = []
    for l in c_part:
        b = l.get('brand_norm') or l.get('brand_raw')
        if is_jetour_soueast(b):
            js_transfers.append(l)
    for l in c_crm:
        if l.get('is_transferred'):
            b = l.get('brand_norm') or l.get('brand_raw')
            if is_jetour_soueast(b):
                js_transfers.append(l)
                
    if js_transfers:
        for t in js_transfers:
            for deal in diff_deals:
                case2_records.append({
                    'client_id': cid,
                    'lead_brand': t.get('brand_norm') or t.get('brand_raw'),
                    'lead_model': t.get('model'),
                    'partner': t.get('partner'),
                    'lead_date': t.get('date_str'),
                    'bought_brand': deal.get('brand'),
                    'bought_tovar': deal.get('tovar'),
                    'deal_date': deal.get('date_str'),
                    'price': deal.get('price'),
                    'b2c': deal.get('b2c'),
                    'deal_id': deal.get('deal_id'),
                    'manager': deal.get('manager'),
                    'company': deal.get('company')
                })

df_c2 = pd.DataFrame(case2_records).drop_duplicates(subset=['client_id', 'bought_tovar', 'deal_id'])
print(f"Unique Case 2 deal pairings: {len(df_c2)}")
print(df_c2.to_string(index=False))

print("\n" + "="*100)
print("DETAILS FOR CASE 1 (PURE CROSS-SELL): ONLY OTHER LEADS -> BOUGHT JETOUR/SOUEAST")
print("="*100)

case1_pure = []
for cid, dlist in deals_by_client.items():
    js_deals = [d for d in dlist if is_jetour_soueast(d.get('brand'))]
    if not js_deals: continue
    
    c_crm = crm_leads_by_client.get(cid, [])
    c_part = partner_leads_by_client.get(cid, [])
    
    all_leads = []
    for l in c_crm:
        b = l.get('brand_norm') or l.get('brand_raw')
        if b: all_leads.append(l)
    for l in c_part:
        b = l.get('brand_norm') or l.get('brand_raw')
        if b: all_leads.append(l)
        
    other_leads = [l for l in all_leads if not is_jetour_soueast(l.get('brand_norm') or l.get('brand_raw'))]
    js_leads = [l for l in all_leads if is_jetour_soueast(l.get('brand_norm') or l.get('brand_raw'))]
    
    if other_leads and not js_leads:
        for deal in js_deals:
            lead_brands_str = ", ".join(sorted(set(f"{l.get('brand_norm') or l.get('brand_raw')} {l.get('model', '')}".strip() for l in other_leads)))
            lead_dates_str = ", ".join(sorted(set(l.get('date_str') for l in other_leads if l.get('date_str'))))
            case1_pure.append({
                'client_id': cid,
                'lead_inquiry': lead_brands_str,
                'lead_dates': lead_dates_str,
                'bought_brand': deal.get('brand'),
                'bought_tovar': deal.get('tovar'),
                'deal_date': deal.get('date_str'),
                'price': deal.get('price'),
                'b2c': deal.get('b2c'),
                'deal_id': deal.get('deal_id'),
                'manager': deal.get('manager')
            })

df_c1_pure = pd.DataFrame(case1_pure).drop_duplicates(subset=['client_id', 'bought_tovar', 'deal_id'])
print(f"Unique Pure Cross-sell pairings: {len(df_c1_pure)}")
print(df_c1_pure.to_string(index=False))

