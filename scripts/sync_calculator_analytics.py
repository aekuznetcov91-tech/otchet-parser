"""Fetch calculator logs and save only anonymous aggregates for reproducible ETL."""
import argparse
import json
import os
from pathlib import Path
import sys
import urllib.request
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.etl.calculator import SNAPSHOT, aggregate_calculator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, help='Local JSON export instead of API')
    args = parser.parse_args()
    if args.input:
        rows = json.loads(args.input.read_text())
    else:
        config = Path(__file__).resolve().parents[1] / 'config.local.json'
        settings = json.loads(config.read_text()) if config.exists() else {}
        url = os.environ.get('CALCULATOR_ANALYTICS_URL') or settings.get('calculator_analytics_url')
        if not url:
            raise SystemExit('Set calculator_analytics_url in config.local.json or CALCULATOR_ANALYTICS_URL')
        with urllib.request.urlopen(url + ('&' if '?' in url else '?') + 't=' + str(time.time_ns()), timeout=120) as response:
            rows = json.load(response)
    snapshot = aggregate_calculator(rows)
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    temp = SNAPSHOT.with_suffix('.tmp')
    temp.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n')
    temp.replace(SNAPSHOT)
    print(f"Calculator: {snapshot['raw_rows']} rows, last event {snapshot['last_event']}")


if __name__ == '__main__':
    main()
