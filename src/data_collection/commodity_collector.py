"""
kip - Commodity & Forex Data Collector
Collects copper prices and ZMW/USD exchange rates
Week 1: Day 3-4
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
from pathlib import Path

# Create data directory if it doesn't exist
Path("data/raw").mkdir(parents=True, exist_ok=True)

def collect_copper_prices(start_date='2010-01-01', end_date=None):
    """
    Collect historical copper prices (critical for Zambia's economy)
    Ticker: HG=F (Copper Futures)
    """
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    print("=" * 60)
    print("COPPER PRICES COLLECTION")
    print("=" * 60)
    print(f"📅 Date range: {start_date} to {end_date}")
    print("📊 Ticker: HG=F (Copper Futures)")
    print("\nFetching data from Yahoo Finance...\n")
    
    try:
        # Download copper data
        copper = yf.download('HG=F', start=start_date, end=end_date, progress=False)
        
        if not copper.empty:
            # Reset index to make Date a column
            copper = copper.reset_index()
            
            # Keep only relevant columns
            copper = copper[['Date', 'Close', 'Volume']]
            copper.columns = ['Date', 'Copper_Price_USD', 'Volume']
            
            # Convert to monthly average for easier merging later
            copper['Date'] = pd.to_datetime(copper['Date'])
            copper['YearMonth'] = copper['Date'].dt.to_period('M')
            
            copper_monthly = copper.groupby('YearMonth').agg({
                'Copper_Price_USD': 'mean',
                'Volume': 'sum'
            }).reset_index()
            
            copper_monthly['Date'] = copper_monthly['YearMonth'].dt.to_timestamp()
            copper_monthly = copper_monthly.drop('YearMonth', axis=1)
            
            # Save both daily and monthly
            copper.to_csv('data/raw/copper_prices_daily.csv', index=False)
            copper_monthly.to_csv('data/raw/copper_prices_monthly.csv', index=False)
            
            print(f"✅ SUCCESS!")
            print(f"   • Daily records: {len(copper)}")
            print(f"   • Monthly records: {len(copper_monthly)}")
            print(f"   • Date range: {copper['Date'].min().date()} to {copper['Date'].max().date()}")
            print(f"   • Avg price: ${copper['Copper_Price_USD'].mean():.2f}")
            print(f"   • Saved to: data/raw/copper_prices_daily.csv")
            print(f"   • Saved to: data/raw/copper_prices_monthly.csv")
            
            return copper, copper_monthly
        else:
            print("❌ No copper data retrieved")
            return None, None
            
    except Exception as e:
        print(f"❌ Error collecting copper data: {str(e)}")
        return None, None

def collect_forex_rates(start_date='2010-01-01', end_date=None):
    """
    Collect ZMW/USD exchange rates
    Ticker: ZMWUSD=X
    """
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    print("\n" + "=" * 60)
    print("FOREX RATES COLLECTION (ZMW/USD)")
    print("=" * 60)
    print(f"📅 Date range: {start_date} to {end_date}")
    print("📊 Ticker: ZMWUSD=X")
    print("\nFetching data from Yahoo Finance...\n")
    
    try:
        # Download forex data
        forex = yf.download('ZMWUSD=X', start=start_date, end=end_date, progress=False)
        
        if not forex.empty:
            # Reset index
            forex = forex.reset_index()
            
            # Keep only relevant columns
            forex = forex[['Date', 'Close']]
            forex.columns = ['Date', 'ZMW_per_USD']
            
            # Convert to monthly average
            forex['Date'] = pd.to_datetime(forex['Date'])
            forex['YearMonth'] = forex['Date'].dt.to_period('M')
            
            forex_monthly = forex.groupby('YearMonth').agg({
                'ZMW_per_USD': 'mean'
            }).reset_index()
            
            forex_monthly['Date'] = forex_monthly['YearMonth'].dt.to_timestamp()
            forex_monthly = forex_monthly.drop('YearMonth', axis=1)
            
            # Save both daily and monthly
            forex.to_csv('data/raw/forex_zmw_usd_daily.csv', index=False)
            forex_monthly.to_csv('data/raw/forex_zmw_usd_monthly.csv', index=False)
            
            print(f"✅ SUCCESS!")
            print(f"   • Daily records: {len(forex)}")
            print(f"   • Monthly records: {len(forex_monthly)}")
            print(f"   • Date range: {forex['Date'].min().date()} to {forex['Date'].max().date()}")
            print(f"   • Current rate: {forex['ZMW_per_USD'].iloc[-1]:.2f} ZMW per USD")
            print(f"   • Saved to: data/raw/forex_zmw_usd_daily.csv")
            print(f"   • Saved to: data/raw/forex_zmw_usd_monthly.csv")
            
            return forex, forex_monthly
        else:
            print("❌ No forex data retrieved")
            return None, None
            
    except Exception as e:
        print(f"❌ Error collecting forex data: {str(e)}")
        return None, None

def main():
    """
    Run all commodity and forex data collection
    """
    print("\n🚀 STARTING COMMODITY & FOREX DATA COLLECTION\n")
    
    # Collect copper prices
    copper_daily, copper_monthly = collect_copper_prices()
    
    # Collect forex rates
    forex_daily, forex_monthly = collect_forex_rates()
    
    print("\n" + "=" * 60)
    print("COLLECTION COMPLETE!")
    print("=" * 60)
    
    if copper_daily is not None and forex_daily is not None:
        print("\n✅ All data collected successfully!")
        print("\n📁 Files created:")
        print("   • data/raw/copper_prices_daily.csv")
        print("   • data/raw/copper_prices_monthly.csv")
        print("   • data/raw/forex_zmw_usd_daily.csv")
        print("   • data/raw/forex_zmw_usd_monthly.csv")
        print("\n📊 Total data points:")
        print(f"   • Copper: {len(copper_daily)} daily, {len(copper_monthly)} monthly")
        print(f"   • Forex: {len(forex_daily)} daily, {len(forex_monthly)} monthly")
        
        print("\n📋 Next steps:")
        print("   1. Run: python src/data_processing/merge_datasets.py")
        print("   2. Explore data in Jupyter notebook")
        print("   3. Check data quality")
    else:
        print("\n⚠️  Some data collection failed. Check errors above.")
    
    print("\n")

if __name__ == "__main__":
    main()
