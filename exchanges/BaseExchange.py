from decimal import Decimal


class BaseExchange:

    name: str = None

    def __init__(self, api_key: str, api_secret: str) -> None:
        self._api_key = api_key
        self._api_secret = api_secret

    async def init(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def get_balance(self) -> Decimal:
        raise NotImplemented()

    async def get_min_withdrawal_amount(self) -> Decimal:
        raise NotImplemented()

    async def withdraw(self, address: str, amount: Decimal) -> None:
        raise NotImplemented()
