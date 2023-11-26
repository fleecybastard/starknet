from dataclasses import dataclass


@dataclass(kw_only=True)
class BaseAccount:
    address: str
    name: str

    def account_url(self) -> str:
        return f'https://starkscan.co/contract/{self.address}'