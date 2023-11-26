from decimal import Decimal

from pydantic import BaseModel


class MinMaxIntValue(BaseModel):
    min: int
    max: int


class MinMaxDecimalValue(BaseModel):
    min: Decimal
    max: Decimal
