import copy
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from plugin import calculations
from plugin.data import scenarios
from verifier import oracle

class RetirementBoundaryTests(unittest.TestCase):
    def test_deferred_withdrawal_grosses_up_for_its_own_tax(self):
        out = calculations.solve({'scenario_id': 'tax-gross-up', 'years': 1})
        first = out['schedule'][0]
        self.assertEqual(first['deferred_withdrawal_cents'], 6000000)
        self.assertEqual(first['tax_cents'], 500000)
        self.assertEqual(first['ending_deferred_cents'], 4000000)
        self.assertTrue(out['sustainable'])

    def test_required_withdrawal_surplus_goes_into_cash(self):
        first = calculations.solve({'scenario_id': 'mandatory-surplus', 'years': 1})['schedule'][0]
        self.assertEqual(first['minimum_deferred_cents'], 1000000)
        self.assertEqual(first['surplus_cents'], 990000)
        self.assertEqual(first['ending_cash_cents'], 990000)

    def test_exact_funds_succeed_then_fail_next_year(self):
        out = calculations.solve({'scenario_id': 'exact-funds', 'years': 30})
        self.assertEqual(out['first_shortfall_year'], 2)
        self.assertEqual(len(out['schedule']), 2)
        self.assertEqual(out['schedule'][0]['shortfall_cents'], 0)
        self.assertEqual(out['schedule'][1]['shortfall_cents'], 10000)

    def test_income_only_supports_sixty_years(self):
        out = calculations.solve({'scenario_id': 'income-only', 'years': 60})
        self.assertTrue(out['sustainable'])
        self.assertEqual(len(out['schedule']), 60)
        self.assertEqual(out['schedule'][-1]['ending_cash_cents'], 12000000)

    def test_signed_half_cent_rounding_and_tax_thresholds(self):
        self.assertEqual(calculations.rounded(-5000), -1)
        self.assertEqual(calculations.rounded(5000), 1)
        bands = scenarios()['comfortable']['tax_schedule']['brackets']
        self.assertEqual(calculations.tax(2000000, bands), 0)
        self.assertEqual(calculations.tax(5000000, bands), 300000)
        self.assertEqual(calculations.tax(6000000, bands), 500000)

    def test_seeded_independent_replay(self):
        rng = random.Random(20261102)
        for _ in range(100):
            fixture = copy.deepcopy(scenarios()['comfortable'])
            fixture['balances'] = {k: rng.randrange(0,10000000) for k in fixture['balances']}
            fixture['assumptions'].update(annual_spending_cents=rng.randrange(0,3000000),annual_income_cents=rng.randrange(0,6000000),
                income_start_year=rng.randrange(1,15),minimum_deferred_bps=rng.randrange(0,10001),
                cash_return_bps=rng.randrange(-2000,2001),deferred_return_bps=rng.randrange(-2000,2001),tax_free_return_bps=rng.randrange(-2000,2001))
            args = {'scenario_id': 'random', 'years': rng.randrange(1,61)}
            with patch.object(calculations, 'scenario', return_value=fixture), patch.object(oracle, 'scenario', return_value=fixture):
                self.assertEqual(calculations.solve(args), oracle.expected(args))
