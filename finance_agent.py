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
       - Fetches current stock price
       - Calculates shares automatically
       
    2. SHARE COUNT: "I bought 10 shares at $150"
       - Use number_of_shares=10, price_per_share=150
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, GOOGL, TSLA, JPM)
        amount_dollars: Total dollar amount invested (e.g., 2000 for $2000)
        number_of_shares: Number of shares purchased (only if not using amount_dollars)
        price_per_share: Price per share in dollars (optional, will fetch current if not provided)
        purchase_date: Date of purchase in YYYY-MM-DD format (defaults to today)
    
    Returns:
        Success message with investment details
    """
    try:
        symbol = symbol.upper().strip()
        
        # If price_per_share not provided, fetch current price
        if price_per_share is None:
            import yfinance as yf
            stock = yf.Ticker(symbol)
            info = stock.info
            price_per_share = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if not price_per_share:
                return f"Error: Could not fetch current price for {symbol}. Please provide price_per_share manually."
        
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
        
        return result
        
    except Exception as e:
        return f"Error adding investment: {str(e)}"


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
        delete_investment
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
    print("\nJust chat naturally! Examples:")
    print("  - I invested $1000 in Apple at $150 per share")
    print("  - How much am I worth?")
    print("  - Show me my portfolio")
    print("  - Add an expense of $45 for groceries")
    print("  - What's my spending breakdown?")
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
