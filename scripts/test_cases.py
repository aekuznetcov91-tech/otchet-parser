import sys
import os
from collections import defaultdict

sys.path.append('.')
from scripts.find_cross_brand_cases import deals_by_client, all_deals

jetour_soueast_buyers = set()
other_buyers = set()

for cid, dlist in deals_by_client.items():
    brands = {d['brand'] for d in dlist}
    if any(b in ('JETOUR', 'SOUEAST') for b in brands):
        jetour_soueast_buyers.add(cid)
    if any(b not in ('JETOUR', 'SOUEAST', None, '') for b in brands):
        other_buyers.add(cid)

print(f"Clients who bought JETOUR or SOUEAST: {len(jetour_soueast_buyers)}")
print(f"Clients who bought other brands: {len(other_buyers)}")
