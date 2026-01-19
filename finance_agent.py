"""
Personal Finance AI Agent using Claude

Full AI agent that understands natural language for finance tracking.
Compatible with langchain-core 1.2.7
"""

# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

import os
import yfinance as yf
import pandas as pd
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnablePassthrough
from transaction_manager import TransactionManager


# Initialize transaction manager
transaction_manager = TransactionManager()


@tool
def add_transaction(transaction_type: str, category: str, amount: float,
                   description: str = "", date: str = None, payment_method: str = "Cash") -> str:
    """
    Add a new income or expense transaction.
    
    Args:
        transaction_type: Either "income" or "expense"
        category: Category like Food, Housing, Salary, etc
        amount: Amount in dollars (positive number)
        description: Optional description
        date: Optional date in YYYY-MM-DD format (defaults to today)
        payment_method: How it was paid (Cash, Credit Card, etc)
    
    Returns:
        Success message with transaction details
    """
    return transaction_manager.add_transaction(
        transaction_type=transaction_type,
        category=category,
        amount=amount,
        description=description,
        date=date,
        payment_method=payment_method
    )


@tool
def view_transactions(transaction_type: str = None, category: str = None, limit: int = 10) -> str:
    """
    View recent transactions.
    
    Args:
        transaction_type: Filter by "income" or "expense" (optional)
        category: Filter by category (optional)
        limit: Number of transactions to show (default 10)
    
    Returns:
        Formatted list of transactions
    """
    df = transaction_manager.get_transactions(
        transaction_type=transaction_type,
        category=category,
        limit=limit
    )
    
    if len(df) == 0:
        return "No transactions found."
    
    result = f"Recent Transactions (showing {len(df)}):\n\n"
    for _, row in df.iterrows():
        result += f"ID: {row['id']} | {row['date'].strftime('%Y-%m-%d')} | "
        result += f"{row['type'].title()} | {row['category']} | "
        result += f"${row['amount']:.2f} | {row['description']}\n"
    
    return result


@tool
def get_financial_summary(start_date: str = None, end_date: str = None) -> str:
    """
    Get financial summary showing income, expenses, and net.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
    
    Returns:
        Financial summary for the period
    """
    summary = transaction_manager.get_summary(start_date, end_date)
    
    period = "All Time"
    if start_date and end_date:
        period = f"{start_date} to {end_date}"
    elif start_date:
        period = f"Since {start_date}"
    elif end_date:
        period = f"Until {end_date}"
    
    result = f"Financial Summary ({period}):\n\n"
    result += f"Total Income: ${summary['total_income']:,.2f}\n"
    result += f"Total Expenses: ${summary['total_expenses']:,.2f}\n"
    result += f"Net (Income - Expenses): ${summary['net']:,.2f}\n"
    result += f"Total Transactions: {summary['transaction_count']}\n"
    result += f"  - Income: {summary['income_count']}\n"
    result += f"  - Expenses: {summary['expense_count']}\n"
    
    if summary['net'] > 0:
        result += f"\n✓ You're saving ${summary['net']:,.2f}"
    elif summary['net'] < 0:
        result += f"\n⚠ Overspending by ${abs(summary['net']):,.2f}"
    
    return result


@tool
def analyze_spending(start_date: str = None, end_date: str = None) -> str:
    """
    Analyze spending breakdown by category.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
    
    Returns:
        Spending analysis with percentages by category
    """
    df = transaction_manager.get_spending_by_category(start_date, end_date)
    
    if len(df) == 0:
        return "No expense data available."
    
    result = "Spending by Category:\n\n"
    for _, row in df.iterrows():
        result += f"{row['category']}: ${row['total']:,.2f} "
        result += f"({row['percentage']:.1f}%) - {int(row['count'])} transactions\n"
    
    total = df['total'].sum()
    result += f"\nTotal Expenses: ${total:,.2f}"
    
    top_category = df.iloc[0]
    result += f"\n\n💡 Top Spending: {top_category['category']} (${top_category['total']:,.2f})"
    
    return result


@tool
def get_stock_quote(symbol: str) -> str:
    """
    Get current stock price and information.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)
    
    Returns:
        Stock quote with current price and details
    """
    try:
        symbol = symbol.strip().upper()
        stock = yf.Ticker(symbol)
        info = stock.info
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        
        if not current_price:
            return f"Could not find stock information for {symbol}."
        
        company_name = info.get('longName', symbol)
        previous_close = info.get('previousClose', 0)
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close else 0
        
        result = f"Stock Quote: {company_name} ({symbol})\n\n"
        result += f"Current Price: ${current_price:.2f}\n"
        result += f"Change: ${change:+.2f} ({change_percent:+.2f}%)\n"
        result += f"Previous Close: ${previous_close:.2f}\n"
        
        market_cap = info.get('marketCap', 0)
        if market_cap:
            result += f"Market Cap: ${market_cap:,.0f}\n"
        
        return result
    except Exception as e:
        return f"Error fetching stock quote: {str(e)}"


@tool
def get_categories(transaction_type: str) -> str:
    """
    Get list of available categories.
    
    Args:
        transaction_type: Either "income" or "expense"
    
    Returns:
        List of available categories for that type
    """
    categories = transaction_manager.get_categories(transaction_type.lower())
    result = f"Available {transaction_type.title()} Categories:\n\n"
    for i, cat in enumerate(categories, 1):
        result += f"{i}. {cat}\n"
    return result


