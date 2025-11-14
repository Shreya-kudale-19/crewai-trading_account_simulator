This is the detailed design for the `accounts.py` module, covering all requirements for the trading simulation account management system.

# Detailed Design: Account Management System (`accounts.py`)

The system will be implemented in a single Python module named `accounts.py`. It will include a mock external pricing function, necessary data structures, and the core `Account` class encapsulating all business logic and state.

## 1. External Dependencies and Helper Functions

### 1.1 `InsufficientFundsError`

A custom exception to handle cases where an action (withdrawal or purchase) cannot be completed due to insufficient cash balance.

```python
class InsufficientFundsError(Exception):
    """Raised when an operation requires more cash than available."""
    pass
```

### 1.2 `InsufficientSharesError`

A custom exception to handle cases where a user attempts to sell shares they do not possess.

```python
class InsufficientSharesError(Exception):
    """Raised when a sell operation requires more shares than available."""
    pass
```

### 1.3 Pricing Function Mock

This function simulates the external market data service.

| Function Signature | Description |
| :--- | :--- |
| `get_share_price(symbol: str) -> float` | Returns the current market price for a given stock symbol. Includes a test implementation with fixed prices for specific symbols. |

**Test Implementation Details:**

| Symbol | Price |
| :--- | :--- |
| `AAPL` | 170.50 |
| `TSLA` | 750.00 |
| `GOOGL` | 2500.25 |
| *Other* | 100.00 |

## 2. Core Class: `Account`

The `Account` class manages all state (balance, holdings, history) and operations for a single trading account.

### 2.1 Class Attributes (Internal State)

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `account_id` | `str` | Unique identifier for the account. |
| `balance` | `float` | Current available cash balance. |
| `holdings` | `dict[str, int]` | A mapping of stock symbol (str) to owned quantity (int). |
| `transactions` | `list[dict]` | Ordered history of all financial and trading activities. |
| `initial_deposit_total` | `float` | Sum of all deposit amounts, used as the baseline for P&L calculation. |

**Transaction Record Structure:**

Each item in the `transactions` list will be a dictionary with the following keys:

| Key | Type | Description |
| :--- | :--- | :--- |
| `timestamp` | `datetime` | Time of the transaction. |
| `type` | `str` | 'DEPOSIT', 'WITHDRAW', 'BUY', or 'SELL'. |
| `symbol` | `str or None` | Stock symbol (N/A for cash transactions). |
| `quantity` | `int or None` | Number of shares (N/A for cash transactions). |
| `price` | `float or None` | Price per share at transaction time (N/A for cash transactions). |
| `amount` | `float` | Total monetary value of the transaction (e.g., total cost, withdrawal amount). |

### 2.2 Methods and Signatures

#### A. Initialization and Core Cash Operations

| Method Signature | Description |
| :--- | :--- |
| `__init__(self, account_id: str)` | Constructor. Initializes account state: `balance=0.0`, `holdings={} ` , `transactions=[]`, `initial_deposit_total=0.0`. |
| `deposit(self, amount: float)` | Adds `amount` to `balance`. Updates `initial_deposit_total` and records a 'DEPOSIT' transaction. |
| `withdraw(self, amount: float)` | Subtracts `amount` from `balance`. Raises `InsufficientFundsError` if `balance - amount < 0`. Records a 'WITHDRAW' transaction. |

#### B. Trading Operations

These methods rely on `get_share_price(symbol)` to determine trade costs. They enforce constraints related to cash and inventory.

| Method Signature | Description |
| :--- | :--- |
| `buy_shares(self, symbol: str, quantity: int)` | Executes a purchase. Fetches current price. Calculates total cost (`price * quantity`). If cost > `balance`, raises `InsufficientFundsError`. Otherwise, deducts cost from `balance`, updates `holdings`, and records a 'BUY' transaction. |
| `sell_shares(self, symbol: str, quantity: int)` | Executes a sale. Checks if `holdings[symbol] >= quantity`. If not, raises `InsufficientSharesError`. Otherwise, fetches current price, calculates proceeds, adds proceeds to `balance`, updates `holdings`, and records a 'SELL' transaction. |

#### C. Reporting and Analysis

These methods provide insights into the current state of the portfolio.

