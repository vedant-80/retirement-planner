"""Independent Decimal replay of the declared financial model."""

from dataclasses import asdict, is_dataclass
from decimal import ROUND_HALF_UP, Decimal, localcontext


def plain(value):
    return asdict(value) if is_dataclass(value) else value


def integer(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer from {low} to {high}")
    return value


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


def expected(value):
    a, defaults = normalize(value)
    with localcontext() as context:
        context.prec = 200
        wealth = a["investments_cents"]
        pay = a["annual_income_cents"]
        cost = a["annual_expenses_cents"]
        age = a["current_age"]
        reason = "search_limit"
        while True:
            if wealth * 400 >= cost * 10000:
                reason = "goal_reached"
                break
            if age >= a["max_search_age"]:
                break
            gain = int(
                (Decimal(wealth) * Decimal(a["investment_return_bps"]) / 10000).quantize(
                    Decimal(1), rounding=ROUND_HALF_UP
                )
            )
            next_wealth = wealth + gain + pay - cost
            pay += int((Decimal(pay) * a["wage_growth_bps"] / 10000).quantize(Decimal(1), rounding=ROUND_HALF_UP))
            cost += int(
                (Decimal(cost) * a["spending_inflation_bps"] / 10000).quantize(Decimal(1), rounding=ROUND_HALF_UP)
            )
            age += 1
            wealth = max(0, next_wealth)
            if next_wealth < 0:
                reason = "funding_shortfall"
                break
        success = reason == "goal_reached"
        return {
            "goal_reached": success,
            "retirement_age": age if success else None,
            "years_until_retirement": age - a["current_age"] if success else None,
            "projection_age": age,
            "projected_investments_cents": wealth,
            "projected_annual_expenses_cents": cost,
            "required_investments_cents": cost * 25,
            "reason": reason,
            "assumptions": a,
            "defaults_applied": defaults,
        }
