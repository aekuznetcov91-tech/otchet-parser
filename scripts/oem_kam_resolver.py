import os
import re
import openpyxl
from collections import defaultdict

def clean_inn(val):
    if val is None:
        return ''
    s = re.sub(r'\D', '', str(val).split('.')[0].strip())
    if not s or s == '0':
        return ''
    if len(s) == 9 or len(s) == 11:
        s = '0' + s
    return s

def clean_key(s):
    return re.sub(r'[^A-ZА-Я0-9]', '', str(s or '').upper())

def normalize_kam(val):
    if not val:
        return 'Не назначен'
    s = str(val).strip()
    sl = s.lower()
    if 'добролюбова' in sl:
        return 'Евгения Добролюбова'
    if 'кузнецов' in sl:
        return 'Андрей Кузнецов'
    if 'чихарев' in sl or 'чихарёв' in sl:
        return 'Алексей Чихарев'
    if 'дариенко' in sl:
        return 'Светлана Дариенко'
    if 'солдатова' in sl:
        return 'Валерия Солдатова'
    return s

class OemKamResolver:
    def __init__(self, oem_excel_path):
        self.oem_excel_path = oem_excel_path
        self.inn_map = {} # inn -> {'default': kam, 'brands': {brand: kam}, 'cities': {city: kam}}
        self.exact_name_map = {} # clean_key(name) -> kam
        self.dc_name_map = {} # clean_key(dc_name) -> kam
        self.brand_inn_map = {} # (inn, brand) -> kam
        self.holding_rules = []
        self._load()

    def _load(self):
        if not os.path.exists(self.oem_excel_path):
            print(f"[!] Warning: OEM file not found: {self.oem_excel_path}")
            return

        wb = openpyxl.load_workbook(self.oem_excel_path, data_only=True)
        inn_entries = defaultdict(list)

        for sname in wb.sheetnames:
            ws = wb[sname]
            headers = []
            resp_col, inn_col, name_col, city_col, brand_col = -1, -1, -1, -1, -1
            header_row = -1

            for r_idx, row in enumerate(ws.iter_rows(values_only=True)):
                if not any(row):
                    continue
                r_str = ' '.join(str(c) for c in row if c).lower()
                if 'ответственный' in r_str or 'кам' in r_str:
                    header_row = r_idx
                    headers = [str(c or '').strip().lower() for c in row]
                    for idx, h in enumerate(headers):
                        if 'ответственн' in h or h == 'кам':
                            resp_col = idx
                        elif 'инн' in h and inn_col == -1:
                            inn_col = idx
                        elif any(x in h for x in ['дилер', 'дц', 'партнер', 'юл', 'название', 'холдинг']) and name_col == -1:
                            name_col = idx
                        elif 'город' in h and city_col == -1:
                            city_col = idx
                        elif 'бренд' in h and brand_col == -1:
                            brand_col = idx
                    break

            if resp_col == -1:
                continue

            sheet_brand = sname.split('&')[0].strip().upper()

            for row in ws.iter_rows(min_row=header_row + 2, values_only=True):
                if not any(row):
                    continue
                resp = str(row[resp_col] or '').strip() if resp_col < len(row) else ''
                if not resp:
                    continue
                kam = normalize_kam(resp)
                if kam == 'Не назначен':
                    continue

                inn = clean_inn(row[inn_col]) if inn_col != -1 and inn_col < len(row) else ''
                name = str(row[name_col] or '').strip() if name_col != -1 and name_col < len(row) else ''
                city = str(row[city_col] or '').strip() if city_col != -1 and city_col < len(row) else ''
                row_brand = str(row[brand_col] or '').strip().upper() if brand_col != -1 and brand_col < len(row) else sheet_brand

                if inn:
                    inn_entries[inn].append({
                        'kam': kam,
                        'brand': row_brand,
                        'city': city,
                        'name': name
                    })

                if name:
                    ck = clean_key(name)
                    if ck:
                        self.exact_name_map[ck] = kam
                        self.exact_name_map[name.lower()] = kam

        wb.close()

        # Build inn_map with brand/city splits
        for inn, entries in inn_entries.items():
            kams = set(e['kam'] for e in entries)
            if len(kams) == 1:
                self.inn_map[inn] = {'default': list(kams)[0], 'brands': {}, 'cities': {}}
            else:
                # Disambiguate by brand / city
                brands = {}
                cities = {}
                for e in entries:
                    if e['brand']:
                        brands[clean_key(e['brand'])] = e['kam']
                    if e['city']:
                        cities[clean_key(e['city'])] = e['kam']
                # default is majority vote
                majority = max(kams, key=lambda k: sum(1 for e in entries if e['kam'] == k))
                self.inn_map[inn] = {
                    'default': majority,
                    'brands': brands,
                    'cities': cities
                }

        # Build holding keywords for robust matching of dealers in September
        self._init_holdings()
        print(f"[*] OemKamResolver: загружено {len(self.inn_map)} уникальных ИНН, {len(self.exact_name_map)} имен из OEM 15.")

    def _init_holdings(self):
        """
        Holdings rules strictly verified against OEM (15).
        These ensure that even if Bitrix deal has no INN or has a slightly different raw dealer string,
        the September deal is routed to the exact KAM assigned in OEM (15).
        """
        self.holding_rules = [
            # 1. Евгения Добролюбова (Поволжье, Урал, Башкирия, Сибирь из OEM 15)
            (('нижегородец',), 'Евгения Добролюбова'),
            (('башавтоком',), 'Евгения Добролюбова'),
            (('тд армада-авто', 'армада-авто'), 'Евгения Добролюбова'),
            (('эксперт авто оренбург', 'эксперт авто самара', 'эксперт самара'), 'Евгения Добролюбова'),
            (('юникор',), 'Евгения Добролюбова'),
            (('самара-лада', 'самара лада'), 'Евгения Добролюбова'),
            (('сатурн-р', 'сатурн р', 'сатурн-р-авто'), 'Евгения Добролюбова'),
            (('дав-авто', 'дав авто'), 'Евгения Добролюбова'),
            (('тсац июль', 'тсац "июль"', 'июль лада'), 'Евгения Добролюбова'),
            (('форвард-авто', 'форвард авто'), 'Евгения Добролюбова'),
            (('авто-моторс сургут', 'автомоторс сургут'), 'Евгения Добролюбова'),
            (('русская ладья',), 'Евгения Добролюбова'),
            (('автофорум',), 'Евгения Добролюбова'), # Chery Уфа (ООО "Автофорум Центр")
            (('сызранская сто', 'сызрань'), 'Евгения Добролюбова'),
            (('урал-лада', 'урал лада'), 'Евгения Добролюбова'),
            (('заводском самара', 'автоцентр на заводском'), 'Евгения Добролюбова'),
            (('оса-холдинг', 'бузулук'), 'Евгения Добролюбова'),
            (('планета авто', 'гольфстрим'), 'Евгения Добролюбова'), # Челябинск (Chery/Haval в OEM 15)

            # 2. Валерия Солдатова (Юг, Черноземье)
            (('боравто',), 'Валерия Солдатова'),
            (('леон-авто', 'леон авто'), 'Валерия Солдатова'),
            (('глобус-моторс', 'гк глобус', 'глобус моторс'), 'Валерия Солдатова'),
            (('олимп', 'темп авто кубань'), 'Валерия Солдатова'), # В OEM 15 Олимп Кубань -> Солдатова
            (('оптима кубань', 'оптима лайн'), 'Валерия Солдатова'),
            (('авто-ревю', 'авторевю'), 'Валерия Солдатова'),
            (('сатурн 2', 'сатурн-2', 'акцент - авто м'), 'Валерия Солдатова'),
            (('темп авто', 'темп авто к', 'техно-темп', 'трансфор'), 'Валерия Солдатова'),
            (('авторитэйл', 'авторитэйл м'), 'Валерия Солдатова'),

            # 3. Светлана Дариенко (СПб, СЗФО, Сибирь/ДВ)
            (('автохолдинг максимум', 'максимум'), 'Светлана Дариенко'),
            (('вагнер авто', 'вагнер'), 'Светлана Дариенко'),
            (('прагматика',), 'Светлана Дариенко'),
            (('автолига',), 'Светлана Дариенко'),
            (('ай-би-эм', 'айбиэм'), 'Светлана Дариенко'),
            (('дюк и к',), 'Светлана Дариенко'),
            (('томь-лада', 'томь лада'), 'Светлана Дариенко'),
            (('моторленд', 'автопроект'), 'Светлана Дариенко'),
            (('авто премиум тверь', 'автопремиум'), 'Светлана Дариенко'),
            (('автоград',), 'Алексей Чихарев'),
            (('премиум авто',), 'Алексей Чихарев'),

            # 4. Алексей Чихарев (Москва/Центр)
            (('кунцево',), 'Алексей Чихарев'),
            (('автокласс',), 'Алексей Чихарев'),
            (('у сервис+', 'у сервис'), 'Алексей Чихарев'),
            (('автопассаж',), 'Алексей Чихарев'),
            (('автотракт',), 'Алексей Чихарев'),
            (('фаворит',), 'Алексей Чихарев'),
            (('сим рыбинск',), 'Алексей Чихарев'),

            # 5. Андрей Кузнецов (РОЛЬФ, АГАТ, Автомир, Fresh)
            (('рольф',), 'Андрей Кузнецов'),
            (('агат', 'автопрофиль', 'аркада', 'квант', 'альтаир', 'приоритет моторс', 'максима авто', 'платинум'), 'Андрей Кузнецов'),
            (('автомир',), 'Андрей Кузнецов'),
            (('фреш', 'fresh'), 'Андрей Кузнецов'),
        ]

    def resolve(self, inn=None, partner_name='', brand='', city='', fallback_kam='Не назначен'):
        """
        Resolve KAM for September deal according to OEM (15) priority.
        """
        c_inn = clean_inn(inn)
        p_clean = clean_key(partner_name)
        p_lower = (partner_name or '').lower()
        b_clean = clean_key(brand)
        c_clean = clean_key(city)
        c_lower = (city or '').lower()

        # 1. Match by INN
        if c_inn and c_inn in self.inn_map:
            inn_info = self.inn_map[c_inn]
            if b_clean and b_clean in inn_info['brands']:
                return inn_info['brands'][b_clean]
            if c_clean and c_clean in inn_info['cities']:
                return inn_info['cities'][c_clean]
            return inn_info['default']

        # 2. Match by exact or normalized partner name
        if p_clean and p_clean in self.exact_name_map:
            return self.exact_name_map[p_clean]
        if p_lower and p_lower in self.exact_name_map:
            return self.exact_name_map[p_lower]

        # 3. Match by holding patterns
        for keywords, kam in self.holding_rules:
            if any(kw in p_lower for kw in keywords):
                # City-based disambiguation if needed
                if 'авторитэйл' in p_lower:
                    if any(spb_k in p_lower or spb_k in c_lower for spb_k in ['спб', 'санкт-петербург']):
                        return 'Светлана Дариенко'
                    return 'Валерия Солдатова'
                if 'автоград' in p_lower:
                    if 'калининград' in p_lower or 'калининград' in c_lower:
                        return 'Светлана Дариенко'
                    return 'Алексей Чихарев'
                if 'премиум авто' in p_lower:
                    if any(spb_k in p_lower or spb_k in c_lower for spb_k in ['спб', 'санкт-петербург']) or 'geely' in b_clean.lower():
                        return 'Светлана Дариенко'
                    return 'Алексей Чихарев'
                return kam

        # 4. Fallback to existing registry / bitrix directory
        return fallback_kam
