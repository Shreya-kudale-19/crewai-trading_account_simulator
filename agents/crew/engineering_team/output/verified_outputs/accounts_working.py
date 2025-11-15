
from datetime import datetime
from typing import Dict, List, Any

# Mock stock prices
STOCK_PRICES = {
    "AAPL": 150.00,
    "TSLA": 850.00,
    "GOOGL": 2500.00
}

class TradingError(Exception):
    """Custom exception for trading-related errors."""
    pass

def get_share_price(symbol: str) -> float:
    """Returns the current share price for a given symbol."""
    symbol = symbol.upper()
    if symbol not in STOCK_PRICES:
        raise ValueError(f"Symbol {symbol} not found in available stocks.")
    return STOCK_PRICES[symbol]

class Account:
    """Represents a trading account with buy/sell functionality."""
    
    def __init__(self, account_holder_name: str, initial_deposit: float):
        self.account_holder_name = account_holder_name
        self.cash_balance = initial_deposit
        self.initial_deposit = initial_deposit
        self.holdings: Dict[str, int] = {}  # {symbol: quantity}
        self.transaction_history: List[Dict[str, Any]] = []
    
    def deposit(self, amount: float):
        """Deposit cash into the account."""
        if amount <= 0:
            raise TradingError("Deposit amount must be positive.")
        self.cash_balance += amount
        self.transaction_history.append({
            "timestamp": datetime.now(),
            "type": "Deposit",
            "symbol": "CASH",
            "quantity": 1,
            "price_per_share": amount,
            "cash_impact": amount,
            "balance_after": self.cash_balance
        })
    
    def withdraw(self, amount: float):
        """Withdraw cash from the account."""
        if amount <= 0:
            raise TradingError("Withdrawal amount must be positive.")
        if amount > self.cash_balance:
            raise TradingError(f"Insufficient funds. Available: ${self.cash_balance:.2f}")
        self.cash_balance -= amount
        self.transaction_history.append({
            "timestamp": datetime.now(),
            "type": "Withdrawal",
            "symbol": "CASH",
            "quantity": 1,
            "price_per_share": amount,
            "cash_impact": -amount,
            "balance_after": self.cash_balance
        })
    
    def buy_shares(self, symbol: str, quantity: int):
        """Buy shares of a given symbol."""
        symbol = symbol.upper()
        if quantity <= 0:
            raise TradingError("Quantity must be positive.")
        
        price = get_share_price(symbol)
        cost = price * quantity
        
        if cost > self.cash_balance:
            raise TradingError(f"Insufficient funds. Need: ${cost:.2f}, Available: ${self.cash_balance:.2f}")
        
        self.cash_balance -= cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        
        self.transaction_history.append({
            "timestamp": datetime.now(),
            "type": "Buy",
            "symbol": symbol,
            "quantity": quantity,
            "price_per_share": price,
            "cash_impact": -cost,
            "balance_after": self.cash_balance
        })
    
    def sell_shares(self, symbol: str, quantity: int):
        """Sell shares of a given symbol."""
        symbol = symbol.upper()
        if quantity <= 0:
            raise TradingError("Quantity must be positive.")
        
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            available = self.holdings.get(symbol, 0)
            raise TradingError(f"Insufficient shares of {symbol}. Available: {available}")
        
        price = get_share_price(symbol)
        proceeds = price * quantity
        
        self.cash_balance += proceeds
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        
        self.transaction_history.append({
            "timestamp": datetime.now(),
            "type": "Sell",
            "symbol": symbol,
            "quantity": quantity,
            "price_per_share": price,
            "cash_impact": proceeds,
            "balance_after": self.cash_balance
        })
    
    def get_balance(self) -> float:
        """Returns current cash balance."""
        return self.cash_balance
    
    def get_holdings(self) -> Dict[str, int]:
        """Returns current holdings."""
        return self.holdings.copy()
    
    def calculate_current_holdings_value(self) -> float:
        """Calculates the current market value of all holdings."""
        total_value = 0
        for symbol, quantity in self.holdings.items():
            price = get_share_price(symbol)
            total_value += price * quantity
        return total_value
    
    def calculate_portfolio_value(self) -> float:
        """Calculates total portfolio value (cash + holdings)."""
        return self.cash_balance + self.calculate_current_holdings_value()
    
    def calculate_profit_loss(self) -> float:
        """Calculates P&L compared to initial deposit."""
        return self.calculate_portfolio_value() - self.initial_deposit
    
    def get_transaction_history(self) -> List[Dict[str, Any]]:
        """Returns the transaction history."""
        return self.transaction_history.copy()