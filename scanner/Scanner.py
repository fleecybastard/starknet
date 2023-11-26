import asyncio
from decimal import Decimal

import aiohttp

# from config import contracts_config


class Scanner:
    URL = 'https://voyager.online/api'

    def __init__(self):
        self.session: aiohttp.ClientSession | None = None

    async def init(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        await self.session.close()

    async def _request(self, method: str, path: str, params: dict = None, data: dict = None) -> dict:
        response = await self.session.request(method=method,
                                              url=f'{self.URL}{path}',
                                              params=params,
                                              data=data)
        return await response.json()

    async def _get_transactions(self, address: str) -> dict:
        params = {
            'to': address,
            'p': 1,
            'ps': 100
        }
        return await self._request('GET', '/txns', params=params)

    async def get_transactions_count(self, address: str) -> int:
        transactions = await self._get_transactions(address)
        count = 0
        for transaction in transactions['items']:
            if transaction['execution_status'] == 'Succeeded':
                count += 1
        return count

    async def get_eth_balance(self, address: str) -> Decimal:
        response = await self._request('GET', f'/contract/{address}/balances')
        for balance in response:
            if balance['name'] == 'Ether':
                return Decimal(balance['balance'])
        return Decimal('0')
