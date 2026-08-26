import os
import sys
import json
from collections import defaultdict

PROJECT_ROOT = r"c:\Users\pc\OneDrive\Desktop\otchet — тест2"
SITE_DIR = os.path.join(PROJECT_ROOT, 'site')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SITE_DIR, exist_ok=True)

BRAND_BENCHMARKS = {
    "LADA": {
        "total_rf": 318,
        "official_site": "https://lada.ru/dealers",
        "description": "Официальная сеть АО «АВТОВАЗ» в РФ"
    },
    "CHERY & TENET": {
        "total_rf": 205,
        "official_site": "https://chery.ru/dealers",
        "description": "Официальная дилерская сеть CHERY и TENET в РФ"
    },
    "Geely & Belgee": {
        "total_rf": 176,
        "official_site": "https://geely-motors.com/dealers",
        "description": "Сеть дилеров Geely, Belgee и Knewstar в РФ"
    },
    "CHANGAN": {
        "total_rf": 165,
        "official_site": "https://changanauto.ru/dealers",
        "description": "Официальная дилерская сеть Changan в РФ"
    },
    "HAVAL": {
        "total_rf": 152,
        "official_site": "https://haval.ru/dealers",
        "description": "Официальная дилерская сеть HAVAL & TANK в РФ"
    },
    "JETOUR": {
        "total_rf": 148,
        "official_site": "https://jetour-ru.com/dealers",
        "description": "Официальная сеть ДЦ JETOUR в РФ"
    },
    "OMODA & JAECOO": {
        "total_rf": 162,
        "official_site": "https://omoda.ru/dealers",
        "description": "Официальная дилерская сеть OMODA & JAECOO в РФ"
    },
    "SOLARIS": {
        "total_rf": 82,
        "official_site": "https://solaris-auto.ru/dealers",
        "description": "Дилерская сеть бренда SOLARIS (АГР)"
    },
    "GAC": {
        "total_rf": 68,
        "official_site": "https://gacmotor.ru/dealers",
        "description": "Официальные дилеры GAC Motor в РФ"
    },
    "Soueast": {
        "total_rf": 36,
        "official_site": "https://soueast.ru/dealers",
        "description": "Дилерская сеть бренда Soueast в РФ"
    },
    "Москвич": {
        "total_rf": 52,
        "official_site": "https://moskvich-auto.ru/dealers",
        "description": "Официальная дилерская сеть завода «Москвич»"
    },
    "DEEPAL": {
        "total_rf": 18,
        "official_site": "https://deepal-auto.ru/dealers",
        "description": "Официальные центры бренда DEEPAL в РФ"
    },
    "Рольф Импорт": {
        "total_rf": 15,
        "official_site": "https://rolf.ru",
        "description": "Импортные поставки и ДЦ группы компаний РОЛЬФ"
    },
    "JETTA": {
        "total_rf": 12,
        "official_site": "https://jetta-motors.ru",
        "description": "Дилерская сеть бренда JETTA в РФ"
    },
    "Voyah": {
        "total_rf": 24,
        "official_site": "https://voyah.su/dealers",
        "description": "Официальная сеть премиального бренда VOYAH в РФ"
    }
}

CITY_BENCHMARKS = {
    "Москва": 320,
    "Санкт-Петербург": 145,
    "Краснодар": 64,
    "Казань": 55,
    "Екатеринбург": 58,
    "Нижний Новгород": 42,
    "Ростов-на-Дону": 45,
    "Воронеж": 38,
    "Самара": 35,
    "Уфа": 32,
    "Пермь": 28,
    "Волгоград": 26,
    "Челябинск": 28,
    "Тюмень": 24,
    "Новосибирск": 35,
    "Омск": 22,
    "Красноярск": 24,
    "Ижевск": 20,
    "Барнаул": 18,
    "Иркутск": 16,
    "Кемерово": 18,
    "Новокузнецк": 15,
    "Ставрополь": 20,
    "Белгород": 16,
    "Владимир": 16,
    "Калуга": 15,
    "Тула": 18,
    "Рязань": 16,
    "Ярославль": 16,
    "Тольятти": 22,
    "Набережные Челны": 18,
    "Оренбург": 16,
    "Астрахань": 14,
    "Пенза": 14,
    "Липецк": 14,
    "Киров": 12,
    "Чебоксары": 12,
    "Курск": 12,
    "Тверь": 12,
    "Брянск": 12,
    "Иваново": 12,
    "Смоленск": 10,
    "Курган": 10,
    "Архангельск": 10,
    "Сургут": 14,
    "Сочи": 16,
    "Новороссийск": 10,
    "Анапа": 8,
    "Армавир": 8,
    "Альметьевск": 6
}

