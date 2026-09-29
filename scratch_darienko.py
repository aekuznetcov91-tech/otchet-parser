import json

with open('scratch_all_rows.json', 'r', encoding='utf-8') as f:
    rows = json.load(f)

current_dealer = None
dealers = {}

for r in rows:
    row_num = r['row']
    if row_num < 2 or row_num > 125:
        continue
    
    vals = r['vals']
    d_name = vals[0]
    brand = vals[1]
    region = vals[2]
    plan_j = vals[9]
    fact_k = vals[10]
    
    if d_name is not None and str(d_name).strip():
        current_dealer = str(d_name).strip()
    
    if current_dealer not in dealers:
        dealers[current_dealer] = {
            'dealer': current_dealer,
            'region': region,
            'brands': [],
            'plans': [],
            'total_plan': 0.0,
            'rows': []
        }
    
    p_val = 0.0
    if plan_j is not None:
        try:
            p_val = float(plan_j)
        except ValueError:
            p_val = 0.0
            
    dealers[current_dealer]['brands'].append(brand)
    dealers[current_dealer]['plans'].append(plan_j)
    dealers[current_dealer]['total_plan'] += p_val
    dealers[current_dealer]['rows'].append(row_num)

total_raw_sum = sum(d['total_plan'] for d in dealers.values())
total_round_sum = sum(round(d['total_plan']) for d in dealers.values())

print(f"Total dealers in rows 2-125: {len(dealers)}")
print(f"Total raw sum of plans: {total_raw_sum:.2f}")
print(f"Total rounded sum of plans: {total_round_sum}")

output_dealers = []
for d_name, d_info in dealers.items():
    output_dealers.append({
        'dealer': d_name,
        'region': d_info['region'],
        'total_plan_raw': round(d_info['total_plan'], 2),
        'total_plan_round': int(round(d_info['total_plan'])),
        'rows_count': len(d_info['rows']),
        'items': [{'row': r, 'brand': b, 'plan': p} for r, b, p in zip(d_info['rows'], d_info['brands'], d_info['plans'])]
    })

with open('scratch_darienko_dealers.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total_dealers': len(dealers),
        'total_raw_sum': round(total_raw_sum, 2),
        'total_round_sum': total_round_sum,
        'dealers': output_dealers
    }, f, ensure_ascii=False, indent=2)

print("Saved scratch_darienko_dealers.json")