| Method Signature | Description |
| :--- | :--- |
| `get_cash_balance(self) -> float` | Returns the current cash balance. |
| `get_holdings(self) -> dict[str, int]` | Returns a dictionary mapping stock symbols to current quantities. |
| `get_transaction_history(self) -> list[dict]` | Returns the full list of chronological transactions. |
| `calculate_portfolio_value(self) -> dict` | Calculates the total real-time value of the portfolio. Uses `get_share_price()` for current stock valuations. Returns a dictionary with keys: `cash_value`, `stock_value`, and `total_value`. |
| `calculate_profit_loss(self) -> dict` | Calculates the overall performance metrics. Uses `calculate_portfolio_value()` to get the current total value. Returns a dictionary with keys: `initial_deposit`, `current_total_value`, `profit_loss_amount`, and `profit_loss_percent`. |

---
## 3. Module Structure (`accounts.py`)

```python
import datetime
from typing import Dict, List, Any

# --- 1. Exceptions ---

class InsufficientFundsError(Exception):
    """Raised when an operation requires more cash than available."""
    pass

class InsufficientSharesError(Exception):
    """Raised when a sell operation requires more shares than available."""
    pass

# --- 2. External Dependency Mock ---

def get_share_price(symbol: str) -> float:
    """
    Mocks an external function to retrieve the current market price of a share.
    """
    if symbol == 'AAPL':
        return 170.50
    elif symbol == 'TSLA':
        return 750.00
    elif symbol == 'GOOGL':
        return 2500.25
    else:
        # Default price for unknown symbols
        return 100.00

# --- 3. Core Class: Account ---

class Account:
    
    def __init__(self, account_id: str):
        self.account_id: str = account_id
        self.balance: float = 0.0
        self.holdings: Dict[str, int] = {}
        self.transactions: List[Dict[str, Any]] = []
        self.initial_deposit_total: float = 0.0

    def _record_transaction(self, type: str, amount: float, symbol: str = None, quantity: int = None, price: float = None):
        """Internal helper to record transactions."""
        self.transactions.append({
            'timestamp': datetime.datetime.now(),
            'type': type,
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'amount': amount
        })

    # --- A. Initialization and Core Cash Operations ---

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        
        self.balance += amount
        self.initial_deposit_total += amount
        self._record_transaction('DEPOSIT', amount=amount)

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if self.balance < amount:
            raise InsufficientFundsError(f"Cannot withdraw {amount:.2f}. Available balance: {self.balance:.2f}")
        
        self.balance -= amount
        self._record_transaction('WITHDRAW', amount=-amount) # Record as negative amount

    # --- B. Trading Operations ---

    def buy_shares(self, symbol: str, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        
        price = get_share_price(symbol)
        cost = price * quantity

        if self.balance < cost:
            raise InsufficientFundsError(
                f"Cannot afford {quantity} shares of {symbol} at {price:.2f}. Total cost: {cost:.2f}. Available cash: {self.balance:.2f}"
            )
        
        self.balance -= cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        self._record_transaction('BUY', amount=-cost, symbol=symbol, quantity=quantity, price=price)

    def sell_shares(self, symbol: str, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
            
        current_holding = self.holdings.get(symbol, 0)
        
        if current_holding < quantity:
            raise InsufficientSharesError(
                f"Cannot sell {quantity} shares of {symbol}. Only {current_holding} shares are held."
            )
        
        price = get_share_price(symbol)
        proceeds = price * quantity

        self.balance += proceeds
        self.holdings[symbol] -= quantity
        
        # Cleanup zero holdings
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
            
        self._record_transaction('SELL', amount=proceeds, symbol=symbol, quantity=quantity, price=price)

    # --- C. Reporting and Analysis ---

    def get_cash_balance(self) -> float:
        return self.balance

    def get_holdings(self) -> Dict[str, int]:
        return {s: q for s, q in self.holdings.items() if q > 0}

    def get_transaction_history(self) -> List[Dict[str, Any]]:
        return self.transactions

    def calculate_portfolio_value(self) -> Dict[str, float]:
        stock_value = 0.0
        
        for symbol, quantity in self.holdings.items():
            if quantity > 0:
                price = get_share_price(symbol)
                stock_value += price * quantity
                
        total_value = self.balance + stock_value
        
        return {
            'cash_value': self.balance,
            'stock_value': stock_value,
            'total_value': total_value
        }

    def calculate_profit_loss(self) -> Dict[str, float]:
        portfolio_value = self.calculate_portfolio_value()
        current_total_value = portfolio_value['total_value']
        
        pl_amount = current_total_value - self.initial_deposit_total
        
        pl_percent = 0.0
        if self.initial_deposit_total > 0:
            pl_percent = (pl_amount / self.initial_deposit_total) * 100
            
        return {
            'initial_deposit': self.initial_deposit_total,
            'current_total_value': current_total_value,
            'profit_loss_amount': pl_amount,
            'profit_loss_percent': pl_percent
        }

```