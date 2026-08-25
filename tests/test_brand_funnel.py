import os
import json
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_JSON_PATH = os.path.join(PROJECT_ROOT, 'site', 'data.json')
INDEX_HTML_PATH = os.path.join(PROJECT_ROOT, 'site', 'index.html')

class TestBrandFunnelAndDataIntegrity(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        self = cls
        if not os.path.exists(DATA_JSON_PATH):
            raise unittest.SkipTest(f"data.json does not exist at {DATA_JSON_PATH}")
        with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
            
    def test_01_data_json_structure(self):
        """Проверка наличия ключевых узлов в data.json"""
        self.assertIn('sys_db', self.data, "sys_db отсутствует в data.json")
        self.assertIn('sys_db_partners', self.data, "sys_db_partners отсутствует в data.json")
        self.assertIn('brand_funnel', self.data, "brand_funnel отсутствует в data.json")
        
    def test_02_sys_db_sales_and_revenue(self):
        """Проверка факта сделок и выручки"""
        db = self.data['sys_db']
        self.assertGreater(len(db), 1000, "В базе должно быть более 1000 записей")
        
        aug_sales = [r for r in db if r.get('SaleMonth') == '2026-08' and r.get('SaleQty') == 1]
        self.assertGreater(len(aug_sales), 1000, f"Август должен содержать > 1000 сделок (факт: {len(aug_sales)})")
        
        aug_rev = sum(r.get('Revenue', 0) for r in aug_sales)
        self.assertGreater(aug_rev, 35000000.0, f"Выручка за август должна быть > 35 млн ₽ (факт: {aug_rev:,.2f})")
        
    def test_03_brand_funnel_months(self):
        """Проверка наличия и структуры по месяцам в brand_funnel"""
        bf = self.data['brand_funnel']
        self.assertIn('by_month', bf, "by_month должен присутствовать в brand_funnel")
        self.assertIn('months', bf, "months список должен присутствовать в brand_funnel")
        
        for m in ['2026-08', '2026-07', 'all']:
            self.assertIn(m, bf['by_month'], f"Месяц {m} должен присутствовать в by_month")
            brands = bf['by_month'][m]['brands']
            self.assertGreaterEqual(len(brands), 6, f"В месяце {m} должно быть минимум 6 брендов")
            self.assertIn('JETOUR', brands, f"JETOUR должен быть в {m}")
            self.assertIn('LADA', brands, f"LADA должна быть в {m}")
            
    def test_04_brand_funnel_math_consistency(self):
        """Проверка математической целостности воронки по брендам"""
        bf = self.data['brand_funnel']
        
        for m, m_data in bf['by_month'].items():
            for b_name, b_data in m_data['brands'].items():
                deals_tot = b_data['deals_total_all']
                deals_no_mp2 = b_data['deals_no_mp2']
                mp2_count = b_data['mp2_count']
                
                # deals_total_all == deals_no_mp2 + mp2_count
                self.assertEqual(deals_tot, deals_no_mp2 + mp2_count, 
                                 f"Не сходится сумма сделок для {b_name} в {m}: {deals_tot} != {deals_no_mp2} + {mp2_count}")
                
                # Check revenue
                rev_no_mp2 = b_data['rev_no_mp2']
                mp2_rev = b_data['mp2_rev']
                self.assertGreaterEqual(rev_no_mp2, 0.0)
                self.assertGreaterEqual(mp2_rev, 0.0)
                
                # Check ARPU
                if deals_no_mp2 > 0:
                    self.assertGreater(b_data['arpu_no_mp2'], 0, f"ARPU розницы для {b_name} в {m} должен быть > 0")

    def test_05_vitrina_ocr_data(self):
        """Проверка наличия данных витрины PostHog из скриншотов"""
        bf = self.data['brand_funnel']
        aug_jetour = bf['by_month']['2026-08']['brands']['JETOUR']['vitrina']
        self.assertGreater(aug_jetour.get('car_card_show', 0), 10000, "У Джетур за август должно быть > 10k показов карточек")
        self.assertGreater(aug_jetour.get('offer_success', 0), 1000, "У Джетур за август должно быть > 1000 экранов успеха")

    def test_06_index_html_ui_components(self):
        """Проверка наличия UI компонентов и обработчиков в index.html"""
        with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
            html = f.read()
            
        self.assertIn('tab-funnel', html, "tab-funnel должен присутствовать в HTML")
        self.assertIn('setFunnelMonth', html, "Функция setFunnelMonth должна присутствовать в JS")
        self.assertIn('f-month-2026-08', html, "Кнопка выбора августа должна быть в DOM")
        self.assertIn('f-month-2026-07', html, "Кнопка выбора июля должна быть в DOM")
        self.assertIn('f-month-all', html, "Кнопка выбора всех месяцев должна быть в DOM")
        self.assertIn('selectFunnelBrand', html, "Функция selectFunnelBrand должна присутствовать в JS")

    def test_07_debtors_and_export_modal(self):
        """Проверка структуры должников ДКП и модального окна экспорта"""
        self.assertIn('debtors', self.data, "debtors должен присутствовать в data.json")
        debtors = self.data['debtors']
        self.assertGreater(len(debtors), 10, "Должно быть более 10 авто должников")
        first_debtor = debtors[0]
        for field in ['company', 'brand', 'vin', 'prepay_date']:
            self.assertIn(field, first_debtor, f"Поле {field} должно быть в записи должника")
            
        with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
            html = f.read()
            
        self.assertIn('tab-details', html, "tab-details должен присутствовать в HTML")
        self.assertIn('modalDebtorsExport', html, "modalDebtorsExport должен присутствовать в HTML")
        self.assertIn('executeDebtorsExcelExport', html, "executeDebtorsExcelExport должен быть в JS")
        self.assertIn('xlsx.full.min.js', html, "SheetJS библиотека должна быть подключена")

if __name__ == '__main__':
    unittest.main(verbosity=2)

