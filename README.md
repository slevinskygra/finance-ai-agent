# Personal Finance AI Agent

An intelligent finance assistant powered by Claude that understands natural language and tracks both expenses and investments with live stock prices, technical analysis, and risk assessment.

## Features

### 💰 Expense Tracking
- Track income and expenses
- Categorize transactions
- Analyze spending patterns
- Financial summaries

### 📈 Investment Portfolio
- Track stock investments with purchase price and date
- **Automatic historical price lookup** - specify a date and get the actual price from that day
- Live portfolio valuation using real-time stock prices
- Calculate gains/losses since purchase
- Net worth calculation including cash and investments

### 📊 Portfolio Visualization
Two powerful chart types to understand your investments:
- **Dollar charts**: See absolute portfolio value over time
- **Percentage charts**: Compare relative returns across investments (better for comparing performance!)

### 📉 Technical Analysis
Get professional trading signals for any stock:
- **Moving Averages** (50-day & 200-day) - Detect Golden Cross and Death Cross patterns
- **RSI (Relative Strength Index)** - Identify overbought/oversold conditions
- **MACD** - Track momentum and trend changes
- **Volume Analysis** - Confirm signal strength
- **Clear buy/sell/hold recommendations** based on multiple indicators

### 🎲 Monte Carlo Risk Analysis
Understand your investment risk with probability-based analysis:
- **Probability of profit/loss** - Know your odds before investing
- **Value at Risk (VaR)** - See worst-case scenarios with 95%/99% confidence
- **Expected outcomes** - Median and mean projections
- **Upside potential** - Best-case scenarios
- **Beautiful visualizations** - Histogram and cumulative distribution charts

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

**Add investment with historical price:**
```
You: I invested $1000 in Apple stock on January 16, 2024

Agent: ✓ Investment added successfully!
Symbol: AAPL
Quantity: 5.41 shares
Purchase Price: $184.86 per share (historical price from Jan 16, 2024)
Total Cost: $1,000.00
```

**Check your net worth:**
```
You: How much am I worth?

Agent: Net Worth Summary:

Cash Balance: $5,250.00
Investment Portfolio: $1,215.50
  Total Invested: $1,000.00
  Gain: $215.50 (+21.55%)

========================================
TOTAL NET WORTH: $6,465.50
========================================
```

### Technical Analysis

```
You: Should I buy Tesla?

Agent: 
═══════════════════════════════════════════════════════════
Technical Analysis: Tesla, Inc. (TSLA)
═══════════════════════════════════════════════════════════

📊 Current Status:
   Price: $238.76
   Volume: High interest (1.3x average)

📈 Moving Averages:
   50-day SMA:  $235.42
   200-day SMA: $218.15
   Signal: 🟢 Bullish Trend

💪 RSI: 58.32
   Signal: ⚪ Neutral

⚡ MACD:
   Signal: 🟢 MACD Above Signal - Bullish

🎯 OVERALL RECOMMENDATION: 🟢 BUY
   Positive signals, good entry point
```

### Monte Carlo Risk Analysis

```
You: Analyze the risk of investing $1000 in Apple for 30 days

Agent:
═══════════════════════════════════════════════════════════
Monte Carlo Risk Analysis: Apple Inc. (AAPL)
═══════════════════════════════════════════════════════════

📊 Investment Details:
   Investment Amount: $1,000.00
   Time Horizon: 30 days
   Simulations: 10,000

🎯 Expected Outcomes:
   Median Value: $1,015.32 (+1.53%)
   
   50% chance above $1,015.32
   50% chance below $1,015.32

📊 Probability Distribution:
   Probability of Profit: 56.3%
   Probability of Loss: 43.7%
   
   Probability of 20%+ Gain: 8.2%
   Probability of 20%+ Loss: 6.1%

⚠️  Value at Risk (VaR):
   95% VaR: $872.45 (-12.76%)
   └─ 95% confident you won't lose more than $127.55
   
   99% VaR: $815.20 (-18.48%)
   └─ 99% confident you won't lose more than $184.80

📈 Upside Potential:
   75th Percentile: $1,098.50 (+9.85%)
   95th Percentile: $1,245.80 (+24.58%)

💡 Interpretation:
   🟡 Moderate probability of profit (56.3%)
   Slightly positive outlook, but significant uncertainty
   
   Risk Level: 🟡 Moderate (Daily volatility: 1.85%)

✓ Risk analysis chart created: risk_analysis_AAPL.png
```

### Portfolio Visualization

**Percentage returns chart:**
```
You: Show me percentage returns for all my investments

Agent: 
✓ Portfolio percentage performance chart created!

Summary (Current Performance vs. Purchase Price):

JPM: +4.59% ✓
AAPL: +10.08% ✓

💡 Tip: The 0% line shows break-even. Above = profit, below = loss.
```

## How It Works

### Technical Analysis

Uses proven technical indicators:

1. **Moving Averages (SMA50 & SMA200)**
   - Detects Golden Cross (bullish) and Death Cross (bearish) patterns
   - Shows current trend direction

2. **RSI (Relative Strength Index)**
   - Identifies overbought (>70) and oversold (<30) conditions
   - Spots potential reversal points

3. **MACD**
   - Generates buy signals on bullish crossovers
   - Generates sell signals on bearish crossovers

4. **Volume Analysis**
   - Confirms strength of price movements

### Monte Carlo Risk Analysis

Uses **Geometric Brownian Motion** to simulate 10,000 possible price paths:

1. Fetches 1 year of historical data
2. Calculates daily returns and volatility
3. Runs 10,000 simulations of possible futures
4. Analyzes results for probabilities, VaR, percentiles
5. Creates distribution charts

**Better than price predictions** - shows you the range of possible outcomes instead of pretending to know the exact future price.

## Data Storage

- `transactions.csv` - All income/expense transactions
- `investments.csv` - Stock purchase records
- Both persist between sessions

## Available Tools

### Portfolio Management
- `add_investment` - Record stock purchases
- `get_portfolio_value` - View current holdings
- `get_net_worth` - Calculate total net worth
- `plot_portfolio_performance` - Dollar value chart
- `plot_portfolio_performance_percent` - Percentage returns chart

### Market Analysis
- `get_stock_quote` - Get current stock price
- `get_trading_signals` - Technical analysis with buy/sell recommendations
- `analyze_risk` - Monte Carlo risk analysis with probability distributions

### Transaction Tracking
- `add_transaction` - Record income/expenses
- `view_transactions` - See transaction history
- `analyze_spending` - Spending breakdown

## Requirements

Key dependencies:
- `anthropic>=0.39.0` - Claude API
- `langchain-anthropic>=0.3.0` - LangChain integration
- `yfinance>=0.2.40` - Stock price data
- `pandas>=2.0.0` - Data manipulation
- `matplotlib>=3.7.0` - Charting
- `seaborn>=0.13.0` - Visualizations
- `numpy>=1.24.0` - Monte Carlo simulations

## Tips

### Example Workflow

```
1. "Should I buy Tesla?" 
   → Get trading signals

2. "Analyze the risk of investing $5000 in Tesla for 30 days"
   → See probability distribution

3. If both look good, buy it
   → "I invested $5000 in Tesla at $238 per share"

4. Track performance
   → "Show me percentage returns for all investments"
```

