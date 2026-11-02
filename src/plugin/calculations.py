"""Offline sample solver using integer monetary arithmetic and bisection."""
from .data import scenario

def rounded(numerator, denominator=10000):
    sign = -1 if numerator < 0 else 1
    return sign * ((2 * abs(numerator) + denominator) // (2 * denominator))

def tax(income, brackets):
    numerator, lower = 0, 0
    for bracket in brackets:
        upper = bracket['upper_cents'] or income
        numerator += max(0, min(income, upper) - lower) * bracket['rate_bps']
        lower = upper
        if upper >= income:
            break
    return rounded(numerator)

def solve(arguments):
    years = arguments['years']
    if type(years) is not int or not 1 <= years <= 60:
        raise ValueError('years must be 1 to 60')
    item = scenario(arguments['scenario_id'])
    a, brackets = item['assumptions'], item['tax_schedule']['brackets']
    balances = [item['balances'][k] for k in ('cash_cents', 'tax_deferred_cents', 'tax_free_cents')]
    rates = [a[k] for k in ('cash_return_bps', 'deferred_return_bps', 'tax_free_return_bps')]
    spending, rows = a['annual_spending_cents'], []
    failure = 0
    for year in range(1, years + 1):
        growth = [rounded(b * r) for b, r in zip(balances, rates)]
        balances = [b + g for b, g in zip(balances, growth)]
        income = a['annual_income_cents'] if year >= a['income_start_year'] else 0
        minimum = min(balances[1], rounded(balances[1] * a['minimum_deferred_bps']))
        withdrawals = [0, minimum, 0]
        def net():
            return income + sum(withdrawals) - tax(income + withdrawals[1], brackets)
        for account in (0, 1, 2):
            if net() >= spending:
                break
            old = withdrawals[account]
            low, high = old, balances[account]
            while low < high:
                mid = (low + high) // 2
                withdrawals[account] = mid
                if net() >= spending:
                    high = mid
                else:
                    low = mid + 1
            withdrawals[account] = low
        taxes = tax(income + withdrawals[1], brackets)
        funds = income + sum(withdrawals) - taxes
        surplus, shortfall = max(0, funds-spending), max(0, spending-funds)
        balances = [b-w for b,w in zip(balances, withdrawals)]
        balances[0] += surplus
        rows.append(dict(year=year, spending_cents=spending, income_cents=income,
                         cash_growth_cents=growth[0], deferred_growth_cents=growth[1], tax_free_growth_cents=growth[2],
                         minimum_deferred_cents=minimum, cash_withdrawal_cents=withdrawals[0],
                         deferred_withdrawal_cents=withdrawals[1], tax_free_withdrawal_cents=withdrawals[2],
                         tax_cents=taxes, surplus_cents=surplus, shortfall_cents=shortfall,
                         ending_cash_cents=balances[0], ending_deferred_cents=balances[1], ending_tax_free_cents=balances[2]))
        if shortfall:
            failure = year
            break
        spending += rounded(spending * a['inflation_bps'])
    return dict(scenario_id=arguments['scenario_id'], years_requested=years, sustainable=not failure,
                first_shortfall_year=failure, total_tax_cents=sum(r['tax_cents'] for r in rows), schedule=rows)
