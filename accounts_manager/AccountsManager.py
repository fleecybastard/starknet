import asyncio
from traceback import format_exc
from random import shuffle

from models import ManagerContext, RouterContext
from router import Router
from scanner import Scanner
from notifiers import get_notifier
from client import Client
from globals import FailedAccount, SuccessfulAccount, NewAccount
from exchanges import get_exchange
from logger import logger
from utils.sleep import random_sleep_time


class AccountsManager:

    SUCCESS_NOTIFY_SLEEP = 120  # seconds

    def __init__(self, manager_context: ManagerContext, private_keys: list[str]) -> None:
        self.manager_context = manager_context
        self.private_keys = private_keys
        if self.manager_context.shuffle_accounts:
            shuffle(self.private_keys)

        self.notifier = get_notifier(
            manager_context.notifier.broker,
            params=manager_context.notifier.credentials
        )

        self.exchange = get_exchange(
            manager_context.exchange.name,
            **manager_context.exchange.credentials
        )

        self.scanner = Scanner()

        self.successful_accounts = []
        self.failed_accounts = []

    async def init(self) -> None:
        await self.scanner.init()
        await self.notifier.init()
        await self.exchange.init()

    async def close(self) -> None:
        await self.scanner.close()
        await self.notifier.close()
        await self.exchange.close()

    async def _get_transactions_left(self, address: str) -> tuple[int, int]:
        transactions = await self.scanner.get_transactions_count(address)
        min_transactions = self.manager_context.total_transactions.min - transactions
        max_transactions = self.manager_context.total_transactions.max - transactions
        return min_transactions, max_transactions

    async def _get_router_context(self, address: str) -> RouterContext:
        context = self.manager_context.router_context
        transactions_left_min, transactions_left_max = await self._get_transactions_left(address)
        if transactions_left_min < context.total_transactions.min:
            context.total_transactions.min = transactions_left_min
        if transactions_left_max < context.total_transactions.max:
            context.total_transactions.max = transactions_left_max
        if context.finish_transactions:
            context.total_transactions.min = transactions_left_min
            context.total_transactions.max = transactions_left_max
        return context

    async def _notify_success(self, account: SuccessfulAccount) -> None:
        # Starkscan updates account transactions with a delay
        await asyncio.sleep(self.SUCCESS_NOTIFY_SLEEP)
        await self.notifier.successful_account(account)

    async def run(self) -> tuple[list[str], list[str]]:

        successful_accounts = []
        failed_accounts = []

        await self.notifier.start()

        for i, private_key in enumerate(self.private_keys):
            name = f'Account {i+1}'
            address = hex(Client.compute_address(private_key))
            await self.notifier.new_account(NewAccount(
                address=address,
                name=name
            ))
            logger.info(f'Account {address} started')
            try:
                router_context = await self._get_router_context(address)
                router = Router(
                    private_key=private_key,
                    exchange=self.exchange,
                    context=router_context
                )
                await router.init()

                await router.run()

                await router.close()

            except:
                logger.error('Manager Error:', exc_info=True)
                transactions = await self.scanner.get_transactions_count(address)
                await self.notifier.failed_account(
                    FailedAccount(
                        address=address,
                        name=name,
                        transactions=transactions,
                        error=format_exc()
                    )
                )
                failed_accounts.append(private_key)
            else:
                transactions = await self.scanner.get_transactions_count(address)
                asyncio.create_task(self._notify_success(SuccessfulAccount(
                    address=address,
                    name=name,
                    transactions=transactions
                )))
                successful_accounts.append(private_key)
            logger.info(f'Account {address} finished')
            await asyncio.sleep(random_sleep_time(
                min_time=self.manager_context.sleep_between_accounts.min,
                max_time=self.manager_context.sleep_between_accounts.max
            ))
        await self.notifier.finish()

        return successful_accounts, failed_accounts