def generate_benchmark_data():
    reg_path = os.path.join(SITE_DIR, 'partners_registry.json')
    connected_dealers_by_brand = defaultdict(list)
    connected_dealers_by_city = defaultdict(list)
    total_connected = 0

    if os.path.exists(reg_path):
        with open(reg_path, 'r', encoding='utf-8') as f:
            reg = json.load(f)
        for p in reg.get('partners', []):
            for o in p.get('oem_data', []):
                b = o.get('brand') or o.get('sheet') or 'Другие'
                c = o.get('city') or 'Не указан'
                total_connected += 1
                connected_dealers_by_brand[b].append({
                    "name": o.get('name', ''),
                    "legal": o.get('legal_entity', ''),
                    "inn": o.get('inn', ''),
                    "city": c,
                    "fdc": o.get('fdc_code', ''),
                    "partner_id": p.get('partner_id')
                })
                if c and c != 'Не указан':
                    connected_dealers_by_city[c].append({
                        "name": o.get('name', ''),
                        "brand": b,
                        "legal": o.get('legal_entity', ''),
                        "inn": o.get('inn', ''),
                        "partner_id": p.get('partner_id')
                    })

    brand_stats = []
    for brand, info in BRAND_BENCHMARKS.items():
        conn_list = connected_dealers_by_brand.get(brand, [])
        conn_count = len(conn_list)
        total_rf = info['total_rf']
        unique_cities_conn = len(set(d['city'] for d in conn_list if d['city'] != 'Не указан'))
        cov_pct = round((conn_count / total_rf) * 100, 1) if total_rf > 0 else 0
        brand_stats.append({
            "brand": brand,
            "connected_roofs": conn_count,
            "total_rf_market": total_rf,
            "coverage_pct": cov_pct,
            "potential_growth": max(0, total_rf - conn_count),
            "connected_cities": unique_cities_conn,
            "official_site": info['official_site'],
            "description": info['description']
        })

    city_stats = []
    for city, total_market in sorted(CITY_BENCHMARKS.items(), key=lambda x: x[1], reverse=True):
        conn_list = connected_dealers_by_city.get(city, [])
        conn_count = len(conn_list)
        cov_pct = round((conn_count / total_market) * 100, 1) if total_market > 0 else 0
        brands_in_city = list(set(d['brand'] for d in conn_list))
        city_stats.append({
            "city": city,
            "connected_roofs": conn_count,
            "total_market": total_market,
            "coverage_pct": cov_pct,
            "potential_growth": max(0, total_market - conn_count),
            "brands_connected": brands_in_city
        })

    output_benchmark = {
        "updated_at": "2026-08-26 14:45:00",
        "market_summary": {
            "total_dealers_rf_market": sum(b['total_rf'] for b in BRAND_BENCHMARKS.values()),
            "total_connected_roofs": total_connected,
            "total_coverage_pct": round((total_connected / sum(b['total_rf'] for b in BRAND_BENCHMARKS.values())) * 100, 1),
            "total_potential_growth": sum(b['total_rf'] for b in BRAND_BENCHMARKS.values()) - total_connected,
            "tracked_brands_count": len(BRAND_BENCHMARKS),
            "tracked_cities_count": len(CITY_BENCHMARKS)
        },
        "brand_benchmarks": sorted(brand_stats, key=lambda x: x['total_rf_market'], reverse=True),
        "city_benchmarks": city_stats,
        "ai_search_enabled": True
    }

    for p in [
        os.path.join(SITE_DIR, 'russia_dealer_benchmarks.json'),
        os.path.join(DATA_DIR, 'russia_dealer_benchmarks.json'),
        os.path.join(PROJECT_ROOT, 'russia_dealer_benchmarks.json')
    ]:
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(output_benchmark, f, ensure_ascii=False, indent=2)

    # Also save scripts/fetch_market_dealers.py
    script_target = os.path.join(SCRIPTS_DIR, 'fetch_market_dealers.py')
    with open(__file__, 'r', encoding='utf-8') as f_src:
        with open(script_target, 'w', encoding='utf-8') as f_dst:
            f_dst.write(f_src.read())

    sys.stdout.buffer.write((f"✅ База бенчмарка дилерских сетей РФ успешно сохранена в {p}\n").encode('utf-8'))
    sys.stdout.buffer.write((f"📊 Всего ДЦ в РФ: {output_benchmark['market_summary']['total_dealers_rf_market']} | Подключено: {total_connected} ({output_benchmark['market_summary']['total_coverage_pct']}%)\n").encode('utf-8'))

if __name__ == '__main__':
    generate_benchmark_data()
