# Finance Agent Updates - Historical Price Fetching

## Summary
Updated the finance agent to automatically fetch **historical stock prices** when a user specifies a purchase date for an investment.

## Problem Solved
Previously, when a user said "On January 16, I bought $1000 worth of Nike stock", the agent would:
- Use the **current** Nike stock price
- Calculate shares based on today's price
- Record incorrect historical data

Now, the agent will:
- Fetch the **actual Nike price from January 16**
- Calculate the correct number of shares purchased
- Store accurate historical investment data

## Key Changes

### 1. Updated `add_investment()` Tool in `finance_agent.py`

**Before:**
```python
# Always fetched current price
if price_per_share is None:
    stock = yf.Ticker(symbol)
    info = stock.info
    price_per_share = info.get('currentPrice')
```

**After:**
```python
# Fetches historical price if date provided
if price_per_share is None:
    if purchase_date:
        # Fetch historical data for the specific date
        hist = stock.history(start=start_date, end=end_date)
        # Find closest trading day
        price_per_share = hist.loc[closest_date, 'Close']
    else:
        # Use current price if no date specified
        price_per_share = info.get('currentPrice')
```

### 2. Smart Date Handling

The updated tool now:
- **Validates dates**: Checks for valid format (YYYY-MM-DD) and prevents future dates
- **Handles weekends/holidays**: If the date is a non-trading day, uses the closest prior trading day
- **Informs the user**: Shows a note when a different trading day was used

Example:
```
User: "I bought Nike stock on January 14, 2024" (this was a Sunday)

Agent response:
✓ Investment added successfully!
Symbol: NKE
Purchase Price: $102.45 per share
Date: 2024-01-14
Note: Using price from 2024-01-12 (closest trading day)
```

### 3. Backwards Compatible

The tool still works with all previous use cases:
- `"I invested $1000 in Apple"` → Uses current price (no date specified)
- `"I bought 10 shares at $150"` → Uses the provided price
- `"On Jan 16, I invested $1000 in Nike"` → Fetches historical price ✨ **NEW**

## Usage Examples

### Example 1: Historical Investment
```
You: On January 16, 2024, I bought $1000 worth of Nike stock

Agent: [Fetches historical data]
✓ Investment added successfully!
Symbol: NKE
Quantity: 9.74 shares
Purchase Price: $102.61 per share
Total Cost: $1,000.00
Date: 2024-01-16
```

### Example 2: Current Investment (No Date)
```
You: I just invested $500 in Tesla

Agent: [Uses current price]
✓ Investment added successfully!
Symbol: TSLA
Quantity: 2.09 shares
Purchase Price: $238.76 per share (current)
Total Cost: $500.00
```

### Example 3: Manual Price (Historical)
```
You: I bought 5 shares of Apple at $175 on December 1, 2023

Agent: [Uses provided price]
✓ Investment added successfully!
Symbol: AAPL
Quantity: 5 shares
Purchase Price: $175.00 per share
Total Cost: $875.00
Date: 2023-12-01
```

## Technical Implementation

### yfinance Historical Data
The tool uses yfinance's `history()` method:
```python
# Fetch data around the target date (±7 days buffer)
hist = stock.history(start=start_date, end=end_date)

# Find closest trading day
hist_dates = hist.index.normalize()
target_normalized = pd.Timestamp(target_date).normalize()
valid_dates = hist_dates[hist_dates <= target_normalized]
closest_date = valid_dates[-1]

# Get closing price
price_per_share = hist.loc[closest_date, 'Close']
```

### Error Handling
- Invalid date format → Clear error message with example
- Future dates → Rejects with error
- No historical data available → Informs user
- Weekend/holiday dates → Uses closest prior trading day with note

## Benefits

1. **Accurate Historical Records**: Portfolio reflects actual purchase prices
2. **Better Gain/Loss Calculations**: Current value vs. actual purchase cost
3. **Natural Language Support**: Users can specify dates conversationally
4. **Automated Data Entry**: No need to manually look up historical prices

## Files Modified

1. **finance_agent.py**
   - Updated `add_investment()` tool with historical price fetching
   - Added pandas import for date handling
   - Enhanced docstring to document historical price feature

2. **README.md**
   - Updated examples to show historical price usage
   - Added "Historical Price Fetching" section
   - Updated features list

3. **transaction_manager.py**
   - No changes needed (already supports date storage)

## Testing Recommendations

Test the following scenarios:
1. ✅ Investment with historical date (weekday)
2. ✅ Investment with historical date (weekend) → should use Friday
3. ✅ Investment with no date → should use current price
4. ✅ Investment with future date → should reject
5. ✅ Investment with invalid date format → should show error
6. ✅ Investment with manual price and date → should use manual price
7. ✅ Check portfolio value calculation with historical vs. current prices

## Next Steps

Consider these potential enhancements:
- Add support for intraday prices (currently uses closing price)
- Support for international markets and different timezones
- Bulk import of historical investments from CSV
- Visualization of portfolio performance over time
