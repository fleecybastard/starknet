from models.Configs import ContractsConfig
from models import Token
from utils.json_to_pydantic import json_to_pydantic
from utils.tokens import load_tokens, get_tokens_dict


contracts_config: ContractsConfig = json_to_pydantic('configs/contracts_config.json', ContractsConfig)

tokens: list[Token] = load_tokens('configs/tokens_config.json')

tokens_dict = get_tokens_dict(tokens)
