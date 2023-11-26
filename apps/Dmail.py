from hashlib import sha256

from client import Client
from utils.email_generator import generate_email_address, generate_email_subject

from .BaseApp import BaseApp
from config import contracts_config


class Dmail(BaseApp):
    contract_address = contracts_config.dmail.hex_address()
    abi = contracts_config.dmail.abi()

    app_name = 'dmail'

    def __init__(self, client: Client) -> None:
        super().__init__(client)

    def _convert_to_hex(self, text: str) -> str:
        return sha256(text.encode('UTF-8')).hexdigest()[:31]

    async def interact(self) -> int | None:
        call = self.contract.functions['transaction'].prepare(to=self._convert_to_hex(generate_email_address()),
                                                              theme=self._convert_to_hex(generate_email_subject()))
        return await self.client.call(calls=[call])
