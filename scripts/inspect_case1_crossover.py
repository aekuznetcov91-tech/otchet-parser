import pickle
import pandas as pd
from collections import defaultdict, Counter

with open('scratch/cross_brand_data.pkl', 'rb') as f:
    data = pickle.load(f)

deals_by_client = data['deals_by_client']
partner_leads_by_client = data['partner_leads_by_client']
crm_leads_by_client = data['crm_leads_by_client']

def is_jetour_soueast(brand_str):
    if not brand_str: return False
    b = str(brand_str).upper()
    return any(k in b for k in ('JETOUR', 'SOUEAST', 'SOUEAS', 'ДЖЕТУР', 'СОУИСТ', 'DASHING', 'X70', 'X90', 'T2', 'S07', 'S09'))

crossover_details = []

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
    
    if other_leads:
        # Sort all leads by date
        valid_dated_leads = [l for l in all_leads if l.get('date')]
        valid_dated_leads.sort(key=lambda x: x['date'])
        
        first_lead = valid_dated_leads[0] if valid_dated_leads else None
        first_is_other = first_lead and not is_jetour_soueast(first_lead.get('brand_norm') or first_lead.get('brand_raw'))
        
        for deal in js_deals:
            other_brands = sorted(set(l.get('brand_norm') or l.get('brand_raw') for l in other_leads))
            crossover_details.append({
                'client_id': cid,
                'first_lead_brand': (first_lead.get('brand_norm') or first_lead.get('brand_raw')) if first_lead else 'N/A',
                'first_lead_date': first_lead.get('date_str') if first_lead else 'N/A',
                'first_is_other': first_is_other,
                'other_brands_requested': ", ".join(other_brands),
                'bought_brand': deal.get('brand'),
                'bought_tovar': deal.get('tovar'),
                'deal_date': deal.get('date_str'),
                'price': deal.get('price'),
                'b2c': deal.get('b2c'),
                'manager': deal.get('manager'),
                'deal_id': deal.get('deal_id')
            })

df_cross = pd.DataFrame(crossover_details).drop_duplicates(subset=['client_id', 'deal_id'])
print(f"Total crossover deal records: {len(df_cross)}")
print(f"Cases where FIRST lead was strictly another brand: {len(df_cross[df_cross['first_is_other'] == True])}")

print("\nBreakdown of initial other brands that clients requested before buying Jetour/Soueast:")
other_brand_counter = Counter()
for b_list in df_cross[df_cross['first_is_other'] == True]['other_brands_requested']:
    for b in b_list.split(', '):
        other_brand_counter[b] += 1
for b, c in other_brand_counter.most_common(10):
    print(f"  {b}: {c}")

print("\nSample records where first lead was another brand:")
sample_first_other = df_cross[df_cross['first_is_other'] == True].head(15)
print(sample_first_other[['client_id', 'first_lead_brand', 'first_lead_date', 'bought_brand', 'bought_tovar', 'deal_date', 'price', 'b2c', 'manager']].to_string(index=False))

