from time import time
from decimal import Decimal, ROUND_HALF_UP


def apply_slippage(amount: int, slippage: float):
    slippage_values = {
        0.1: lambda x: (x / 1000) * 999,
        0.5: lambda x: (x / 1000) * 995,
        1: lambda x: (x / 1000) * 990,
        2: lambda x: (x / 1000) * 980,
    }

    amount = Decimal(amount)
    slippage_fn = slippage_values.get(slippage, lambda x: x)

    result = slippage_fn(amount).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

    return int(result)


def get_deadline():
    return int(time() + 3600)
