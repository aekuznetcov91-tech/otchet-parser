import pickle
import pandas as pd
from collections import defaultdict, Counter

with open('scratch/cross_brand_data.pkl', 'rb') as f:
    data = pickle.load(f)

deals_by_client = data['deals_by_client']
partner_leads_by_client = data['partner_leads_by_client']
crm_leads_by_client = data['crm_leads_by_client']

print(f"Total clients with deals: {len(deals_by_client)}")
print(f"Total clients with partner leads: {len(partner_leads_by_client)}")
print(f"Total clients with CRM leads: {len(crm_leads_by_client)}")

def is_jetour_soueast(brand_str):
    if not brand_str: return False
    b = str(brand_str).upper()
    return any(k in b for k in ('JETOUR', 'SOUEAST', 'SOUEAS', 'ДЖЕТУР', 'СОУИСТ', 'DASHING', 'X70', 'X90', 'T2', 'S07', 'S09'))

# ==============================================================================
# CASE 1: Client submitted lead for other brand (not Jetour/Soueast), but bought Jetour or Soueast
# ==============================================================================
print("\n" + "="*80)
print("CASE 1: Lead for other brand -> Bought JETOUR or SOUEAST")
print("="*80)

case1_pure_cross = [] # Client had leads ONLY for other brands (never Jetour/Soueast lead)
case1_crossover = []  # Client had leads for other brands AND Jetour/Soueast

for cid, dlist in deals_by_client.items():
    # Check if client bought Jetour or Soueast
    js_deals = [d for d in dlist if is_jetour_soueast(d.get('brand'))]
    if not js_deals:
        continue
    
    # Collect all leads for this client (CRM and Partner)
    c_crm = crm_leads_by_client.get(cid, [])
    c_part = partner_leads_by_client.get(cid, [])
    
    if not c_crm and not c_part:
        # No lead record in our lead exports (might be direct walk-in, offline, or MP2)
        continue
    
    lead_brands = []
    for l in c_crm:
        b = l.get('brand_norm') or l.get('brand_raw')
        if b: lead_brands.append((b, l.get('model'), l.get('date_str'), 'CRM', l.get('event')))
    for l in c_part:
        b = l.get('brand_norm') or l.get('brand_raw')
        if b: lead_brands.append((b, l.get('model'), l.get('date_str'), 'Partner', l.get('partner')))
        
    other_lead_brands = [lb for lb in lead_brands if not is_jetour_soueast(lb[0])]
    js_lead_brands = [lb for lb in lead_brands if is_jetour_soueast(lb[0])]
    
    if other_lead_brands and not js_lead_brands:
        case1_pure_cross.append({
            'client_id': cid,
            'deals': js_deals,
            'other_leads': other_lead_brands,
            'all_leads': lead_brands
        })
    elif other_lead_brands and js_lead_brands:
        case1_crossover.append({
            'client_id': cid,
            'deals': js_deals,
            'other_leads': other_lead_brands,
            'js_leads': js_lead_brands,
            'all_leads': lead_brands
        })

print(f"1. Pure Cross-Sell cases (ONLY leads on other brands, bought Jetour/Soueast): {len(case1_pure_cross)}")
print(f"2. Multi-brand Crossover cases (Leads on other brands + Jetour/Soueast, bought Jetour/Soueast): {len(case1_crossover)}")
print(f"TOTAL Case 1 clients: {len(case1_pure_cross) + len(case1_crossover)}")

# ==============================================================================
# CASE 2: Transferred lead for JETOUR or SOUEAST -> Bought a DIFFERENT car
# ==============================================================================
print("\n" + "="*80)
print("CASE 2: Transferred lead for JETOUR or SOUEAST -> Bought a DIFFERENT car")
print("="*80)

case2_clients = []

for cid, dlist in deals_by_client.items():
    # Check if client bought a DIFFERENT brand (not Jetour, not Soueast)
    diff_deals = [d for d in dlist if not is_jetour_soueast(d.get('brand')) and d.get('brand')]
    if not diff_deals:
        continue
    
    # Check if client had a TRANSFERRED lead for Jetour or Soueast
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
        case2_clients.append({
            'client_id': cid,
            'transfers': js_transfers,
            'diff_deals': diff_deals,
            'all_deals': dlist
        })

print(f"TOTAL Case 2 clients: {len(case2_clients)}")

