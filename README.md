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
- **Live portfolio valuation** using real-time stock prices
- **Calculate gains/losses** since purchase
- **Net worth calculation** including cash and investments

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

## How It Works

### Investment Tracking
1. When you add an investment, it records:
   - Stock symbol
   - Number of shares
   - Purchase price per share
   - Purchase date
   - Total cost

2. When you ask about your worth:
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

This is the modern, recommended approach for building agents!
