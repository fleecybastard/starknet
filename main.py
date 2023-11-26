import asyncio

from data_storage import DataStorage
from accounts_manager import AccountsManager
from utils.json_to_pydantic import json_to_pydantic
from models import ManagerContext


async def main():
    data_storage = DataStorage(
        private_keys_file='data/private_keys.txt',
        successful_accounts_file='data/successful_accounts.txt',
        failed_accounts_file='data/failed_accounts.txt'
    )

    private_keys = data_storage.get_private_keys()
    manager_context: ManagerContext = json_to_pydantic('data/manager_context.json', ManagerContext)
    manager = AccountsManager(
        manager_context=manager_context,
        private_keys=private_keys
    )

    await manager.init()

    successful_accounts, failed_accounts = await manager.run()

    if failed_accounts:
        data_storage.add_failed_accounts(failed_accounts)
    if successful_accounts:
        data_storage.add_successful_accounts(successful_accounts)

    await manager.close()


if __name__ == '__main__':
    asyncio.run(main())
