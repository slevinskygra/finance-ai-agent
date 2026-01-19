# Finance Agent - Change Log

## Version 2.0 - Portfolio Visualization & Historical Tracking

**Date:** January 19, 2026

### 🎉 Major Features Added

#### 1. Historical Stock Price Fetching
**What:** Automatically fetch actual historical stock prices when adding investments with a date.

**Before:**
```
User: "On January 11, I bought $1000 of JPM"
Agent: Uses current price (incorrect for past dates)
```

**After:**
```
User: "On January 11, I bought $1000 of JPM"
Agent: Fetches actual JPM price from January 11, 2026
✓ Uses correct historical price!
```

**Technical Details:**
- Uses yfinance `history()` method to fetch closing prices
- Handles weekends/holidays by finding closest trading day
- Falls back to current price for very recent dates (< 3-5 days)
- Timezone-aware date handling
- Supports multiple date formats

**Files Modified:**
- `finance_agent.py`: Updated `add_investment()` tool
- `transaction_manager.py`: No changes needed (already stored dates)

---

#### 2. Portfolio Performance Visualization (Dollar Values)
**What:** Create beautiful charts showing portfolio value over time.

**Usage:**
```
"Plot my portfolio performance"
"Show me a chart of my investments"
"How has my portfolio grown over time?"
```

**Features:**
- Line chart for each investment
- Shows dollar value from purchase date to present
- Cost basis reference lines
- Professional seaborn styling
- 300 DPI high-quality output
- Combines multiple purchases of same stock

**Output:**
- PNG file: `portfolio_performance.png`
- Text summary with current values and gains/losses

**New Tool Added:**
```python
@tool
def plot_portfolio_performance(symbol: str = None, 
                               output_file: str = "portfolio_performance.png") -> str
```

**Files Modified:**
- `finance_agent.py`: Added `plot_portfolio_performance()` function
- `requirements.txt`: Added matplotlib, seaborn

---

#### 3. Portfolio Performance Visualization (Percentage Returns)
**What:** Create charts showing percentage gains/losses for easy comparison.

**Usage:**
```
"Show me percentage returns for all investments"
"Compare my stocks' performance"
"Which investment performed best?"
```

**Why This Matters:**
Makes it easy to compare investments of different sizes:
- $1000 investment gaining $50 = 5%
- $100 investment gaining $20 = 20%
- Percentage chart clearly shows 20% > 5%!

**Features:**
- All investments start at 0% (normalized)
- Break-even reference line (red dashed at 0%)
- Easy identification of winners/losers
- Percentage-formatted Y-axis
- Same professional styling as dollar chart

**Output:**
- PNG file: `portfolio_performance_percent.png`
- Text summary with percentage performance

**New Tool Added:**
```python
@tool
def plot_portfolio_performance_percent(symbol: str = None,
                                       output_file: str = "portfolio_performance_percent.png") -> str
```

**Files Modified:**
- `finance_agent.py`: Added `plot_portfolio_performance_percent()` function

---

### 🐛 Critical Bug Fixes

#### Fix 1: Timezone Awareness Issue
**Problem:** 
```
TypeError: Invalid comparison between dtype=datetime64[ns, America/New_York] and Timestamp
```

**Root Cause:**
yfinance returns timezone-aware timestamps (America/New_York), but our comparison used timezone-naive timestamps. Pandas refuses to compare these.

**Solution:**
```python
# Match timezone if needed
if hist_dates.tz is not None:
    target_normalized = target_normalized.tz_localize(hist_dates.tz)
```

**Impact:** This was preventing ALL historical price lookups from working.

**Files Modified:**
- `finance_agent.py`: `add_investment()` function

---

#### Fix 2: Date Format Confusion in System Prompt
**Problem:**
System prompt examples showed 2024 dates, but current year is 2026.

**Solution:**
Updated all examples to use 2026 and made Claude explicitly aware of current year.

**Files Modified:**
- `finance_agent.py`: System prompt in `create_finance_agent()`

---

#### Fix 3: Time-of-Day Handling
**Problem:**
Users would say "at 10am" but tool only uses daily closing prices.

