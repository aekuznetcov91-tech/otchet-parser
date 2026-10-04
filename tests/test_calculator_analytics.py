"""Regressions for evidence-only funnel data and calculator snapshots."""
import json
from pathlib import Path
import unittest
from scripts.etl.calculator import aggregate_calculator, calculator_metrics, client_id
from scripts.etl.funnel import calculate_brand_funnel


def event(cid='1', car='JETOUR T2', day='01.08.2026', action='Расчет автомобиля', **extra):
    return dict(timestamp=f'{day}, 10:00:00', clientId=cid, managerId='7',
                action=action, details=json.dumps({'car': car}), **extra)


class CalculatorAnalyticsTests(unittest.TestCase):
    def test_events_clients_duplicates_and_missing_ids(self):
        first = event()
        snapshot = aggregate_calculator([first, first, event(action='Клиент на калькуляторе'), event(cid='Нет в базе')])
        metric = calculator_metrics(snapshot, '2026-08', 'ALL')['calc']
        self.assertEqual(metric, {'events': 3, 'clients': 1, 'without_id': 1})
        self.assertEqual(snapshot['duplicates_removed'], 1)
        self.assertNotIn('clientId', json.dumps(snapshot))
        self.assertNotIn('managerId', json.dumps(snapshot))

    def test_global_clients_are_unioned_across_brands_and_months(self):
        snapshot = aggregate_calculator([event(), event(car='GAC GS8'), event(day='01.09.2026')])
        self.assertEqual(snapshot['by_month']['2026-08']['ALL']['calc']['clients'], 1)
        self.assertEqual(snapshot['by_month']['all']['ALL']['calc']['clients'], 1)
        self.assertEqual(snapshot['by_month']['all']['ALL']['calc']['events'], 3)

    def test_unknown_brand_and_brand_only_form_are_preserved(self):
        row = event(action='Анкета ФДЦ заполнена')
        row['details'] = json.dumps({'brand': 'GAC'})
        snapshot = aggregate_calculator([event(car='Unrecognized private text'), row])
        self.assertEqual(snapshot['by_month']['2026-08']['НЕ ОПРЕДЕЛЁН']['calc']['events'], 1)
        self.assertEqual(snapshot['by_month']['2026-08']['GAC']['fdc_form']['events'], 1)

    def test_coverage_unknown_vs_observed_zero(self):
        snapshot = aggregate_calculator([event()])
        self.assertIsNone(calculator_metrics(snapshot, '2026-06', 'JETOUR'))
        self.assertEqual(calculator_metrics(snapshot, '2026-08', 'GAC')['calc']['events'], 0)
        self.assertIsNone(calculator_metrics(None, '2026-08', 'GAC'))

    def test_invalid_date_not_assigned_to_september(self):
        snapshot = aggregate_calculator([event(), event(day='invalid')])
        self.assertEqual(snapshot['invalid_dates'], 1)
        self.assertNotIn('2026-09', snapshot['by_month'])
        for value in ({'error': 'failed'}, [], [event(day='bad')]):
            with self.assertRaises(ValueError):
                aggregate_calculator(value)

    def test_monthly_jeland_consolidation(self):
        snapshot = aggregate_calculator([event(car='OMODA C5'), event(car='OMODA C5', day='01.09.2026')])
        self.assertEqual(snapshot['by_month']['2026-08']['OMODA']['calc']['events'], 1)
        self.assertEqual(snapshot['by_month']['2026-09']['JELAND']['calc']['events'], 1)

    def test_placeholder_ids_are_not_unique_clients(self):
        for value in ['0', 'Нет в базе', 'Ошибка ID', '', 'https://crm/7']:
            self.assertEqual(client_id(value), '')
        self.assertEqual(client_id('007.0'), '7')

    def test_missing_crm_stages_never_estimated_from_sales_or_logs(self):
        snapshot = aggregate_calculator([event()])
        result = calculate_brand_funnel([], [], snapshot, [])
        brand = result['by_month']['2026-08']['brands']['JETOUR']
        self.assertEqual(brand['calc_total'], 1)
        self.assertEqual(brand['offer_total'], 0)
        for key in ('leads', 'qual', 'fdc_app', 'fdc_appr', 'dealer', 'calc_matched', 'offer_matched'):
            self.assertIsNone(brand[key], key)

    def test_crm_event_name_and_qualification_order(self):
        rows = [
            {'client_id':'1','Дата':'01.08.2026','event_name':'Новый лид','Бренд':'GAC'},
            {'client_id':'1','Дата':'02.08.2026','event_name':'Закрепление менеджера','Бренд':'GAC'},
            {'client_id':'2','Дата':'02.08.2026','event_name':'Новый лид','Бренд':'GAC'},
            {'client_id':'2','Дата':'01.08.2026','event_name':'Закрепление менеджера','Бренд':'GAC'},
            {'client_id':'3','Дата':'bad','event_name':'Новый лид','Бренд':'GAC'},
        ]
        result = calculate_brand_funnel([], rows, {}, [])
        totals = result['by_month']['2026-08']['crm_totals']
        self.assertEqual(totals['leads'], 2)
        self.assertEqual(totals['qual'], 1)
        self.assertIsNone(totals['fdc_appr'])

    def test_qualification_does_not_reverse_same_day_timestamps(self):
        rows = [{'client_id':'1','Дата':dt,'event_name':ev,'Бренд':'GAC'} for dt,ev in [
            ('01.08.2026 12:00:00','Новый лид'), ('01.08.2026 11:00:00','Закрепление менеджера')]]
        result = calculate_brand_funnel([], rows, {}, [])
        self.assertIsNone(result['by_month']['2026-08']['crm_totals']['qual'])

    def test_transfers_only_from_canonical_partner_registry(self):
        partner = {'Type':'Лид','Month':'2026-08','ClientId':'1','Brand':'GAC'}
        result = calculate_brand_funnel([], [], {}, [partner, partner])
        self.assertEqual(result['by_month']['2026-08']['crm_totals']['dealer'], 1)

    def test_every_sale_allocated_once_including_unknown_brands(self):
        sales = [{'SaleMonth':'2026-08','SaleQty':1,'Brand':b,'Model':m,'B2C':c,'Revenue':100}
                 for b,m,c in [('CHERY & TENET','CHERY TIGGO','Online'),('JETOUR','T2','МП2'),('Other','Other','МП1')]]
        result = calculate_brand_funnel(sales, [], {}, [])
        rows = result['by_month']['2026-08']['brands'].values()
        self.assertEqual(sum(r['deals_total_all'] for r in rows), 3)
        self.assertEqual(sum(r['mp2_count'] for r in rows), 1)
        self.assertEqual(sum(r['rev_no_mp2']+r['mp2_rev'] for r in rows), 300)

    def test_deployed_payload_matches_snapshot(self):
        root = Path(__file__).resolve().parents[1]
        snapshot = json.loads((root/'data/calculator_analytics.json').read_text(encoding='utf-8'))
        payload = json.loads((root/'site/data.json').read_text(encoding='utf-8'))
        funnel = payload['brand_funnel']
        for month, expected in snapshot['by_month'].items():
            self.assertEqual(funnel['by_month'][month]['calculator'], expected['ALL'])
            self.assertEqual(sum(row['calculator']['calc']['events'] for row in funnel['by_month'][month]['brands'].values()), expected['ALL']['calc']['events'])
