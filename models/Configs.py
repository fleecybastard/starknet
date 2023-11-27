from pydantic import BaseModel
from utils.abi import load_abi


class ContractConfig(BaseModel):
    address: str
    abi_path: str

    def abi(self) -> dict:
        return load_abi(self.abi_path)

    def hex_address(self) -> int:
        return int(self.address, 16)


class ContractsConfig(BaseModel):
    jediswap: ContractConfig
    myswap: ContractConfig
    tenkswap: ContractConfig
    sithswap: ContractConfig
    avnu: ContractConfig
    fibrous: ContractConfig

    dmail: ContractConfig
    starknetid: ContractConfig
    starkverse: ContractConfig

    zklend: ContractConfig
