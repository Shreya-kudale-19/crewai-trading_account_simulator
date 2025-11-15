This detailed design outlines the structure, functions, and methods for the `accounts.py` module, which implements the core logic for the trading simulation account management system.

## Design for `accounts.py` Module

The module will contain a mock external pricing function, necessary custom exceptions, and the main `Account` class.

### 1. External Data Mock Function

This function simulates fetching real-time share prices, as required by the system specification.

| Function | Signature | Description |
| :--- | :--- | :--- |
| `get_share_price` | `def get_share_price(symbol: str) -> float:` | Returns the current market price for a given stock symbol. Includes a hardcoded dictionary for testing fixed prices for AAPL, TSLA, and GOOGL. Raises a `ValueError` if the symbol is not recognized. |

### 2. Custom Exceptions

To ensure clear error handling when constraints are violated, a specific exception class is defined.

| Class | Description |
| :--- | :--- |
| `TradingError` | A base exception class for failures specific to account operations (e.g., insufficient funds, insufficient shares). |

### 3. The `Account` Class

The central class managing all account state, transactions, and calculations.

#### Internal Attributes

The following protected attributes will store the state of the account:

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `_account_holder_name` | `str` | Name associated with the account. |
| `_balance` | `float` | Current available cash balance. |
| `_holdings` | `Dict[str, int]` | Dictionary storing share holdings: `{symbol: quantity}`. |
| `_transactions` | `List[Dict]` | Ordered list of all historical transactions (deposits, withdrawals, trades). |
| `_initial_deposit` | `float` | The total value initially deposited used as the baseline for P&L calculation. |

#### Methods

##### A. Constructor and Basic Accessors

| Method | Signature | Description |
| :--- | :--- | :--- |
| `__init__` | `def __init__(self, account_holder_name: str, initial_deposit: float = 0.0):` | Initializes the account state. Sets name, initial deposit, and ensures balance, holdings, and transactions are empty/zeroed. |
| `get_balance` | `def get_balance(self) -> float:` | Returns the current cash balance. |
| `get_holdings` | `def get_holdings(self) -> Dict[str, int]:` | Returns a copy of the current share holdings (symbol to quantity mapping). |
| `get_transaction_history` | `def get_transaction_history(self) -> List[Dict]:` | Returns the complete list of transactions recorded chronologically. |

##### B. Funds Management Operations

These methods modify the cash balance and record transactions.

| Method | Signature | Description |
| :--- | :--- | :--- |
| `deposit` | `def deposit(self, amount: float) -> None:` | Adds `amount` to the account balance. Must ensure `amount` is positive. Records a DEPOSIT transaction. |
| `withdraw` | `def withdraw(self, amount: float) -> None:` | Subtracts `amount` from the account balance. Raises `TradingError` if the withdrawal would result in a negative balance. Records a WITHDRAWAL transaction. |

##### C. Trading Operations

These methods handle buying and selling shares, enforcing trading constraints, and updating holdings and balance. They rely on the external `get_share_price` function.

| Method | Signature | Description |
| :--- | :--- | :--- |
| `buy_shares` | `def buy_shares(self, symbol: str, quantity: int) -> None:` | Executes a share purchase. Calculates total cost using the current market price. Raises `TradingError` if the account balance is insufficient for the purchase. Updates holdings and subtracts cost from the balance. Records a BUY transaction, including the price paid. |
| `sell_shares` | `def sell_shares(self, symbol: str, quantity: int) -> None:` | Executes a share sale. Calculates total proceeds using the current market price. Raises `TradingError` if the user does not own the required `quantity` of `symbol`. Updates holdings and adds proceeds to the balance. Records a SELL transaction, including the price received. |

##### D. Reporting and Valuation

These methods calculate current portfolio metrics based on state and current market prices.

| Method | Signature | Description |
| :--- | :--- | :--- |
| `calculate_current_holdings_value` | `def calculate_current_holdings_value(self) -> float:` | Calculates the total market value of all held shares by iterating over holdings and calling `get_share_price` for each symbol. |
| `calculate_portfolio_value` | `def calculate_portfolio_value(self) -> float:` | Calculates the total portfolio value: `Current Cash Balance + Current Holdings Value`. |
| `calculate_profit_loss` | `def calculate_profit_loss(self) -> float:` | Calculates the profit or loss realized since account creation: `Total Portfolio Value - Initial Deposit`. |

---
## Transaction Record Structure

All transactions stored in the `_transactions` list will be dictionaries conforming to this minimum structure:

```python
{
    'timestamp': datetime.datetime, 
    'type': str,  # e.g., 'DEPOSIT', 'WITHDRAWAL', 'BUY', 'SELL'
    'cash_impact': float, # The monetary amount added (+) or subtracted (-)
    'balance_after': float, # The cash balance immediately after the transaction
    'symbol': str | None, 
    'quantity': int | None,
    'price_per_share': float | None # Price at which the trade executed
}
```<ctrl63>