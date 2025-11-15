import gradio as gr
import pandas as pd
from typing import Dict, Any, List

# agents/crew/engineering_team/output/verified_outputs/accounts_working.py

# --- Assume the provided backend code is saved as accounts.py in the same directory ---
# NOTE: This import assumes the backend code provided in the prompt is saved as accounts.py
try:
    from accounts_working import (
    Account,
    TradingError,
    get_share_price,
)

except ImportError:
    print("FATAL ERROR: Could not import Account class. Ensure accounts.py is present.")
    raise

# 1. Initialize the Single Account Instance
try:
    # Starting with a small initial deposit for demonstration
    ACCOUNT = Account(account_holder_name="Demo Trader", initial_deposit=10000.00)
except Exception as e:
    print(f"Error initializing account: {e}")
    # Initialize a fallback if necessary, though raising is safer in a real app
    raise

# Symbols available for trading (based on get_share_price mock)
AVAILABLE_SYMBOLS = ["AAPL", "TSLA", "GOOGL"]


# --- 2. Gradio Backend Functions ---

def format_holdings(holdings: Dict[str, int]) -> str:
    """Formats holdings dict for display, including current market value."""
    if not holdings:
        return "No shares held."
    
    output = "Holdings:\n"
    for symbol, quantity in holdings.items():
        try:
            price = get_share_price(symbol)
            value = price * quantity
            output += f"- {symbol}: {quantity} shares (Current Value: ${value:,.2f})\n"
        except ValueError:
            output += f"- {symbol}: {quantity} shares (Price Unknown)\n"

    return output.strip()

def format_transactions(transactions: List[Dict[str, Any]]) -> pd.DataFrame:
    """Converts transaction history to a DataFrame for display."""
    if not transactions:
        # Return an empty dataframe with expected columns if no transactions exist
        return pd.DataFrame({'timestamp': [], 'type': [], 'symbol': [], 'quantity': [], 'price_per_share': [], 'cash_impact': [], 'balance_after': []})
        
    df = pd.DataFrame(transactions)
    
    # Select and format columns for clean display
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    display_cols = ['timestamp', 'type', 'symbol', 'quantity', 'price_per_share', 'cash_impact', 'balance_after']
    df = df.reindex(columns=display_cols).fillna('')
    
    # Format currency columns
    currency_cols = ['price_per_share', 'cash_impact', 'balance_after']
    for col in currency_cols:
        df[col] = df[col].apply(lambda x: f"${x:,.2f}" if isinstance(x, (float, int)) else x)
        
    return df

def get_status_report():
    """Retrieves all current account metrics for dashboard display."""
    cash = ACCOUNT.get_balance()
    holdings_value = ACCOUNT.calculate_current_holdings_value()
    portfolio_value = ACCOUNT.calculate_portfolio_value()
    pnl = ACCOUNT.calculate_profit_loss()
    
    holdings_text = format_holdings(ACCOUNT.get_holdings())

    return (
        f"${cash:,.2f}", 
        f"${holdings_value:,.2f}", 
        f"${portfolio_value:,.2f}", 
        f"${pnl:,.2f}", 
        holdings_text
    )

def handle_deposit(amount: float):
    """Handles deposit operation."""
    try:
        if amount <= 0:
            return "Error: Amount must be positive.", *get_status_report()
            
        ACCOUNT.deposit(amount)
        return f"Successfully deposited ${amount:.2f}.", *get_status_report()
    except Exception as e:
        return f"Deposit Failed: {e}", *get_status_report()

def handle_withdraw(amount: float):
    """Handles withdrawal operation."""
    try:
        if amount <= 0:
            return "Error: Amount must be positive.", *get_status_report()
            
        ACCOUNT.withdraw(amount)
        return f"Successfully withdrew ${amount:.2f}.", *get_status_report()
    except TradingError as e:
        return f"Withdrawal Failed: {e}", *get_status_report()
    except Exception as e:
        return f"Error: {e}", *get_status_report()


