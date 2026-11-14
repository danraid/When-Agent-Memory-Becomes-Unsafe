"""Single-process API cost preflight (NOT concurrency-safe billing)."""
from decimal import Decimal


def permit(limits, spent, *, calls, input_tokens, output_tokens, usd):
    additions = {'calls': calls, 'input_tokens': input_tokens, 'output_tokens': output_tokens}
    for key, increment in additions.items():
        if type(increment) is not int or increment < 0:
            raise ValueError('Usage increments must be nonnegative integers')
        cap = limits.get('max_'+key)
        if type(cap) is not int or cap < 0:
            raise ValueError('Invalid budget for '+key)
        observed = spent.get(key, 0)
        if type(observed) is not int or observed < 0:
            raise ValueError('Invalid previous budget usage for ' + key)
        if observed + increment > cap:
            return False, key.upper()+'_CAP'
    amount = Decimal(str(usd))
    previous_usd = Decimal(str(spent.get('usd', '0')))
    if not amount.is_finite() or amount < 0 or not previous_usd.is_finite() or previous_usd < 0:
        raise ValueError('Invalid USD accounting amount')
    # Explicit opt-out of a *monetary* ceiling. Finite calls/tokens remain a
    # scientific experiment definition and a protection against retry loops.
    ceiling_value = limits.get('max_usd')
    if ceiling_value is None:
        return True, 'USD_UNCAPPED_WITH_FINITE_EXPERIMENT_LIMITS'
    ceiling = Decimal(str(ceiling_value))
    if not ceiling.is_finite() or ceiling < 0:
        raise ValueError('Invalid USD ceiling')
    if previous_usd + amount > ceiling:
        return False, 'USD_CAP'
    return True, 'WITHIN_BUDGET_NOT_RESERVED'
