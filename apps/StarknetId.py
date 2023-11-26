from random import randint

from .BaseApp import BaseApp
from config import contracts_config


class StarknetId(BaseApp):
    contract_address = contracts_config.starknetid.hex_address()
    abi = contracts_config.starknetid.abi()

    app_name = 'starknet_id'

    @staticmethod
    def _generate_starknet_id() -> int:
        return randint(500000, 40000000000)

    async def interact(self) -> int | None:
        starknet_id = self._generate_starknet_id()
        call = self.contract.functions['mint'].prepare(starknet_id=starknet_id)
        return await self.client.call(call)
