import json

with open('scratch_matched_darienko.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

planned_dealers = [it for it in items if it['plan_raw'] > 0]
print(f"Total planned dealers (plan > 0): {len(planned_dealers)}")
print(f"Sum of raw plans: {sum(it['plan_raw'] for it in planned_dealers):.2f}")
print(f"Sum of round plans: {sum(it['plan_round'] for it in planned_dealers)}")

for idx, it in enumerate(planned_dealers, 1):
    brands_str = ', '.join([f"{x['brand']} ({x['plan']})" for x in it['items'] if x['plan'] > 0])
    print(f"{idx:2d}. {it['excel_dealer']} [{it['region']}] -> raw: {it['plan_raw']:.1f}, round: {it['plan_round']} | Matched: {it['matched_id']} - {it['matched_name']} ({it['matched_kam']}) | Brands: {brands_str}")
