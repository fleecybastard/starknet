from globals import NewAccount, FailedAccount, SuccessfulAccount


class BaseNotifier:

    broker: str = None

    async def init(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def start(self) -> None:
        pass

    async def finish(self) -> None:
        pass

    async def new_account(self, account: NewAccount) -> None:
        pass

    async def failed_account(self, account: FailedAccount) -> None:
        pass

    async def successful_account(self, account: SuccessfulAccount) -> None:
        pass
