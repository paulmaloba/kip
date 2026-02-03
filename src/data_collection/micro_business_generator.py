"""
Project Kwacha - Micro-Business Scenario Generator
Generates realistic low-capital business ideas (K1,000 - K50,000)
Addresses dataset imbalance toward large businesses
Week 2: Enhanced Training Data
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

class MicroBusinessGenerator:
    """
    Generate realistic micro and small business scenarios
    Focus: K1,000 - K50,000 capital range
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        if ANTHROPIC_AVAILABLE and api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = None
        
        # Load economic context
        self.economic_data = self.load_economic_context()
        
        # Zambian micro-business categories
        self.micro_categories = self.define_micro_categories()
    
    def load_economic_context(self):
        """Load economic indicators"""
        try:
            df = pd.read_csv('data/processed/master_dataset.csv')
            return df
        except:
            print("⚠️  Economic data not found, using defaults")
            return None
    
    def define_micro_categories(self):
        """
        Define realistic Zambian micro-business categories
        Based on actual informal sector activities
        """
        return {
            "Street Vending": {
                "capital_range": (1000, 5000),
                "examples": ["Mobile phone accessories", "Airtime", "Snacks", "Drinks", 
                           "Vegetables", "Fruits", "Second-hand clothes"],
                "location": ["Market", "Street corner", "Bus station", "Shopping area"],
                "skills": "Low",
                "permits": "Market fee, Trading license (K50-200)"
            },
            
            "Home-Based Food": {
                "capital_range": (2000, 15000),
                "examples": ["Fritters (vitumbuwa)", "Samosas", "Cakes", "Ice blocks",
                           "Home cooked meals", "Traditional beer (munkoyo)", "Popcorn"],
                "location": ["Home", "Neighborhood"],
                "skills": "Cooking",
                "permits": "Food handling certificate (K150)"
            },
            
            "Mobile Services": {
                "capital_range": (3000, 20000),
                "examples": ["Barber (mobile)", "Hairdressing (home visits)", "Phone repair",
                           "Tailoring (home-based)", "Shoe repair", "Laundry service"],
                "location": ["Customer location", "Home workshop"],
                "skills": "Technical skill required",
                "permits": "Skills certificate helpful"
            },
            
            "Market Trading": {
                "capital_range": (5000, 30000),
                "examples": ["Vegetable stall", "Fish trading", "Charcoal sales",
                           "Secondhand clothes", "Household items", "Traditional medicine"],
                "location": ["Market stall", "Roadside"],
                "skills": "Basic business",
                "permits": "Market fee (K200-500/month)"
            },
            
            "Agriculture (Small-Scale)": {
                "capital_range": (10000, 50000),
                "examples": ["Backyard chickens (50-100 birds)", "Mushroom growing",
                           "Vegetable garden (1-2 plots)", "Rabbit farming", "Goat rearing (5-10)"],
                "location": ["Backyard", "Rented plot", "Peri-urban"],
                "skills": "Agricultural knowledge",
                "permits": "Minimal"
            },
            
            "Transport Services": {
                "capital_range": (15000, 50000),
                "examples": ["Bicycle taxi (2-3 bikes)", "Wheelbarrow transport",
                           "Delivery service (bicycle)", "Market porter service"],
                "location": ["Market", "Shopping areas", "Residential"],
                "skills": "Physical fitness",
                "permits": "Council permit (K100-300)"
            },
            
            "Retail (Micro)": {
                "capital_range": (5000, 25000),
                "examples": ["Tuck shop (home-based)", "Grocery kiosk", "Airtime kiosk",
                           "Small hardware", "School supplies", "Beauty products (small stock)"],
                "location": ["Home", "Rented kiosk", "Container"],
                "skills": "Basic literacy, numeracy",
                "permits": "Trading license (K150-500)"
            },
            
            "Creative/Craft": {
                "capital_range": (2000, 15000),
                "examples": ["Basket weaving", "Jewelry making", "Screen printing",
                           "Soap making", "Candle making", "Art/crafts for tourists"],
                "location": ["Home", "Craft market", "Tourist areas"],
                "skills": "Artistic/craft skills",
                "permits": "Minimal"
            }
        }
    
    def generate_micro_business_prompt(self, category_info, capital, location, year):
        """
        Generate detailed prompt for micro-business
        """
        category_name = category_info['name']
        details = category_info['details']
        
        # Get economic context
        econ_context = ""
        if self.economic_data is not None:
            year_data = self.economic_data[self.economic_data['year'] == year]
            if not year_data.empty:
                row = year_data.iloc[0]
                econ_context = f"""
Economic Context ({year}):
- GDP Growth: {row.get('GDP_growth', 3.5):.1f}%
- Inflation: {row.get('Inflation', 12.0):.1f}%
- Unemployment: {row.get('Unemployment', 13.0):.1f}%
- Exchange Rate: K{row.get('ZMW_per_USD', 20.0):.1f}/USD
"""
        
        prompt = f"""Generate a realistic micro-business scenario for Zambia.

BUSINESS TYPE: {category_name}
TARGET CAPITAL: K{capital:,} Zambian Kwacha
LOCATION: {location}
YEAR: {year}

{econ_context}

CATEGORY CONTEXT:
- Typical businesses in this category: {', '.join(details['examples'][:3])}
- Typical locations: {', '.join(details['location'])}
- Skills required: {details['skills']}
- Permits/licenses: {details['permits']}

ZAMBIAN MICRO-BUSINESS REALITY:
- Most entrepreneurs are women (60-70%)
- Starting with savings, family loans, or ROSCAs (chilimba)
- No access to formal credit
- Operating in informal sector initially
- High competition, low profit margins
- Weather-dependent (for street/market vendors)
- Customer base: Local community, low-income
- Daily income targets: K50-200 per day

Generate a REALISTIC business scenario that:
1. Uses exactly K{capital:,} capital (be specific about allocation)
2. Is actually viable in {location}, Zambia
3. Targets low-income customers
4. Accounts for Zambian challenges (power cuts, water issues, transport)
5. Includes realistic daily/monthly income projections
6. Addresses seasonal variations
7. Considers competition from similar businesses

Return as JSON:
{{
  "business_name": "Simple, descriptive name",
  "business_description": "2-3 sentences describing the business",
  "category": "{category_name}",
  "capital_breakdown": {{
    "stock_inventory": 0,
    "equipment_tools": 0,
    "licenses_permits": 0,
    "working_capital": 0,
    "marketing_setup": 0,
    "total": {capital}
  }},
  "location_specifics": "{location} - explain why this location works",
  "target_customers": "Specific demographic description",
  "daily_operations": "Typical day description",
  "revenue_model": {{
    "daily_sales_target": "K100-150",
    "monthly_revenue": "K3,000-4,500",
    "profit_margin": "20-30%",
    "breakeven_months": 3
  }},
  "success_factors": ["factor 1", "factor 2", "factor 3"],
  "risk_factors": ["risk 1", "risk 2"],
  "growth_path": "How to scale from K{capital} to K50,000+",
  "zambian_challenges": ["Challenge specific to Zambia"],
  "capital_usd": {capital/20},
  "year": {year},
  "informal_sector": true,
  "requires_credit": false,
  "startup_time_days": 7,
  "failure_risk": "Medium"
}}

Be SPECIFIC and REALISTIC. This is for real entrepreneurs with limited capital."""

        return prompt
    
    def generate_scenario(self, category_name, capital, location, year):
        """Generate one micro-business scenario"""
        if not self.client:
            print("⚠️  No API client available")
            return None
        
        category_info = {
            'name': category_name,
            'details': self.micro_categories[category_name]
        }
        
        prompt = self.generate_micro_business_prompt(category_info, capital, location, year)
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Clean JSON
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            scenario = json.loads(response_text.strip())
            return scenario
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def generate_batch(self, num_scenarios=100):
        """
        Generate batch of micro-business scenarios
        """
        print(f"\n{'='*70}")
        print(f"GENERATING MICRO-BUSINESS SCENARIOS: {num_scenarios}")
        print(f"{'='*70}\n")
        
        scenarios = []
        
        # Varied parameters for diversity
        locations = ['Lusaka', 'Kitwe', 'Ndola', 'Livingstone', 'Kabwe', 
                    'Chingola', 'Mufulira', 'Kasama', 'Chipata', 'Solwezi']
        years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
        
        categories = list(self.micro_categories.keys())
        
        for i in range(num_scenarios):
            # Random but weighted toward common categories
            category = np.random.choice(categories)
            capital_range = self.micro_categories[category]['capital_range']
            capital = np.random.randint(capital_range[0], capital_range[1])
            location = np.random.choice(locations)
            year = np.random.choice(years)
            
            print(f"[{i+1}/{num_scenarios}] Generating {category} business (K{capital:,}) in {location}...")
            
            scenario = self.generate_scenario(category, capital, location, year)
            
            if scenario:
                scenarios.append(scenario)
                print(f"   ✅ {scenario.get('business_name', 'Generated')}")
            else:
                print(f"   ❌ Failed")
            
            # Rate limiting
            import time
            time.sleep(1)
        
        if scenarios:
            df = pd.DataFrame(scenarios)
            
            Path('data/synthetic').mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'data/synthetic/micro_businesses_{timestamp}.csv'
            df.to_csv(output_file, index=False)
            
            print(f"\n✅ Saved {len(scenarios)} scenarios to {output_file}")
            
            # Summary
            print(f"\n📊 Capital Distribution:")
            print(f"   • K1,000-K5,000: {len(df[df['capital_breakdown'].apply(lambda x: json.loads(str(x))['total'] if isinstance(x, str) else x.get('total', 0)) < 5000])}")
            print(f"   • K5,000-K15,000: {len(df[(df['capital_breakdown'].apply(lambda x: json.loads(str(x))['total'] if isinstance(x, str) else x.get('total', 0)) >= 5000) & (df['capital_breakdown'].apply(lambda x: json.loads(str(x))['total'] if isinstance(x, str) else x.get('total', 0)) < 15000)])}")
            print(f"   • K15,000-K50,000: {len(df[df['capital_breakdown'].apply(lambda x: json.loads(str(x))['total'] if isinstance(x, str) else x.get('total', 0)) >= 15000])}")
            
            return df
        
        return None