@tool
def delete_transaction(transaction_id: int) -> str:
    """
    Delete a transaction by ID.
    
    Args:
        transaction_id: ID of the transaction to delete
    
    Returns:
        Success or error message
    """
    return transaction_manager.delete_transaction(transaction_id)


@tool
def add_investment(symbol: str, amount_dollars: float = None, number_of_shares: float = None,
                   price_per_share: float = None, purchase_date: str = None) -> str:
    """
    Add a stock investment to the portfolio. 
    
    IMPORTANT: This tool automatically:
    1. Records the investment in the portfolio
    2. Deducts the cost from cash balance (adds expense transaction)
    
    DO NOT call add_transaction separately - this tool handles everything!
    
    IMPORTANT: Use 'amount_dollars' for the total $ amount invested (most common case).
    
    Two ways to use this:
    1. DOLLAR AMOUNT (recommended): "I invested $2000 in Apple"
       - Use amount_dollars=2000
       - Fetches current/historical stock price based on date
       - Calculates shares automatically
       
    2. SHARE COUNT: "I bought 10 shares at $150"
       - Use number_of_shares=10, price_per_share=150
    
    PRICE DATA NOTES:
    - Uses DAILY CLOSING PRICES only (not intraday prices)
    - Time of day (10am, 2pm, etc.) is ignored
    - For dates within the last 3-5 days, historical data may not be available yet
    - In such cases, tool will fall back to current price with a warning
    - For accurate prices from very recent dates, provide price_per_share manually
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, GOOGL, TSLA, JPM)
        amount_dollars: Total dollar amount invested (e.g., 2000 for $2000)
        number_of_shares: Number of shares purchased (only if not using amount_dollars)
        price_per_share: Price per share in dollars (optional, will fetch based on purchase_date)
        purchase_date: Date of purchase in YYYY-MM-DD format (defaults to today)
                      NOTE: Only the date matters, time of day is not used
    
    Returns:
        Success message with investment details
    """
    try:
        # Log the inputs for debugging
        debug_info = f"add_investment called with: symbol={symbol}, amount_dollars={amount_dollars}, number_of_shares={number_of_shares}, price_per_share={price_per_share}, purchase_date={purchase_date}"
        print(f"[DEBUG] {debug_info}")
        
        symbol = symbol.upper().strip()
        
        # If price_per_share not provided, fetch price based on date
        if price_per_share is None:
            import yfinance as yf
            import pandas as pd
            from datetime import datetime, timedelta
            
            stock = yf.Ticker(symbol)
            
            # Determine which date to use for price lookup
            if purchase_date:
                # Parse the purchase date - try multiple formats
                target_date = None
                date_formats = [
                    '%Y-%m-%d',      # 2024-01-16
                    '%Y/%m/%d',      # 2024/01/16
                    '%m/%d/%Y',      # 01/16/2024
                    '%m-%d-%Y',      # 01-16-2024
                    '%d/%m/%Y',      # 16/01/2024
                    '%d-%m-%Y',      # 16-01-2024
                ]
                
                for fmt in date_formats:
                    try:
                        target_date = datetime.strptime(purchase_date, fmt)
                        break
                    except ValueError:
                        continue
                
                if target_date is None:
                    return f"Error: Could not parse date '{purchase_date}'. Please use YYYY-MM-DD format (e.g., 2024-01-16)"
                
                # Check if date is in the future
                if target_date > datetime.now():
                    return f"Error: Purchase date cannot be in the future"
                
                # Fetch historical data for the specific date
                # Add a buffer to handle weekends/holidays
                start_date = (target_date - timedelta(days=7)).strftime('%Y-%m-%d')
                end_date = (target_date + timedelta(days=1)).strftime('%Y-%m-%d')
                
                try:
                    hist = stock.history(start=start_date, end=end_date)
                except Exception as e:
                    return f"Error: Failed to fetch historical data for {symbol}: {str(e)}\nTry providing the price manually or use current price."
                
                if hist.empty:
                    # Check if it's a very recent date (within last 3 days)
                    days_ago = (datetime.now() - target_date).days
                    if days_ago <= 3:
                        # For very recent dates, yfinance might not have data yet
                        # Fall back to current price with a warning
                        info = stock.info
                        price_per_share = info.get('currentPrice') or info.get('regularMarketPrice')
                        if price_per_share:
                            date_note = f"\nNote: Historical data not yet available for {purchase_date} (only {days_ago} days ago). Using current price instead."
                        else:
                            return f"Error: No historical or current price data available for {symbol}. Please provide price_per_share manually."
                    else:
                        return f"Error: No historical data found for {symbol} around {purchase_date}. Try a different date or provide price_per_share manually."
                else:
                    # Find the closest trading day to the purchase date
                    hist_dates = hist.index.normalize()
                    
                    # Make target_normalized timezone-aware to match hist_dates
                    # yfinance returns timezone-aware datetimes (typically America/New_York)
                    target_normalized = pd.Timestamp(target_date).normalize()
                    
                    # If hist_dates is timezone-aware, make target_normalized match
                    if hist_dates.tz is not None:
                        target_normalized = target_normalized.tz_localize(hist_dates.tz)
                    
                    # Get the closest date (on or before the target)
                    valid_dates = hist_dates[hist_dates <= target_normalized]
                    if len(valid_dates) == 0:
                        # If no date on or before, get the first available date after
                        closest_date = hist_dates[0]
                    else:
                        closest_date = valid_dates[-1]
                    
                    # Get the close price for that date
                    price_per_share = hist.loc[closest_date, 'Close']
                    
                    # Inform about the actual date used if different
                    actual_date_str = closest_date.strftime('%Y-%m-%d')
                    if actual_date_str != purchase_date:
                        date_note = f"\nNote: Using closing price from {actual_date_str} (closest trading day)"
                    else:
                        date_note = f"\nNote: Using closing price from {purchase_date} (4:00 PM ET)"
            else:
                # No date provided, use current price
                info = stock.info
                price_per_share = info.get('currentPrice') or info.get('regularMarketPrice')
                date_note = ""
            
            if not price_per_share:
                return f"Error: Could not fetch price for {symbol}. Please provide price_per_share manually."
        else:
            date_note = ""
        
        # Calculate quantity based on what's provided
        if amount_dollars is not None:
            # User said "I invested $X" - this is the most common case
            quantity = amount_dollars / price_per_share
            total_cost = amount_dollars
        elif number_of_shares is not None:
            # User specified exact number of shares
            quantity = float(number_of_shares)
            total_cost = quantity * price_per_share
        else:
            return "Error: Must provide either 'amount_dollars' (total $ invested) or 'number_of_shares'"
        
        # Add the investment
        result = transaction_manager.add_investment(
            symbol=symbol,
            quantity=quantity,
            purchase_price=price_per_share,
            purchase_date=purchase_date
        )
        
        # Append date note if applicable
        if date_note:
            result += date_note
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_msg = f"Error adding investment: {str(e)}\n\nDebug details:\n{error_details}"
        print(f"[ERROR] {error_msg}")
        return error_msg


