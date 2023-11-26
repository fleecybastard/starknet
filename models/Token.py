from typing import Any, Optional
from pydantic import BaseModel, Field, Json, field_validator, FieldValidationInfo

from utils.abi import load_abi


class Token(BaseModel):
    address: str
    name: str
    decimals: int
    abi_path: str

    def __hash__(self):
        return hash(self.address)

    def abi(self) -> Json[Any]:
        try:
            return self._abi
        except AttributeError:
            abi_ = load_abi(self.abi_path)
            self._abi = abi_
            return self._abi

    def hex_address(self) -> int:
        return int(self.address, 16)
