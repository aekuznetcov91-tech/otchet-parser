"""Compare isolated old/new ETL outputs, excluding only generation timestamps.

Run both pipelines with PYTHONHASHSEED=0 and identical copies of input files.
Never run the baseline pipeline against the production checkout.
"""
import argparse
import json
from pathlib import Path

FILES = ('site/data.json', 'site/geo_clients.json', 'site/banking_deals.json',
         'data/historical_deals_cache.json', 'data/partners_registry.json')


def compare(before, after):
    for name in FILES:
        values = [json.loads((root / name).read_text(encoding='utf-8')) for root in (before, after)]
        if name == 'site/data.json':
            for value in values:
                value['metadata'].pop('updated_at', None)
                value.get('banking_analytics', {}).pop('updated_at', None)
        if values[0] != values[1]:
            raise RuntimeError('ETL output changed: ' + name)
        print('Equivalent:', name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    args = parser.parse_args()
    compare(args.before, args.after)