@tool
def get_portfolio_value() -> str:
    """
    Get current portfolio value with live stock prices.
    Shows all stock holdings, their current value, and gains/losses.
    
    Returns:
        Portfolio valuation with current prices and performance
    """
    try:
        portfolio = transaction_manager.get_portfolio_value()
        
        if portfolio['total_invested'] == 0:
            return "No investments in portfolio yet."
        
        result = "Investment Portfolio:\n\n"
        
        for holding in portfolio['holdings']:
            result += f"{holding['symbol']}:\n"
            result += f"  Quantity: {holding['quantity']} shares\n"
            result += f"  Avg Purchase Price: ${holding['avg_purchase_price']:.2f}\n"
            result += f"  Current Price: ${holding['current_price']:.2f}\n"
            result += f"  Total Cost: ${holding['total_cost']:,.2f}\n"
            result += f"  Current Value: ${holding['current_value']:,.2f}\n"
            
            if holding['gain_loss'] >= 0:
                result += f"  Gain: ${holding['gain_loss']:,.2f} (+{holding['gain_loss_percent']:.2f}%) ✓\n"
            else:
                result += f"  Loss: ${abs(holding['gain_loss']):,.2f} ({holding['gain_loss_percent']:.2f}%) ⚠\n"
            result += "\n"
        
        result += f"Portfolio Summary:\n"
        result += f"Total Invested: ${portfolio['total_invested']:,.2f}\n"
        result += f"Current Value: ${portfolio['current_value']:,.2f}\n"
        
        if portfolio['total_gain_loss'] >= 0:
            result += f"Total Gain: ${portfolio['total_gain_loss']:,.2f} (+{portfolio['total_gain_loss_percent']:.2f}%) ✓"
        else:
            result += f"Total Loss: ${abs(portfolio['total_gain_loss']):,.2f} ({portfolio['total_gain_loss_percent']:.2f}%) ⚠"
        
        return result
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Error getting portfolio value: {str(e)}\n\nDetails:\n{error_details}"


@tool
def get_net_worth() -> str:
    """
    Calculate total net worth including cash balance and investment portfolio.
    This shows your complete financial picture.
    
    Returns:
        Complete net worth breakdown
    """
    try:
        net_worth = transaction_manager.get_net_worth()
        
        result = "Net Worth Summary:\n\n"
        result += f"Cash Balance: ${net_worth['cash_balance']:,.2f}\n"
        result += f"  (Income - Expenses from transactions)\n\n"
        result += f"Investment Portfolio: ${net_worth['investment_value']:,.2f}\n"
        
        portfolio = net_worth['portfolio_details']
        if portfolio['holdings']:
            result += f"  Total Invested: ${portfolio['total_invested']:,.2f}\n"
            if portfolio['total_gain_loss'] >= 0:
                result += f"  Gain: ${portfolio['total_gain_loss']:,.2f} (+{portfolio['total_gain_loss_percent']:.2f}%)\n"
            else:
                result += f"  Loss: ${abs(portfolio['total_gain_loss']):,.2f} ({portfolio['total_gain_loss_percent']:.2f}%)\n"
        
        result += f"\n{'='*40}\n"
        result += f"TOTAL NET WORTH: ${net_worth['total_net_worth']:,.2f}\n"
        result += f"{'='*40}"
        
        return result
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Error calculating net worth: {str(e)}\n\nDetails:\n{error_details}"


