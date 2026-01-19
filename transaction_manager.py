"""
Transaction Manager - Handles financial data storage and retrieval

This module manages:
- Transaction recording (income, expenses)
- Data persistence (CSV-based storage)
- Category management
- Transaction queries and filters
"""

import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


class TransactionManager:
    """
    Manages financial transactions with CSV-based persistence.
    """
    
    def __init__(self, data_file: str = "transactions.csv"):
        """
        Initialize the transaction manager.
        
        Args:
            data_file: Path to the CSV file for storing transactions
        """
        self.data_file = data_file
        self.transactions = self._load_transactions()
        
        # Default categories
        self.income_categories = [
            "Salary", "Freelance", "Investment", "Gift", "Refund", "Other Income"
        ]
        
        self.expense_categories = [
            "Housing", "Transportation", "Food", "Utilities", "Healthcare",
            "Entertainment", "Shopping", "Education", "Travel", "Savings",
            "Debt Payment", "Insurance", "Investment Purchase", "Other Expense"
        ]
        
        # Investment tracking file
        self.investment_file = "investments.csv"
        self.investments = self._load_investments()
    
    def _load_transactions(self) -> pd.DataFrame:
        """Load transactions from CSV file or create new DataFrame."""
        if os.path.exists(self.data_file):
            try:
                df = pd.read_csv(self.data_file)
                # Parse dates flexibly - handles both "2026-01-17" and "2026-01-17 00:00:00"
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                # Drop rows with invalid dates
                if df['date'].isna().any():
                    print(f"Warning: Found {df['date'].isna().sum()} transactions with invalid dates, removing them")
                    df = df.dropna(subset=['date'])
                return df
            except Exception as e:
                print(f"Error loading transactions: {e}")
                # Return empty DataFrame on error
                return pd.DataFrame(columns=[
                    'id', 'date', 'type', 'category', 'amount',
                    'description', 'payment_method'
                ])
        else:
            # Create empty DataFrame with schema
            return pd.DataFrame(columns=[
                'id', 'date', 'type', 'category', 'amount',
                'description', 'payment_method'
            ])
    
    def _load_investments(self) -> pd.DataFrame:
        """Load investments from CSV file or create new DataFrame."""
        if os.path.exists(self.investment_file):
            try:
                df = pd.read_csv(self.investment_file)
                # Parse dates flexibly - handles both "2026-01-17" and "2026-01-17 00:00:00"
                df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
                # Drop rows with invalid dates
                if df['purchase_date'].isna().any():
                    print(f"Warning: Found {df['purchase_date'].isna().sum()} investments with invalid dates, removing them")
                    df = df.dropna(subset=['purchase_date'])
                return df
            except Exception as e:
                print(f"Error loading investments: {e}")
                # Return empty DataFrame on error
                return pd.DataFrame(columns=[
                    'id', 'symbol', 'quantity', 'purchase_price',
                    'purchase_date', 'total_cost'
                ])
        else:
            # Create empty DataFrame with schema
            return pd.DataFrame(columns=[
                'id', 'symbol', 'quantity', 'purchase_price',
                'purchase_date', 'total_cost'
            ])
    
    def _save_investments(self):
        """Save investments to CSV file."""
        # Ensure date column is properly formatted with timestamp
        df = self.investments.copy()
        df['purchase_date'] = pd.to_datetime(df['purchase_date']).dt.strftime('%Y-%m-%d %H:%M:%S')
        df.to_csv(self.investment_file, index=False)
    
    def _save_transactions(self):
        """Save transactions to CSV file."""
        # Ensure date column is properly formatted with timestamp
        df = self.transactions.copy()
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')
        df.to_csv(self.data_file, index=False)
    
    def add_transaction(
        self,
        transaction_type: str,
        category: str,
        amount: float,
        description: str = "",
        date: Optional[str] = None,
        payment_method: str = "Cash"
    ) -> str:
        """
        Add a new transaction.
        
        Args:
            transaction_type: "income" or "expense"
            category: Transaction category
            amount: Amount (positive number)
            description: Optional description
            date: Date in YYYY-MM-DD format (defaults to today)
            payment_method: How it was paid (Cash, Credit Card, Debit Card, etc.)
            
        Returns:
            Success message with transaction details
        """
        try:
            # Validate inputs
            transaction_type = transaction_type.lower()
            if transaction_type not in ['income', 'expense']:
                return "Error: Transaction type must be 'income' or 'expense'"
            
            amount = abs(float(amount))  # Ensure positive
            
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            else:
                # Validate date format
                datetime.strptime(date, '%Y-%m-%d')
            
            # Convert date to pandas datetime for consistency with loaded data
            date_dt = pd.to_datetime(date)
            
            # Generate ID
            transaction_id = len(self.transactions) + 1
            
            # Create transaction
            new_transaction = {
                'id': transaction_id,
                'date': date_dt,  # Use datetime object
                'type': transaction_type,
                'category': category,
                'amount': amount,
                'description': description,
                'payment_method': payment_method
            }
            
            # Add to DataFrame
            self.transactions = pd.concat([
                self.transactions,
                pd.DataFrame([new_transaction])
            ], ignore_index=True)
            
            # Save to file
            self._save_transactions()
            
            return (f"✓ Transaction added successfully!\n"
                   f"ID: {transaction_id}\n"
                   f"Type: {transaction_type.title()}\n"
                   f"Category: {category}\n"
                   f"Amount: ${amount:,.2f}\n"
                   f"Date: {date}")
        
        except ValueError as e:
            return f"Error: Invalid input - {str(e)}"
        except Exception as e:
            return f"Error adding transaction: {str(e)}"
    
    def get_transactions(
        self,
        transaction_type: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 10
    ) -> pd.DataFrame:
        """
        Get transactions with optional filters.
        
        Args:
            transaction_type: Filter by "income" or "expense"
            category: Filter by category
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of transactions to return
            
        Returns:
            Filtered DataFrame of transactions
        """
        df = self.transactions.copy()
        
        if len(df) == 0:
            return df
        
        # Apply filters
        if transaction_type:
            df = df[df['type'] == transaction_type.lower()]
        
        if category:
            df = df[df['category'] == category]
        
        if start_date:
            start = pd.to_datetime(start_date)
            df = df[df['date'] >= start]
        
        if end_date:
            end = pd.to_datetime(end_date)
            df = df[df['date'] <= end]
        
        # Sort by date (most recent first) and limit
        df = df.sort_values('date', ascending=False).head(limit)
        
        return df
    
    def get_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get financial summary for a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with summary statistics
        """
        df = self.get_transactions(start_date=start_date, end_date=end_date, limit=999999)
        
        if len(df) == 0:
            return {
                "total_income": 0,
                "total_expenses": 0,
                "net": 0,
                "transaction_count": 0
            }
        
        income = df[df['type'] == 'income']['amount'].sum()
        expenses = df[df['type'] == 'expense']['amount'].sum()
        
        return {
            "total_income": income,
            "total_expenses": expenses,
            "net": income - expenses,
            "transaction_count": len(df),
            "income_count": len(df[df['type'] == 'income']),
            "expense_count": len(df[df['type'] == 'expense'])
        }
    
    def get_spending_by_category(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get spending breakdown by category.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with category totals
        """
        df = self.get_transactions(
            transaction_type='expense',
            start_date=start_date,
            end_date=end_date,
            limit=999999
        )
        
        if len(df) == 0:
            return pd.DataFrame(columns=['category', 'total', 'count', 'percentage'])
        
        category_totals = df.groupby('category').agg({
            'amount': ['sum', 'count']
        }).reset_index()
        
        category_totals.columns = ['category', 'total', 'count']
        total_expenses = category_totals['total'].sum()
        category_totals['percentage'] = (category_totals['total'] / total_expenses * 100).round(2)
        
        return category_totals.sort_values('total', ascending=False)
    
    def get_monthly_trend(self, months: int = 6) -> pd.DataFrame:
        """
        Get monthly income and expense trends.
        
        Args:
            months: Number of months to include
            
        Returns:
            DataFrame with monthly totals
        """
        if len(self.transactions) == 0:
            return pd.DataFrame(columns=['month', 'income', 'expenses', 'net'])
        
        df = self.transactions.copy()
        df['month'] = df['date'].dt.to_period('M')
        
        monthly = df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
        
        if 'income' not in monthly.columns:
            monthly['income'] = 0
        if 'expense' not in monthly.columns:
            monthly['expense'] = 0
        
        monthly['net'] = monthly.get('income', 0) - monthly.get('expense', 0)
        monthly = monthly.reset_index()
        monthly['month'] = monthly['month'].astype(str)
        
        return monthly.tail(months)
    
    def delete_transaction(self, transaction_id: int) -> str:
        """
        Delete a transaction by ID.
        
        Args:
            transaction_id: ID of transaction to delete
            
        Returns:
            Success or error message
        """
        try:
            initial_count = len(self.transactions)
            self.transactions = self.transactions[self.transactions['id'] != transaction_id]
            
            if len(self.transactions) < initial_count:
                self._save_transactions()
                return f"✓ Transaction {transaction_id} deleted successfully"
            else:
                return f"Error: Transaction {transaction_id} not found"
        
        except Exception as e:
            return f"Error deleting transaction: {str(e)}"
    
    def get_categories(self, transaction_type: str = 'expense') -> List[str]:
        """Get available categories for a transaction type."""
        if transaction_type.lower() == 'income':
            return self.income_categories
        else:
            return self.expense_categories
    
    def add_investment(
        self,
        symbol: str,
        quantity: float,
        purchase_price: float,
        purchase_date: Optional[str] = None
    ) -> str:
        """
        Add a stock investment to the portfolio.
        
        Args:
            symbol: Stock ticker symbol (e.g., AAPL, GOOGL)
            quantity: Number of shares purchased
            purchase_price: Price per share at purchase
            purchase_date: Date of purchase (YYYY-MM-DD, defaults to today)
            
        Returns:
            Success message with investment details
        """
        try:
            if purchase_date is None:
                purchase_date = datetime.now().strftime('%Y-%m-%d')
            else:
                # Validate date
                datetime.strptime(purchase_date, '%Y-%m-%d')
            
            symbol = symbol.upper().strip()
            quantity = float(quantity)
            purchase_price = float(purchase_price)
            total_cost = quantity * purchase_price
            
            # Convert purchase_date to pandas datetime for consistency
            purchase_date_dt = pd.to_datetime(purchase_date)
            
            # Generate ID
            investment_id = len(self.investments) + 1
            
            # Create investment record
            new_investment = {
                'id': investment_id,
                'symbol': symbol,
                'quantity': quantity,
                'purchase_price': purchase_price,
                'purchase_date': purchase_date_dt,  # Use datetime object
                'total_cost': total_cost
            }
            
            # Add to DataFrame
            self.investments = pd.concat([
                self.investments,
                pd.DataFrame([new_investment])
            ], ignore_index=True)
            
            # Save to file
            self._save_investments()
            
            # Automatically add as an expense transaction to track cash flow
            # This ensures cash balance decreases when investments are made
            self.add_transaction(
                transaction_type='expense',
                category='Investment Purchase',
                amount=total_cost,
                description=f"Purchased {quantity} shares of {symbol} at ${purchase_price:.2f}",
                date=purchase_date
            )
            
            return (f"✓ Investment added successfully!\n"
                   f"Symbol: {symbol}\n"
                   f"Quantity: {quantity} shares\n"
                   f"Purchase Price: ${purchase_price:.2f} per share\n"
                   f"Total Cost: ${total_cost:,.2f}\n"
                   f"Date: {purchase_date}")
        
        except Exception as e:
            return f"Error adding investment: {str(e)}"
    
    def get_portfolio_value(self) -> Dict[str, Any]:
        """
        Get current portfolio value with live stock prices.
        
        Returns:
            Dictionary with portfolio details including current value and gains/losses
        """
        if len(self.investments) == 0:
            return {
                "total_invested": 0,
                "current_value": 0,
                "total_gain_loss": 0,
                "total_gain_loss_percent": 0,
                "holdings": []
            }
        
        import yfinance as yf
        
        total_invested = 0
        current_value = 0
        holdings = []
        
        # Group investments by symbol
        grouped = self.investments.groupby('symbol').agg({
            'quantity': 'sum',
            'total_cost': 'sum'
        }).reset_index()
        
        for _, row in grouped.iterrows():
            symbol = row['symbol']
            quantity = row['quantity']
            cost = row['total_cost']
            avg_purchase_price = cost / quantity
            
            # Get current price with timeout and error handling
            try:
                stock = yf.Ticker(symbol)
                # Set a short timeout for the info fetch
                info = stock.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                
                if not current_price or current_price == 0:
                    # Fallback to purchase price if API fails
                    print(f"Warning: Could not fetch current price for {symbol}, using purchase price")
                    current_price = avg_purchase_price
            except Exception as e:
                print(f"Warning: Error fetching {symbol} price: {e}, using purchase price")
                current_price = avg_purchase_price
            
            value = quantity * current_price
            gain_loss = value - cost
            gain_loss_percent = (gain_loss / cost * 100) if cost > 0 else 0
            
            holdings.append({
                'symbol': symbol,
                'quantity': quantity,
                'avg_purchase_price': avg_purchase_price,
                'current_price': current_price,
                'total_cost': cost,
                'current_value': value,
                'gain_loss': gain_loss,
                'gain_loss_percent': gain_loss_percent
            })
            
            total_invested += cost
            current_value += value
        
        total_gain_loss = current_value - total_invested
        total_gain_loss_percent = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0
        
        return {
            "total_invested": total_invested,
            "current_value": current_value,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_percent": total_gain_loss_percent,
            "holdings": holdings
        }
    
    def get_investments(self) -> pd.DataFrame:
        """Get all investments."""
        return self.investments.copy()
    
    def get_net_worth(self) -> Dict[str, Any]:
        """
        Calculate total net worth including cash and investments.
        
        Returns:
            Dictionary with net worth breakdown
        """
        # Get financial summary (cash flow)
        summary = self.get_summary()
        cash_balance = summary['net']  # Income - Expenses
        
        # Get portfolio value
        portfolio = self.get_portfolio_value()
        investment_value = portfolio['current_value']
        
        # Total net worth
        net_worth = cash_balance + investment_value
        
        return {
            "cash_balance": cash_balance,
            "investment_value": investment_value,
            "total_net_worth": net_worth,
            "portfolio_details": portfolio
        }
    
    def export_to_csv(self, filename: str) -> str:
        """
        Export transactions to a CSV file.
        
        Args:
            filename: Output filename
            
        Returns:
            Success message
        """
        try:
            self.transactions.to_csv(filename, index=False)
            return f"✓ Transactions exported to {filename}"
        except Exception as e:
            return f"Error exporting: {str(e)}"
