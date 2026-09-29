import json

with open('scratch_all_dealers.json', 'r', encoding='utf-8') as f:
    rows = json.load(f)

by_dealer = {}
total_plan = 0

for r in rows:
    d = r['dealer'] or 'UNKNOWN'
    p = r['plan_j']
    if p is not None:
        try:
            p_float = float(p)
        except ValueError:
            p_float = 0.0
    else:
        p_float = 0.0
    
    if d not in by_dealer:
        by_dealer[d] = {'brands': [], 'plans': [], 'total_plan': 0.0, 'rows': []}
    
    by_dealer[d]['brands'].append(r['brand'])
    by_dealer[d]['plans'].append(p)
    by_dealer[d]['total_plan'] += p_float
    by_dealer[d]['rows'].append(r['row'])
    total_plan += p_float

print(f'Distinct dealers: {len(by_dealer)}')
print(f'Total plan sum: {total_plan:.2f}')

output_list = []
for d, info in by_dealer.items():
    output_list.append({
        'dealer': d,
        'total_plan': round(info['total_plan'], 2),
        'row_count': len(info['rows']),
        'rows': info['rows'],
        'brands_plans': list(zip(info['brands'], info['plans']))
    })

with open('scratch_dealers_summary.json', 'w', encoding='utf-8') as f:
    json.dump({'total_plan': round(total_plan, 2), 'dealers': output_list}, f, ensure_ascii=False, indent=2)

print('Saved scratch_dealers_summary.json')
