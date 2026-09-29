import unittest
import json
import os
import openpyxl

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestAuditSoldatovaAndDebtors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(PROJECT_ROOT, 'data.json'), 'r', encoding='utf-8') as f:
            cls.data = json.load(f)
        with open(os.path.join(PROJECT_ROOT, 'partners_registry.json'), 'r', encoding='utf-8') as f:
            cls.registry = json.load(f)

    def test_01_km_ch_strictly_chikharev(self):
        """1. КМ/Ч must be 100% assigned to Алексей Чихарев"""
        sys_db = self.data.get('sys_db_partners', [])
        km_records = [r for r in sys_db if r.get('PartnerId') in [1095, 1203] or 'км/ч' in str(r.get('Partner', '')).lower()]
        self.assertGreater(len(km_records), 0, "KM/Ch records should exist in sys_db_partners")
        for r in km_records:
            self.assertEqual(r.get('KAM'), 'Алексей Чихарев', f"Record {r} must be assigned to Алексей Чихарев")

        # In registry
        partners = self.registry.get('partners', [])
        km_partner = next((p for p in partners if p.get('partner_id') == 1095), None)
        self.assertIsNotNone(km_partner, "Partner 1095 КМ/Ч must exist in registry")
        self.assertEqual(km_partner.get('kam'), 'Алексей Чихарев')

    def test_02_tambov_avto_in_globus(self):
        """3. ООО 'Тамбов-Авто' (1115) must be merged into ГК Глобус (1013, Валерия Солдатова)"""
        sys_db = self.data.get('sys_db_partners', [])
        tambov_records = [r for r in sys_db if 'тамбов' in str(r.get('RawPartner', '')).lower()]
        self.assertGreater(len(tambov_records), 0, "Tambov-Auto records should exist")
        for r in tambov_records:
            self.assertEqual(r.get('PartnerId'), 1013, "Tambov-Auto records must have PartnerId 1013 (ГК Глобус)")
            self.assertEqual(r.get('Partner'), 'ГК Глобус', "Tambov-Auto partner name must be ГК Глобус")
            self.assertEqual(r.get('KAM'), 'Валерия Солдатова', "Tambov-Auto must be under Валерия Солдатова")

    def test_03_wagner_city_split_in_registry(self):
        """2. Partner 1285 (Вагнер Авто / Авторитэйл) OEM geography must strictly separate Krasnodar and SPb"""
        partners = self.registry.get('partners', [])
        p1285 = next((p for p in partners if p.get('partner_id') == 1285), None)
        self.assertIsNotNone(p1285)
        oem = p1285.get('oem_data', [])
        
        soldatova_cities = {o.get('city') for o in oem if o.get('responsible') == 'Валерия Солдатова'}
        darienko_cities = {o.get('city') for o in oem if o.get('responsible') == 'Светлана Дариенко'}
        
        self.assertIn('Краснодар', soldatova_cities)
        self.assertNotIn('Санкт-Петербург', soldatova_cities, "Soldatova must NEVER have SPb under Wagner")
        self.assertIn('Санкт-Петербург', darienko_cities)
        self.assertNotIn('Краснодар', darienko_cities, "Darienko must NOT have Krasnodar under Wagner")

    def test_04_stale_advances_excel_file(self):
        """8. Verify generated Excel file for aging advances >= 20 days"""
        xlsx_path = os.path.join(PROJECT_ROOT, 'Зависшие_авансы_от_20_дней.xlsx')
        self.assertTrue(os.path.exists(xlsx_path), f"File {xlsx_path} must exist")
        wb = openpyxl.load_workbook(xlsx_path, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        # Title, subtitle, empty, header, then data rows
        data_rows = rows[4:]
        self.assertGreaterEqual(len(data_rows), 50, "Should contain all aging advances >= 20 days")
        for r in data_rows:
            aging_days = r[7] # Column 8 (index 7)
            self.assertGreaterEqual(aging_days, 20, f"Row {r} aging days must be >= 20")

    def test_05_ui_features_present(self):
        """Verify UI elements in index.html and js/"""
        with open(os.path.join(PROJECT_ROOT, 'index.html'), 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('id="filterDebtorsKam"', html, "KAM filter dropdown in Debtors must exist")
        self.assertIn('id="btnReturnToKam"', html, "Return to KAM button must exist")
        self.assertIn('id="modalTransferredLeads"', html, "Transferred Leads modal must exist")
        self.assertIn('executeAging20DebtorsExcelExport', html, "Aging 20 days export button must exist")

        with open(os.path.join(PROJECT_ROOT, 'js', 'debtors.js'), 'r', encoding='utf-8') as f:
            js_debtors = f.read()
        self.assertIn('toggleDebtorCompany', js_debtors, "Accordion toggle must exist in debtors.js")
        self.assertIn('applyDebtorKamFilter', js_debtors, "KAM filter function must exist in debtors.js")
        self.assertIn('returnToKamDashboard', js_debtors, "Return function must exist in debtors.js")

        with open(os.path.join(PROJECT_ROOT, 'js', 'kam-dashboard.js'), 'r', encoding='utf-8') as f:
            js_kam = f.read()
        self.assertIn('openTransferredLeadsModal', js_kam, "openTransferredLeadsModal must exist in kam-dashboard.js")
        self.assertIn('exportTransferredLeadsToExcel', js_kam, "exportTransferredLeadsToExcel must exist in kam-dashboard.js")

if __name__ == '__main__':
    unittest.main()