@tool
def delete_investment(symbol: str) -> str:
    """
    Delete ALL investments for a specific stock symbol.
    Use this to correct mistakes or remove positions you've sold.
    
    Args:
        symbol: Stock ticker symbol to remove (e.g., AAPL, JPM)
    
    Returns:
        Confirmation message
    """
    try:
        symbol = symbol.upper().strip()
        
        # Remove from investments
        initial_count = len(transaction_manager.investments)
        transaction_manager.investments = transaction_manager.investments[
            transaction_manager.investments['symbol'] != symbol
        ]
        removed_count = initial_count - len(transaction_manager.investments)
        
        if removed_count > 0:
            transaction_manager._save_investments()
            return f"✓ Removed {removed_count} investment(s) in {symbol}"
        else:
            return f"No investments found for {symbol}"
            
    except Exception as e:
        return f"Error deleting investment: {str(e)}"


@tool
def plot_portfolio_performance(symbol: str = None, output_file: str = "portfolio_performance.png") -> str:
    """
    Create a visualization showing how investments have performed over time.
    
    For each company, plots the value from purchase date to current date,
    showing growth or loss over time. Uses actual historical stock prices.
    
    Args:
        symbol: Specific stock symbol to plot (e.g., "JPM", "AAPL"). 
                If None, plots all investments in portfolio.
        output_file: Name for the output image file (default: portfolio_performance.png)
    
    Returns:
        Success message with file path, or error if no investments found
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        import seaborn as sns
        from datetime import datetime, timedelta
        import yfinance as yf
        
        # Get investments
        investments = transaction_manager.get_investments()
        
        if len(investments) == 0:
            return "No investments found in portfolio. Add some investments first!"
        
        # Filter by symbol if specified
        if symbol:
            symbol = symbol.upper().strip()
            investments = investments[investments['symbol'] == symbol]
            if len(investments) == 0:
                return f"No investments found for {symbol}"
        
        # Set up the plot style
        sns.set_style("darkgrid")
        plt.figure(figsize=(14, 8))
        
        # Track if we successfully plotted anything
        plotted_any = False
        
        # For each unique symbol
        symbols = investments['symbol'].unique()
        
        for sym in symbols:
            sym_investments = investments[investments['symbol'] == sym]
            
            # Get earliest purchase date for this symbol
            earliest_date = sym_investments['purchase_date'].min()
            
            # Get total shares owned
            total_shares = sym_investments['quantity'].sum()
            total_cost = sym_investments['total_cost'].sum()
            avg_purchase_price = total_cost / total_shares
            
            # Fetch historical data from earliest purchase to now
            try:
                stock = yf.Ticker(sym)
                
                # Get data from purchase date to today
                hist = stock.history(start=earliest_date, end=datetime.now() + timedelta(days=1))
                
                if hist.empty:
                    print(f"Warning: No historical data for {sym}, skipping")
                    continue
                
                # Calculate portfolio value over time for this symbol
                portfolio_values = hist['Close'] * total_shares
                
                # Plot this investment
                plt.plot(portfolio_values.index, portfolio_values.values,
                        label=f'{sym} ({total_shares:.2f} shares)',
                        linewidth=2, marker='o', markersize=3, alpha=0.8)
                
                # Add a horizontal line at the cost basis
                plt.axhline(y=total_cost, color='gray', linestyle='--',
                           alpha=0.3, linewidth=1)
                
                plotted_any = True
                
            except Exception as e:
                print(f"Warning: Error fetching data for {sym}: {e}")
                continue
        
        if not plotted_any:
            return "Could not fetch historical data for any investments. Try again later."
        
        # Formatting
        plt.xlabel('Date', fontsize=12, fontweight='bold')
        plt.ylabel('Portfolio Value ($)', fontsize=12, fontweight='bold')
        
        if symbol:
            plt.title(f'Investment Performance: {symbol}\nFrom Purchase Date to Present',
                     fontsize=14, fontweight='bold', pad=20)
        else:
            plt.title('Portfolio Performance Over Time\nAll Investments',
                     fontsize=14, fontweight='bold', pad=20)
        
        plt.legend(loc='best', fontsize=10, framealpha=0.9)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Generate summary
        result = f"✓ Portfolio performance chart created: {output_file}\n\n"
        result += "Summary:\n"
        
        for sym in symbols:
            sym_investments = investments[investments['symbol'] == sym]
            total_shares = sym_investments['quantity'].sum()
            total_cost = sym_investments['total_cost'].sum()
            
            # Get current price
            try:
                stock = yf.Ticker(sym)
                info = stock.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                current_value = total_shares * current_price
                gain_loss = current_value - total_cost
                gain_loss_pct = (gain_loss / total_cost * 100) if total_cost > 0 else 0
                
                result += f"\n{sym}:\n"
                result += f"  Purchase Date: {sym_investments['purchase_date'].min().strftime('%Y-%m-%d')}\n"
                result += f"  Total Cost: ${total_cost:,.2f}\n"
                result += f"  Current Value: ${current_value:,.2f}\n"
                
                if gain_loss >= 0:
                    result += f"  Gain: ${gain_loss:,.2f} (+{gain_loss_pct:.2f}%) ✓\n"
                else:
                    result += f"  Loss: ${abs(gain_loss):,.2f} ({gain_loss_pct:.2f}%) ⚠\n"
            except:
                pass
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Error creating plot: {str(e)}\n\nDetails:\n{error_details}"


@tool
def plot_portfolio_performance_percent(symbol: str = None, output_file: str = "portfolio_performance_percent.png") -> str:
    """
    Create a visualization showing investment performance as percentage gains/losses over time.
    
    This shows how much each investment has gained or lost (in %) from its purchase price,
    making it easy to compare relative performance across different investments.
    
    Unlike plot_portfolio_performance (which shows dollar values), this shows:
    - All investments start at 0% (purchase date)
    - Positive % = profit, Negative % = loss
    - Easy comparison between stocks of different sizes
    
    Args:
        symbol: Specific stock symbol to plot (e.g., "JPM", "AAPL"). 
                If None, plots all investments in portfolio.
        output_file: Name for the output image file (default: portfolio_performance_percent.png)
    
    Returns:
        Success message with file path, or error if no investments found
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        import seaborn as sns
        from datetime import datetime, timedelta
        import yfinance as yf
        
        # Get investments
        investments = transaction_manager.get_investments()
        
        if len(investments) == 0:
            return "No investments found in portfolio. Add some investments first!"
        
        # Filter by symbol if specified
        if symbol:
            symbol = symbol.upper().strip()
            investments = investments[investments['symbol'] == symbol]
            if len(investments) == 0:
                return f"No investments found for {symbol}"
        
        # Set up the plot style
        sns.set_style("darkgrid")
        plt.figure(figsize=(14, 8))
        
        # Track if we successfully plotted anything
        plotted_any = False
        
        # For each unique symbol
        symbols = investments['symbol'].unique()
        
        for sym in symbols:
            sym_investments = investments[investments['symbol'] == sym]
            
            # Get earliest purchase date for this symbol
            earliest_date = sym_investments['purchase_date'].min()
            
            # Get total shares owned and average purchase price
            total_shares = sym_investments['quantity'].sum()
            total_cost = sym_investments['total_cost'].sum()
            avg_purchase_price = total_cost / total_shares
            
            # Fetch historical data from earliest purchase to now
            try:
                stock = yf.Ticker(sym)
                
                # Get data from purchase date to today
                hist = stock.history(start=earliest_date, end=datetime.now() + timedelta(days=1))
                
                if hist.empty:
                    print(f"Warning: No historical data for {sym}, skipping")
                    continue
                
                # Calculate percentage gain/loss from purchase price
                # Formula: ((Current Price - Purchase Price) / Purchase Price) * 100
                percent_change = ((hist['Close'] - avg_purchase_price) / avg_purchase_price) * 100
                
                # Plot this investment
                plt.plot(percent_change.index, percent_change.values,
                        label=f'{sym} (avg buy: ${avg_purchase_price:.2f})',
                        linewidth=2.5, marker='o', markersize=3, alpha=0.8)
                
                plotted_any = True
                
            except Exception as e:
                print(f"Warning: Error fetching data for {sym}: {e}")
                continue
        
        if not plotted_any:
            return "Could not fetch historical data for any investments. Try again later."
        
        # Add a horizontal line at 0% (break-even point)
        plt.axhline(y=0, color='red', linestyle='--', linewidth=2,
                   alpha=0.6, label='Break-even (0%)')
        
        # Formatting
        plt.xlabel('Date', fontsize=12, fontweight='bold')
        plt.ylabel('Gain/Loss (%)', fontsize=12, fontweight='bold')
        
        if symbol:
            plt.title(f'Investment Performance: {symbol}\nPercentage Gains/Losses from Purchase Price',
                     fontsize=14, fontweight='bold', pad=20)
        else:
            plt.title('Portfolio Performance: Relative Gains/Losses\nAll Investments Compared (%)',
                     fontsize=14, fontweight='bold', pad=20)
        
        plt.legend(loc='best', fontsize=10, framealpha=0.9)
        plt.grid(True, alpha=0.3)
        
        # Add percentage formatting to y-axis
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1f}%'))
        
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Generate summary
        result = f"✓ Portfolio percentage performance chart created: {output_file}\n\n"
        result += "Summary (Current Performance vs. Purchase Price):\n"
        
        for sym in symbols:
            sym_investments = investments[investments['symbol'] == sym]
            total_shares = sym_investments['quantity'].sum()
            total_cost = sym_investments['total_cost'].sum()
            avg_purchase_price = total_cost / total_shares
            
            # Get current price
            try:
                stock = yf.Ticker(sym)
                info = stock.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                
                # Calculate percentage change
                pct_change = ((current_price - avg_purchase_price) / avg_purchase_price) * 100
                
                result += f"\n{sym}:\n"
                result += f"  Purchase Date: {sym_investments['purchase_date'].min().strftime('%Y-%m-%d')}\n"
                result += f"  Avg Purchase Price: ${avg_purchase_price:.2f}\n"
                result += f"  Current Price: ${current_price:.2f}\n"
                
                if pct_change >= 0:
                    result += f"  Performance: +{pct_change:.2f}% ✓\n"
                else:
                    result += f"  Performance: {pct_change:.2f}% ⚠\n"
            except:
                pass
        
        result += "\n💡 Tip: The 0% line shows break-even. Above = profit, below = loss."
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Error creating percentage plot: {str(e)}\n\nDetails:\n{error_details}"


