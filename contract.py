"""Typed tool and task declarations; money is always integer cents."""
from dataclasses import dataclass
from enum import Enum
from slimconfig import Output

@dataclass
class ScenarioInput(Output):
    scenario_id: str

@dataclass
class RulesInput(Output):
    pass

@dataclass
class RulesOutput(Output):
    rules: list[str]

class Tool(Enum):
    GET_ACCOUNT_BALANCES = 'get_account_balances'
    GET_ASSUMPTIONS = 'get_assumptions'
    GET_TAX_SCHEDULE = 'get_tax_schedule'
    GET_RULES = 'get_rules'

class Task(Enum):
    PROJECT_RETIREMENT = 'project-retirement'

@dataclass
class RetirementInput(Output):
    scenario_id: str
    years: int

@dataclass
class BalancesOutput(Output):
    cash_cents: int
    tax_deferred_cents: int
    tax_free_cents: int

@dataclass
class AssumptionsOutput(Output):
    annual_spending_cents: int
    annual_income_cents: int
    income_start_year: int
    inflation_bps: int
    cash_return_bps: int
    deferred_return_bps: int
    tax_free_return_bps: int
    minimum_deferred_bps: int

@dataclass
class TaxBracket(Output):
    upper_cents: int
    rate_bps: int

@dataclass
class TaxScheduleOutput(Output):
    brackets: list[TaxBracket]

@dataclass
class RetirementYear(Output):
    year: int
    spending_cents: int
    income_cents: int
    cash_growth_cents: int
    deferred_growth_cents: int
    tax_free_growth_cents: int
    minimum_deferred_cents: int
    cash_withdrawal_cents: int
    deferred_withdrawal_cents: int
    tax_free_withdrawal_cents: int
    tax_cents: int
    surplus_cents: int
    shortfall_cents: int
    ending_cash_cents: int
    ending_deferred_cents: int
    ending_tax_free_cents: int

@dataclass
class RetirementOutput(Output):
    scenario_id: str
    years_requested: int
    sustainable: bool
    first_shortfall_year: int
    total_tax_cents: int
    schedule: list[RetirementYear]

TOOLS = {
    Tool.GET_ACCOUNT_BALANCES: (ScenarioInput, BalancesOutput),
    Tool.GET_ASSUMPTIONS: (ScenarioInput, AssumptionsOutput),
    Tool.GET_TAX_SCHEDULE: (ScenarioInput, TaxScheduleOutput),
    Tool.GET_RULES: (RulesInput, RulesOutput),
}
TASKS = {Task.PROJECT_RETIREMENT: (RetirementInput, RetirementOutput)}
