from starknet_py.contract import PreparedFunctionCall

from .BaseLending import BaseLending
from config import contracts_config
from models import Token


class ZkLend(BaseLending):
    contract_address = contracts_config.zklend.hex_address()
    abi = contracts_config.zklend.abi()

    app_name = 'zklend'

    async def _is_collateral_enabled(self, token: Token) -> bool:
        response = await self.contract.functions['is_collateral_enabled'].call(
            user=self.client.address, token=token.hex_address())
        return bool(response.enabled)

    def _enable_collateral(self, token: Token) -> PreparedFunctionCall:
        call = self.contract.functions['enable_collateral'].prepare(token=token.hex_address())
        return call

    async def lend(self, token: Token, amount: int) -> int | None:
        calls = []
        approve = await self.client.approve(token=token,
                                            spender=self.contract_address,
                                            amount=amount)
        if approve:
            calls.append(approve)

        if not await self._is_collateral_enabled(token=token):
            enable = self._enable_collateral(token=token)
            calls.append(enable)
        lend_call = self.contract.functions['deposit'].prepare(token=token.hex_address(),
                                                               amount=amount)
        calls.append(lend_call)
        return await self.client.call(calls=calls)
