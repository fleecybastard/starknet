import asyncio

import aiohttp

from .BaseProxy import BaseProxy


class MobileProxy(BaseProxy):
    def __init__(self, proxy: str, change_ip_url: str) -> None:
        super().__init__(proxy)
        self._change_ip_url = change_ip_url

    async def change_ip(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(self._change_ip_url):
                pass

    @property
    def proxy(self):
        asyncio.create_task(self.change_ip())
        return self._proxy
