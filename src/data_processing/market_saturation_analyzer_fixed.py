"""
Project Kwacha - Market Saturation Analyzer (FIXED)
Analyzes business density and identifies market gaps
Week 2: Market Intelligence
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
import json

class MarketSaturationAnalyzer:
    """
    Analyzes market saturation and identifies business opportunities
    """
    
    def __init__(self):
        self.businesses = None
        self.saturation_data = {}
        
    def load_data(self, rentech_file=None, zambiayp_file=None):
        """
        Load business data from multiple sources
        """
        print("=" * 70)
        print("LOADING BUSINESS DATA")
        print("=" * 70 + "\n")
        
        dataframes = []
        
        # Load Rentech data
        if rentech_file and Path(rentech_file).exists():
            print("📊 Loading Rentech data...")
            df_rentech = pd.read_csv(rentech_file)
            df_rentech['source'] = 'rentech'
            dataframes.append(df_rentech)
            print(f"   ✅ {len(df_rentech)} businesses")
        
        # Load ZambiaYP data
        if zambiayp_file and Path(zambiayp_file).exists():
            print("📊 Loading ZambiaYP data...")
            df_yp = pd.read_csv(zambiayp_file)
            df_yp['source'] = 'zambiayp'
            dataframes.append(df_yp)
            print(f"   ✅ {len(df_yp)} businesses")
        
        if not dataframes:
            print("❌ No data loaded!")
            return None
        
        # Combine all sources
        self.businesses = pd.concat(dataframes, ignore_index=True)
        
        # Standardize column names
        self.businesses = self.standardize_columns(self.businesses)
        
        print(f"\n✅ Total businesses loaded: {len(self.businesses)}")
        
        return self.businesses
    
    def standardize_columns(self, df):
        """
        Standardize column names across different sources
        """
        # Map different naming conventions
        column_mapping = {
            'primary_category_name': 'category',
            'category_name': 'categories',
            'state': 'province',
        }
        
        df = df.rename(columns=column_mapping)
        
        # Handle category column - convert lists to strings
        if 'category' in df.columns:
            def clean_category(cat):
                if pd.isna(cat):
                    return 'Uncategorized'
                if isinstance(cat, list):
                    return cat[0] if cat else 'Uncategorized'
                if isinstance(cat, str):
                    # If it's a string representation of a list
                    if cat.startswith('['):
                        try:
                            import ast
                            cat_list = ast.literal_eval(cat)
                            return cat_list[0] if cat_list else 'Uncategorized'
                        except:
                            pass
                    return cat
                return 'Uncategorized'
            
            df['category'] = df['category'].apply(clean_category)
        
        # Ensure key columns exist
        if 'category' not in df.columns and 'categories' in df.columns:
            df['category'] = df['categories'].str.split(',').str[0]
        
        return df
    
    def analyze_by_area(self, city='Lusaka', radius_km=2):
        """
        Analyze business saturation by geographic area
        """
        print(f"\n{'='*70}")
        print(f"ANALYZING {city.upper()} BY AREA")
        print(f"{'='*70}\n")
        
        city_businesses = self.businesses[
            self.businesses['city'].str.lower() == city.lower()
        ].copy()  # Use .copy() to avoid SettingWithCopyWarning
        
        print(f"📍 Total businesses in {city}: {len(city_businesses)}")
        
        # Group by coordinates (cluster businesses in same area)
        if 'lat' in city_businesses.columns and 'lng' in city_businesses.columns:
            # Remove businesses without coordinates
            with_coords = city_businesses[
                city_businesses['lat'].notna() & city_businesses['lng'].notna()
            ].copy()
            
            if len(with_coords) > 0:
                with_coords['area_cluster'] = self.cluster_by_location(
                    with_coords, radius_km
                )
                
                # Group and aggregate
                area_analysis = with_coords.groupby('area_cluster').agg({
                    'name': 'count',
                    'category': lambda x: ', '.join(x.value_counts().head(3).index.tolist()),
                    'lat': 'mean',
                    'lng': 'mean'
                }).reset_index()
                
                area_analysis.columns = ['area_id', 'business_count', 'top_categories', 'lat', 'lng']
                
                print(f"\n🗺️  Identified {len(area_analysis)} geographic clusters")
                print(f"\n📊 Top 5 densest areas:")
                print(area_analysis.nlargest(5, 'business_count')[['area_id', 'business_count', 'top_categories']])
                
                return area_analysis
            else:
                print("⚠️  No businesses with valid coordinates")
                return None
        else:
            print("⚠️  No location data available")
            return None
    
    def cluster_by_location(self, df, radius_km):
        """
        Cluster businesses by geographic proximity
        Simple clustering: businesses within radius_km are in same cluster
        """
        clusters = []
        cluster_id = 0
        
        for idx, row in df.iterrows():
            if not clusters:
                clusters.append({
                    'id': cluster_id,
                    'lat': row['lat'],
                    'lng': row['lng'],
                    'members': [idx]
                })
                cluster_id += 1
            else:
                # Find nearest cluster
                min_dist = float('inf')
                nearest_cluster = None
                
                for cluster in clusters:
                    dist = self.haversine_distance(
                        row['lat'], row['lng'],
                        cluster['lat'], cluster['lng']
                    )
                    if dist < min_dist:
                        min_dist = dist
                        nearest_cluster = cluster
                
                if min_dist <= radius_km:
                    nearest_cluster['members'].append(idx)
                else:
                    clusters.append({
                        'id': cluster_id,
                        'lat': row['lat'],
                        'lng': row['lng'],
                        'members': [idx]
                    })
                    cluster_id += 1
        
        # Map back to dataframe
        cluster_map = {}
        for cluster in clusters:
            for member in cluster['members']:
                cluster_map[member] = cluster['id']
        
        return df.index.map(lambda x: cluster_map.get(x, -1))
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two points in kilometers
        """
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def analyze_category_saturation(self, city='Lusaka'):
        """
        Analyze saturation by business category
        """
        print(f"\n{'='*70}")
        print(f"CATEGORY SATURATION ANALYSIS - {city.upper()}")
        print(f"{'='*70}\n")
        
        city_businesses = self.businesses[
            self.businesses['city'].str.lower() == city.lower()
        ]
        
        # Category counts
        category_counts = city_businesses['category'].value_counts()
        
        # Calculate saturation scores (0-1, where 1 = highly saturated)
        max_count = category_counts.max()
        saturation_scores = category_counts / max_count
        
        saturation_df = pd.DataFrame({
            'category': category_counts.index,
            'business_count': category_counts.values,
            'saturation_score': saturation_scores.values,
            'saturation_level': saturation_scores.apply(self.categorize_saturation)
        })
        
        print("📊 Category Saturation:")
        print(saturation_df.head(15))
        
        # Identify opportunities
        opportunities = saturation_df[
            saturation_df['saturation_level'].isin(['Low', 'Medium'])
        ].sort_values('business_count')
        
        print(f"\n🎯 MARKET OPPORTUNITIES (Low/Medium saturation):")
        print(f"   Found {len(opportunities)} categories")
        if len(opportunities) > 0:
            print("\n", opportunities.head(10))
        
        return saturation_df
    
    def categorize_saturation(self, score):
        """
        Categorize saturation level
        """
        if score < 0.3:
            return 'Low'
        elif score < 0.6:
            return 'Medium'
        elif score < 0.8:
            return 'High'
        else:
            return 'Very High'
    
    def identify_market_gaps(self, city='Lusaka', target_categories=None):
        """
        Identify specific market gaps and opportunities
        """
        print(f"\n{'='*70}")
        print(f"MARKET GAP IDENTIFICATION - {city.upper()}")
        print(f"{'='*70}\n")
        
        city_businesses = self.businesses[
            self.businesses['city'].str.lower() == city.lower()
        ]
        
        gaps = []
        
        # Common business categories that should exist
        expected_categories = [
            'Coffee Shops', 'Bakeries', 'Gyms', 'Bookstores', 
            'Pet Stores', 'Coworking Spaces', 'Tutoring Services',
            'Photography Studios', 'Event Planning', 'Catering',
            'Dry Cleaning', 'Car Wash', 'Beauty Salons',
            'Restaurants', 'Supermarkets', 'Pharmacies',
            'Laundromats', 'Day Care', 'Fitness Centers',
            'Yoga Studios', 'Art Galleries', 'Music Schools'
        ]
        
        if target_categories:
            expected_categories = target_categories
        
        existing_categories = city_businesses['category'].str.lower().unique()
        
        for category in expected_categories:
            matches = sum([category.lower() in str(cat).lower() for cat in existing_categories])
            
            gap = {
                'category': category,
                'existing_count': matches,
                'gap_type': 'missing' if matches == 0 else 'underserved' if matches < 3 else 'exists',
                'opportunity_score': 1.0 if matches == 0 else 0.7 if matches < 3 else 0.3,
                'reasoning': self.get_gap_reasoning(category, matches)
            }
            
            if gap['opportunity_score'] > 0.5:  # High opportunity
                gaps.append(gap)
        
        gaps_df = pd.DataFrame(gaps).sort_values('opportunity_score', ascending=False)
        
        print(f"🎯 Identified {len(gaps_df)} high-opportunity gaps:\n")
        print(gaps_df)
        
        return gaps_df
    
    def get_gap_reasoning(self, category, count):
        """
        Generate reasoning for market gap
        """
        if count == 0:
            return f"No {category} found - completely untapped market"
        elif count < 3:
            return f"Only {count} {category} - underserved market with room for growth"
        else:
            return f"{count} existing - moderate competition"
    
    def export_analysis(self):
        """
        Export all analysis results
        """
        Path('data/processed').mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*70}")
        print("EXPORTING ANALYSIS")
        print(f"{'='*70}\n")
        
        # Save saturation data
        if hasattr(self, 'saturation_analysis'):
            self.saturation_analysis.to_csv(
                'data/processed/category_saturation.csv', index=False
            )
            print("✅ Saved: category_saturation.csv")
        
        # Save gap analysis
        if hasattr(self, 'gap_analysis'):
            self.gap_analysis.to_csv(
                'data/processed/market_gaps.csv', index=False
            )
            print("✅ Saved: market_gaps.csv")
        
        # Save area analysis
        if hasattr(self, 'area_analysis') and self.area_analysis is not None:
            self.area_analysis.to_csv(
                'data/processed/area_analysis.csv', index=False
            )
            print("✅ Saved: area_analysis.csv")
        
        # Save summary report
        report = self.generate_summary_report()
        with open('data/processed/market_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        print("✅ Saved: market_analysis_report.txt")
    
    def generate_summary_report(self):
        """
        Generate comprehensive analysis report
        """
        report = []
        report.append("=" * 70)
        report.append("MARKET SATURATION & GAP ANALYSIS REPORT")
        report.append("Project Kwacha - KIP Intelligence")
        report.append("=" * 70)
        report.append(f"\nTotal Businesses Analyzed: {len(self.businesses)}")
        
        # Data sources
        report.append(f"\nData Sources:")
        source_counts = self.businesses['source'].value_counts()
        for source, count in source_counts.items():
            report.append(f"  • {source}: {count} businesses")
        
        # City distribution
        report.append(f"\nCity Distribution:")
        city_counts = self.businesses['city'].value_counts()
        for city, count in city_counts.items():
            report.append(f"  • {city}: {count} businesses")
        
        if hasattr(self, 'saturation_analysis'):
            report.append(f"\nCategories Analyzed: {len(self.saturation_analysis)}")
            report.append(f"\nTop 5 Most Saturated:")
            for _, row in self.saturation_analysis.head(5).iterrows():
                report.append(f"  • {row['category']}: {row['business_count']} businesses ({row['saturation_level']})")
        
        if hasattr(self, 'gap_analysis'):
            report.append(f"\n\nMarket Gaps Identified: {len(self.gap_analysis)}")
            report.append(f"\nTop 5 Opportunities:")
            for _, row in self.gap_analysis.head(5).iterrows():
                report.append(f"  • {row['category']}: Score {row['opportunity_score']:.2f}")
                report.append(f"    {row['reasoning']}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)

def main():
    """
    Run market saturation analysis
    """
    print("\n" + "📊" * 35)
    print("MARKET SATURATION & GAP ANALYZER")
    print("📊" * 35)
    
    analyzer = MarketSaturationAnalyzer()
    
    # Load data
    analyzer.load_data(
        rentech_file='data/raw/sample-data-Companies.csv',
        zambiayp_file='data/raw/zambiayp_businesses.csv'
    )
    
    if analyzer.businesses is None:
        print("\n❌ No data to analyze!")
        return
    
    # Analyze by area (if location data available)
    analyzer.area_analysis = analyzer.analyze_by_area(city='Lusaka', radius_km=2)
    
    # Analyze category saturation
    analyzer.saturation_analysis = analyzer.analyze_category_saturation(city='Lusaka')
    
    # Identify market gaps
    analyzer.gap_analysis = analyzer.identify_market_gaps(city='Lusaka')
    
    # Export results
    analyzer.export_analysis()
    
    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE!")
    print(f"{'='*70}")
    
    print("\n📁 Generated files:")
    print("   • data/processed/category_saturation.csv")
    print("   • data/processed/market_gaps.csv")
    print("   • data/processed/area_analysis.csv")
    print("   • data/processed/market_analysis_report.txt")
    
    print("\n📋 Next steps:")
    print("   1. Review market gaps for opportunity validation")
    print("   2. Cross-reference with economic data")
    print("   3. Generate contextual business scenarios")
    print("   4. Feed into KIP model training")
    
    print("\n")

if __name__ == "__main__":
    main()
