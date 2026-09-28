import json

with open('active_splits.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect all groups
sections = text.split("==================== ROOT: ")
print(f"Total sections: {len(sections)-1}")

with open('splits_summary.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total sections: {len(sections)-1}\n")
    for sec in sections[1:]:
        lines = sec.strip().splitlines()
        root_name = lines[0].split(" ")[0].strip("'")
        entries = []
        curr = {}
        for l in lines[1:]:
            if l.strip().startswith("ID "):
                if curr: entries.append(curr)
                curr = {'header': l.strip(), 'names': [], 'kam': '', 'stats': '', 'raw': []}
            elif 'Names in data:' in l:
                curr['names'] = l.split("Names in data:")[1].strip()
            elif 'KAM:' in l:
                curr['kam'] = l.split("KAM:")[1].strip()
            elif 'Stats ->' in l:
                curr['stats'] = l.split("Stats ->")[1].strip()
            elif 'Raw sample:' in l:
                curr['raw'] = l.split("Raw sample:")[1].strip()
        if curr: entries.append(curr)
        
        out.write(f"\n--- {root_name} ({len(entries)} IDs) ---\n")
        for e in entries:
            out.write(f"  {e['header']} | {e['kam']} | {e['stats']}\n")
