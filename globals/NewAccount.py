from dataclasses import dataclass

from .BaseAccount import BaseAccount


@dataclass(kw_only=True)
class NewAccount(BaseAccount):
    pass
