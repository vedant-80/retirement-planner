"""Trusted verifier fixtures. Keep in sync with src/plugin/data; tests enforce equality."""

def scenarios():
    return {'comfortable': {'assumptions': {'annual_income_cents': 1200000,
                                     'annual_spending_cents': 4000000,
                                     'cash_return_bps': 100,
                                     'deferred_return_bps': 400,
                                     'income_start_year': 1,
                                     'inflation_bps': 250,
                                     'minimum_deferred_bps': 400,
                                     'tax_free_return_bps': 400},
                     'balances': {'cash_cents': 5000000,
                                  'tax_deferred_cents': 80000000,
                                  'tax_free_cents': 20000000},
                     'tax_schedule': {'brackets': [{'rate_bps': 0, 'upper_cents': 2000000},
                                                   {'rate_bps': 1000, 'upper_cents': 5000000},
                                                   {'rate_bps': 2000, 'upper_cents': 0}]}},
     'depleting': {'assumptions': {'annual_income_cents': 1000000,
                                   'annual_spending_cents': 3500000,
                                   'cash_return_bps': 100,
                                   'deferred_return_bps': 400,
                                   'income_start_year': 1,
                                   'inflation_bps': 250,
                                   'minimum_deferred_bps': 400,
                                   'tax_free_return_bps': 400},
                   'balances': {'cash_cents': 100000, 'tax_deferred_cents': 3000000, 'tax_free_cents': 200000},
                   'tax_schedule': {'brackets': [{'rate_bps': 0, 'upper_cents': 2000000},
                                                 {'rate_bps': 1000, 'upper_cents': 5000000},
                                                 {'rate_bps': 2000, 'upper_cents': 0}]}},
     'early-retirement': {'assumptions': {'annual_income_cents': 1200000,
                                          'annual_spending_cents': 4500000,
                                          'cash_return_bps': 100,
                                          'deferred_return_bps': 400,
                                          'income_start_year': 8,
                                          'inflation_bps': 250,
                                          'minimum_deferred_bps': 400,
                                          'tax_free_return_bps': 400},
                          'balances': {'cash_cents': 10000000,
                                       'tax_deferred_cents': 40000000,
                                       'tax_free_cents': 10000000},
                          'tax_schedule': {'brackets': [{'rate_bps': 0, 'upper_cents': 2000000},
                                                        {'rate_bps': 1000, 'upper_cents': 5000000},
                                                        {'rate_bps': 2000, 'upper_cents': 0}]}},
     'exact-funds': {'assumptions': {'annual_income_cents': 0,
                                     'annual_spending_cents': 10000,
                                     'cash_return_bps': 0,
                                     'deferred_return_bps': 0,
                                     'income_start_year': 1,
                                     'inflation_bps': 0,
                                     'minimum_deferred_bps': 0,
                                     'tax_free_return_bps': 0},
                     'balances': {'cash_cents': 10000, 'tax_deferred_cents': 0, 'tax_free_cents': 0},
                     'tax_schedule': {'brackets': [{'rate_bps': 0, 'upper_cents': 2000000},
                                                   {'rate_bps': 1000, 'upper_cents': 5000000},
                                                   {'rate_bps': 2000, 'upper_cents': 0}]}},
     'income-only': {'assumptions': {'annual_income_cents': 1200000,
                                     'annual_spending_cents': 1000000,
                                     'cash_return_bps': 0,
                                     'deferred_return_bps': 0,
                                     'income_start_year': 1,
                                     'inflation_bps': 0,
                                     'minimum_deferred_bps': 0,
                                     'tax_free_return_bps': 0},
                     'balances': {'cash_cents': 0, 'tax_deferred_cents': 0, 'tax_free_cents': 0},
                     'tax_schedule': {'brackets': [{'rate_bps': 0, 'upper_cents': 2000000},
                                                   {'rate_bps': 1000, 'upper_cents': 5000000},
                                                   {'rate_bps': 2000, 'upper_cents': 0}]}},
     'mandatory-surplus': {'assumptions': {'annual_income_cents': 0,
                                           'annual_spending_cents': 10000,
                                           'cash_return_bps': 0,
                                           'deferred_return_bps': 0,
                                           'income_start_year': 1,
                                           'inflation_bps': 0,
                                           'minimum_deferred_bps': 1000,
                                           'tax_free_return_bps': 0},
                           'balances': {'cash_cents': 0, 'tax_deferred_cents': 10000000, 'tax_free_cents': 0},
                           'tax_schedule': {'brackets': [{'rate_bps': 0, 'upper_cents': 2000000},
                                                         {'rate_bps': 1000, 'upper_cents': 5000000},
                                                         {'rate_bps': 2000, 'upper_cents': 0}]}},
     'market-loss': {'assumptions': {'annual_income_cents': 1200000,
                                     'annual_spending_cents': 2000000,
                                     'cash_return_bps': 0,
                                     'deferred_return_bps': -500,
                                     'income_start_year': 1,
                                     'inflation_bps': 250,
                                     'minimum_deferred_bps': 400,
                                     'tax_free_return_bps': -1000},
                     'balances': {'cash_cents': 1000000,
                                  'tax_deferred_cents': 15000000,
                                  'tax_free_cents': 5000000},
                     'tax_schedule': {'brackets': [{'rate_bps': 0, 'upper_cents': 2000000},
                                                   {'rate_bps': 1000, 'upper_cents': 5000000},
                                                   {'rate_bps': 2000, 'upper_cents': 0}]}},
     'tax-gross-up': {'assumptions': {'annual_income_cents': 0,
                                      'annual_spending_cents': 5500000,
                                      'cash_return_bps': 0,
                                      'deferred_return_bps': 0,
                                      'income_start_year': 1,
                                      'inflation_bps': 0,
                                      'minimum_deferred_bps': 0,
                                      'tax_free_return_bps': 0},
                      'balances': {'cash_cents': 0, 'tax_deferred_cents': 10000000, 'tax_free_cents': 0},
                      'tax_schedule': {'brackets': [{'rate_bps': 0, 'upper_cents': 2000000},
                                                    {'rate_bps': 1000, 'upper_cents': 5000000},
                                                    {'rate_bps': 2000, 'upper_cents': 0}]}}}

