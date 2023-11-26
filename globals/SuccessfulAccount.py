from dataclasses import dataclass

from .BaseAccount import BaseAccount


@dataclass(kw_only=True)
class SuccessfulAccount(BaseAccount):

    transactions: int
