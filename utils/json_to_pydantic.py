from pydantic import BaseModel
import json


def json_to_pydantic(file_path: str, model_class: BaseModel.__class__) -> BaseModel:
    with open(file_path, 'r', encoding='utf-8') as f:
        obj = json.load(f)
        return model_class(**obj)
