from pydantic import BaseModel

from .MinMax import MinMaxIntValue, MinMaxDecimalValue


class RouterContext(BaseModel):
    swap_or_lend: MinMaxIntValue
    dmail: MinMaxIntValue
    starknet_id: MinMaxIntValue
    zklend_collateral: MinMaxIntValue
    starkverse: MinMaxIntValue
    total_transactions: MinMaxIntValue

    eth_transaction_amount: MinMaxDecimalValue

    eth_top_up_amount: MinMaxDecimalValue

    sleep_between_transactions: MinMaxIntValue

    swap_or_lend_first: bool

    second_top_up: bool

    max_gwei: int

    leave_eth: MinMaxDecimalValue

