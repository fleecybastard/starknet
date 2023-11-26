from random import randint, shuffle

from apps import BaseApp
from enums import AppTypeEnum


def random_transactions_amount(min_amount: int, max_amount: int,
                               transactions_before: int = 0,
                               total_transactions: int = float('inf')):
    amount = randint(min_amount, max_amount)
    transactions_left = total_transactions - transactions_before
    return min(amount, transactions_left)


def shuffle_path(path: list[BaseApp], swap_or_lend_first: bool) -> list[BaseApp]:
    shuffle(path)
    if not swap_or_lend_first:
        return path

    shuffled_path = []

    for app in path:
        if app.app_type_ in [AppTypeEnum.lending, AppTypeEnum.dex]:
            max_i = max(len(shuffled_path), len(path) // 2 - 1)
            i = randint(0, max_i)
            shuffled_path.insert(i, app)
        else:
            shuffled_path.append(app)
    return shuffled_path




