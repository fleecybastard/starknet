from .BaseDex import BaseDex
from config import contracts_config
from client import Client
from models import Token
from utils.swaps import get_deadline, apply_slippage


class SithSwap(BaseDex):
    contract_address = contracts_config.sithswap.hex_address()
    abi = contracts_config.sithswap.abi()
    slippage = 2

    app_name = 'sithswap'


    def __init__(self, client: Client) -> None:
        super().__init__(client)

    async def _get_amount_out_min(self, amount: int, routes: list[dict]) -> int:
        amount_out_min = await self.contract.functions['getAmountsOut'].call(
            amount_in=amount,
            routes=routes
        )
        return apply_slippage(amount_out_min.amounts[1], slippage=self.slippage)

    async def swap(self, from_token: Token, to_token: Token, amount: int) -> int | None:
        calls = []

        approve = await self.client.approve(token=from_token,
                                            spender=self.contract_address,
                                            amount=amount)
        if approve:
            calls.append(approve)

        routes = [{
            'from_address': from_token.hex_address(),
            'to_address': to_token.hex_address(),
            'stable': 0
        }]

        amount_out_min = await self._get_amount_out_min(amount=amount, routes=routes)

        swap = self.contract.functions['swapExactTokensForTokensSupportingFeeOnTransferTokens'].prepare(
            amount_in=amount,
            amount_out_min=amount_out_min,
            routes=routes,
            to=self.client.address,
            deadline=get_deadline()
        )

        calls.append(swap)

        return await self.client.call(calls=calls)
