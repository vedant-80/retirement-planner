"""Integer-cent computation. No model calls or scenario lookup."""

from dataclasses import asdict, is_dataclass


def plain(value):
    return asdict(value) if is_dataclass(value) else value


def integer(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer from {low} to {high}")
    return value


def rounded(numerator, denominator=10000):
    sign = -1 if numerator < 0 else 1
    return sign * ((2 * abs(numerator) + denominator) // (2 * denominator))


def normalize(value):
    args = plain(value)
    fields = {
        "current_age",
        "investments_cents",
        "annual_income_cents",
        "annual_expenses_cents",
        "investment_return_bps",
        "wage_growth_bps",
        "spending_inflation_bps",
    }
    if type(args) is not dict or set(args) != fields:
        raise ValueError("Supply every declared field; use null for optional rate defaults")
    if type(args["current_age"]) is int and args["current_age"] >= 100:
        raise ValueError("Starting age must be below 100; the retirement search ends at age 100")
    result = {"current_age": integer(args["current_age"], "current_age", 0, 99)}
    for key in ("investments_cents", "annual_income_cents", "annual_expenses_cents"):
        result[key] = integer(args[key], key, 0, 10**15)
    defaults = []
    for key, default, low in (
        ("investment_return_bps", 900, -10000),
        ("wage_growth_bps", 200, -10000),
        ("spending_inflation_bps", 200, 0),
    ):
        value = args[key]
        if value is None:
            defaults.append(key)
            value = default
        result[key] = integer(value, key, low, 10000)
    result.update(max_search_age=100, withdrawal_rate_bps=400)
    return result, defaults


def solve(value):
    a, defaults = normalize(value)
    assets, income, expenses = (a[k] for k in ("investments_cents", "annual_income_cents", "annual_expenses_cents"))
    reason = "search_limit"
    age = a["current_age"]
    for age in range(a["current_age"], 101):
        if assets >= 25 * expenses:
            reason = "goal_reached"
            break
        if age == 100:
            break
        after_year = assets + rounded(assets * a["investment_return_bps"]) + income - expenses
        income += rounded(income * a["wage_growth_bps"])
        expenses += rounded(expenses * a["spending_inflation_bps"])
        if after_year < 0:
            assets = 0
            age += 1
            reason = "funding_shortfall"
            break
        assets = after_year
    reached = reason == "goal_reached"
    return {
        "goal_reached": reached,
        "retirement_age": age if reached else None,
        "years_until_retirement": age - a["current_age"] if reached else None,
        "projection_age": age,
        "projected_investments_cents": assets,
        "projected_annual_expenses_cents": expenses,
        "required_investments_cents": 25 * expenses,
        "reason": reason,
        "assumptions": a,
        "defaults_applied": defaults,
    }
