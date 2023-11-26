from pydantic import BaseModel

from .MinMax import MinMaxIntValue, MinMaxDecimalValue
from .RouterContext import RouterContext


class NotifierConfig(BaseModel):
    broker: str
    credentials: dict


class ExchangeConfig(BaseModel):
    name: str
    credentials: dict


class ManagerContext(BaseModel):
    total_transactions: MinMaxIntValue

    sleep_between_accounts: MinMaxIntValue

    notifier: NotifierConfig

    exchange: ExchangeConfig

    shuffle_accounts: bool

    router_context: RouterContext
