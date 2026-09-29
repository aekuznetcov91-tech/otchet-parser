import json

with open('scratch_matched_darienko.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

planned_dealers = [it for it in items if it['plan_raw'] > 0]

lines = []
lines.append(f"Total planned dealers: {len(planned_dealers)}")
lines.append(f"Raw sum: {sum(it['plan_raw'] for it in planned_dealers):.2f}")
lines.append(f"Rounded sum: {sum(it['plan_round'] for it in planned_dealers)}\n")

for idx, it in enumerate(planned_dealers, 1):
    brands_str = ', '.join([f"{x['brand']} ({x['plan']})" for x in it['items'] if x['plan'] > 0])
    lines.append(f"{idx:2d}. {it['excel_dealer']} [{it['region']}] -> raw: {it['plan_raw']:.1f}, round: {it['plan_round']} | Matched: {it['matched_id']} - {it['matched_name']} ({it['matched_kam']}) | Brands: {brands_str}")

with open('scratch_planned_table.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Wrote scratch_planned_table.txt")
