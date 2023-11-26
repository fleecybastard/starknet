from decimal import Decimal
import hmac
from datetime import datetime
import base64

import aiohttp

from .BaseExchange import BaseExchange


class Okx(BaseExchange):
    URL = 'https://www.okx.com'
    SYMBOL = 'ETH'
    CHAIN = 'ETH-Starknet'

    name = 'okx'

    def __init__(self, api_key: str, api_secret: str, pass_phrase: str) -> None:
        super().__init__(api_key, api_secret)
        self._pass_phrase = pass_phrase
        self.session: aiohttp.ClientSession | None = None

    async def init(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        await self.session.close()

    def _generate_signature(self, timestamp: str, method: str, url_postfix: str,
                            body: dict) -> str:
        if str(body) == '{}' or str(body) == 'None':
            body = ''
        message = timestamp + method.upper() + url_postfix + str(body)
        mac = hmac.new(bytes(self._api_secret, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d).decode('utf-8')

    def _generate_headers(self, method: str, url_postfix: str, body: dict) -> dict:
        timestamp = datetime.utcnow().isoformat()[:-3]+'Z'
        headers = {
            'Content-Type': 'application/json',
            'OK-ACCESS-KEY': self._api_key,
            'OK-ACCESS-SIGN': self._generate_signature(timestamp, method, url_postfix, body),
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self._pass_phrase,
            'x-simulated-trading': '0'
        }

        return headers

    async def get_balance(self) -> float:
        url_postfix = '/api/v5/asset/balances'
        url_postfix += f'?ccy={self.SYMBOL}'
        url = self.URL + url_postfix
        response = await self.session.get(url, headers=self._generate_headers('GET', url_postfix, {}))
        return float((await response.json())['data'][0]['availBal'])

    async def get_withdrawal_fee(self) -> float:
        params = {'ccy': self.SYMBOL}
        url_postfix = f'/api/v5/asset/currencies?ccy={self.SYMBOL}'
        url = self.URL + url_postfix
        response = await self.session.get(url, headers=self._generate_headers('GET', url_postfix, params), data=str(params))
        for data in (await response.json())['data']:
            if data['chain'] == self.CHAIN:
                return float(data['minFeeForCtAddr'])
        raise ValueError('No such chain')

    async def get_min_withdrawal_amount(self) -> Decimal:
        params = {'ccy': self.SYMBOL}
        url_postfix = f'/api/v5/asset/currencies?ccy={self.SYMBOL}'
        url = self.URL + url_postfix
        response = await self.session.get(url, headers=self._generate_headers('GET', url_postfix, params),
                                          data=str(params))
        for data in (await response.json())['data']:
            if data['chain'] == self.CHAIN:
                return Decimal(data['minWd'])
        raise ValueError('No such chain')

    async def withdraw(self, address: str, amount: Decimal) -> None:
        params = {
            "amt": str(amount),
            "fee": str(await self.get_withdrawal_fee()),
            "dest": "4",  # on-chain withdrawal
            "ccy": self.SYMBOL,
            "chain": self.CHAIN,
            "toAddr": address
        }
        url_postfix = '/api/v5/asset/withdrawal'
        url = self.URL + url_postfix
        response = await self.session.post(url, headers=self._generate_headers('POST', url_postfix, params),
                                           data=str(params))
        response_json = await response.json()
        if response_json['code'] != '0':
            raise Exception(f'Withdraw Failed: {response_json["msg"]}')
