"""
Project Kwacha - Fixed Data Merger
Properly handles World Bank date format
Week 1: Day 4-5 (FIXED VERSION)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

def load_datasets():
    """Load all raw datasets with proper date parsing"""
    print("=" * 70)
    print("LOADING DATASETS (FIXED VERSION)")
    print("=" * 70 + "\n")
    
    # Load World Bank data (yearly) - FIX DATE PARSING
    print("📊 Loading World Bank data...")
    wb = pd.read_csv('data/raw/worldbank_zambia.csv')
    
    # Check the date format
    print(f"   Sample date values: {wb['date'].head(3).tolist()}")
    
    # Convert to datetime - this should give us actual years, not 1970
    wb['date'] = pd.to_datetime(wb['date'])
    
    # If dates are showing as 1970, extract year from string instead
    if wb['date'].dt.year.nunique() == 1 and wb['date'].dt.year.iloc[0] == 1970:
        print("   ⚠️  Date format issue detected, extracting years from original data...")
        wb = pd.read_csv('data/raw/worldbank_zambia.csv')
        # The 'date' column might actually contain just years
        # Convert year to datetime (January 1st of each year)
        wb['year'] = pd.to_datetime(wb['date']).dt.year
        if wb['year'].nunique() == 1:
            # Date column contains year as string like "2020"
            wb['year'] = wb['date'].astype(str).str[:4].astype(int)
        wb['date'] = pd.to_datetime(wb['year'].astype(str) + '-01-01')
    
    print(f"   ✅ {len(wb)} rows")
    print(f"   📅 Years: {wb['date'].dt.year.min()} - {wb['date'].dt.year.max()}")
    
    # Load Copper prices (monthly)
    print("\n💰 Loading Copper prices...")
    copper = pd.read_csv('data/raw/copper_prices_monthly.csv')
    copper['Date'] = pd.to_datetime(copper['Date'])
    print(f"   ✅ {len(copper)} rows")
    print(f"   📅 {copper['Date'].dt.year.min()} - {copper['Date'].dt.year.max()}")
    
    # Load Forex rates (monthly)
    print("\n💱 Loading Forex rates...")
    forex = pd.read_csv('data/raw/forex_zmw_usd_monthly.csv')
    forex['Date'] = pd.to_datetime(forex['Date'])
    print(f"   ✅ {len(forex)} rows")
    print(f"   📅 {forex['Date'].dt.year.min()} - {forex['Date'].dt.year.max()}")
    
    return wb, copper, forex

def expand_yearly_to_monthly(wb_df):
    """
    Convert World Bank yearly data to monthly data
    """
    print("\n" + "=" * 70)
    print("EXPANDING YEARLY DATA TO MONTHLY")
    print("=" * 70 + "\n")
    
    monthly_data = []
    
    for _, row in wb_df.iterrows():
        year = row['date'].year
        
        # Create 12 rows (one for each month)
        for month in range(1, 13):
            new_row = row.copy()
            new_row['date'] = pd.Timestamp(year=year, month=month, day=1)
            monthly_data.append(new_row)
    
    wb_monthly = pd.DataFrame(monthly_data)
    wb_monthly = wb_monthly.sort_values('date').reset_index(drop=True)
    
    print(f"✅ Expanded: {len(wb_df)} years → {len(wb_monthly)} months")
    print(f"   📅 {wb_monthly['date'].min().date()} to {wb_monthly['date'].max().date()}")
    
    # Show year distribution
    print(f"\n📊 Year range check:")
    print(f"   Min year: {wb_monthly['date'].dt.year.min()}")
    print(f"   Max year: {wb_monthly['date'].dt.year.max()}")
    print(f"   Unique years: {wb_monthly['date'].dt.year.nunique()}")
    
    return wb_monthly

def merge_all_datasets(wb_monthly, copper, forex):
    """
    Merge all datasets on date (month level)
    """
    print("\n" + "=" * 70)
    print("MERGING DATASETS")
    print("=" * 70 + "\n")
    
    # Rename date columns for consistency
    copper = copper.rename(columns={'Date': 'date'})
    forex = forex.rename(columns={'Date': 'date'})
    
    # Show overlap periods
    wb_start, wb_end = wb_monthly['date'].min(), wb_monthly['date'].max()
    copper_start, copper_end = copper['date'].min(), copper['date'].max()
    forex_start, forex_end = forex['date'].min(), forex['date'].max()
    
    print(f"📅 Date Ranges:")
    print(f"   World Bank: {wb_start.date()} to {wb_end.date()}")
    print(f"   Copper:     {copper_start.date()} to {copper_end.date()}")
    print(f"   Forex:      {forex_start.date()} to {forex_end.date()}")
    
    # Calculate overlap
    overlap_start = max(wb_start, copper_start, forex_start)
    overlap_end = min(wb_end, copper_end, forex_end)
    
    print(f"\n🔗 Overlap period: {overlap_start.date()} to {overlap_end.date()}")
    
    print("\n🔗 Merging World Bank + Copper prices...")
    master = pd.merge(wb_monthly, copper, on='date', how='left')
    print(f"   ✅ {len(master)} rows")
    
    print("🔗 Merging + Forex rates...")
    master = pd.merge(master, forex, on='date', how='left')
    print(f"   ✅ {len(master)} rows")
    
    # Count how many rows have all data
    complete_rows = master[
        master['Copper_Price_USD'].notna() & 
        master['ZMW_per_USD'].notna()
    ]
    
    print(f"\n📊 Merge Results:")
    print(f"   • Total rows: {len(master)}")
    print(f"   • Rows with all data: {len(complete_rows)} ({len(complete_rows)/len(master)*100:.1f}%)")
    print(f"   • Copper data: {master['Copper_Price_USD'].notna().sum()} rows")
    print(f"   • Forex data: {master['ZMW_per_USD'].notna().sum()} rows")
    
    # Sort by date
    master = master.sort_values('date').reset_index(drop=True)
    
    return master

def handle_missing_values(df):
    """Handle missing values"""
    print("\n" + "=" * 70)
    print("HANDLING MISSING VALUES")
    print("=" * 70 + "\n")
    
    missing_before = df.isnull().sum().sum()
    print(f"⚠️  Missing values before: {missing_before:,}")
    
    df_filled = df.copy()
    
    # Forward fill for time-series
    numeric_cols = df_filled.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        before_fill = df_filled[col].isnull().sum()
        df_filled[col] = df_filled[col].fillna(method='ffill')
        after_fill = df_filled[col].isnull().sum()
        if before_fill > 0:
            print(f"   • {col}: {before_fill} → {after_fill}")
    
    # Backward fill for any remaining
    for col in numeric_cols:
        df_filled[col] = df_filled[col].fillna(method='bfill')
    
    missing_after = df_filled.isnull().sum().sum()
    print(f"\n✅ Missing values after: {missing_after}")
    
    return df_filled

def add_engineered_features(df):
    """Add ML-ready features"""
    print("\n" + "=" * 70)
    print("ENGINEERING FEATURES")
    print("=" * 70 + "\n")
    
    df_eng = df.copy()
    
    # Time features
    print("📅 Time features...")
    df_eng['year'] = df_eng['date'].dt.year
    df_eng['month'] = df_eng['date'].dt.month
    df_eng['quarter'] = df_eng['date'].dt.quarter
    
    # Lagged GDP
    if 'GDP_growth' in df_eng.columns:
        print("📈 GDP lags...")
        df_eng['GDP_growth_lag_1'] = df_eng['GDP_growth'].shift(1)
        df_eng['GDP_growth_lag_3'] = df_eng['GDP_growth'].shift(3)
        df_eng['GDP_growth_lag_12'] = df_eng['GDP_growth'].shift(12)
    
    # Moving averages
    if 'Copper_Price_USD' in df_eng.columns:
        print("💰 Copper MAs...")
        df_eng['Copper_MA_3'] = df_eng['Copper_Price_USD'].rolling(window=3, min_periods=1).mean()
        df_eng['Copper_MA_12'] = df_eng['Copper_Price_USD'].rolling(window=12, min_periods=1).mean()
    
    if 'ZMW_per_USD' in df_eng.columns:
        print("💱 Forex MAs...")
        df_eng['Forex_MA_3'] = df_eng['ZMW_per_USD'].rolling(window=3, min_periods=1).mean()
        df_eng['Forex_MA_12'] = df_eng['ZMW_per_USD'].rolling(window=12, min_periods=1).mean()
    
    # Economic trend labels
    if 'GDP_growth' in df_eng.columns:
        print("🏷️  Trend labels...")
        df_eng['Economic_Trend'] = pd.cut(
            df_eng['GDP_growth'],
            bins=[-np.inf, 2, 4, np.inf],
            labels=['Decline', 'Stable', 'Growth']
        )
    
    print(f"\n✅ Features: {len(df_eng.columns)} ({len(df_eng.columns) - len(df)} new)")
    
    return df_eng

def save_master_dataset(df):
    """Save final datasets"""
    print("\n" + "=" * 70)
    print("SAVING DATASETS")
    print("=" * 70 + "\n")
    
    Path('data/processed').mkdir(parents=True, exist_ok=True)
    
    # Full dataset
    output_file = 'data/processed/master_dataset.csv'
    df.to_csv(output_file, index=False)
    print(f"✅ {output_file}")
    print(f"   • {len(df):,} rows × {len(df.columns)} columns")
    
    # Recent data (last 10 years)
    current_year = df['date'].dt.year.max()
    cutoff_year = current_year - 10
    recent_df = df[df['date'].dt.year >= cutoff_year].copy()
    recent_file = 'data/processed/master_dataset_recent.csv'
    recent_df.to_csv(recent_file, index=False)
    print(f"✅ {recent_file}")
    print(f"   • {len(recent_df):,} rows ({cutoff_year}-{current_year})")
    
    # Save data dictionary
    dict_lines = []
    dict_lines.append("=" * 70)
    dict_lines.append("PROJECT KWACHA - DATA DICTIONARY")
    dict_lines.append("=" * 70)
    dict_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    dict_lines.append(f"Rows: {len(df):,}")
    dict_lines.append(f"Columns: {len(df.columns)}")
    dict_lines.append(f"Date Range: {df['date'].min().date()} to {df['date'].max().date()}")
    dict_lines.append(f"\n{'Column':<30} {'Type':<15} {'Non-Null':<10} {'Missing %':<10}")
    dict_lines.append("-" * 70)
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = df[col].notna().sum()
        missing_pct = (df[col].isnull().sum() / len(df)) * 100
        dict_lines.append(f"{col:<30} {dtype:<15} {non_null:<10} {missing_pct:<10.1f}")
    
    dict_file = 'data/processed/data_dictionary.txt'
    with open(dict_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(dict_lines))
    print(f"✅ {dict_file}")

def main():
    """Run fixed merge pipeline"""
    print("\n" + "🔗" * 35)
    print("PROJECT KWACHA - DATA MERGER (FIXED)")
    print("🔗" * 35 + "\n")
    
    # Load with proper date handling
    wb, copper, forex = load_datasets()
    
    # Expand yearly to monthly
    wb_monthly = expand_yearly_to_monthly(wb)
    
    # Merge all
    master = merge_all_datasets(wb_monthly, copper, forex)
    
    # Handle missing values
    master_clean = handle_missing_values(master)
    
    # Add features
    master_final = add_engineered_features(master_clean)
    
    # Save
    save_master_dataset(master_final)
    
    print("\n" + "=" * 70)
    print("MERGE COMPLETE!")
    print("=" * 70)
    
    # Summary statistics
    print(f"\n✅ Final Dataset Summary:")
    print(f"   • Total rows: {len(master_final):,}")
    print(f"   • Features: {len(master_final.columns)}")
    print(f"   • Date range: {master_final['date'].min().date()} to {master_final['date'].max().date()}")
    print(f"   • Years covered: {master_final['date'].dt.year.nunique()}")
    
    # Check data availability
    has_copper = master_final['Copper_Price_USD'].notna().sum()
    has_forex = master_final['ZMW_per_USD'].notna().sum()
    has_all = master_final[
        master_final['Copper_Price_USD'].notna() & 
        master_final['ZMW_per_USD'].notna()
    ].shape[0]
    
    print(f"\n📊 Data Coverage:")
    print(f"   • World Bank data: {len(master_final)} rows (100%)")
    print(f"   • Copper data: {has_copper} rows ({has_copper/len(master_final)*100:.1f}%)")
    print(f"   • Forex data: {has_forex} rows ({has_forex/len(master_final)*100:.1f}%)")
    print(f"   • Complete data: {has_all} rows ({has_all/len(master_final)*100:.1f}%)")
    
    print("\n📋 Next steps:")
    print("   1. Check data/processed/master_dataset.csv")
    print("   2. Review data_dictionary.txt")
    print("   3. Start Jupyter notebook exploration")
    print("   4. Week 1 is COMPLETE! 🎉")
    
    print("\n")

if __name__ == "__main__":
    main()
