from .BaseDex import BaseDex
from config import contracts_config, tokens
from client import Client
from models import Token
from utils.swaps import apply_slippage


class MySwap(BaseDex):
    contract_address = contracts_config.myswap.hex_address()
    abi = contracts_config.myswap.abi()

    slippage = 2
    pools_ids = {'eth-usdc': 1, 'dai-eth': 2, 'eth-usdt': 4, 'usdc-usdt': 5, 'dai-usdc': 6}

    app_name = 'myswap'


    def __init__(self, client: Client) -> None:
        super().__init__(client)

    @staticmethod
    def _get_pool_name(from_token: str, to_token: str):
        return from_token + '-' + to_token

    def _get_pool_id_and_reverse(self, from_token: Token, to_token: Token) -> tuple[int, bool]:
        pool_name = self._get_pool_name(from_token=from_token.name, to_token=to_token.name)
        pool_id = self.pools_ids.get(pool_name)
        if pool_id:
            return pool_id, False
        pool_name = self._get_pool_name(from_token=to_token.name, to_token=from_token.name)
        pool_id = self.pools_ids.get(pool_name)
        if pool_id:
            return pool_id, True
        pool_name = self._get_pool_name(from_token=from_token.name, to_token='eth')
        pool_id = self.pools_ids.get(pool_name)
        if pool_id:
            return pool_id, False
        pool_name = self._get_pool_name(from_token='eth', to_token=from_token.name)
        pool_id = self.pools_ids.get(pool_name)
        if pool_id:
            return pool_id, True

    async def _get_amount_out_min(self, pool_id: int, reverse: bool, amount: int) -> int:
        pool_data = await self.contract.functions["get_pool"].prepare(
            pool_id=pool_id
        ).call()
        pool_data = pool_data.pool
        reserve_a = pool_data.get('token_a_reserves')
        reserve_b = pool_data.get('token_b_reserves')
        if reverse:
            reserve_a, reserve_b = reserve_b, reserve_a
        amount_out_min = reserve_b * amount / reserve_a
        return apply_slippage(amount_out_min, self.slippage)

    async def swap(self, from_token: Token, to_token: Token, amount: int) -> int | None:
        pool_id, reverse = self._get_pool_id_and_reverse(from_token=from_token, to_token=to_token)
        if pool_id is None:
            return None

        calls = []

        approve = await self.client.approve(token=from_token,
                                            spender=self.contract_address,
                                            amount=amount)
        if approve:
            calls.append(approve)

        amount_out_min = await self._get_amount_out_min(pool_id=pool_id,
                                                        reverse=reverse,
                                                        amount=amount)

        swap = self.contract.functions['swap'].prepare(
            pool_id=pool_id,
            token_from_addr=from_token.hex_address(),
            amount_from=amount,
            amount_to_min=amount_out_min
        )

        calls.append(swap)

        return await self.client.call(calls)
