from dataclasses import dataclass

from .BaseAccount import BaseAccount


@dataclass(kw_only=True)
class FailedAccount(BaseAccount):

    transactions: int
    error: str