**Solution:**
- Tool now ignores time-of-day information
- System prompt instructs Claude to strip out time
- Documentation clarifies daily closing prices are used

**Files Modified:**
- `finance_agent.py`: System prompt and tool docstring

---

### 🔧 Improvements

#### 1. Flexible Date Parsing
**What:** Accept multiple date formats instead of just YYYY-MM-DD.

**Formats Supported:**
- YYYY-MM-DD (2026-01-11)
- YYYY/MM/DD (2026/01/11)
- MM/DD/YYYY (01/11/2026)
- MM-DD-YYYY (01-11-2026)
- DD/MM/YYYY (11/01/2026)
- DD-MM-YYYY (11-01-2026)

**Files Modified:**
- `finance_agent.py`: `add_investment()` function

---

#### 2. Better Error Messages
**What:** Show actual errors to users instead of hiding them.

**Before:**
```
"I encountered a technical issue"
```

**After:**
```
"Error: No historical data found for TSLA around 2026-01-11
Try a different date or provide price_per_share manually."
```

**Also Added:**
- Debug logging (shows parameters passed to tools)
- Detailed tracebacks for troubleshooting
- Clear guidance on next steps

**Files Modified:**
- `finance_agent.py`: Error handling in multiple functions

---

#### 3. Enhanced System Prompt
**What:** Better instructions for Claude on date handling and error reporting.

**Key Additions:**
- Explicit date conversion examples
- Instructions to ignore time-of-day
- Requirement to share errors with users
- Mention of both plotting tools

**Files Modified:**
- `finance_agent.py`: `create_finance_agent()` system message

---

### 📦 New Dependencies

Added to `requirements.txt`:
```
matplotlib>=3.7.0
seaborn>=0.13.0
```

**Installation:**
```bash
pip install matplotlib seaborn
# or
pip install -r requirements.txt
```

---


1. **README.md**
   - Added plotting features
   - Updated examples
   - Added architecture notes

---

### 🔄 Breaking Changes

**None!** All changes are backward compatible.

Existing investments and transactions continue to work exactly as before.

---

### 🎯 Usage Examples

#### Example 1: Add Investment with Historical Date
```
You: On January 11, I bought $1000 worth of JPMorgan shares

Agent: [Fetches historical price for 2026-01-11]
✓ Investment added successfully!
Symbol: JPM
Quantity: 4.08 shares
Purchase Price: $245.10 per share
Total Cost: $1,000.00
Date: 2026-01-11
```

#### Example 2: Plot Dollar Values
```
You: Plot my portfolio performance

Agent: [Creates chart]
✓ Portfolio performance chart created: portfolio_performance.png

JPM:
  Total Cost: $1,000.00
  Current Value: $1,045.23
  Gain: $45.23 (+4.52%) ✓
```

#### Example 3: Plot Percentage Returns
```
You: Show me percentage returns for all investments

Agent: [Creates percentage chart]
✓ Portfolio percentage performance chart created!

JPM:
  Performance: +4.59% ✓

AAPL:
  Performance: +10.08% ✓

💡 AAPL outperformed JPM!
```

---

### 🏗️ Technical Architecture

#### Tool Chain:
```
User Input → Claude (LLM)
           ↓
    Tool Selection
           ↓
    add_investment / plot_portfolio_performance / plot_portfolio_performance_percent
           ↓
    yfinance API (historical data)
           ↓
    pandas (data processing)
           ↓
    matplotlib + seaborn (visualization)
           ↓
    PNG output + Text summary
```

#### Data Flow:
```
1. User specifies date and amount
2. Claude converts natural language to YYYY-MM-DD
3. Tool fetches historical price from yfinance
4. Investment saved to investments.csv
5. Expense transaction auto-created
6. Charts can be generated anytime after
```

---

### 📊 Feature Comparison

| Feature | Before | After |
|---------|--------|-------|
| Historical prices | ❌ Used current price | ✅ Fetches actual historical price |
| Date formats | Only YYYY-MM-DD | 6+ formats supported |
| Visualization | ❌ None | ✅ Two chart types |
| Comparison | Manual calculation | Easy visual comparison |
| Error messages | Hidden/vague | Clear and actionable |
| Timezone handling | ❌ Crashed | ✅ Timezone-aware |
| Time-of-day | Confusing | Clarified (uses closing) |