@tool
def get_trading_signals(symbol: str) -> str:
    """
    Analyze stock using technical indicators and provide buy/sell signals.
    
    This tool performs technical analysis using:
    - Moving Averages (50-day and 200-day)
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Volume analysis
    
    Provides clear buy/hold/sell recommendations based on multiple indicators.
    
    Args:
        symbol: Stock ticker symbol (e.g., "AAPL", "JPM", "TSLA")
    
    Returns:
        Comprehensive technical analysis with trading signals and recommendations
    """
    try:
        symbol = symbol.upper().strip()
        
        # Fetch historical data (1 year for calculations)
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1y")
        
        if hist.empty:
            return f"Error: No data available for {symbol}. Check if the symbol is correct."
        
        # Get current info
        info = stock.info
        company_name = info.get('longName', symbol)
        current_price = hist['Close'].iloc[-1]
        
        # Calculate Moving Averages
        hist['SMA50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA200'] = hist['Close'].rolling(window=200).mean()
        
        current_sma50 = hist['SMA50'].iloc[-1]
        current_sma200 = hist['SMA200'].iloc[-1]
        
        # Check for Golden Cross or Death Cross
        if len(hist) >= 2:
            prev_sma50 = hist['SMA50'].iloc[-2]
            prev_sma200 = hist['SMA200'].iloc[-2]
            
            if prev_sma50 <= prev_sma200 and current_sma50 > current_sma200:
                ma_signal = "🟢 GOLDEN CROSS - Strong Buy Signal!"
                ma_strength = "STRONG BUY"
            elif prev_sma50 >= prev_sma200 and current_sma50 < current_sma200:
                ma_signal = "🔴 DEATH CROSS - Strong Sell Signal!"
                ma_strength = "STRONG SELL"
            elif current_sma50 > current_sma200:
                ma_signal = "🟢 Bullish Trend - 50-day MA above 200-day MA"
                ma_strength = "BUY"
            else:
                ma_signal = "🔴 Bearish Trend - 50-day MA below 200-day MA"
                ma_strength = "SELL"
        else:
            ma_signal = "⚪ Insufficient data for moving average crossover"
            ma_strength = "HOLD"
        
        # Calculate RSI (Relative Strength Index)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        if current_rsi > 70:
            rsi_signal = "🔴 Overbought (RSI > 70) - Potential Sell"
            rsi_strength = "SELL"
        elif current_rsi < 30:
            rsi_signal = "🟢 Oversold (RSI < 30) - Potential Buy"
            rsi_strength = "BUY"
        elif current_rsi > 60:
            rsi_signal = "⚠️ Approaching Overbought - Caution"
            rsi_strength = "HOLD"
        elif current_rsi < 40:
            rsi_signal = "🟡 Approaching Oversold - Watch for Entry"
            rsi_strength = "HOLD"
        else:
            rsi_signal = "⚪ Neutral - No strong signal"
            rsi_strength = "HOLD"
        
        # Calculate MACD (Moving Average Convergence Divergence)
        exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
        exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=9, adjust=False).mean()
        
        current_macd = macd.iloc[-1]
        current_signal = signal_line.iloc[-1]
        prev_macd = macd.iloc[-2]
        prev_signal = signal_line.iloc[-2]
        
        if prev_macd <= prev_signal and current_macd > current_signal:
            macd_signal = "🟢 MACD Bullish Crossover - Buy Signal"
            macd_strength = "BUY"
        elif prev_macd >= prev_signal and current_macd < current_signal:
            macd_signal = "🔴 MACD Bearish Crossover - Sell Signal"
            macd_strength = "SELL"
        elif current_macd > current_signal:
            macd_signal = "🟢 MACD Above Signal - Bullish"
            macd_strength = "BUY"
        else:
            macd_signal = "🔴 MACD Below Signal - Bearish"
            macd_strength = "SELL"
        
        # Volume Analysis
        avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
        current_volume = hist['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        if volume_ratio > 1.5:
            volume_signal = f"🔥 High Volume ({volume_ratio:.1f}x average) - Strong Interest"
        elif volume_ratio > 1.2:
            volume_signal = f"📈 Above Average Volume ({volume_ratio:.1f}x) - Increased Interest"
        elif volume_ratio < 0.5:
            volume_signal = f"📉 Low Volume ({volume_ratio:.1f}x average) - Weak Interest"
        else:
            volume_signal = f"⚪ Normal Volume ({volume_ratio:.1f}x average)"
        
        # Overall Signal Calculation
        signal_votes = {
            "BUY": 0,
            "SELL": 0,
            "HOLD": 0,
            "STRONG BUY": 0,
            "STRONG SELL": 0
        }
        
        signal_votes[ma_strength] += 2  # Moving averages get double weight
        signal_votes[rsi_strength] += 1
        signal_votes[macd_strength] += 1
        
        # Determine overall recommendation
        if signal_votes["STRONG BUY"] > 0 or signal_votes["BUY"] >= 3:
            overall = "🟢 STRONG BUY"
            recommendation = "Consider buying or adding to position"
        elif signal_votes["BUY"] > signal_votes["SELL"]:
            overall = "🟢 BUY"
            recommendation = "Positive signals, good entry point"
        elif signal_votes["STRONG SELL"] > 0 or signal_votes["SELL"] >= 3:
            overall = "🔴 STRONG SELL"
            recommendation = "Consider selling or avoiding"
        elif signal_votes["SELL"] > signal_votes["BUY"]:
            overall = "🔴 SELL"
            recommendation = "Negative signals, consider exiting"
        else:
            overall = "⚪ HOLD"
            recommendation = "Mixed signals, maintain current position"
        
        # Build comprehensive result
        result = f"""
═══════════════════════════════════════════════════════════
Technical Analysis: {company_name} ({symbol})
═══════════════════════════════════════════════════════════

📊 Current Status:
   Price: ${current_price:.2f}
   Volume: {current_volume:,.0f} shares ({volume_signal})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 Moving Averages:
   50-day SMA:  ${current_sma50:.2f}
   200-day SMA: ${current_sma200:.2f}
   
   Signal: {ma_signal}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💪 RSI (Relative Strength):
   Current RSI: {current_rsi:.2f}
   
   Signal: {rsi_signal}
   
   Note: RSI < 30 = Oversold (buy opportunity)
         RSI > 70 = Overbought (sell signal)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ MACD (Momentum):
   MACD: {current_macd:.2f}
   Signal Line: {current_signal:.2f}
   
   Signal: {macd_signal}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 OVERALL RECOMMENDATION: {overall}

   {recommendation}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  Disclaimer: This is technical analysis only. Not financial advice.
    Always do your own research and consider your risk tolerance.
═══════════════════════════════════════════════════════════
"""
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Error analyzing {symbol}: {str(e)}\n\nDetails:\n{error_details}"


def create_finance_agent():
    """Create the AI agent with tool calling."""
    
    # Initialize Claude
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        temperature=0,
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    # Bind tools to LLM
    tools = [
        add_transaction,
        view_transactions,
        get_financial_summary,
        analyze_spending,
        get_stock_quote,
        get_categories,
        delete_transaction,
        add_investment,
        get_portfolio_value,
        get_net_worth,
        delete_investment,
        plot_portfolio_performance,
        plot_portfolio_performance_percent,
        get_trading_signals
    ]
    
    llm_with_tools = llm.bind_tools(tools)
    
    # Create system message about data persistence
    system_msg = SystemMessage(content="""You are a personal finance assistant. 

IMPORTANT: All transaction and investment data is automatically saved to CSV files and persists between sessions. When the user restarts, all their previous data is automatically loaded. You have access to ALL historical data through your tools.

When a user asks about their data:
- Use view_transactions to see transaction history
- Use get_portfolio_value to see investments
- Use get_net_worth to see complete financial picture
- Use get_financial_summary for income/expense totals
- Use plot_portfolio_performance to create charts showing dollar value over time
- Use plot_portfolio_performance_percent to create charts showing percentage gains/losses (better for comparing investments)
- Use get_trading_signals to analyze stocks with technical indicators (moving averages, RSI, MACD) and provide buy/sell recommendations

DATE HANDLING:
When the user mentions dates in natural language (like "on the 12 of january", "january 12th", "12/1/2026"), you MUST convert them to YYYY-MM-DD format before calling tools.

IMPORTANT: Ignore any time-of-day information (like "at 10am", "at 2pm"). The tools only use DAILY closing prices, not intraday prices.

Examples:
- "on the 12 of january at 10am" → "2026-01-12" (ignore the "at 10am" part)
- "january 12, 2024" → "2024-01-12"
- "12/1/2026" → "2026-01-12"
- "1/12/26 at 2:30pm" → "2026-01-12" (ignore the time)

Always use the current year (2026) if the user doesn't specify a year.

CRITICAL: When a tool returns an error, you MUST share that exact error message with the user so they understand what went wrong. Do not hide errors or try alternative approaches without first explaining the error to the user.

The data is ALWAYS there - you just need to use the right tool to access it.""")
    
    return llm_with_tools, tools, system_msg


def execute_tool_call(tool_call, tools):
    """Execute a tool call and return the result."""
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    
    # Find and execute the tool
    for tool in tools:
        if tool.name == tool_name:
            try:
                result = tool.invoke(tool_args)
                return result
            except Exception as e:
                return f"Error executing {tool_name}: {str(e)}"
    
    return f"Tool {tool_name} not found"


def main():
    """Main function to run the finance AI agent."""
    print("=" * 60)
    print("Personal Finance AI Agent with Claude")
    print("=" * 60)
    print("\nThis AI agent can help you:")
    print("  • Track income and expenses")
    print("  • Track stock investments")
    print("  • Calculate net worth with live stock prices")
    print("  • Analyze spending patterns")
    print("  • View financial summaries")
    print("  • Get stock quotes")
    print("  • Visualize portfolio performance over time")
    print("  • Get buy/sell trading signals with technical analysis")
    print("\nJust chat naturally! Examples:")
    print("  - I invested $1000 in Apple at $150 per share")
    print("  - How much am I worth?")
    print("  - Show me my portfolio")
    print("  - Add an expense of $45 for groceries")
    print("  - What's my spending breakdown?")
    print("  - Plot my portfolio performance")
    print("  - Show me percentage gains for all investments")
    print("  - Should I buy Tesla? (gets trading signals)")
    print("  - Analyze JPM and give me trading recommendations")
    print("\nType 'quit' or 'exit' to stop.\n")
    
    # Create the agent
    try:
        llm_with_tools, tools, system_msg = create_finance_agent()
    except Exception as e:
        print(f"Error initializing agent: {e}")
        print("\nMake sure you have:")
        print("1. Created a .env file with your ANTHROPIC_API_KEY")
        print("2. Installed all requirements: pip install -r requirements.txt")
        return
    
    # Show what data was loaded
    print("Loading your financial data...")
    transaction_count = len(transaction_manager.transactions)
    investment_count = len(transaction_manager.investments)
    
    if transaction_count > 0 or investment_count > 0:
        print(f"✓ Loaded {transaction_count} transactions")
        print(f"✓ Loaded {investment_count} investments")
        
        # Show quick summary
        summary = transaction_manager.get_summary()
        print(f"\nQuick Summary:")
        print(f"  Cash Balance: ${summary['net']:,.2f}")
        
        if investment_count > 0:
            portfolio = transaction_manager.get_portfolio_value()
            print(f"  Investment Portfolio: ${portfolio['current_value']:,.2f}")
            net_worth = summary['net'] + portfolio['current_value']
            print(f"  Total Net Worth: ${net_worth:,.2f}")
    else:
        print("No previous data found - starting fresh!")
    
    print("\n" + "="*60 + "\n")
    
    # Conversation history - start with system message
    messages = [system_msg]
    
    # Main interaction loop
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! Keep tracking those finances! 💰\n")
                break
            
            if not user_input:
                continue
            
            # Add user message to history
            messages.append(HumanMessage(content=user_input))
            
            try:
                # Get response from Claude
                response = llm_with_tools.invoke(messages)
                
                # Check if Claude wants to use tools
                if hasattr(response, 'tool_calls') and response.tool_calls and len(response.tool_calls) > 0:
                    # Extract and print only the text content (not tool_calls)
                    if hasattr(response, 'content'):
                        if isinstance(response.content, str):
                            if response.content:
                                print(f"\nAgent: {response.content}")
                        elif isinstance(response.content, list):
                            # Content is a list of blocks - extract text blocks only
                            text_content = []
                            for block in response.content:
                                if isinstance(block, dict) and block.get('type') == 'text':
                                    text_content.append(block.get('text', ''))
                                elif isinstance(block, str):
                                    text_content.append(block)
                            if text_content:
                                print(f"\nAgent: {' '.join(text_content)}")
                    
                    # Add Claude's response with tool calls to history
                    messages.append(response)
                    
                    # Execute each tool call and collect results
                    tool_results = []
                    for tool_call in response.tool_calls:
                        print(f"[Using tool: {tool_call['name']}]")
                        result = execute_tool_call(tool_call, tools)
                        
                        # Create tool message
                        tool_msg = ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call['id']
                        )
                        tool_results.append(tool_msg)
                    
                    # Add ALL tool results at once
                    messages.extend(tool_results)
                    
                    # Get final response after tool execution
                    final_response = llm_with_tools.invoke(messages)
                    messages.append(final_response)
                    
                    # Print final response content properly
                    if isinstance(final_response.content, str):
                        print(f"\nAgent: {final_response.content}\n")
                    elif isinstance(final_response.content, list):
                        text_parts = []
                        for block in final_response.content:
                            if isinstance(block, dict) and block.get('type') == 'text':
                                text_parts.append(block.get('text', ''))
                            elif isinstance(block, str):
                                text_parts.append(block)
                        if text_parts:
                            print(f"\nAgent: {' '.join(text_parts)}\n")
                else:
                    # No tools needed, just respond
                    messages.append(response)
                    if isinstance(response.content, str):
                        print(f"\nAgent: {response.content}\n")
                    else:
                        print(f"\nAgent: {str(response.content)}\n")
            
            except Exception as e:
                print(f"\nError: {e}\n")
                
                # Clean up corrupted message history
                print("[Cleaning up message history...]")
                
                # Keep only valid message pairs (user -> assistant)
                clean_messages = [system_msg]  # Always keep system message
                
                i = 0
                while i < len(messages):
                    msg = messages[i]
                    
                    # Skip system message (already added)
                    if isinstance(msg, SystemMessage):
                        i += 1
                        continue
                    
                    # If it's a human message
                    if isinstance(msg, HumanMessage):
                        # Look for the complete response (AI message without pending tool calls)
                        if i + 1 < len(messages):
                            next_msg = messages[i + 1]
                            if isinstance(next_msg, AIMessage):
                                # Check if this AI message has unresolved tool calls
                                if hasattr(next_msg, 'tool_calls') and next_msg.tool_calls:
                                    # Skip this pair - tool calls were never resolved
                                    i += 2
                                    continue
                                else:
                                    # Good pair - keep it
                                    clean_messages.append(msg)
                                    clean_messages.append(next_msg)
                                    i += 2
                                    continue
                        # Orphaned human message
                        i += 1
                        continue
                    
                    i += 1
                
                messages = clean_messages
                print(f"[Recovered {len(messages)} valid messages]\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 💰\n")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}\n")


if __name__ == "__main__":
    main()
