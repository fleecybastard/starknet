from ..BaseApp import BaseApp
from client import Client
from models import Token
from enums import AppTypeEnum


class BaseDex(BaseApp):

    app_type_ = AppTypeEnum.dex

    def __init__(self, client: Client) -> None:
        super().__init__(client)

    async def swap(self, from_token: Token, to_token: Token, amount: int):
        raise NotImplemented()
