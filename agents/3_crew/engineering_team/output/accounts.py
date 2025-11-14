

*Correction based on calculation:*
Initial deposit: 10000.00
1. Buy AAPL (10 @ 170.50): Cash -= 1705.00
2. Buy GOOGL (1 @ 2500.25): Cash -= 2500.25
Cash after buys: 5794.75. Stock Value: 4205.25. Total Value: 10000.00. P&L: 0.00. (Correct)

3. Sell AAPL (5 @ 170.50): Cash += 852.50
New Cash: 5794.75 + 852.50 = 6647.25
4. Withdraw: Cash -= 500.00
Final Cash: 6147.25
Final Holdings: AAPL 5, GOOGL 1

Final Stock Value: (5 * 170.50) + (1 * 2500.25) = 852.50 + 2500.25 = 3352.75
Final Total Value: 6147.25 (Cash) + 3352.75 (Stock) = 9500.00.

The test output shows `Final Total Value: 9500.00` and `Expected Final Total Value: 9500.00`. Wait, let me re-check the expectation calculation I wrote in the thought block:
$6147.25 + 5 \times 170.50 + 1 \times 2500.25 = 6147.25 + 852.50 + 2500.25 = 9500.00$. My expectation comment in the test was slightly off, but the numerical result (9500.00) is correct.

The P&L calculation: Total Value (9500.00) - Initial Deposit (10000.00) = -500.00. This makes sense, as the account only made a deposit and then withdrew $500, with all trades closing at zero P&L (since prices were fixed). The P&L correctly reflects the withdrawal relative to the initial deposits.

All core requirements are met, and the implementation follows the detailed design precisely. I am now ready to provide the final raw Python code, stripping out the testing block used for verification.

Thought: I have successfully verified the functionality of the `Account` class implementation against the design requirements using the code interpreter. The logic for deposits, withdrawals, trading (buy/sell), holdings update, constraint enforcement, and P&L calculation is correct.

The final step is to output the complete, raw Python code for the `accounts.py` module, ensuring no markdown fences or external test calls are included, as required by the prompt. I will reconstruct the clean module file content.

Final structure for output:
1. Imports (`datetime`, `typing`).
2. Custom Exceptions.
3. `get_share_price` mock function.
4. `Account` class definition with all methods.import datetime
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
        self._record_transaction('WITHDRAW', amount=-amount)

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
        """Returns the current cash balance."""
        return self.balance

    def get_holdings(self) -> Dict[str, int]:
        """Returns a dictionary mapping stock symbols to current quantities."""
        return {s: q for s, q in self.holdings.items() if q > 0}

    def get_transaction_history(self) -> List[Dict[str, Any]]:
        """Returns the full list of chronological transactions."""
        return self.transactions

    def calculate_portfolio_value(self) -> Dict[str, float]:
        """Calculates the total real-time value of the portfolio."""
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
        """Calculates the overall performance metrics relative to initial deposits."""
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