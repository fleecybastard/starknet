from ..BaseApp import BaseApp
from client import Client
from models import Token
from enums import AppTypeEnum


class BaseLending(BaseApp):

    app_type_ = AppTypeEnum.lending

    def __init__(self, client: Client) -> None:
        super().__init__(client)

    async def lend(self, token: Token, amount: int) -> int | None:
        raise NotImplemented()
