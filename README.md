# Starknet automation for cheap accounts by <a href="https://t.me/fleecybastard">@fleecybastard</a>
<img src="https://www.starknet-ecosystem.com/starknet-map.png">
This project is built to create cheap starknet accounts, that interact with various starknet contracts depending 
on the configured parameters.

**DISCLAIMER**: This is not a financial advice. Use this software at your own risk, I am not responsible for any money 
loss.

## Installation
1. Clone project
```bash
git clone https://github.com/fleecybastard/starknet
```

2. Install requirements
```bash
pip install -r requirements.txt
```

3. Configure starknet-py library
starknet-py requires additional configuration. Necessary steps can be found <a href="https://starknetpy.readthedocs.io/en/latest/installation.html">here</a>. 
If you have troubles configuring it on windows, use wsl.

## Configuration
1. Copy **data/manager_context.example.json** file to **data/manager_context.json**
2. Change all necessary configurations in **data/manager_context.json**:

**total_transactions** - int values for min and max. Script picks a random amount of transactions for each account in the range of (min, max)

**sleep_between_accounts** - int values for min and max. Script picks a random amount of seconds to sleep between accounts in the range of (min, max)

**notifier** - *broker* - "telegram_bot" (Only telegram bot notifier is available at the moment) *credentials* - *bot_token* - Create a telegram bot using <a href="https://t.me/BotFather">BotFather</a>, *chat_id* - id of the chat bot will send logs to (can be a group)

**exchange** - *name* - "okx" (Only okx is available at the moment), *credentials* - exchange credentials

**shuffle_accounts** - boolean value (true/false). true if you want to randomise accounts order.

**router_context** - configuration of account. (Read Account Strategy to fully understand these parameters). 

*swap_or_lend* - int values for min and max. Script picks a random amount of transactions of type swap or lend for each account in the range of (min, max)

*starkverse* - int values for min and max. Script picks a random amount of starkverse mint transactions for each account in the range of (min, max)

*dmail* - int values for min and max. Script picks a random amount of dmail transactions for each account in the range of (min, max)

*starknet_id* - int values for min and max. Script picks a random amount of starknet id mint transactions for each account in the range of (min, max)

*zklend_collateral* - int values for min and max. Script picks a random amount of zklend enable/disable collateral transactions for each account in the range of (min, max)

*total_transactions* - int values for min and max. Script picks a random amount of total transactions for each account in the range of (min, max).

*eth_transaction_amount* - Decimal values for min and max (in ether). Script picks a random amount of eth to use for swap or lending for each transaction in the range of (min, max)

*eth_top_up_amount* - Decimal values for min and max (in ether). Script picks a random amount of eth to deposit to account from exchange for each account in the range of (min, max)

*sleep_between_transactions* - int values for min and max. Script picks a random amount of seconds to sleep between transactions in the range of (min, max)

*swap_or_lend_first* -  boolean value (true/false). If true is set, it will put all swap and lend transactions in the first half of the transactions. Necessary when account balance is low.

*second_top_up* - boolean value (true/false). If false is set, script won't top up values if it has at least 1 wei. If true is set it will top up account by **top_up_amount** - **eth_balance**

*max_gwei* - int value. Script waits for set starknet mainnet gwei.

*leave_eth* - Decimal values for min and max (in ether). Script picks a random amount of eth to leave for account in the range of (min, max). If the balance becomes lower than *leave_eth* value, left transactions will be skipped

## Usage

1. Add private keys to **data/private_keys.txt**. Each private key on a new line
2. Create **data/manager_context.json** file using the guide above
3. Run script
```bash
python main.py
```
4. After script is done two files will appear: **successful_accounts.txt** and **failed_accounts.txt**


## Account Strategy
This project was built to create cheap accounts only. It doesn't utilise volumes at all. 
The account strategy is the following: The script chooses account transactions order based on the router_context from manager_context.json.

First of all it chooses swap or lend transactions, afterwards dmail, then starknet id and finally zklend collateral. If the amount of transactions is lower than total_transactions, the script will randomly add dmail, starknet id or zklend collateral transactions.

Software is suitable for Argent X Cairo 1.0 accounts only.

Available dapps: Dmail, Starknet Id, Zklend, JediSwap, MySwap, SithSwap, 10kSwap, Starkverse

### If you have any questions contact me on telegram <a href="https://t.me/fleecybastard">@fleecybastard</a>
