import asyncio

from web3 import AsyncWeb3
from starknet_py.net.gateway_client import GatewayClient

from utils.sleep import random_sleep_time


async def get_current_eth_gwei():
    web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider('https://rpc.ankr.com/eth'))
    gas_price = await web3.eth.gas_price
    gwei = gas_price / 10 ** 9
    return gwei


async def get_current_starknet_gwei():
    try:
        gateway_client = GatewayClient(net='mainnet')
        block = await gateway_client.get_block(block_number='pending')
        return block.gas_price / 10 ** 9
    except:
        return float('inf')


def ensure_low_gas(max_gwei: int):
    def inner(func):
        async def wrapper(*args, **kwargs):
            while True:
                starknet_gwei = await get_current_starknet_gwei()
                if starknet_gwei <= max_gwei:
                    return await func(*args, **kwargs)
                await asyncio.sleep(random_sleep_time(10, 45))
        return wrapper
    return inner
