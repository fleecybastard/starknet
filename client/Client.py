import asyncio

from starknet_py.contract import PreparedFunctionCall
from starknet_py.net.client_models import TransactionExecutionStatus
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract
from starknet_py.net.models import StarknetChainId
from starknet_py.hash.address import compute_address


from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

from proxy.BaseProxy import BaseProxy
from utils.browser_data_generator import generate_user_agent
from utils.sleep import random_sleep_time
from utils.ensure_low_gas import ensure_low_gas
from models import Token
from logger import logger


class Client:
    network = 'mainnet'

    rpc_url = 'https://starknet-mainnet.public.blastapi.io'

    send_transaction_attempts = 4
    get_receipt_attempts = 20

    wait_after_deploy = 20  # s

    deploy_class_hash = 0x1a736d6ed154502257f02b1ccdf4d9d1089f80811cd6acad48e6b6a9d1f2003  # argent

    def __init__(self, private_key: str, max_gwei: int, proxy: BaseProxy = None):
        self.proxy = proxy
        self.session: ClientSession | None = None
        self.node_client: FullNodeClient | None = None
        self.account: Account | None = None
        self.private_key = private_key
        self.key_pair = KeyPair.from_private_key(
            key=private_key
        )

        # decorate functions with params from init
        self._deploy = ensure_low_gas(max_gwei)(self._deploy)
        self.call = ensure_low_gas(max_gwei)(self.call)

    async def init(self) -> None:
        self.session = await self.__create_client_session(self.proxy)
        self.node_client = FullNodeClient(self.rpc_url)
        self.account = self.__create_account()

    async def close(self) -> None:
        await self.session.close()

    @property
    def address(self) -> int:
        return self.account.address

    @staticmethod
    def compute_address(private_key: str):

        key_pair = KeyPair.from_private_key(
            key=private_key
        )

        return compute_address(
            class_hash=Client.deploy_class_hash,
            constructor_calldata=[key_pair.public_key, 0],
            salt=key_pair.public_key
        )

    def _compute_address(self) -> int:
        return compute_address(
            class_hash=self.deploy_class_hash,
            constructor_calldata=self._get_deploy_constructor_call_data(),
            salt=self.key_pair.public_key
        )

    @staticmethod
    async def __create_client_session(proxy: BaseProxy = None) -> ClientSession:
        headers = {
            'user-agent': generate_user_agent(),
        }
        connector = None
        if proxy:
            headers['proxy'] = proxy
            connector = ProxyConnector.from_url(url=proxy.proxy)
        return ClientSession(headers=headers, connector=connector)

    def _get_deploy_constructor_call_data(self) -> list:
        return [self.key_pair.public_key, 0]

    def __create_account(self) -> Account:
        return Account(
            address=self._compute_address(),
            client=self.node_client,
            key_pair=self.key_pair,
            chain=StarknetChainId.MAINNET
        )

    async def _is_deployed(self) -> bool:
        nonce = await self.get_nonce()
        return nonce > 0

    async def _deploy(self) -> int | None:
        deploy_tx = await self.account.deploy_account(
            address=self._compute_address(),
            class_hash=self.deploy_class_hash,
            salt=self.key_pair.public_key,
            key_pair=self.key_pair,
            client=self.account.client,
            chain=StarknetChainId.MAINNET,
            constructor_calldata=self._get_deploy_constructor_call_data(),
            auto_estimate=True
        )
        if await deploy_tx.wait_for_acceptance():
            # starknet responds with account not deployed error during next interaction right after deploy, so we wait
            await asyncio.sleep(self.wait_after_deploy)
            return deploy_tx.hash
        return None

    async def deploy(self) -> int | None:
        if not await self._is_deployed():
            return await self._deploy()

    async def get_balance(self, token: Token) -> int:
        return await self.account.get_balance(token.hex_address())

    async def get_nonce(self) -> int:
        return await self.account.get_nonce()

    async def approve(self, token: Token, spender: int, amount: int) -> PreparedFunctionCall | None:
        allowance = await self._get_allowance(token, spender)
        if allowance < amount:
            contract = Contract(address=token.hex_address(),
                                abi=token.abi(),
                                provider=self.account)
            call = contract.functions['approve'].prepare(
                spender=spender,
                amount=amount
            )
            return call

    async def _get_allowance(self, token: Token, spender: int) -> int:
        try:
            contract = Contract(address=token.hex_address(),
                                abi=token.abi(),
                                provider=self.account)
            allowance = await contract.functions['allowance'].prepare(
                owner=self.address,
                spender=spender
            ).call()
            try:
                amount = allowance.remaining
            except:
                amount = allowance.res

            return amount
        except:
            return 0

    async def call(self, calls: list[PreparedFunctionCall] | PreparedFunctionCall) -> int | None:
        if not calls:
            return
        for _ in range(self.send_transaction_attempts):
            try:
                transaction_response = await self.account.execute(calls, auto_estimate=True)
                transaction = await self.account.client.wait_for_tx(
                    tx_hash=transaction_response.transaction_hash
                )
                transaction_hash = transaction.transaction_hash
                logger.info(f'Call hash: {hex(transaction_hash)}')
                for _ in range(self.get_receipt_attempts):
                    try:
                        receipt = await self.account.client.get_transaction_receipt(transaction_hash)
                        if receipt.execution_status == TransactionExecutionStatus.SUCCEEDED:
                            return transaction_hash
                    finally:
                        await asyncio.sleep(random_sleep_time(2, 4))
                else:
                    raise Exception('Transaction not accepted')
            except asyncio.CancelledError:
                break
            except:
                logger.error('Client call error:', exc_info=True)
            await asyncio.sleep(random_sleep_time(5, 10))
