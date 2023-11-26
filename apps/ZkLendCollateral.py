from random import choice

from client import Client
from .BaseApp import BaseApp
from config import contracts_config, tokens
from models import Token
from enums import AppTypeEnum


class ZkLendCollateral(BaseApp):
    contract_address = contracts_config.zklend.hex_address()
    abi = contracts_config.zklend.abi()

    app_type_ = AppTypeEnum.app
    app_name = 'zklend_collateral'

    def __init__(self, client: Client) -> None:
        super().__init__(client)

    @staticmethod
    def _choose_token() -> Token:
        return choice(tokens)

    async def _is_collateral_enabled(self, token: Token) -> bool:
        response = await self.contract.functions['is_collateral_enabled'].call(
            user=self.client.address, token=token.hex_address())
        return bool(response.enabled)

    async def _enable_collateral(self, token: Token) -> int | None:
        call = self.contract.functions['enable_collateral'].prepare(token=token.hex_address())
        return await self.client.call(calls=[call])

    async def _disable_collateral(self, token: Token) -> None:
        call = self.contract.functions['disable_collateral'].prepare(token=token.hex_address())
        return await self.client.call(calls=[call])

    async def interact(self):
        token = self._choose_token()
        if await self._is_collateral_enabled(token):
            return await self._disable_collateral(token)
        else:
            return await self._enable_collateral(token)
