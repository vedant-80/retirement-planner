"""Typed custom financial inputs and compact outputs. No field defaults: null selects documented assumptions."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    CALCULATE = "calculate_retirement"


class Task(Enum):
    CALCULATE = "project-retirement"


@dataclass
class RetirementInput(Output):
    current_age: Annotated[int, "Current age in whole years, 0 to 99; ask if missing. Ages 100 or above are rejected."]
    investments_cents: Annotated[
        int, "Current invested balance in integer cents; ask if missing. No currency conversion is performed."
    ]
    annual_income_cents: Annotated[
        int, "Annual take-home income in integer cents; ask if missing. Do not infer taxes from gross salary."
    ]
    annual_expenses_cents: Annotated[
        int, "Current annual expenses in integer cents; ask if missing. Include all spending; use one currency."
    ]
    investment_return_bps: Annotated[
        int | None, "Nominal annual investment return in basis points (9% = 900). Use null if unspecified: default 900."
    ]
    wage_growth_bps: Annotated[int | None, "Nominal annual wage growth in basis points; null defaults to 200 (2%)."]
    spending_inflation_bps: Annotated[
        int | None, "Annual spending inflation in basis points; null defaults to 200 (2%)."
    ]


@dataclass
class RetirementAssumptions(Output):
    current_age: Annotated[int, "Current age in whole years, 0 to 99; ask if missing. Ages 100 or above are rejected."]
    investments_cents: Annotated[
        int, "Current invested balance in integer cents; ask if missing. No currency conversion is performed."
    ]
    annual_income_cents: Annotated[
        int, "Annual take-home income in integer cents; ask if missing. Do not infer taxes from gross salary."
    ]
    annual_expenses_cents: Annotated[
        int, "Current annual expenses in integer cents; ask if missing. Include all spending; use one currency."
    ]
    investment_return_bps: Annotated[
        int, "Nominal annual investment return in basis points (9% = 900). Use null if unspecified: default 900."
    ]
    wage_growth_bps: Annotated[int, "Nominal annual wage growth in basis points; null defaults to 200 (2%)."]
    spending_inflation_bps: Annotated[int, "Annual spending inflation in basis points; null defaults to 200 (2%)."]
    max_search_age: Annotated[int, "Search ends at age 100, including that birthday."]
    withdrawal_rate_bps: Annotated[
        int, "Fixed 400 basis points (4%); required investments equal 25 times annual expenses."
    ]


@dataclass
class RetirementOutput(Output):
    goal_reached: Annotated[bool, "Whether the 4% target was reached by age 100."]
    retirement_age: Annotated[int | None, "Earliest whole-year retirement age, or null if not found."]
    years_until_retirement: Annotated[int | None, "Whole years until retirement, or null if not found."]
    projection_age: Annotated[int, "Age at the final target check or unfunded year end."]
    projected_investments_cents: Annotated[
        int, "Investments at projection_age; zero if an income shortfall exhausted funds."
    ]
    projected_annual_expenses_cents: Annotated[int, "Annual expenses projected for projection_age."]
    required_investments_cents: Annotated[int, "25 times projected annual expenses."]
    reason: Annotated[
        str, "goal_reached, search_limit, or funding_shortfall. This is a fixed-assumption projection, not a guarantee."
    ]
    assumptions: Annotated[RetirementAssumptions, "All effective inputs, including defaults and fixed policy."]
    defaults_applied: Annotated[list[str], "Names of nullable input fields that used their defaults."]


TOOLS = {Tool.CALCULATE: (RetirementInput, RetirementOutput)}
TASKS = {Task.CALCULATE: (RetirementInput, RetirementOutput)}