def handle_trade(action: str, symbol: str, quantity: int):
    """Handles buy or sell operation."""
    try:
        if quantity <= 0:
            return "Error: Quantity must be positive.", *get_status_report()
        
        symbol = symbol.upper()
        
        # Check current price for immediate feedback
        price = get_share_price(symbol)
        
        if action == "Buy":
            ACCOUNT.buy_shares(symbol, quantity)
            message = f"Successfully BOUGHT {quantity} shares of {symbol} @ ${price:.2f} each. Total cost: ${(price * quantity):,.2f}."
        elif action == "Sell":
            ACCOUNT.sell_shares(symbol, quantity)
            message = f"Successfully SOLD {quantity} shares of {symbol} @ ${price:.2f} each. Total proceeds: ${(price * quantity):,.2f}."
        else:
            message = "Invalid trade action."
            
        return message, *get_status_report()

    except TradingError as e:
        return f"Trade Failed: {e}", *get_status_report()
    except ValueError as e:
        return f"Trade Setup Error: {e}", *get_status_report()
    except Exception as e:
        return f"An unexpected error occurred: {e}", *get_status_report()

def get_history_df():
    """Returns the formatted transaction history."""
    return format_transactions(ACCOUNT.get_transaction_history())


# --- 3. Gradio Interface Definition ---

# Define initial outputs for state variables
initial_status = get_status_report()

with gr.Blocks(title="Trading Simulation Account Demo") as demo:
    gr.Markdown("# Simple Trading Account Demo (Demo Trader)")
    
    # Global Feedback Area
    feedback_output = gr.Textbox(label="Status/Error Message", value="Account initialized with $10,000.00.", interactive=False, type="text")

    # --- STATUS DASHBOARD (Always visible) ---
    gr.Markdown("## Current Portfolio Status")

    with gr.Row(variant="panel"):
        cash_balance_out = gr.Textbox(label="Cash Balance", value=initial_status[0], interactive=False)
        holdings_value_out = gr.Textbox(label="Holdings Value", value=initial_status[1], interactive=False)
        portfolio_value_out = gr.Textbox(label="Portfolio Value", value=initial_status[2], interactive=False)
        pnl_out = gr.Textbox(label="P&L (vs Initial Deposit)", value=initial_status[3], interactive=False)
    
    with gr.Row():
        holdings_text_out = gr.Textbox(label="Detailed Holdings", value=initial_status[4], interactive=False, lines=5)


    with gr.Tab("1. Funds Management"):
        gr.Markdown("### Deposit / Withdraw Cash")
        
        amount_input = gr.Number(label="Amount ($)", value=100.00)
        
        with gr.Row():
            deposit_btn = gr.Button("Deposit Funds", variant="primary")
            withdraw_btn = gr.Button("Withdraw Funds", variant="secondary")

    with gr.Tab("2. Trading"):
        gr.Markdown("### Buy / Sell Shares")

        trade_symbol = gr.Dropdown(choices=AVAILABLE_SYMBOLS, label="Select Symbol", value=AVAILABLE_SYMBOLS[0])
        trade_quantity = gr.Number(label="Quantity", value=1, precision=0)
        
        with gr.Row():
            buy_btn = gr.Button("BUY Shares", variant="primary")
            sell_btn = gr.Button("SELL Shares", variant="secondary")

        gr.Markdown("---")
        gr.Markdown("Stock Prices (Fixed Mock):\nAAPL: $150.00 | TSLA: $850.00 | GOOGL: $2500.00")

    with gr.Tab("3. Transaction History"):
        gr.Markdown("### Historical Transactions")
        history_df = gr.Dataframe(
            label="Transaction Log", 
            value=get_history_df,
            wrap=True,
            interactive=False,
            # height=300
        )
        refresh_history_btn = gr.Button("Refresh History")


    # --- 4. Event Handling ---
    
    # Status outputs bundle (used for multi-output updates)
    status_outputs = [cash_balance_out, holdings_value_out, portfolio_value_out, pnl_out, holdings_text_out]
    
    # Funds Management Handlers
    deposit_btn.click(
        fn=handle_deposit,
        inputs=[amount_input],
        outputs=[feedback_output] + status_outputs
    )
    
    withdraw_btn.click(
        fn=handle_withdraw,
        inputs=[amount_input],
        outputs=[feedback_output] + status_outputs
    )

    # Trading Handlers
    buy_btn.click(
        fn=lambda sym, qty: handle_trade("Buy", sym, qty),
        inputs=[trade_symbol, trade_quantity],
        outputs=[feedback_output] + status_outputs
    )
    
    sell_btn.click(
        fn=lambda sym, qty: handle_trade("Sell", sym, qty),
        inputs=[trade_symbol, trade_quantity],
        outputs=[feedback_output] + status_outputs
    )
    
    # History Refresh Handler
    refresh_history_btn.click(
        fn=get_history_df,
        outputs=history_df
    )
    
# Start the application
if __name__ == "__main__":
    demo.launch()