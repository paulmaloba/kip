"""
kip - World Bank Data Collector
Collects economic indicators for Zambia from World Bank API
Week 1: Day 3
"""

import wbdata
import pandas as pd
from datetime import datetime
import os
from pathlib import Path

# Create data directory if it doesn't exist
Path("data/raw").mkdir(parents=True, exist_ok=True)

def collect_worldbank_data():
    """
    Collect key economic indicators for Zambia from World Bank
    """
    print("=" * 60)
    print("WORLD BANK DATA COLLECTION - ZAMBIA")
    print("=" * 60)
    
    # Define indicators we need
    indicators = {
        'NY.GDP.MKTP.KD.ZG': 'GDP_growth',              # GDP growth (annual %)
        'FP.CPI.TOTL.ZG': 'Inflation',                   # Inflation, consumer prices (annual %)
        'SL.UEM.TOTL.ZS': 'Unemployment',                # Unemployment, total (% of labor force)
        'NE.EXP.GNFS.ZS': 'Exports_pct_GDP',            # Exports (% of GDP)
        'NE.IMP.GNFS.ZS': 'Imports_pct_GDP',            # Imports (% of GDP)
        'NY.GDP.PCAP.CD': 'GDP_per_capita',             # GDP per capita (current US$)
        'NV.AGR.TOTL.ZS': 'Agriculture_pct_GDP',        # Agriculture, % of GDP
        'NV.IND.TOTL.ZS': 'Industry_pct_GDP',           # Industry, % of GDP
        'NV.SRV.TOTL.ZS': 'Services_pct_GDP',           # Services, % of GDP
        'BX.KLT.DINV.WD.GD.ZS': 'FDI_pct_GDP',         # Foreign direct investment (% of GDP)
    }
    
    country = 'ZM'  # Zambia ISO code
    
    print(f"\n📊 Collecting data for: Zambia ({country})")
    print(f"📅 Time period: 1990 - Present")
    print(f"📈 Indicators: {len(indicators)}")
    print("\nFetching data from World Bank API...\n")
    
    # Collect each indicator
    data_frames = []
    
    for indicator_code, indicator_name in indicators.items():
        try:
            print(f"  → Fetching: {indicator_name}...", end=" ")
            
            # Fetch data from World Bank
            df = wbdata.get_dataframe({indicator_code: indicator_name}, country=country)
            
            if not df.empty:
                print(f"✅ ({len(df)} records)")
                data_frames.append(df)
            else:
                print("⚠️  No data")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Combine all indicators
    if data_frames:
        print("\n🔄 Combining all indicators...")
        zambia_data = pd.concat(data_frames, axis=1)
        
        # Reset index (date becomes a column)
        zambia_data = zambia_data.reset_index()
        zambia_data = zambia_data.rename(columns={'index': 'date'})
        
        # Sort by date
        zambia_data = zambia_data.sort_values('date', ascending=True)
        
        # Save to CSV
        output_file = 'data/raw/worldbank_zambia.csv'
        zambia_data.to_csv(output_file, index=False)
        
        print(f"\n✅ SUCCESS!")
        print(f"   • Total records: {len(zambia_data)}")
        print(f"   • Date range: {zambia_data['date'].min()} to {zambia_data['date'].max()}")
        print(f"   • Columns: {len(zambia_data.columns)}")
        print(f"   • Saved to: {output_file}")
        
        # Show data summary
        print("\n📊 DATA SUMMARY:")
        print("-" * 60)
        print(zambia_data.describe())
        
        print("\n📋 FIRST 5 ROWS:")
        print("-" * 60)
        print(zambia_data.head())
        
        print("\n📋 LAST 5 ROWS:")
        print("-" * 60)
        print(zambia_data.tail())
        
        # Check for missing values
        print("\n⚠️  MISSING VALUES:")
        print("-" * 60)
        missing = zambia_data.isnull().sum()
        print(missing[missing > 0])
        
        return zambia_data
    else:
        print("\n❌ No data collected!")
        return None

if __name__ == "__main__":
    # Run the data collection
    data = collect_worldbank_data()
    
    print("\n" + "=" * 60)
    print("COLLECTION COMPLETE!")
    print("=" * 60)
    print("\n📁 Next steps:")
    print("   1. Check data/raw/worldbank_zambia.csv")
    print("   2. Run: python src/data_collection/commodity_collector.py")
    print("   3. Run: python notebooks/01_data_exploration.ipynb")
    print("\n")
