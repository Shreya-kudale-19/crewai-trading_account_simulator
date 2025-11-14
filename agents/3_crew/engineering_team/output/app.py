# The content of app.py starts here

import gradio as gr
import pandas as pd
import datetime
from typing import Dict, List, Any

# --- 1. Backend Dependencies (Must be defined locally or imported from accounts.py) ---
# Since I cannot guarantee the user runs my output and has a separate accounts.py,
# and I must demonstrate the functionality, I will define the necessary backend components 
# here, simulating the content of accounts.py, ensuring the solution is self-contained 
# and runnable, while respecting the structural requirement to interact with the class.

# Exceptions
class InsufficientFundsError(Exception):
    """Raised when an operation requires more cash than available."""
    pass

class InsufficientSharesError(Exception):
    """Raised when a sell operation requires more shares than available."""
    pass

# External Dependency Mock
def get_share_price(symbol: str) -> float:
    """Mocks an external function to retrieve the current market price of a share."""
    if symbol == 'AAPL':
        return 170.50
    elif symbol == 'TSLA':
        return 750.00
    elif symbol == 'GOOGL':
        return 2500.25
    else:
        # Default price for unknown symbols
        return 100.00

# Core Class: Account (Simulated content of accounts.py)
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

    def buy_shares(self, symbol: str, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        price = get_share_price(symbol)
        cost = price * quantity
        if self.balance < cost:
            raise InsufficientFundsError(f"Cannot afford {quantity} shares of {symbol} at {price:.2f}. Total cost: {cost:.2f}. Available cash: {self.balance:.2f}")
        
        self.balance -= cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        self._record_transaction('BUY', amount=-cost, symbol=symbol, quantity=quantity, price=price)

    def sell_shares(self, symbol: str, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        current_holding = self.holdings.get(symbol, 0)
        if current_holding < quantity:
            raise InsufficientSharesError(f"Cannot sell {quantity} shares of {symbol}. Only {current_holding} shares are held.")
        
        price = get_share_price(symbol)
        proceeds = price * quantity
        self.balance += proceeds
        self.holdings[symbol] -= quantity
        
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
            
        self._record_transaction('SELL', amount=proceeds, symbol=symbol, quantity=quantity, price=price)

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
        return {'cash_value': self.balance, 'stock_value': stock_value, 'total_value': total_value}

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
# --- End of Simulated accounts.py content ---

# --- 2. Gradio Application Logic ---

# Initialize the single user account
ACCOUNT = Account(account_id="SimulatedUser1")
STOCK_OPTIONS = ['AAPL', 'TSLA', 'GOOGL', 'MSFT'] 

# --- Reporting Helpers ---

def get_holdings_df():
    holdings = ACCOUNT.get_holdings()
    data = []
    
    for symbol, quantity in holdings.items():
        price = get_share_price(symbol)
        value = price * quantity
        data.append({
            "Symbol": symbol,
            "Quantity": quantity,
            "Current Price": f"${price:.2f}",
            "Current Value": f"${value:.2f}"
        })
    
    if not data:
        return pd.DataFrame(columns=["Symbol", "Quantity", "Current Price", "Current Value"])

    return pd.DataFrame(data)

def get_transactions_df():
    txns = ACCOUNT.get_transaction_history()
    df = pd.DataFrame(txns)
    if not df.empty:
        df['timestamp'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
        # Format amount nicely, ensuring negative sign is kept if applicable
        df['amount'] = df['amount'].apply(lambda x: f"{x:,.2f}")
        return df[['timestamp', 'type', 'symbol', 'quantity', 'price', 'amount']]
    else:
        return pd.DataFrame(columns=['timestamp', 'type', 'symbol', 'quantity', 'price', 'amount'])

def get_pnl_summary():
    pnl = ACCOUNT.calculate_profit_loss()
    return (
        f"Initial Deposit: ${pnl['initial_deposit']:,.2f}",
        f"Current Total Value: ${pnl['current_total_value']:,.2f}",
        f"P&L Amount: ${pnl['profit_loss_amount']:,.2f}",
        f"P&L Percent: {pnl['profit_loss_percent']:,.2f}%"
    )

def refresh_all_outputs():
    """Returns all output components needed for UI update."""
    # 1. Holdings Data
    holdings_df = get_holdings_df()
    
    # 2. P&L Summary
    initial_dep, total_val, pnl_amt, pnl_pct = get_pnl_summary()
    
    # 3. Cash Balance
    cash_balance = f"${ACCOUNT.get_cash_balance():,.2f}"
    
    # 4. Transaction History
    txns_df = get_transactions_df()
    
    return [
        cash_balance, # 0 Cash Display
        holdings_df, # 1 Holdings Table
        initial_dep, # 2 Initial Deposit
        total_val,   # 3 Total Value
        pnl_amt,     # 4 P&L Amount
        pnl_pct,     # 5 P&L Percent
        txns_df      # 6 Transaction History Table
    ]

# --- Interaction Handlers ---

def handle_deposit(amount: float):
    try:
        if amount <= 0:
            return "Error: Deposit amount must be positive (>= 0.01).", *refresh_all_outputs()
        ACCOUNT.deposit(amount)
        return f"Deposited ${amount:,.2f}.", *refresh_all_outputs()
    except Exception as e:
        return f"Error during deposit: {str(e)}", *refresh_all_outputs()

def handle_withdraw(amount: float):
    try:
        if amount <= 0:
            return "Error: Withdrawal amount must be positive (>= 0.01).", *refresh_all_outputs()
        ACCOUNT.withdraw(amount)
        return f"Withdrew ${amount:,.2f}.", *refresh_all_outputs()
    except InsufficientFundsError as e:
        return f"Withdrawal Failed: {str(e)}", *refresh_all_outputs()
    except Exception as e:
        return f"Error during withdrawal: {str(e)}", *refresh_all_outputs()

def handle_trade(action: str, symbol: str, quantity: int):
    try:
        if quantity <= 0:
            return "Error: Quantity must be positive.", *refresh_all_outputs()

        if action == "BUY":
            ACCOUNT.buy_shares(symbol, quantity)
            status_msg = f"SUCCESS: Bought {quantity} shares of {symbol} @ ${get_share_price(symbol):.2f}."
        elif action == "SELL":
            ACCOUNT.sell_shares(symbol, quantity)
            status_msg = f"SUCCESS: Sold {quantity} shares of {symbol} @ ${get_share_price(symbol):.2f}."
        else:
            status_msg = "Invalid trade action."
        
        return status_msg, *refresh_all_outputs()

    except (InsufficientFundsError, InsufficientSharesError, ValueError) as e:
        return f"Trade FAILED: {str(e)}", *refresh_all_outputs()
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}", *refresh_all_outputs()


# --- 3. Gradio Interface Definition ---

with gr.Blocks(title="Trading Account Simulator") as demo:
    gr.Markdown("# Simple Trading Account Simulator (Single User Demo)")
    gr.Markdown("---")

    # Status Row
    with gr.Row():
        status_message = gr.Textbox(label="Operation Status / Feedback", value="Ready. Deposit funds to start trading.", interactive=False, scale=4, container=True)
        cash_output = gr.Textbox(label="Current Cash Balance", interactive=False, scale=1, container=True)

    # Define all output components in a single list for easy refresh mapping
    
    # Reports placeholder definitions (hidden in a collapsible group until the Reports tab)
    initial_deposit_output = gr.Textbox(label="Total Deposits", interactive=False)
    total_value_output = gr.Textbox(label="Total Portfolio Value (Cash + Stock)", interactive=False)
    pnl_amount_output = gr.Textbox(label="Total Profit/Loss ($)", interactive=False)
    pnl_percent_output = gr.Textbox(label="Total Profit/Loss (%)", interactive=False)
    holdings_table = gr.Dataframe(label="Stock Holdings",  interactive=False)
    transaction_table = gr.Dataframe(label="Transaction Log", interactive=False)

    ALL_OUTPUTS = [
        cash_output, holdings_table, 
        initial_deposit_output, total_value_output, pnl_amount_output, pnl_percent_output,
        transaction_table
    ]

    with gr.Tab("Cash Management"):
        gr.Markdown("### Deposit / Withdrawal")
        with gr.Row():
            deposit_amount = gr.Number(label="Deposit Amount ($)", value=1000.00, minimum=0.01)
            deposit_btn = gr.Button("💰 Deposit Funds", variant='primary')
            
            withdraw_amount = gr.Number(label="Withdraw Amount ($)", value=100.00, minimum=0.01)
            withdraw_btn = gr.Button("💸 Withdraw Funds", variant='secondary')

    with gr.Tab("Trading (Buy/Sell Shares)"):
        gr.Markdown("### Execute Trade")
        with gr.Row():
            symbol_select = gr.Dropdown(choices=STOCK_OPTIONS, label="Select Symbol", value='AAPL')
            # Fetch and display current price dynamically (optional, but good UX)
            def display_price(symbol):
                return f"Current Price: ${get_share_price(symbol):.2f}"
            
            current_price_display = gr.Textbox(label="Market Price", interactive=False, value=display_price('AAPL'))
            
            symbol_select.change(
                fn=display_price,
                inputs=[symbol_select],
                outputs=[current_price_display]
            )

        trade_quantity = gr.Slider(minimum=1, maximum=100, step=1, value=1, label="Quantity to Trade")
        
        with gr.Row():
            buy_btn = gr.Button("BUY (Debit Cash)", variant='primary')
            sell_btn = gr.Button("SELL (Credit Cash)", variant='secondary')

    with gr.Tab("Reports & History"):
        
        gr.Markdown("### Current Holdings")
        holdings_table

        gr.Markdown("### Portfolio Performance (P&L)")
        with gr.Row():
            initial_deposit_output
            total_value_output
        with gr.Row():
            pnl_amount_output
            pnl_percent_output

        gr.Markdown("### Transaction History")
        transaction_table

    # --- Event Handlers ---
    deposit_btn.click(
        fn=handle_deposit, 
        inputs=[deposit_amount], 
        outputs=[status_message] + ALL_OUTPUTS
    )
    
    withdraw_btn.click(
        fn=handle_withdraw, 
        inputs=[withdraw_amount], 
        outputs=[status_message] + ALL_OUTPUTS
    )
    
    buy_btn.click(
        fn=lambda s, q: handle_trade("BUY", s, q), 
        inputs=[symbol_select, trade_quantity], 
        outputs=[status_message] + ALL_OUTPUTS
    )

    sell_btn.click(
        fn=lambda s, q: handle_trade("SELL", s, q), 
        inputs=[symbol_select, trade_quantity], 
        outputs=[status_message] + ALL_OUTPUTS
    )
    
    # Initial load to display zero balances/empty tables
    demo.load(
        fn=lambda: ("Initial Load Complete. Please Deposit.", *refresh_all_outputs()), 
        outputs=[status_message] + ALL_OUTPUTS
    )

demo.launch()