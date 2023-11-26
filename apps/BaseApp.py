from starknet_py.contract import Contract

from client import Client
from enums import AppTypeEnum


class BaseApp:
    contract_address: int = None
    abi: list = None
    cairo_version: int = 0

    app_type_: AppTypeEnum = AppTypeEnum.app
    app_name: str = 'app'

    def __init__(self, client: Client):
        self.client = client
        self.contract = Contract(address=self.contract_address,
                                 abi=self.abi,
                                 provider=self.client.account,
                                 cairo_version=self.cairo_version)
