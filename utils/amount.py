from random import randint, uniform
from decimal import Decimal


def convert_to_wei(amount: Decimal, decimals: int) -> int:
    return int(amount * (10 ** decimals))


def convert_to_ether(amount: int, decimals: int) -> Decimal:
    return Decimal(amount) / Decimal(10 ** decimals)


def random_amount_wei(min_amount: Decimal | int, max_amount: Decimal | int, decimals: int = None) -> int:
    if decimals is not None:
        min_amount = convert_to_wei(min_amount, decimals)
        max_amount = convert_to_wei(max_amount, decimals)
    return randint(min_amount, max_amount)


def random_amount_ether(min_amount: Decimal, max_amount: Decimal, decimals: int) -> Decimal:
    return Decimal(round(uniform(float(min_amount), float(max_amount)), decimals))