---

### 🚀 Performance

#### Typical Operation Times:
- Add investment with historical date: 1-3 seconds
- Generate dollar chart: 2-5 seconds (first time)
- Generate percentage chart: 2-5 seconds (first time)
- Subsequent charts: 1-2 seconds (some caching)

#### File Sizes:
- Dollar chart PNG: ~150-500 KB
- Percentage chart PNG: ~150-600 KB
- Depends on number of data points and date range

---

### 🔮 Future Enhancements

Potential additions for next version:

#### Visualization Improvements:
- [ ] Compare to market indices (S&P 500, NASDAQ)
- [ ] Show dividends and total return
- [ ] Moving averages (50-day, 200-day)
- [ ] Volume indicators
- [ ] Candlestick charts
- [ ] Interactive plots with plotly
- [ ] Portfolio allocation pie chart
- [ ] Correlation heatmap

#### Analytics:
- [ ] Sharpe ratio calculation
- [ ] Risk-adjusted returns
- [ ] Annualized returns
- [ ] Volatility metrics
- [ ] Beta calculations
- [ ] Time-weighted vs money-weighted returns

#### Functionality:
- [ ] Intraday price support
- [ ] International markets
- [ ] Bulk CSV import
- [ ] Export reports to PDF
- [ ] Email summaries
- [ ] Scheduled charts

---

### 🐛 Known Issues

#### Issue 1: Very Recent Dates (< 3 days)
**Status:** By design / Limitation of yfinance

**Description:**
Historical data for very recent dates may not be available yet.

**Workaround:**
Tool automatically falls back to current price with a note.

**Alternative:**
Provide the exact price manually:
```
"I bought JPM on January 16 at $245.50 per share"
```

---

#### Issue 2: Market Holidays
**Status:** Handled gracefully

**Description:**
If you specify a date when markets were closed (weekend/holiday), the tool uses the closest prior trading day.

**Behavior:**
```
User: "On January 13, 2026" (Sunday)
Tool: Uses price from January 10, 2026 (Friday)
Note: "Using closing price from 2026-01-10 (closest trading day)"
```

---

### 🔒 Security & Privacy

**Data Storage:**
- All data stored locally in CSV files
- No cloud storage or external databases
- You control your own data

**API Keys:**
- yfinance: Free, no API key needed
- Anthropic: Your key, stored in .env file locally

**Network Access:**
- yfinance: Fetches public stock data only
- Anthropic: API calls to Claude for intelligence

---

### 📝 Migration Guide

**From Previous Version:**

No migration needed! Just:

1. Update your code:
   ```bash
   # Copy the new finance_agent.py
   ```

2. Install new dependencies:
   ```bash
   pip install matplotlib seaborn
   ```

3. Start using new features:
   ```bash
   python finance_agent.py
   ```

All existing data (transactions.csv, investments.csv) will work without changes.

---

### 📋 Checklist for Users

After updating, verify:

- [ ] Can add investment with date: `"On Jan 11, I bought $1000 of JPM"`
- [ ] Historical price is fetched (not current price)
- [ ] Can generate dollar chart: `"Plot my portfolio"`
- [ ] Can generate percentage chart: `"Show percentage returns"`
- [ ] Charts are saved as PNG files
- [ ] Can open and view charts
- [ ] Summary shows correct gains/losses

---

## Summary

**This release transforms the finance agent from a basic tracker to a comprehensive portfolio analysis tool.**

### Key Improvements:
✅ **Historical accuracy** - Uses actual purchase prices  
✅ **Visual insights** - Two powerful chart types  
✅ **Better comparisons** - Percentage charts reveal true performance  
✅ **Robust handling** - Fixed timezone issues, improved error messages  
✅ **User-friendly** - Natural language, flexible dates, clear feedback  

### Impact:
Users can now:
- Track investments with historical accuracy
- Visualize portfolio growth over time
- Compare investment performance easily
- Make data-driven decisions
- Understand what's working and what's not