def main():
    """
    Generate micro-business scenarios
    """
    print("\n" + "💰" * 35)
    print("MICRO-BUSINESS SCENARIO GENERATOR")
    print("💰" * 35)
    
    # Check for API key
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("\n❌ No ANTHROPIC_API_KEY found")
        print("   Add to .env: ANTHROPIC_API_KEY=your_key_here")
        return
    
    generator = MicroBusinessGenerator(api_key=api_key)
    
    print("\n📋 Micro-Business Categories:")
    for i, (cat, details) in enumerate(generator.micro_categories.items(), 1):
        capital_range = details['capital_range']
        print(f"   {i}. {cat}: K{capital_range[0]:,} - K{capital_range[1]:,}")
    
    print(f"\n💡 These categories represent actual Zambian informal sector businesses")
    print(f"   They will balance your dataset of large companies")
    
    print(f"\n📋 Generation Options:")
    print(f"   1. Small batch (50 scenarios) ~1 hour")
    print(f"   2. Medium batch (200 scenarios) ~3.5 hours")
    print(f"   3. Large batch (500 scenarios) ~8 hours")
    print(f"   4. Custom amount")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '1':
        num = 50
    elif choice == '2':
        num = 200
    elif choice == '3':
        num = 500
    elif choice == '4':
        num = int(input("How many scenarios? ").strip())
    else:
        print("Invalid choice")
        return
    
    print(f"\n⏱️  Estimated time: {num * 1.2 / 60:.1f} minutes")
    input("Press Enter to start...")
    
    df = generator.generate_batch(num)
    
    if df is not None:
        print(f"\n{'='*70}")
        print("GENERATION COMPLETE!")
        print(f"{'='*70}")
        
        print(f"\n📊 Dataset Balance:")
        print(f"   • Large businesses (existing): 4,852")
        print(f"   • Micro businesses (generated): {len(df)}")
        print(f"   • Total training data: {4852 + len(df):,}")
        
        print(f"\n📋 Next steps:")
        print(f"   1. Review generated scenarios")
        print(f"   2. Merge with main dataset")
        print(f"   3. Run market gap analysis")
        print(f"   4. Begin model training")
    
    print("\n")

if __name__ == "__main__":
    main()
