from .BaseProxy import BaseProxy


class ResidentialProxy(BaseProxy):
    def __init__(self, proxy: str) -> None:
        super().__init__(proxy)
