"""
KIP - Consumer Price Index Analyzer
Analyzes sectoral price trends to inform business recommendations
Week 2-3: Enhanced Economic Intelligence
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

class ConsumerPriceAnalyzer:
    """
    Analyze consumer price trends by sector
    Critical for sector-specific business recommendations
    """
    
    def __init__(self):
        self.cpi_data = None
        self.sector_trends = None
        self.latest_trends = None
        
    def load_data(self, file_path='consumer-price_index.csv'):
        """Load consumer price index data"""
        print("=" * 70)
        print("LOADING CONSUMER PRICE INDEX DATA")
        print("=" * 70 + "\n")
        
        self.cpi_data = pd.read_csv(file_path)
        
        # Parse date
        self.cpi_data['Date'] = pd.to_datetime(self.cpi_data['Date'], format='%YM%m')
        
        # Clean column names
        self.cpi_data.columns = ['indicator', 'region', 'unit', 'date', 'value']
        
        print(f"✅ Loaded {len(self.cpi_data)} records")
        print(f"📅 Date range: {self.cpi_data['date'].min()} to {self.cpi_data['date'].max()}")
        print(f"📊 Sectors: {self.cpi_data['indicator'].nunique()}")
        
        # Show sectors
        print(f"\n🏷️  Consumer Price Sectors:")
        for i, sector in enumerate(self.cpi_data['indicator'].unique(), 1):
            print(f"   {i}. {sector}")
        
        return self.cpi_data
    
    def calculate_sector_trends(self, months_lookback=12):
        """
        Calculate YoY change for each sector
        """
        print(f"\n{'='*70}")
        print(f"CALCULATING SECTOR PRICE TRENDS ({months_lookback}-Month)")
        print(f"{'='*70}\n")
        
        trends = []
        
        for sector in self.cpi_data['indicator'].unique():
            sector_data = self.cpi_data[self.cpi_data['indicator'] == sector].sort_values('date')
            
            if len(sector_data) < months_lookback + 1:
                continue
            
            # Get latest value
            latest = sector_data.iloc[-1]
            latest_value = latest['value']
            latest_date = latest['date']
            
            # Get value from 12 months ago
            months_ago = sector_data.iloc[-(months_lookback + 1)]
            past_value = months_ago['value']
            
            # Calculate YoY change
            yoy_change = ((latest_value - past_value) / past_value) * 100
            
            # Calculate recent trend (last 3 months)
            if len(sector_data) >= 4:
                recent_avg = sector_data.iloc[-3:]['value'].mean()
                older_avg = sector_data.iloc[-6:-3]['value'].mean()
                recent_trend = ((recent_avg - older_avg) / older_avg) * 100
            else:
                recent_trend = yoy_change
            
            trends.append({
                'sector': sector,
                'latest_index': latest_value,
                'latest_date': latest_date,
                'yoy_change_pct': yoy_change,
                'recent_trend_pct': recent_trend,
                'status': 'Rising' if yoy_change > 0 else 'Falling'
            })
        
        self.sector_trends = pd.DataFrame(trends)
        self.sector_trends = self.sector_trends.sort_values('yoy_change_pct', ascending=False)
        
        print("📊 Sector Price Trends:")
        print("=" * 70)
        print(self.sector_trends.to_string(index=False))
        
        return self.sector_trends
    
    def identify_opportunities(self):
        """
        Identify business opportunities based on price trends
        """
        print(f"\n{'='*70}")
        print("BUSINESS OPPORTUNITY ANALYSIS")
        print(f"{'='*70}\n")
        
        # Get overall inflation (average)
        overall_inflation = self.sector_trends['yoy_change_pct'].mean()
        
        print(f"📈 Overall CPI Inflation: {overall_inflation:.2f}%\n")
        
        # Categories
        high_inflation = self.sector_trends[self.sector_trends['yoy_change_pct'] > overall_inflation]
        low_inflation = self.sector_trends[self.sector_trends['yoy_change_pct'] <= overall_inflation]
        
        print("🔥 HIGH INFLATION SECTORS (Above average):")
        print("   → High demand, consumers willing to pay more")
        print("   → Good for supply-side businesses\n")
        
        for _, row in high_inflation.head(5).iterrows():
            print(f"   • {row['sector']}: {row['yoy_change_pct']:.2f}%")
            print(f"     Latest Index: {row['latest_index']:.1f}")
            print(f"     Recent Trend: {row['recent_trend_pct']:.2f}%\n")
        
        print("\n❄️  LOW INFLATION SECTORS (Below average):")
        print("   → Price competition, tight margins")
        print("   → Need efficiency/differentiation\n")
        
        for _, row in low_inflation.head(5).iterrows():
            print(f"   • {row['sector']}: {row['yoy_change_pct']:.2f}%")
            print(f"     Latest Index: {row['latest_index']:.1f}\n")
        
        # Business recommendations
        print("\n💡 KIP BUSINESS RECOMMENDATIONS:\n")
        
        recommendations = {
            'Food and non-alcoholic beverages': {
                'if_high': "Food delivery, catering, convenience stores - people paying premium",
                'if_low': "Budget food options, bulk buying, meal prep services"
            },
            'Transport': {
                'if_high': "Ride-sharing, delivery services - capitalize on high prices",
                'if_low': "Avoid transport businesses unless differentiated"
            },
            'Housing, water, electricity, gas': {
                'if_high': "Energy-saving products, alternative power, water solutions",
                'if_low': "Construction, real estate services"
            },
            'Education': {
                'if_high': "Tutoring, online courses, educational supplies",
                'if_low': "Standard education services may be saturated"
            },
            'Clothing and footwear': {
                'if_high': "Quality/premium clothing, alterations, repairs",
                'if_low': "Fast fashion, bulk clothing sales"
            },
            'Communication': {
                'if_high': "Data bundles reselling, internet cafes",
                'if_low': "Avoid - likely oversupplied"
            },
            'Health': {
                'if_high': "Pharmacy, home care, health products",
                'if_low': "Standard health services"
            },
            'Recreation and culture': {
                'if_high': "Event planning, entertainment, leisure services",
                'if_low': "Basic recreation - tight margins"
            },
            'Restaurants and hotels': {
                'if_high': "Fast casual dining, delivery, food trucks",
                'if_low': "Avoid premium dining - price sensitive"
            }
        }
        
        for sector in high_inflation['sector'].head(3):
            for key, rec in recommendations.items():
                if key.lower() in sector.lower():
                    print(f"✅ {sector}:")
                    print(f"   {rec['if_high']}\n")
        
        return {
            'overall_inflation': overall_inflation,
            'high_inflation_sectors': high_inflation,
            'low_inflation_sectors': low_inflation
        }
    
    def plot_trends(self, top_n=10, save=True):
        """
        Visualize sector price trends
        """
        # Get top N rising and falling
        rising = self.sector_trends.nlargest(top_n, 'yoy_change_pct')
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colors = ['#e74c3c' if x > 0 else '#27ae60' for x in rising['yoy_change_pct']]
        
        bars = ax.barh(range(len(rising)), rising['yoy_change_pct'], color=colors)
        ax.set_yticks(range(len(rising)))
        ax.set_yticklabels(rising['sector'], fontsize=10)
        ax.set_xlabel('YoY Change (%)', fontsize=12)
        ax.set_title('Consumer Price Index - Sectoral Trends (12-Month)', 
                    fontsize=14, fontweight='bold')
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, rising['yoy_change_pct'])):
            ax.text(val, bar.get_y() + bar.get_height()/2, 
                   f'{val:.1f}%', 
                   va='center', ha='left' if val > 0 else 'right',
                   fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        
        if save:
            Path('outputs/plots').mkdir(parents=True, exist_ok=True)
            plt.savefig('outputs/plots/cpi_sector_trends.png', dpi=300, bbox_inches='tight')
            print(f"\n✅ Plot saved: outputs/plots/cpi_sector_trends.png")
        
        # plt.show()
    
    def generate_kip_integration_guide(self):
        """
        Generate guide for integrating CPI into KIP
        """
        print(f"\n{'='*70}")
        print("KIP INTEGRATION GUIDE")
        print(f"{'='*70}\n")
        
        guide = []
        guide.append("# Integrating Consumer Price Index into KIP\n")
        guide.append("## How to Use Sectoral Price Trends\n")
        
        guide.append("### 1. User Inputs Business Sector Interest\n")
        guide.append("```python")
        guide.append("user_interest = 'Food business'")
        guide.append("user_capital = 10000")
        guide.append("user_location = 'Lusaka'")
        guide.append("```\n")
        
        guide.append("### 2. Check Sector Price Trend\n")
        guide.append("```python")
        guide.append("# Map user interest to CPI sector")
        guide.append("sector_map = {")
        guide.append("    'food': 'Food and non-alcoholic beverages',")
        guide.append("    'transport': 'Transport',")
        guide.append("    'education': 'Education',")
        guide.append("    # ... etc")
        guide.append("}\n")
        
        guide.append("sector = sector_map.get(user_interest.lower())")
        guide.append("trend = cpi_analyzer.sector_trends[")
        guide.append("    cpi_analyzer.sector_trends['sector'] == sector")
        guide.append("]")
        guide.append("yoy_change = trend['yoy_change_pct'].values[0]")
        guide.append("```\n")
        
        guide.append("### 3. Adjust Recommendation Based on Trend\n")
        guide.append("```python")
        guide.append("if yoy_change > overall_inflation + 3:")
        guide.append("    advice = f\"\"\"")
        guide.append("    ✅ STRONG OPPORTUNITY")
        guide.append("    This sector is growing {yoy_change:.1f}% (above average).")
        guide.append("    Consumers willing to pay premium prices.")
        guide.append("    Recommend: Supply-side businesses, premium offerings")
        guide.append("    \"\"\"")
        guide.append("\nelif yoy_change > overall_inflation:")
        guide.append("    advice = f\"\"\"")
        guide.append("    ⚠️  MODERATE OPPORTUNITY")
        guide.append("    Growing at {yoy_change:.1f}%, slightly above average.")
        guide.append("    Recommend: Efficiency focus, good quality at fair price")
        guide.append("    \"\"\"")
        guide.append("\nelse:")
        guide.append("    advice = f\"\"\"")
        guide.append("    ❌ CHALLENGING SECTOR")
        guide.append("    Growing at {yoy_change:.1f}%, below average.")
        guide.append("    High competition, tight margins.")
        guide.append("    Recommend: Only if you have unique advantage")
        guide.append("    \"\"\"")
        guide.append("```\n")
        
        guide.append("### 4. Combine with Other Factors\n")
        guide.append("```python")
        guide.append("# Final KIP recommendation combines:")
        guide.append("# - CPI sector trend (price dynamics)")
        guide.append("# - Market saturation (competition)")
        guide.append("# - User capital (feasibility)")
        guide.append("# - Location demographics (demand)")
        guide.append("# - Economic forecast (GDP, inflation)")
        guide.append("```\n")
        
        guide_text = "\n".join(guide)
        
        # Save guide
        Path('outputs/docs').mkdir(parents=True, exist_ok=True)
        with open('outputs/docs/CPI_KIP_INTEGRATION.md', 'w', encoding='utf-8') as f:
            f.write(guide_text)
        
        print(guide_text)
        print(f"\n✅ Integration guide saved: outputs/docs/CPI_KIP_INTEGRATION.md")
    
    def save_analysis(self):
        """Save analysis results"""
        Path('data/processed').mkdir(parents=True, exist_ok=True)
        
        self.sector_trends.to_csv('data/processed/cpi_sector_trends.csv', index=False)
        print(f"\n✅ Saved: data/processed/cpi_sector_trends.csv")

def main():
    """
    Main CPI analysis workflow
    """
    print("\n" + "💰" * 35)
    print("CONSUMER PRICE INDEX ANALYZER")
    print("💰" * 35)
    
    analyzer = ConsumerPriceAnalyzer()
    
    # Load data
    analyzer.load_data('data/raw/consumer-price_index.csv')
    
    # Calculate trends
    analyzer.calculate_sector_trends(months_lookback=12)
    
    # Identify opportunities
    analyzer.identify_opportunities()
    
    # Visualize
    analyzer.plot_trends(top_n=12)
    
    # Generate integration guide
    analyzer.generate_kip_integration_guide()
    
    # Save
    analyzer.save_analysis()
    
    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE!")
    print(f"{'='*70}")
    
    print("\n📋 Next steps:")
    print("   1. Review sector trends")
    print("   2. Integrate into Business Generator module")
    print("   3. Use for sector-specific recommendations")
    print("   4. Combine with market saturation data")
    
    print("\n")

if __name__ == "__main__":
    main()
