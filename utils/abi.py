import json


def load_abi(file: str) -> dict:
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)
