import json
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from plugin.calculations import solve
from verifier.oracle import expected


def example(**changes):
    return json.loads((ROOT / "tests/example.json").read_text()) | changes


class RetirementCalculationTests(unittest.TestCase):
    def test_custom_situation_and_defaults(self):
        result = solve(example())
        self.assertTrue(result["goal_reached"])
        self.assertEqual(result["assumptions"]["investment_return_bps"], 900)
        self.assertEqual(result["assumptions"]["wage_growth_bps"], 200)
        self.assertEqual(result["assumptions"]["spending_inflation_bps"], 200)
        self.assertEqual(len(result["defaults_applied"]), 3)
        self.assertEqual(result["assumptions"]["withdrawal_rate_bps"], 400)
        self.assertGreaterEqual(result["projected_investments_cents"], result["required_investments_cents"])
        self.assertLess(len(json.dumps(result)), 2000)
        self.assertNotIn("schedule", result)

    def test_exact_target_and_above_qualify_now(self):
        for wealth in (2500000, 2500001):
            out = solve(example(current_age=50, investments_cents=wealth, annual_expenses_cents=100000))
            self.assertEqual(out["retirement_age"], 50)
            self.assertEqual(out["years_until_retirement"], 0)

    def test_one_cent_below_target_does_not_qualify(self):
        out = solve(
            example(
                current_age=99,
                investments_cents=2499999,
                annual_expenses_cents=100000,
                annual_income_cents=100000,
                investment_return_bps=0,
                wage_growth_bps=0,
                spending_inflation_bps=0,
            )
        )
        self.assertFalse(out["goal_reached"])
        self.assertIsNone(out["retirement_age"])
        self.assertEqual(out["projection_age"], 100)
        self.assertEqual(out["reason"], "search_limit")

    def test_hand_calculated_earliest_age_and_end_year_savings(self):
        # Expenses 100, annual savings 100, target 2500, zero returns: exactly 25 years.
        out = solve(
            example(
                current_age=30,
                investments_cents=0,
                annual_expenses_cents=100,
                annual_income_cents=200,
                investment_return_bps=0,
                wage_growth_bps=0,
                spending_inflation_bps=0,
            )
        )
        self.assertEqual(out["retirement_age"], 55)
        self.assertEqual(out["projected_investments_cents"], 2500)
        self.assertEqual(out["defaults_applied"], [])
        # Contributions do not receive opening-year returns: 0 + 100, not 109.
        out = solve(
            example(
                current_age=99,
                investments_cents=0,
                annual_expenses_cents=100,
                annual_income_cents=200,
                investment_return_bps=900,
                wage_growth_bps=0,
                spending_inflation_bps=0,
            )
        )
        self.assertEqual(out["projected_investments_cents"], 100)

    def test_income_and_expenses_grow_separately(self):
        out = solve(
            example(
                current_age=99,
                investments_cents=1000,
                annual_income_cents=1000,
                annual_expenses_cents=100,
                investment_return_bps=0,
                wage_growth_bps=1000,
                spending_inflation_bps=2000,
            )
        )
        self.assertEqual(out["projected_investments_cents"], 1900)
        self.assertEqual(out["projected_annual_expenses_cents"], 120)
        self.assertEqual(out["required_investments_cents"], 3000)

    def test_signed_half_cent_and_no_borrowing(self):
        out = solve(
            example(
                current_age=99,
                investments_cents=1,
                annual_income_cents=0,
                annual_expenses_cents=1,
                investment_return_bps=-5000,
                wage_growth_bps=0,
                spending_inflation_bps=0,
            )
        )
        self.assertEqual(out["reason"], "funding_shortfall")
        self.assertEqual(out["projected_investments_cents"], 0)
        self.assertEqual(out["projection_age"], 100)
        # A covered income shortfall reduces wealth but does not stop the projection early.
        out = solve(
            example(
                current_age=99,
                investments_cents=50,
                annual_income_cents=0,
                annual_expenses_cents=10,
                investment_return_bps=0,
                wage_growth_bps=0,
                spending_inflation_bps=0,
            )
        )
        self.assertEqual(out["projected_investments_cents"], 40)
        self.assertEqual(out["reason"], "search_limit")

    def test_age_limit_is_inclusive_for_results_but_not_starting_age(self):
        out = solve(
            example(
                current_age=99,
                investments_cents=2400,
                annual_income_cents=200,
                annual_expenses_cents=100,
                investment_return_bps=0,
                wage_growth_bps=0,
                spending_inflation_bps=0,
            )
        )
        self.assertEqual(out["retirement_age"], 100)
        for age in (100, 101, 150):
            with self.assertRaisesRegex(ValueError, "below 100"):
                solve(example(current_age=age))

    def test_zero_expenses_and_extreme_supported_rates(self):
        self.assertEqual(solve(example(investments_cents=0, annual_expenses_cents=0))["retirement_age"], 40)
        for rate in (-10000, 10000):
            args = example(
                current_age=0, investment_return_bps=rate, wage_growth_bps=rate, spending_inflation_bps=10000
            )
            self.assertEqual(solve(args), expected(args))

    def test_seeded_custom_input_differential_replay(self):
        rng = random.Random(1701)
        for _ in range(300):
            args = example(
                current_age=rng.randrange(100),
                investments_cents=rng.randrange(10**9),
                annual_income_cents=rng.randrange(10**7),
                annual_expenses_cents=rng.randrange(10**7),
                investment_return_bps=rng.randrange(-10000, 10001),
                wage_growth_bps=rng.randrange(-10000, 10001),
                spending_inflation_bps=rng.randrange(10001),
            )
            self.assertEqual(solve(args), expected(args))
