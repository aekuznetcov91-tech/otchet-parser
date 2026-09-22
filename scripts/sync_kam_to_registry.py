import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import json
from scripts.oem_kam_resolver import OemKamResolver
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'raw_data')

def sync_kam_to_registry():
    print("[*] Синхронизация Master Partners Registry с OEM СберАвто финал (15)...")
    oem_file = os.path.join(RAW_DATA_DIR, 'OEM СберАвто финал (15).xlsx')
    if not os.path.exists(oem_file):
        print(f"[!] Warning: OEM file not found: {oem_file}")
        return

    resolver = OemKamResolver(oem_file)
    reg_paths = [
        os.path.join(PROJECT_ROOT, 'partners_registry.json'),
        os.path.join(PROJECT_ROOT, 'data', 'partners_registry.json'),
        os.path.join(PROJECT_ROOT, 'site', 'partners_registry.json'),
    ]

    base_reg = None
    for rp in reg_paths:
        if os.path.exists(rp):
            with open(rp, 'r', encoding='utf-8') as f:
                base_reg = json.load(f)
            break

    if not base_reg:
        print("[!] Warning: partners_registry.json not found")
        return

    partners = base_reg.get('partners', [])
    updated_count = 0

    for p in partners:
        current_kam = p.get('kam', 'Не назначен')
        inns = p.get('inns', [])
        p_name = p.get('canonical_name') or p.get('name') or ''
        aliases = p.get('aliases', [])

        new_kam = None
        for inn in inns:
            res = resolver.resolve(inn=inn, fallback_kam=None)
            if res and res != 'Не назначен':
                new_kam = res
                break

        if not new_kam:
            res = resolver.resolve(partner_name=p_name, fallback_kam=None)
            if res and res != 'Не назначен':
                new_kam = res

        if not new_kam:
            for al in aliases:
                res = resolver.resolve(partner_name=al, fallback_kam=None)
                if res and res != 'Не назначен':
                    new_kam = res
                    break

        if new_kam and new_kam != current_kam:
            p['kam'] = new_kam
            updated_count += 1

    print(f"[*] Актуализировано КАМ в реестре: {updated_count} партнеров.")

    for rp in reg_paths:
        os.makedirs(os.path.dirname(rp), exist_ok=True)
        with open(rp, 'w', encoding='utf-8') as f:
            json.dump(base_reg, f, ensure_ascii=False, indent=2)

    print("[+] Реестр партнеров успешно сохранен во всех директориях.")

if __name__ == '__main__':
    sync_kam_to_registry()
