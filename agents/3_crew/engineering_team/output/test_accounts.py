import unittest
from unittest.mock import patch
import datetime
# In a standard environment, we assume accounts.py is importable
import accounts 
from accounts import InsufficientFundsError, InsufficientSharesError 


class TestAccount(unittest.TestCase):
        
    def setUp(self):
        """Initialize a fresh account for each test."""
        self.account = accounts.Account(account_id="test_acc_123")
        
    # --- 1. Initialization and Basic State ---
    
    def test_initialization(self):
        self.assertEqual(self.account.account_id, "test_acc_123")
        self.assertEqual(self.account.balance, 0.0)
        self.assertEqual(self.account.get_holdings(), {})
        self.assertEqual(self.account.initial_deposit_total, 0.0)
        self.assertEqual(len(self.account.get_transaction_history()), 0)

    # --- 2. Deposit Functionality ---

    def test_deposit_success(self):
        self.account.deposit(1000.50)
        self.assertAlmostEqual(self.account.balance, 1000.50)
        self.assertAlmostEqual(self.account.initial_deposit_total, 1000.50)
        
        history = self.account.get_transaction_history()
        self.assertEqual(history[0]['type'], 'DEPOSIT')
        self.assertAlmostEqual(history[0]['amount'], 1000.50)
        
    def test_deposit_negative_value_raises_error(self):
        with self.assertRaisesRegex(ValueError, "Deposit amount must be positive"):
            self.account.deposit(-100)
        self.assertAlmostEqual(self.account.balance, 0.0)

    # --- 3. Withdrawal Functionality ---

    def test_withdraw_success(self):
        self.account.deposit(1000.00)
        self.account.withdraw(500.00)
        self.assertAlmostEqual(self.account.balance, 500.00)
        
        history = self.account.get_transaction_history()
        self.assertEqual(history[-1]['type'], 'WITHDRAW')
        self.assertAlmostEqual(history[-1]['amount'], -500.00)

    def test_withdraw_insufficient_funds(self):
        self.account.deposit(100.00)
        with self.assertRaises(InsufficientFundsError):
            self.account.withdraw(100.01)
        self.assertAlmostEqual(self.account.balance, 100.00)

    def test_withdraw_negative_value_raises_error(self):
        with self.assertRaisesRegex(ValueError, "Withdrawal amount must be positive"):
            self.account.withdraw(-10)

    # --- 4. Buy Shares Functionality ---
    
    def test_buy_shares_success(self):
        # Using AAPL static price: 170.50. Buy 5 shares = 852.50
        self.account.deposit(1000.00) 
        self.account.buy_shares('AAPL', 5)
        
        self.assertAlmostEqual(self.account.get_cash_balance(), 147.50)
        self.assertEqual(self.account.get_holdings(), {'AAPL': 5})
        
        tx = self.account.get_transaction_history()[-1]
        self.assertEqual(tx['type'], 'BUY')
        self.assertAlmostEqual(tx['price'], 170.50)

    @patch('accounts.get_share_price', return_value=100.00)
    def test_buy_shares_insufficient_funds(self, mock_get_price):
        # 10 shares @ 100.00 cost 1000.00
        self.account.deposit(999.00) 
        with self.assertRaises(InsufficientFundsError):
            self.account.buy_shares('TSLA', 10)
        
        self.assertAlmostEqual(self.account.get_cash_balance(), 999.00)

    def test_buy_shares_negative_quantity_raises_error(self):
        self.account.deposit(1000)
        with self.assertRaisesRegex(ValueError, "Quantity must be positive"):
            self.account.buy_shares('TSLA', -1)

    # --- 5. Sell Shares Functionality ---
    
    def test_sell_shares_success(self):
        # Using GOOGL static price: 2500.25. Buy 2 shares = 5000.50
        self.account.deposit(10000.00)
        self.account.buy_shares('GOOGL', 2)
        cash_after_buy = 10000.00 - 5000.50
        
        # Sell 1 share @ 2500.25
        self.account.sell_shares('GOOGL', 1) 
        proceeds = 2500.25
        
        self.assertAlmostEqual(self.account.get_cash_balance(), cash_after_buy + proceeds) 
        self.assertEqual(self.account.get_holdings(), {'GOOGL': 1})
        
        # Sell remaining share, verifies holding cleanup
        self.account.sell_shares('GOOGL', 1)
        self.assertEqual(self.account.get_holdings(), {})

    def test_sell_shares_insufficient_shares(self):
        self.account.deposit(1000)
        self.account.buy_shares('TSLA', 5) # Uses default price 100.00
        
        with self.assertRaises(InsufficientSharesError):
            self.account.sell_shares('TSLA', 6)
        
        self.assertEqual(self.account.get_holdings(), {'TSLA': 5})

    # --- 6. Reporting - Portfolio Value ---

    def test_calculate_portfolio_value(self):
        # Use AAPL (170.50) and GOOGL (2500.25)
        self.account.balance = 500.00
        self.account.holdings = {'AAPL': 2, 'GOOGL': 1}
        
        expected_stock_value = (2 * 170.50) + (1 * 2500.25) # 2841.25
        expected_total_value = 500.00 + expected_stock_value # 3341.25
        
        report = self.account.calculate_portfolio_value()
        
        self.assertAlmostEqual(report['cash_value'], 500.00)
        self.assertAlmostEqual(report['stock_value'], expected_stock_value)
        self.assertAlmostEqual(report['total_value'], expected_total_value)

    # --- 7. Reporting - Profit and Loss ---

    def test_calculate_profit_loss(self):
        
        # 7a. Zero P&L scenario (Market price = acquisition price)
        self.account.deposit(1000.00) 
        self.account.buy_shares('AAPL', 5) # Cost 852.50. Cash 147.50, Initial Deposit 1000.00

        pl_report_initial = self.account.calculate_profit_loss()
        self.assertAlmostEqual(pl_report_initial['profit_loss_amount'], 0.0)

        # 7b. Positive P&L (Mock price rises to 200.0)
        # Using __main__ patch target is safer for tests relying on price variance in the same execution context
        # In a real environment, if `accounts` is a module, this path is correct:
        with patch('accounts.get_share_price', return_value=200.0):
            pl_report_up = self.account.calculate_profit_loss()
            # Expected P/L amount: 1147.50 - 1000.00 = 147.50
            self.assertAlmostEqual(pl_report_up['profit_loss_amount'], 147.50)
            self.assertAlmostEqual(pl_report_up['profit_loss_percent'], 14.75)

        # 7c. P&L with Zero Deposit (Should show 0% P/L)
        no_deposit_acc = accounts.Account(account_id="nodep")
        no_deposit_acc.balance = 500 
        pl_zero_deposit = no_deposit_acc.calculate_profit_loss()
        self.assertAlmostEqual(pl_zero_deposit['profit_loss_amount'], 500.0)
        self.assertAlmostEqual(pl_zero_deposit['profit_loss_percent'], 0.0) 

    # --- 8. Transaction History Verification ---

    def test_transaction_history_contents(self):
        self.account.deposit(3000) 
        self.account.withdraw(500) 
        # Buy 10 AAPL @ 170.50. Cost 1705.00
        self.account.buy_shares('AAPL', 10) 
        
        history = self.account.get_transaction_history()
        self.assertEqual(len(history), 3)
        
        # Verify deposit
        self.assertEqual(history[0]['type'], 'DEPOSIT')
        
        # Verify buy trade details
        self.assertEqual(history[2]['type'], 'BUY')
        self.assertAlmostEqual(history[2]['amount'], -1705.00)
        self.assertEqual(history[2]['symbol'], 'AAPL')
        self.assertEqual(history[2]['quantity'], 10)

if __name__ == '__main__':
    unittest.main()