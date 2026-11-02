"""Read-only scenario tools. None calculates the task's final answer."""
import json
from importlib.resources import files
from .data import scenario, field

def get_rules(value, workspace):
    """Retrieve the precise fictional financial rules and rounding conventions."""
    return json.loads(files('plugin').joinpath('data/rules.json').read_text())


def get_account_balances(value, workspace):
    """Retrieve starting cash, tax-deferred, and tax-free account balances."""
    return scenario(field(value, 'scenario_id'))['balances']

def get_assumptions(value, workspace):
    """Retrieve fixed annual spending, pension, growth, and withdrawal assumptions."""
    return scenario(field(value, 'scenario_id'))['assumptions']

def get_tax_schedule(value, workspace):
    """Retrieve fictional progressive brackets; upper_cents=0 means unlimited."""
    return scenario(field(value, 'scenario_id'))['tax_schedule']


IMPLEMENTATIONS = {'get_account_balances': get_account_balances, 'get_assumptions': get_assumptions, 'get_tax_schedule': get_tax_schedule, 'get_rules': get_rules}
