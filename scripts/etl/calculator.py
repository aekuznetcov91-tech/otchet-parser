"""Aggregate observed calculator events. Raw client data never enters the snapshot."""
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from .config import DATA_DIR
from .normalization import normalize_brand

SNAPSHOT = Path(DATA_DIR) / 'calculator_analytics.json'
ACTIONS = {
    'Расчет автомобиля': 'calc', 'Клиент на калькуляторе': 'calc',
    'Оффер отправлен клиенту': 'offer', 'Отправлено сравнение': 'offer',
    'Отправлена подборка авто': 'offer', 'DIRECT_OFFER_COPIED': 'offer',
    'REVERSE_COPIED': 'offer', 'COMPARE_COPIED': 'offer',
    'Анкета ФДЦ заполнена': 'fdc_form', 'CRM_FORM_FILLED': 'fdc_form',
}


def event_date(value):
    try:
        return datetime.strptime(str(value).strip(), '%d.%m.%Y, %H:%M:%S')
    except ValueError:
        return None


def client_id(value):
    value = str(value or '').strip()
    # CRM IDs are decimal identifiers. Placeholders and links are not identities.
    return str(int(value.split('.')[0])) if re.fullmatch(r'\d+(?:\.0)?', value) and int(value.split('.')[0]) > 0 else ''


def event_brand(car, month):
    text = str(car or '').upper()
    brand = normalize_brand(text, month=month)
    if brand == 'CHERY & TENET':
        return 'TENET' if re.search(r'TENET|ТЕНЕТ', text) else 'CHERY'
    if brand == 'OMODA & JAECOO':
        return 'JAECOO' if re.search(r'JAECOO|ДЖЕЙКУ|ДЖАКУ', text) else 'OMODA'
    known = {'JETOUR', 'LADA', 'CHANGAN', 'GAC', 'SOLARIS', 'SOUEAST', 'BELGEE',
             'GEELY', 'KNEWSTAR', 'HAVAL', 'JELAND', 'МОСКВИЧ', 'TOYOTA', 'TANK',
             'EXEED', 'HONGQI', 'XCITE', 'KIA', 'HYUNDAI', 'VOYAH', 'DEEPAL'}
    # normalize_brand has a permissive first-word fallback; never publish free text.
    return str(brand).upper() if str(brand).upper() in known else 'НЕ ОПРЕДЕЛЁН'


def aggregate_calculator(rows, fetched_at=None):
    if not isinstance(rows, list) or not rows or any(not isinstance(r, dict) for r in rows):
        raise ValueError('Calculator API must return a non-empty array of events')
    buckets = defaultdict(lambda: defaultdict(lambda: {'events': 0, 'clients': set(), 'without_id': 0}))
    dates, invalid_dates, seen, duplicates = [], 0, set(), 0
    for row in rows:
        signature = tuple(str(row.get(k, '')) for k in ('timestamp', 'managerId', 'clientId', 'action', 'details', 'clientLink'))
        if signature in seen:
            duplicates += 1
            continue
        seen.add(signature)
        dt = event_date(row.get('timestamp'))
        if not dt:
            invalid_dates += 1
            continue
        dates.append(dt)
        kind = ACTIONS.get(row.get('action'))
        if not kind:
            continue
        try:
            details = json.loads(row.get('details') or '{}')
        except (ValueError, TypeError):
            details = {}
        if not isinstance(details, dict):
            details = {}
        month = dt.strftime('%Y-%m')
        # No inference from client history: clients may compare multiple brands.
        brand = event_brand(details.get('car') or details.get('brand', ''), month)
        cid = client_id(row.get('clientId'))
        for period, scope in [(month, brand), (month, 'ALL'), ('all', brand), ('all', 'ALL')]:
            item = buckets[(period, scope)][kind]
            item['events'] += 1
            if cid:
                item['clients'].add(cid)
            else:
                item['without_id'] += 1
    if not dates:
        raise ValueError('Calculator response has no valid timestamps')
    by_month = {}
    first, last = min(dates), max(dates)
    # Every covered month has an explicit zero baseline; outside coverage is unavailable.
    year, month = first.year, first.month
    periods = ['all']
    while (year, month) <= (last.year, last.month):
        periods.append(f'{year:04d}-{month:02d}')
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    for period in periods:
        scopes = {'ALL'} | {scope for p, scope in buckets if p == period}
        by_month[period] = {}
        for scope in sorted(scopes):
            by_month[period][scope] = {}
            for kind in ('calc', 'offer', 'fdc_form'):
                item = buckets[(period, scope)][kind]
                by_month[period][scope][kind] = {
                    'events': item['events'], 'clients': len(item['clients']),
                    'without_id': item['without_id'],
                }
    return {'schema_version': 1, 'source': 'Google Sheets / Calculator',
            'fetched_at': fetched_at or datetime.now(timezone.utc).isoformat(),
            'first_event': first.isoformat(), 'last_event': last.isoformat(),
            'raw_rows': len(rows), 'duplicates_removed': duplicates,
            'invalid_dates': invalid_dates, 'by_month': by_month}


def load_calculator_snapshot():
    if not SNAPSHOT.exists():
        return None
    data = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    if data.get('schema_version') != 1 or not isinstance(data.get('by_month'), dict):
        raise ValueError('Invalid calculator snapshot; refresh it before running ETL')
    return data


def calculator_metrics(snapshot, month, brand):
    if not snapshot or month not in snapshot['by_month']:
        return None
    return snapshot['by_month'][month].get(brand, {
        key: {'events': 0, 'clients': 0, 'without_id': 0} for key in ('calc', 'offer', 'fdc_form')})
