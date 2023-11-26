from .BaseExchange import BaseExchange
from .Okx import Okx

exchanges_classes = [
    Okx
]


def get_exchange(name: str, api_key: str, api_secret: str, **kwargs) -> BaseExchange | None:
    for exchange_class in exchanges_classes:
        if exchange_class.name == name:
            return exchange_class(api_key=api_key,
                                  api_secret=api_secret,
                                  **kwargs)
    return None
