from client import Client

from .BaseApp import BaseApp
from config import contracts_config


class StarkVerse(BaseApp):
    contract_address = contracts_config.starkverse.hex_address()
    abi = contracts_config.starkverse.abi()

    app_name = 'starkverse'

    def __init__(self, client: Client) -> None:
        super().__init__(client)

    async def interact(self) -> int | None:
        call = self.contract.functions['publicMint'].prepare(
            to=self.client.address
        )
        return await self.client.call(call)
