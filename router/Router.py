import asyncio
from random import choice
from decimal import Decimal
from time import time

from client import Client
from proxy import BaseProxy
from config import tokens, tokens_dict
from models import Token, RouterContext
from apps import get_apps, BaseApp, BaseDex, BaseLending
from enums import AppTypeEnum
from utils.amount import random_amount_wei, random_amount_ether
from utils.sleep import random_sleep_time
from utils.router_path import random_transactions_amount, shuffle_path
from exchanges import BaseExchange
from logger import logger


class Router:

    MAX_TOP_UP_WAIT_TIME = 300  # seconds
    TOP_UP_CHECK_TIME = 5  # seconds

    def __init__(self, private_key: str,
                 exchange: BaseExchange,
                 context: RouterContext,
                 proxy: BaseProxy = None) -> None:
        self.client = Client(
            private_key=private_key,
            max_gwei=context.max_gwei,
            proxy=proxy)
        self.exchange = exchange

        self.context = context

        self.apps = None
        self.dexes = None
        self.lendings = None

    async def init(self):
        await self.client.init()
        self.apps: list[BaseApp] = get_apps(self.client, app_type=AppTypeEnum.app)
        self.dexes: list[BaseDex] = get_apps(self.client, app_type=AppTypeEnum.dex)
        self.lendings: list[BaseLending] = get_apps(self.client, app_type=AppTypeEnum.lending)

    async def close(self):
        await self.client.close()

    async def _top_up_account(self) -> None:
        amount = await self._get_top_up_amount()
        if amount:
            previous_balance = await self._get_eth_balance()
            await self.exchange.withdraw(
                address=hex(self.client.address),
                amount=amount
            )
            await self._wait_for_top_up(previous_balance)

    async def _wait_for_top_up(self, previous_balance: int) -> None:
        start_time = time()
        while time() - start_time <= self.MAX_TOP_UP_WAIT_TIME:
            balance = await self._get_eth_balance()
            if balance > previous_balance:
                return
            await asyncio.sleep(self.TOP_UP_CHECK_TIME)
        raise TimeoutError('Withdraw took too long')

    async def _get_top_up_amount(self) -> Decimal | None:
        eth_balance = await self._get_eth_balance()
        if eth_balance > 0 and not self.context.second_top_up:
            return None
        decimals = tokens_dict['eth'].decimals
        min_top_up_amount = self.context.eth_top_up_amount.min
        max_top_up_amount = self.context.eth_top_up_amount.max
        top_up_amount = random_amount_ether(min_top_up_amount, max_top_up_amount, decimals) - eth_balance
        min_withdrawal_amount = await self.exchange.get_min_withdrawal_amount()
        if min_withdrawal_amount > top_up_amount:
            return None
        return top_up_amount

    async def _get_balances(self) -> dict[Token, int]:
        balances = {}
        for token in tokens:
            token_balance = await self.client.get_balance(token)
            if token_balance > 0:
                balances[token] = token_balance
        return balances

    async def _get_eth_balance(self) -> int:
        return await self.client.get_balance(tokens_dict['eth'])

    def _get_leave_eth_amount(self) -> int:
        eth_token = tokens_dict['eth']
        return random_amount_wei(self.context.leave_eth.min, self.context.leave_eth.max, eth_token.decimals)

    def _choose_app(self, apps: list[BaseApp]) -> BaseApp:
        return choice(apps)

    async def _choose_token_with_balance(self) -> tuple[Token, int]:
        balances = await self._get_balances()
        token = choice(list(balances.keys()))
        if token.name == 'eth':
            min_amount = self.context.eth_transaction_amount.min
            max_amount = self.context.eth_transaction_amount.max
            amount = random_amount_wei(min_amount, max_amount, token.decimals)
            return token, amount
        return token, random_amount_wei(int(0.5 * balances[token]), balances[token])

    def _choose_token(self, exclude: Token = None) -> Token:
        tokens_ = [t for t in tokens if t != exclude]
        return choice(tokens_)

    async def _app_interact(self, app: BaseApp) -> None:
        return await app.interact()

    async def _dex_interact(self, dex: BaseDex) -> None:
        from_token, amount = await self._choose_token_with_balance()
        to_token = self._choose_token(exclude=from_token)
        return await dex.swap(from_token, to_token, amount)

    async def _lending_interact(self, lending: BaseLending) -> None:
        token, amount = await self._choose_token_with_balance()
        return await lending.lend(token=token, amount=amount)

    async def _interact(self, app: BaseApp) -> int | None:
        if app.app_type_ == AppTypeEnum.app:
            return await self._app_interact(app)
        elif app.app_name == AppTypeEnum.lending:
            return await self._lending_interact(app)
        elif app.app_type_ == AppTypeEnum.dex:
            return await self._dex_interact(app)

    def _construct_path(self) -> list[BaseApp]:
        path = []

        dmail = None
        starknet_id = None
        zklend_collateral = None
        starkverse = None
        for app in self.apps:
            if app.app_name == 'dmail':
                dmail = app
            elif app.app_name == 'starknet_id':
                starknet_id = app
            elif app.app_name == 'zklend_collateral':
                zklend_collateral = app
            elif app.app_name == 'starkverse':
                starkverse = app

        total_transactions_amount = random_transactions_amount(
            min_amount=self.context.total_transactions.min,
            max_amount=self.context.total_transactions.max
        )

        swap_or_lend_amount = random_transactions_amount(min_amount=self.context.swap_or_lend.min,
                                                         max_amount=self.context.swap_or_lend.max,
                                                         transactions_before=len(path),
                                                         total_transactions=total_transactions_amount)
        for _ in range(swap_or_lend_amount):
            path.append(self._choose_app(self.dexes + self.lendings))

        if starkverse:
            starkverse_amount = random_transactions_amount(
                min_amount=self.context.starkverse.min,
                max_amount=self.context.starkverse.max,
                transactions_before=len(path),
                total_transactions=total_transactions_amount
            )
            for _ in range(starkverse_amount):
                path.append(starkverse)

        if dmail:
            dmail_amount = random_transactions_amount(
                min_amount=self.context.dmail.min,
                max_amount=self.context.dmail.max,
                transactions_before=len(path),
                total_transactions=total_transactions_amount
            )

            for _ in range(dmail_amount):
                path.append(dmail)

        if starknet_id:
            starknet_id_amount = random_transactions_amount(
                min_amount=self.context.starknet_id.min,
                max_amount=self.context.starknet_id.max,
                transactions_before=len(path),
                total_transactions=total_transactions_amount
            )

            for _ in range(starknet_id_amount):
                path.append(starknet_id)

        if zklend_collateral:
            zklend_collateral_amount = random_transactions_amount(
                min_amount=self.context.zklend_collateral.min,
                max_amount=self.context.zklend_collateral.max,
                transactions_before=len(path),
                total_transactions=total_transactions_amount
            )

            for _ in range(zklend_collateral_amount):
                path.append(zklend_collateral)

        for _ in range(total_transactions_amount - len(path)):
            path.append(self._choose_app(self.apps))

        return shuffle_path(path=path, swap_or_lend_first=self.context.swap_or_lend_first)

    async def run(self) -> None:
        await self._top_up_account()
        await self.client.deploy()
        path = self._construct_path()
        logger.info(f'Path: {[a.app_name for a in path]}')
        leave_eth_amount = self._get_leave_eth_amount()
        for app in path:
            eth_balance = await self._get_eth_balance()
            if eth_balance <= leave_eth_amount:
                logger.info(f'Leave eth {leave_eth_amount} is higher than eth balance {eth_balance}')
                return
            logger.info(f'{app.app_name} Started')
            try:
                transaction_hash = await self._interact(app)
            except:
                logger.error('Router Error:', exc_info=True)
            else:
                transaction_hash = hex(transaction_hash) if transaction_hash else None
                logger.info(f'{app.app_name} Finished. Hash: {transaction_hash}')
            await asyncio.sleep(random_sleep_time(
                min_time=self.context.sleep_between_transactions.min,
                max_time=self.context.sleep_between_transactions.max
            ))
