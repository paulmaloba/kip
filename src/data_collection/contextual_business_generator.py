"""
kip - Contextual Business Scenario Generator
Generates realistic business ideas based on market gaps and economic context
Week 2: Enhanced Synthetic Data
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️  Anthropic not installed. Install with: pip install anthropic")

class ContextualBusinessGenerator:
    """
    Generate business scenarios using real market intelligence
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        if ANTHROPIC_AVAILABLE and api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = None
        
        # Load data
        self.economic_data = None
        self.market_gaps = None
        self.sme_insights = None
        self.saturation_data = None
        
    def load_intelligence(self):
        """
        Load all market intelligence data
        """
        print("=" * 70)
        print("LOADING MARKET INTELLIGENCE")
        print("=" * 70 + "\n")
        
        try:
            # Economic data
            self.economic_data = pd.read_csv('data/processed/master_dataset.csv')
            print(f"✅ Economic data: {len(self.economic_data)} rows")
            
            # Market gaps
            if Path('data/processed/market_gaps.csv').exists():
                self.market_gaps = pd.read_csv('data/processed/market_gaps.csv')
                print(f"✅ Market gaps: {len(self.market_gaps)} opportunities")
            
            # SME insights
            if Path('data/processed/sme_sector_insights.csv').exists():
                self.sme_insights = pd.read_csv('data/processed/sme_sector_insights.csv')
                print(f"✅ SME insights: {len(self.sme_insights)} sectors")
            
            # Saturation data
            if Path('data/processed/category_saturation.csv').exists():
                self.saturation_data = pd.read_csv('data/processed/category_saturation.csv')
                print(f"✅ Saturation data: {len(self.saturation_data)} categories")
            
            print("\n✅ All intelligence loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading intelligence: {str(e)}")
            return False
    
    def create_context(self, year, location='Lusaka', area=None, sector=None):
        """
        Create comprehensive context for business generation
        """
        context = {
            'year': year,
            'location': location,
            'area': area or 'General',
            'sector': sector
        }
        
        # Get economic indicators for that year
        economic_year = self.economic_data[
            self.economic_data['year'] == year
        ]
        
        if not economic_year.empty:
            row = economic_year.iloc[0]
            context['gdp_growth'] = round(row['GDP_growth'], 2)
            context['inflation'] = round(row['Inflation'], 2)
            context['unemployment'] = round(row['Unemployment'], 2)
            if 'Copper_Price_USD' in row:
                context['copper_price'] = round(row['Copper_Price_USD'], 2)
            if 'ZMW_per_USD' in row:
                context['exchange_rate'] = round(row['ZMW_per_USD'], 2)
        
        # Get market gaps for location
        if self.market_gaps is not None:
            high_opportunity = self.market_gaps[
                self.market_gaps['opportunity_score'] > 0.7
            ]
            context['market_gaps'] = high_opportunity['category'].tolist()[:5]
        
        # Get sector insights
        if self.sme_insights is not None and sector:
            sector_info = self.sme_insights[
                self.sme_insights['sector'].str.contains(sector, case=False, na=False)
            ]
            if not sector_info.empty:
                context['sector_saturation'] = sector_info.iloc[0]['saturation_level']
                context['sector_innovation_rate'] = sector_info.iloc[0]['innovation_rate']
        
        return context
    
    def generate_prompt(self, context, budget_usd):
        """
        Generate detailed prompt for LLM
        """
        prompt = f"""Generate a realistic, data-driven business idea for Zambia.

MARKET INTELLIGENCE:
===================
Location: {context['location']}, {context['area']}
Year: {context['year']}

Economic Context:
- GDP Growth: {context.get('gdp_growth', 'N/A')}%
- Inflation: {context.get('inflation', 'N/A')}%
- Unemployment: {context.get('unemployment', 'N/A')}%
- Copper Price: ${context.get('copper_price', 'N/A')} (key Zambian commodity)
- Exchange Rate: {context.get('exchange_rate', 'N/A')} ZMW/USD

Market Gaps Identified (Underserved Categories):
{', '.join(context.get('market_gaps', ['Various opportunities']))}

Sector Context:
- Target Sector: {context.get('sector', 'Open')}
- Saturation Level: {context.get('sector_saturation', 'Medium')}
- Innovation Rate: {context.get('sector_innovation_rate', 40)}%

BUSINESS REQUIREMENTS:
=====================
- Startup Capital: ${budget_usd:,} USD
- Must address a specific market gap
- Must be realistic for {context['location']}
- Must consider economic conditions

CRITICAL SUCCESS FACTORS (from SME survey):
- 70% of SMEs fail within 3 years
- Only 7% of SMEs export (opportunity: 64% want to)
- 51% in manufacturing are in value chains
- Access to finance is #1 challenge
- 70% concerned about environmental changes

Generate a business idea that:
1. Fills a specific market gap from the list above
2. Is realistic for the budget and location
3. Has clear competitive advantage
4. Accounts for economic conditions
5. Addresses known SME challenges
6. Has specific target demographics
7. Has measurable success metrics

Return as JSON with these exact fields:
{{
  "business_name": "Creative, memorable name",
  "business_description": "2-3 sentence elevator pitch",
  "sector": "Primary sector classification",
  "subsector": "Specific niche",
  "capital_usd": {budget_usd},
  "location": "{context['location']}",
  "area": "{context['area']}",
  "market_gap_addressed": "Which gap from the list",
  "target_market": "Specific demographic and size",
  "competitive_advantage": "Why this works now in this location",
  "revenue_streams": ["List 2-3 main revenue sources"],
  "success_factors": ["List 3-5 critical success factors"],
  "risk_factors": ["List 2-3 main risks"],
  "economic_context_alignment": "How this fits current economic conditions",
  "expected_roi_months": 18,
  "breakeven_months": 12,
  "year": {context['year']},
  "success_probability": 0.65,
  "innovation_level": "Low/Medium/High",
  "export_potential": "None/Low/Medium/High",
  "sustainability_score": 0.7,
  "failure_risk": "Low/Medium/High"
}}

Be specific, realistic, and data-driven. This is for actual entrepreneurs."""

        return prompt
    
    def generate_scenario(self, context, budget_usd):
        """
        Generate one business scenario
        """
        if not self.client:
            print("⚠️  No Claude client available")
            return None
        
        prompt = self.generate_prompt(context, budget_usd)
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            response_text = message.content[0].text
            
            # Clean JSON if wrapped in markdown
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            scenario = json.loads(response_text.strip())
            return scenario
            
        except Exception as e:
            print(f"❌ Error generating scenario: {str(e)}")
            return None
    
    def generate_batch(self, num_scenarios=50, batch_name='batch_1'):
        """
        Generate multiple scenarios with variation
        """
        print(f"\n{'='*70}")
        print(f"GENERATING BATCH: {batch_name} ({num_scenarios} scenarios)")
        print(f"{'='*70}\n")
        
        scenarios = []
        
        # Vary parameters for diversity
        years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
        budgets = [1000, 2000, 3000, 5000, 7500, 10000, 15000, 20000, 30000, 50000]
        locations = ['Lusaka', 'Kitwe', 'Ndola', 'Livingstone']
        areas = ['CBD', 'Residential', 'Industrial', 'Suburban']
        sectors = ['Agri-food', 'Manufacturing', 'Services', 'Retail', 'Technology']
        
        for i in range(num_scenarios):
            print(f"Generating scenario {i+1}/{num_scenarios}...", end=" ")
            
            # Random combination
            year = np.random.choice(years)
            budget = np.random.choice(budgets)
            location = np.random.choice(locations)
            area = np.random.choice(areas)
            sector = np.random.choice(sectors)
            
            # Create context
            context = self.create_context(year, location, area, sector)
            
            # Generate
            scenario = self.generate_scenario(context, budget)
            
            if scenario:
                scenarios.append(scenario)
                print("✅")
            else:
                print("❌")
            
            # Rate limiting
            import time
            time.sleep(1)  # Be polite to API
        
        # Save batch
        if scenarios:
            df = pd.DataFrame(scenarios)
            
            Path('data/synthetic').mkdir(parents=True, exist_ok=True)
            output_file = f'data/synthetic/{batch_name}.csv'
            df.to_csv(output_file, index=False)
            
            print(f"\n✅ Saved {len(scenarios)} scenarios to {output_file}")
            return df
        else:
            print("\n❌ No scenarios generated")
            return None
    
    def generate_complete_dataset(self, total_scenarios=500):
        """
        Generate complete training dataset
        """
        print(f"\n{'='*70}")
        print(f"GENERATING COMPLETE DATASET: {total_scenarios} scenarios")
        print(f"{'='*70}\n")
        
        batch_size = 50
        num_batches = total_scenarios // batch_size
        
        all_scenarios = []
        
        for i in range(num_batches):
            batch_name = f'business_scenarios_batch_{i+1}'
            batch_df = self.generate_batch(batch_size, batch_name)
            
            if batch_df is not None:
                all_scenarios.append(batch_df)
            
            print(f"\nProgress: {len(all_scenarios) * batch_size}/{total_scenarios}\n")
        
        # Combine all batches
        if all_scenarios:
            combined = pd.concat(all_scenarios, ignore_index=True)
            
            output_file = 'data/synthetic/all_business_scenarios.csv'
            combined.to_csv(output_file, index=False)
            
            print(f"\n{'='*70}")
            print("GENERATION COMPLETE!")
            print(f"{'='*70}")
            print(f"\n✅ Total scenarios generated: {len(combined)}")
            print(f"✅ Saved to: {output_file}")
            
            # Show summary
            print(f"\n📊 Dataset Summary:")
            print(f"   • Sectors: {combined['sector'].nunique()}")
            print(f"   • Locations: {combined['location'].nunique()}")
            print(f"   • Budget range: ${combined['capital_usd'].min():,} - ${combined['capital_usd'].max():,}")
            print(f"   • Years: {combined['year'].min()} - {combined['year'].max()}")
            
            return combined
        
        return None

