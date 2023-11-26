from .BaseDex import BaseDex
from config import contracts_config
from client import Client
from models import Token
from utils.swaps import apply_slippage, get_deadline


class JediSwap(BaseDex):
    contract_address = contracts_config.jediswap.hex_address()
    abi = contracts_config.jediswap.abi()
    slippage = 2

    app_name = 'jediswap'

    def __init__(self, client: Client) -> None:
        super().__init__(client)

    async def _get_amount_out_min(self, amount: int, path: list[int]) -> int:
        amount_out_min = await self.contract.functions['get_amounts_out'].call(
            amountIn=amount,
            path=path
        )
        return apply_slippage(amount_out_min.amounts[1], slippage=self.slippage)

    async def swap(self, from_token: Token, to_token: Token, amount: int) -> int | None:
        calls = []

        approve = await self.client.approve(token=from_token,
                                            spender=self.contract_address,
                                            amount=amount)
        if approve:
            calls.append(approve)

        path = [from_token.hex_address(), to_token.hex_address()]
        amount_out_min = await self._get_amount_out_min(amount=amount, path=path)

        swap = self.contract.functions['swap_exact_tokens_for_tokens'].prepare(
            amountIn=amount,
            amountOutMin=amount_out_min,
            path=path,
            to=self.client.address,
            deadline=get_deadline()
        )
        calls.append(swap)
        return await self.client.call(calls=calls)