def rules():
    return {'rules': ['This is a fictional deterministic model, not current tax law or investment advice. Money is '
               'integer cents.',
               'Project 1 to 60 years (default CLI example: 30). Year 1 uses annual_spending_cents; later '
               'spending increases by inflation_bps, rounded to cents.',
               'At the start of each year apply each account annual return to its opening balance, rounding the '
               'signed gain to nearest cent, ties away from zero.',
               'Pension income is taxable and starts in income_start_year. There is no other income or tax '
               'deduction.',
               'Tax brackets list cumulative upper_cents and rate_bps, with upper_cents=0 for the final '
               'unlimited bracket. Compute total progressive tax exactly, then round once to cents, ties up.',
               'First withdraw the required minimum from tax_deferred: post-growth balance times '
               'minimum_deferred_bps, rounded to cents.',
               'To cover spending plus tax, use cash first, then additional tax_deferred, then tax_free. At each '
               'step withdraw the smallest whole-cent amount sufficient, or exhaust the account.',
               'Cash and tax_free withdrawals are untaxed. All tax_deferred withdrawals are taxable. Recompute '
               'tax as withdrawals increase.',
               'Any surplus after spending and tax is deposited into cash at year end. On failure, report the '
               'shortfall and stop at that year. first_shortfall_year=0 means no failure in the requested '
               'horizon.']}

def scenario(identifier):
    items = scenarios()
    if type(identifier) is not str or identifier not in items:
        raise ValueError('Unknown scenario_id')
    return items[identifier]

def tool_output(name, arguments):
    if name == 'get_rules':
        return rules()
    item = scenario(arguments['scenario_id'])
    if name == 'get_account_balances':
        return item['balances']
    if name == 'get_assumptions':
        return item['assumptions']
    if name == 'get_tax_schedule':
        return item['tax_schedule']
    raise ValueError('Unknown tool')