def main():
    """
    Generate contextual business scenarios
    """
    print("\n" + "🤖" * 35)
    print("CONTEXTUAL BUSINESS SCENARIO GENERATOR")
    print("🤖" * 35)
    
    # Get API key
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("\n❌ No ANTHROPIC_API_KEY found in .env file")
        print("   Add it: ANTHROPIC_API_KEY=your_key_here")
        return
    
    generator = ContextualBusinessGenerator(api_key=api_key)
    
    # Load intelligence
    if not generator.load_intelligence():
        print("\n❌ Failed to load market intelligence")
        print("   Make sure you've run:")
        print("   1. market_saturation_analyzer.py")
        print("   2. sme_survey_extractor.py")
        return
    
    # Generate dataset
    print("\n📋 Generation options:")
    print("   1. Test (generate 5 scenarios)")
    print("   2. Small batch (50 scenarios)")
    print("   3. Medium batch (100 scenarios)")
    print("   4. Full dataset (500 scenarios)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        generator.generate_batch(5, 'test_batch')
    elif choice == '2':
        generator.generate_batch(50, 'small_batch')
    elif choice == '3':
        generator.generate_complete_dataset(100)
    elif choice == '4':
        generator.generate_complete_dataset(500)
    else:
        print("Invalid choice")
        return
    
    print("\n📋 Next steps:")
    print("   1. Review generated scenarios")
    print("   2. Merge with economic data")
    print("   3. Begin model training (Week 4)")
    
    print("\n")

if __name__ == "__main__":
    main()
