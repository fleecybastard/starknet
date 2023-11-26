import aiohttp

from .BaseNotifier import BaseNotifier
from logger import logger
from globals import NewAccount, FailedAccount, SuccessfulAccount


class TelegramNotifier(BaseNotifier):

    def __init__(self, bot_token: str, chat_id: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.url = f'https://api.telegram.org/bot{bot_token}'
        self.session: aiohttp.ClientSession | None = None

    async def init(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        await self.session.close()

    async def _send_message(self, message: str) -> None:
        data = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        try:
            await self.session.post(f'{self.url}/sendMessage', json=data)
        except:
            logger.error('Telegram send message error:', exc_info=True)

    def _address_text(self, address: str, address_url: str) -> str:
        return f'<a href="{address_url}">{address[:4]}...{address[-4:]}</a>'

    def _new_account_message(self, account: NewAccount) -> str:
        return f'New Account\n' \
               f'Address: {self._address_text(address=account.address, address_url=account.account_url())}\n' \
               f'Name: {account.name}'

    def _failed_account_messsage(self, account: FailedAccount) -> str:
        return f'Failed Account\n' \
               f'Address: {self._address_text(address=account.address, address_url=account.account_url())}\n' \
               f'Name: {account.name}\n' \
               f'Transactions: {account.transactions}\n' \
               f'Error: {account.error[:4000]}'

    def _successful_account_message(self, account: SuccessfulAccount) -> str:
        return f'Successful Account\n' \
               f'Address: {self._address_text(address=account.address, address_url=account.account_url())}\n' \
               f'Name: {account.name}\n' \
               f'Transactions: {account.transactions}\n'

    async def start(self) -> None:
        await self._send_message('✴️Started script')

    async def finish(self) -> None:
        await self._send_message('🏁 Finished script')

    async def new_account(self, account: NewAccount) -> None:
        message = self._new_account_message(account)
        await self._send_message(message)

    async def failed_account(self, account: FailedAccount) -> None:
        message = self._failed_account_messsage(account)
        await self._send_message(message)

    async def successful_account(self, account: SuccessfulAccount) -> None:
        message = self._successful_account_message(account)
        await self._send_message(message)
