#!/usr/bin/env python3
"""
Test script for the price prediction feature

This tests the predict_price tool with various stocks and timeframes.
"""

import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Price Prediction Feature Test")
print("=" * 60)

try:
    # Import the function
    from finance_agent import predict_price
    
    print("\n✓ Successfully imported predict_price")
    
    # Check for statsmodels
    try:
        import statsmodels
        print("✓ statsmodels library available")
    except ImportError:
        print("\n❌ statsmodels not installed!")
        print("\nInstall it with:")
        print("  pip install statsmodels")
        print("\nOr install all requirements:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    # Test stocks
    test_cases = [
        ("AAPL", 30, "Apple - 30 day prediction"),
        ("JPM", 14, "JPMorgan - 2 week prediction"),
        ("TSLA", 7, "Tesla - 1 week prediction")
    ]
    
    print(f"\nRunning {len(test_cases)} test predictions...")
    print("(This may take 1-2 minutes per stock as ARIMA trains)\n")
    
    for symbol, days, description in test_cases:
        print("=" * 60)
        print(f"Test: {description}")
        print("=" * 60)
        
        try:
            result = predict_price.invoke({
                "symbol": symbol,
                "days": days
            })
            
            print(result)
            
            # Check if chart was created
            chart_file = f"price_prediction_{symbol}.png"
            if os.path.exists(chart_file):
                print(f"\n✓ Chart created: {chart_file}")
                size = os.path.getsize(chart_file)
                print(f"  File size: {size:,} bytes")
            
            print("\n")
            
        except Exception as e:
            print(f"✗ Error predicting {symbol}: {e}\n")
            import traceback
            traceback.print_exc()
            continue
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
    
    print("\n📈 Generated charts:")
    for symbol, _, _ in test_cases:
        chart_file = f"price_prediction_{symbol}.png"
        if os.path.exists(chart_file):
            print(f"  ✓ {chart_file}")
    
    print("\n💡 How to interpret results:")
    print("  • Expected Price: Most likely outcome")
    print("  • Confidence Interval: Range of possibilities (95%)")
    print("  • Expected Return: Percentage gain/loss")
    print("  • Uncertainty: Width of confidence band")
    print()
    print("  Green (bullish): Price expected to rise")
    print("  Red (bearish): Price expected to fall")
    print("  Wide interval: High uncertainty, be cautious")
    print("  Narrow interval: Model is confident")
    
    print("\n🎯 Usage in the agent:")
    print("  'Predict Apple's price for the next month'")
    print("  'What will Tesla be worth in 2 weeks?'")
    print("  'Forecast JPM for 30 days'")
    
    print("\n⚠️  Remember:")
    print("  • Predictions are probabilistic, not guaranteed")
    print("  • Combine with trading signals for best results")
    print("  • Short-term (7-30 days) is most reliable")
    print("  • News events can invalidate predictions")
    
except ImportError as e:
    print(f"\n✗ Failed to import: {e}")
    print("\nMake sure you have all dependencies installed:")
    print("  pip install statsmodels yfinance pandas matplotlib")
except Exception as e:
    print(f"\n✗ Error during testing: {e}")
    import traceback
    traceback.print_exc()
