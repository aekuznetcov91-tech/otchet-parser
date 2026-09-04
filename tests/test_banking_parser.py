# -*- coding: utf-8 -*-
import unittest
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.banking_dc_parser import resolve_location, find_file_with_bank_column, parse_banking_analytics

class TestBankingDcParser(unittest.TestCase):
    def test_location_resolution(self):
        city, macro = resolve_location('г. Казань, ул. Спартаковская', '', '')
        self.assertEqual(macro, 'Волга')
        self.assertEqual(city, 'Казань')

        city, macro = resolve_location('', '', 'РОЛЬФ ХИМКИ')
        self.assertEqual(macro, 'Москва')

        city, macro = resolve_location('', '', 'Максимум Лахта СПб')
        self.assertEqual(macro, 'Северо-Запад')

    def test_find_file_with_bank_column(self):
        raw_dir = os.path.join(PROJECT_ROOT, 'raw_data')
        fpath = find_file_with_bank_column([raw_dir])
        self.assertIsNotNone(fpath)
        self.assertTrue(os.path.exists(fpath))

    def test_banking_analytics_calculation(self):
        res = parse_banking_analytics(PROJECT_ROOT)
        self.assertIsNotNone(res)
        self.assertGreater(res['deals_total'], 0)
        self.assertEqual(res['deals_total'], res['lead_deals_total'] + res['other_deals_total'])
        self.assertEqual(res['deals_total'], res['deals_sber'] + res['deals_other_banks'] + res['deals_cash'])
        self.assertEqual(len(res['macro_rows']), 8)

if __name__ == '__main__':
    unittest.main()
