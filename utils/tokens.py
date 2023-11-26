import json

from models import Token


def load_tokens(file_path: str) -> list[Token]:
    tokens = []
    with open(file_path, 'r', encoding='utf-8') as f:
        obj = json.load(f)
        for token in obj:
            tokens.append(Token(**token))
    return tokens


def get_tokens_dict(tokens: list[Token]) -> dict[str, Token]:
    return {token.name: token for token in tokens}
