

class BaseProxy:
    def __init__(self, proxy: str):
        self._proxy = proxy

    @property
    def proxy(self):
        return self._proxy
