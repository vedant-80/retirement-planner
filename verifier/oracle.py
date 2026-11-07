"""Independent Decimal annual replay with bracketwise withdrawal gross-up."""
from decimal import Decimal, ROUND_HALF_UP, localcontext
from .fixtures import scenario

def validate_arguments(args):
    if type(args) is not dict or set(args) != {'scenario_id', 'years'}:
        raise ValueError('Expected scenario_id and years')
    scenario(args['scenario_id'])
    if type(args['years']) is not int or not 1 <= args['years'] <= 60:
        raise ValueError('years must be integer 1 to 60')

def money(value):
    return int(value.quantize(Decimal(1), rounding=ROUND_HALF_UP))

def expected(args):
    with localcontext() as context:
        context.prec = 60
        return replay(args)

def replay(args):
    fixture = scenario(args['scenario_id'])
    rules = fixture['assumptions']
    brackets = fixture['tax_schedule']['brackets']
    def taxes(income):
        total, previous = Decimal(0), 0
        for band in brackets:
            ceiling = income if band['upper_cents'] == 0 else band['upper_cents']
            width = max(0, min(ceiling, income)-previous)
            total += Decimal(width) * Decimal(band['rate_bps']) / 10000
            previous = ceiling
            if income <= ceiling:
                break
        return money(total)
    cash = fixture['balances']['cash_cents']
    deferred = fixture['balances']['tax_deferred_cents']
    free = fixture['balances']['tax_free_cents']
    spending = rules['annual_spending_cents']
    history, failure = [], 0
    for year in range(1, args['years'] + 1):
        gains = [money(Decimal(amount) * rules[key] / 10000) for amount,key in
                 ((cash,'cash_return_bps'), (deferred,'deferred_return_bps'), (free,'tax_free_return_bps'))]
        cash += gains[0]
        deferred += gains[1]
        free += gains[2]
        pension = rules['annual_income_cents'] if year >= rules['income_start_year'] else 0
        required = min(deferred, money(Decimal(deferred) * rules['minimum_deferred_bps'] / 10000))
        dw = required
        cw = min(cash, max(0, spending + taxes(pension+dw) - pension - dw))
        # Solve each marginal tax segment algebraically, correcting for cent rounding.
        need = spending - pension - cw
        if dw - taxes(pension+dw) < need:
            chosen = None
            lower = 0
            base_tax = Decimal(0)
            for band in brackets:
                upper = band['upper_cents'] or (pension + deferred + 1)
                rate = Decimal(band['rate_bps']) / 10000
                # dw - (base_tax + (pension+dw-lower)*rate) >= need.
                root = (Decimal(need) + base_tax + (pension-lower)*rate) / (1-rate)
                candidate = max(required, lower-pension, int(root)-2, 0)
                while candidate <= deferred and pension+candidate <= upper:
                    if candidate - taxes(pension+candidate) >= need:
                        chosen = candidate
                        break
                    candidate += 1
                if chosen is not None:
                    break
                base_tax += Decimal(upper-lower)*rate
                lower = upper
            dw = deferred if chosen is None else chosen
        fw = min(free, max(0, spending + taxes(pension+dw) - pension - cw - dw))
        paid_tax = taxes(pension+dw)
        available = pension + cw + dw + fw - paid_tax
        excess = max(0, available-spending)
        shortage = max(0, spending-available)
        cash, deferred, free = cash-cw+excess, deferred-dw, free-fw
        history.append({'year': year, 'spending_cents': spending, 'income_cents': pension,
                        'cash_growth_cents': gains[0], 'deferred_growth_cents': gains[1], 'tax_free_growth_cents': gains[2],
                        'minimum_deferred_cents': required, 'cash_withdrawal_cents': cw,
                        'deferred_withdrawal_cents': dw, 'tax_free_withdrawal_cents': fw,
                        'tax_cents': paid_tax, 'surplus_cents': excess, 'shortfall_cents': shortage,
                        'ending_cash_cents': cash, 'ending_deferred_cents': deferred, 'ending_tax_free_cents': free})
        if shortage:
            failure = year
            break
        spending = money(Decimal(spending) * (10000 + rules['inflation_bps']) / 10000)
    return {'scenario_id': args['scenario_id'], 'years_requested': args['years'], 'sustainable': failure == 0,
            'first_shortfall_year': failure, 'total_tax_cents': sum(r['tax_cents'] for r in history), 'schedule': history}
