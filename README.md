# Personal Finance AI Agent

An intelligent finance assistant powered by Claude that understands natural language and tracks both expenses and investments with live stock prices.

## Features

### 💰 Expense Tracking
- Track income and expenses
- Categorize transactions
- Analyze spending patterns
- Financial summaries

### 📈 Investment Portfolio
- **Track stock investments** with purchase price and date
- **Automatic historical price lookup** - specify a date and get the actual price from that day
- **Live portfolio valuation** using real-time stock prices
- **Calculate gains/losses** since purchase
- **Net worth calculation** including cash and investments
- **📊 Visualize performance** - Two chart types:
  - **Dollar charts**: See absolute portfolio value over time
  - **Percentage charts**: Compare relative returns across investments

### 🤖 AI-Powered
- Natural language interface
- Smart tool selection
- Conversation memory
- Context-aware responses

## Setup

### 1. Create Environment

```bash
conda create -n finance-agent python=3.10
conda activate finance-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key.

### 4. Run

```bash
python finance_agent.py
```

## Usage Examples

### Investment Tracking

```
You: I invested $1000 in Apple stock on January 16, 2024

Agent: [Fetches historical price for January 16, 2024 and uses add_investment tool]
✓ Investment added successfully!
Symbol: AAPL
Quantity: 5.41 shares
Purchase Price: $184.86 per share (historical price from Jan 16, 2024)
Total Cost: $1,000.00

You: On 16 of January, I bought $500 worth of Nike actions

Agent: [Fetches historical Nike price for January 16 and calculates quantity]
✓ Investment added successfully!
Symbol: NKE
Quantity: 4.87 shares
Purchase Price: $102.61 per share
Total Cost: $500.00
Note: Using price from 2024-01-16 (closest trading day)

You: I invested $1000 in Apple stock, I bought at $150 per share

Agent: [Calculates quantity and uses add_investment tool]
✓ Investment added successfully!
Symbol: AAPL
Quantity: 6.67 shares
Purchase Price: $150.00 per share
Total Cost: $1,000.00

You: How much am I worth?

Agent: [Uses get_net_worth tool with live prices]
Net Worth Summary:

Cash Balance: $5,250.00
  (Income - Expenses from transactions)

Investment Portfolio: $1,215.50
  Total Invested: $1,000.00
  Gain: $215.50 (+21.55%)

========================================
TOTAL NET WORTH: $6,465.50
========================================

You: Show me my portfolio

Agent: [Uses get_portfolio_value tool]
Investment Portfolio:

AAPL:
  Quantity: 6.67 shares
  Avg Purchase Price: $150.00
  Current Price: $182.45
  Total Cost: $1,000.00
  Current Value: $1,215.50
  Gain: $215.50 (+21.55%) ✓

Portfolio Summary:
Total Invested: $1,000.00
Current Value: $1,215.50
Total Gain: $215.50 (+21.55%) ✓
```

### Expense Tracking

```
You: Add a $45 expense for groceries

Agent: [Uses add_transaction tool]
✓ Transaction added successfully!

You: What's my spending breakdown?

Agent: [Uses analyze_spending tool]
Spending by Category:
Food: $450.00 (35.0%) - 12 transactions
Housing: $1,200.00 (50.0%) - 1 transaction
...
```

### Stock Quotes

```
You: What's Tesla's stock price?

Agent: [Uses get_stock_quote tool]
Stock Quote: Tesla, Inc. (TSLA)
Current Price: $238.76
Change: +$5.23 (+2.24%)
...
```

### Portfolio Visualization

#### Dollar Value Chart
```
You: Plot my portfolio performance

Agent: [Uses plot_portfolio_performance tool]
✓ Portfolio performance chart created: portfolio_performance.png

Summary:

JPM:
  Purchase Date: 2026-01-11
  Total Cost: $1,000.00
  Current Value: $1,045.23
  Gain: $45.23 (+4.52%) ✓

[Chart shows line graph of portfolio dollar value from purchase date to now]
```

#### Percentage Returns Chart
```
You: Show me percentage returns for all my investments

Agent: [Uses plot_portfolio_performance_percent tool]
✓ Portfolio percentage performance chart created: portfolio_performance_percent.png

Summary (Current Performance vs. Purchase Price):

JPM:
  Avg Purchase Price: $245.10
  Current Price: $256.35
  Performance: +4.59% ✓

AAPL:
  Avg Purchase Price: $195.50
  Current Price: $215.20
  Performance: +10.08% ✓

💡 Tip: The 0% line shows break-even. Above = profit, below = loss.

[Chart shows percentage gains/losses - easy to compare relative performance!]
```

**Two views, complete picture:**
- **Dollar chart**: Shows absolute wealth and portfolio value
- **Percentage chart**: Shows relative performance and investment skill

## How It Works

### Investment Tracking
1. When you add an investment, it records:
   - Stock symbol
   - Number of shares
   - Purchase price per share (fetched automatically based on date)
   - Purchase date
   - Total cost

2. **Historical Price Fetching**:
   - If you specify a purchase date (e.g., "on January 16"), the agent fetches the actual stock price from that date
   - Uses yfinance historical data to get the closing price on the specified date
   - If the date falls on a weekend/holiday, it uses the closest prior trading day
   - If no date is specified, uses the current market price

3. When you ask about your worth:
   - Fetches current stock prices via yfinance
   - Calculates current value = shares × current price
   - Shows gain/loss = current value - purchase cost
   - Combines with cash balance for total net worth

### Data Storage
- `transactions.csv` - All income/expense transactions
- `investments.csv` - Stock purchase records
- Both persist between sessions

## Architecture

Uses Claude's native tool calling with langchain-core 1.2.7:
- `@tool` decorator for clean tool definitions
- `bind_tools()` to give Claude access to tools
- Claude decides which tools to use based on your query
- Live stock prices via yfinance API
- Beautiful visualizations with seaborn and matplotlib

