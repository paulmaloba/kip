"""
kip - Rentech Data Analyzer
Quick analysis of Lusaka business landscape from Rentech dataset
Week 2: Market Intelligence
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter

def analyze_rentech_data(file_path):
    """
    Analyze the Rentech Lusaka companies dataset
    """
    print("=" * 70)
    print("RENTECH LUSAKA BUSINESS ANALYSIS")
    print("=" * 70 + "\n")
    
    # Load data
    df = pd.read_csv(file_path)
    
    print(f"📊 Dataset Overview:")
    print(f"   • Total Companies: {len(df)}")
    print(f"   • Date Range: Present (Current businesses)")
    print(f"   • Location: {df['city'].iloc[0]}, {df['state'].iloc[0]}")
    
    # Category analysis
    print(f"\n🏢 Category Distribution:")
    categories = df['primary_category_name'].value_counts()
    print(categories.head(20))
    
    # Geographic clustering
    if 'lat' in df.columns and 'lng' in df.columns:
        print(f"\n📍 Geographic Coverage:")
        print(f"   • Companies with coordinates: {df[['lat', 'lng']].notna().all(axis=1).sum()}")
        print(f"   • Latitude range: {df['lat'].min():.4f} to {df['lat'].max():.4f}")
        print(f"   • Longitude range: {df['lng'].min():.4f} to {df['lng'].max():.4f}")
        
        # Identify geographic clusters (simplified)
        lat_clusters = pd.cut(df['lat'], bins=5, labels=['North', 'North-Central', 'Central', 'South-Central', 'South'])
        lng_clusters = pd.cut(df['lng'], bins=5, labels=['West', 'West-Central', 'Central', 'East-Central', 'East'])
        
        df['area_estimate'] = lat_clusters.astype(str) + '-' + lng_clusters.astype(str)
        
        print(f"\n🗺️  Estimated Area Distribution:")
        print(df['area_estimate'].value_counts().head(10))
    
    # Contact info completeness
    print(f"\n📞 Contact Information:")
    print(f"   • Phone: {df['phone'].notna().sum()} ({df['phone'].notna().sum()/len(df)*100:.1f}%)")
    print(f"   • Email: {df['email'].notna().sum()} ({df['email'].notna().sum()/len(df)*100:.1f}%)")
    print(f"   • Website: {df['url'].notna().sum()} ({df['url'].notna().sum()/len(df)*100:.1f}%)")
    
    # Social media presence
    print(f"\n📱 Social Media Presence:")
    social_cols = ['Facebook Profile', 'Instagram Handle', 'LinkedIn', 'Twitter', 'WhatsApp', 'YouTube', 'TikTok']
    for col in social_cols:
        if col in df.columns:
            count = df[col].notna().sum()
            pct = count / len(df) * 100
            print(f"   • {col}: {count} ({pct:.1f}%)")
    
    # Ratings analysis
    if 'star_count' in df.columns and 'rating_count' in df.columns:
        rated = df[df['rating_count'] > 0]
        print(f"\n⭐ Rating Analysis:")
        print(f"   • Companies with ratings: {len(rated)} ({len(rated)/len(df)*100:.1f}%)")
        if len(rated) > 0:
            print(f"   • Average rating: {rated['star_count'].mean():.2f}")
            print(f"   • Average review count: {rated['rating_count'].mean():.1f}")
    
    # Market saturation hints
    print(f"\n🎯 Market Saturation Indicators:")
    print(f"   • Unique categories: {df['primary_category_name'].nunique()}")
    print(f"   • Average companies per category: {len(df) / df['primary_category_name'].nunique():.1f}")
    
    print(f"\n📊 Most Saturated Categories:")
    saturated = categories.head(10)
    for cat, count in saturated.items():
        saturation_level = 'Very High' if count > 50 else 'High' if count > 20 else 'Medium' if count > 10 else 'Low'
        print(f"   • {cat}: {count} businesses ({saturation_level} saturation)")
    
    print(f"\n💡 Underrepresented Categories (opportunities):")
    underrep = categories[categories <= 3]
    print(f"   • Found {len(underrep)} categories with ≤3 businesses")
    print(f"   • Examples: {', '.join(underrep.index[:10].tolist())}")
    
    return df

def save_processed_data(df, output_dir='data/processed'):
    """
    Save processed and categorized data
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Save cleaned data
    output_file = f'{output_dir}/rentech_lusaka_processed.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✅ Saved processed data to: {output_file}")
    
    # Save category saturation
    saturation = df['primary_category_name'].value_counts().reset_index()
    saturation.columns = ['category', 'count']
    saturation['saturation_score'] = saturation['count'] / saturation['count'].max()
    saturation['saturation_level'] = saturation['saturation_score'].apply(
        lambda x: 'Very High' if x > 0.8 else 'High' if x > 0.5 else 'Medium' if x > 0.3 else 'Low'
    )
    
    sat_file = f'{output_dir}/lusaka_category_saturation.csv'
    saturation.to_csv(sat_file, index=False)
    print(f"✅ Saved saturation analysis to: {sat_file}")
    
    # Save geographic distribution
    if 'area_estimate' in df.columns:
        geo_dist = df['area_estimate'].value_counts().reset_index()
        geo_dist.columns = ['area', 'business_count']
        
        geo_file = f'{output_dir}/lusaka_geographic_distribution.csv'
        geo_dist.to_csv(geo_file, index=False)
        print(f"✅ Saved geographic distribution to: {geo_file}")

def main():
    """
    Run Rentech data analysis
    """
    print("\n" + "📊" * 35)
    print("RENTECH LUSAKA DATA ANALYZER")
    print("📊" * 35 + "\n")
    
    # Analyze
    df = analyze_rentech_data('data/raw/rentech_lusaka_companies.csv')
    
    # Save processed data
    save_processed_data(df)
    
    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE!")
    print(f"{'='*70}")
    
    print("\n📋 Generated insights:")
    print("   • Category saturation levels")
    print("   • Geographic distribution")
    print("   • Market opportunities")
    
    print("\n💡 This is a SAMPLE dataset (10 companies)")
    print("   The full Rentech dataset likely has 1,000-10,000+ businesses")
    print("   These insights scale proportionally")
    
    print("\n📋 Next steps:")
    print("   1. Get full Rentech dataset if available")
    print("   2. Run web scraper for additional data")
    print("   3. Merge all sources for comprehensive analysis")
    print("   4. Generate market gap report")
    
    print("\n")

if __name__ == "__main__":
    main()
