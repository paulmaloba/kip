"""
Project Kwacha - SME Survey Data Extractor
Extracts structured insights from Zambia SME Survey Report
Week 2: Business Intelligence
"""

import pandas as pd
from pathlib import Path

class SMESurveyExtractor:
    """
    Extract and structure insights from SME survey
    """
    
    def __init__(self):
        self.sector_data = None
        self.challenges = None
        self.opportunities = None
        
    def extract_sector_insights(self):
        """
        Extract sector-specific competitiveness data
        Based on the PDF survey results
        """
        print("=" * 70)
        print("EXTRACTING SME SURVEY INSIGHTS")
        print("=" * 70 + "\n")
        
        # Agri-food sector
        agrifood = {
            'sector': 'Agri-food',
            'gdp_contribution': 6.7,
            'employment_pct': 50.0,
            'sample_size': 55,
            'sme_percentage': 90,
            'on_time_delivery': 74,
            'certification_rate': 55,
            'export_rate_direct': 16,
            'export_rate_indirect': 15,
            'export_interest': 64,
            'logistics_quality': 57,
            'value_chain_participation': 50,
            'innovation_rate': 35,
            'competitiveness_score': 62,
            'saturation_level': 'Medium',
            'key_challenges': 'Access to finance, export capacity, supplier dependency',
            'opportunities': 'Export market (64% interested), value addition, regional markets'
        }
        
        # Manufacturing sector
        manufacturing = {
            'sector': 'Manufacturing',
            'gdp_contribution': 7.5,
            'employment_pct': 30.0,
            'sample_size': 74,
            'sme_percentage': 78,
            'on_time_delivery': 70,
            'certification_rate': 40,
            'export_rate_direct': 11,
            'export_rate_indirect': 0,
            'export_interest': 50,
            'logistics_quality': 55,
            'value_chain_participation': 51,
            'innovation_rate': 48,
            'competitiveness_score': 65,
            'saturation_level': 'High',
            'key_challenges': 'Supplier dependency, technology adoption, market access',
            'opportunities': 'Value chains, innovation (48%), regional demand (COMESA/SADC)'
        }
        
        # Business support services
        services = {
            'sector': 'Business Support Services',
            'gdp_contribution': 52.2,
            'employment_pct': 21.0,
            'sample_size': 36,
            'sme_percentage': 98,
            'on_time_delivery': 75,
            'certification_rate': 30,
            'export_rate_direct': 3,
            'export_rate_indirect': 0,
            'export_interest': 40,
            'logistics_quality': 60,
            'value_chain_participation': 70,
            'innovation_rate': 30,
            'competitiveness_score': 58,
            'saturation_level': 'Medium-High',
            'key_challenges': 'Limited export capacity, technology gaps, skill shortages',
            'opportunities': 'ICT growth, tourism expansion, professional services demand'
        }
        
        self.sector_data = pd.DataFrame([agrifood, manufacturing, services])
        
        print("📊 Sector Insights Extracted:\n")
        print(self.sector_data[['sector', 'gdp_contribution', 'innovation_rate', 
                                 'export_interest', 'saturation_level']])
        
        return self.sector_data
    
    def extract_challenges(self):
        """
        Extract major challenges SMEs face
        """
        challenges = [
            {
                'challenge': 'Access to Finance',
                'severity': 'Critical',
                'affected_sectors': 'All',
                'percentage_affected': 95,
                'description': 'Difficulty obtaining credit and low-interest loans'
            },
            {
                'challenge': 'Export Capacity',
                'severity': 'High',
                'affected_sectors': 'Agri-food, Manufacturing',
                'percentage_affected': 93,
                'description': 'Only 7% of SMEs export, 64% interested but lack capacity'
            },
            {
                'challenge': 'Environmental Changes',
                'severity': 'High',
                'affected_sectors': 'Agri-food',
                'percentage_affected': 70,
                'description': 'Climate change affecting 70% of SMEs, especially agri-food'
            },
            {
                'challenge': 'Supplier Dependency',
                'severity': 'Medium-High',
                'affected_sectors': 'Manufacturing',
                'percentage_affected': 69,
                'description': '69% of manufacturers outside value chains rely on single supplier'
            },
            {
                'challenge': 'Technology Adoption',
                'severity': 'Medium',
                'affected_sectors': 'All',
                'percentage_affected': 60,
                'description': 'Limited ICT infrastructure and digital literacy'
            },
            {
                'challenge': 'Skills Shortage',
                'severity': 'Medium',
                'affected_sectors': 'Services, Manufacturing',
                'percentage_affected': 47,
                'description': 'Skills mismatch in technical and business services'
            }
        ]
        
        self.challenges = pd.DataFrame(challenges)
        
        print("\n⚠️  Key Challenges:\n")
        print(self.challenges[['challenge', 'severity', 'percentage_affected']])
        
        return self.challenges
    
    def extract_opportunities(self):
        """
        Extract market opportunities identified in survey
        """
        opportunities = [
            {
                'opportunity': 'Export Market Development',
                'potential': 'Very High',
                'readiness': 'Medium',
                'target_sectors': 'Agri-food, Manufacturing',
                'market_size': 'Regional (COMESA, SADC)',
                'description': '64% agri-food firms want to export, regional markets accessible',
                'enablers': 'Certification support, logistics improvement, market linkages'
            },
            {
                'opportunity': 'Value Chain Integration',
                'potential': 'High',
                'readiness': 'High',
                'target_sectors': 'Manufacturing, Services',
                'market_size': 'National + Regional',
                'description': '51% manufacturers in value chains, reduces supplier dependency',
                'enablers': 'Supplier directories, contract farming, digital platforms'
            },
            {
                'opportunity': 'Sustainability Services',
                'potential': 'High',
                'readiness': 'Medium',
                'target_sectors': 'All',
                'market_size': 'Growing',
                'description': '53% investing in environmental mitigation, demand growing',
                'enablers': 'Green financing, sustainability standards, tech solutions'
            },
            {
                'opportunity': 'Innovation & Product Development',
                'potential': 'High',
                'readiness': 'Medium-High',
                'target_sectors': 'Manufacturing',
                'market_size': 'National',
                'description': '48% innovating, textile/garment at 72%',
                'enablers': 'R&D support, patent assistance, market research'
            },
            {
                'opportunity': 'Digital Services',
                'potential': 'Very High',
                'readiness': 'Medium',
                'target_sectors': 'Services',
                'market_size': 'National + International',
                'description': '52% with quality internet, ICT hub positioning',
                'enablers': 'Digital infrastructure, skills training, online platforms'
            },
            {
                'opportunity': 'Premium/Middle-Class Services',
                'potential': 'High',
                'readiness': 'High',
                'target_sectors': 'Services, Retail',
                'market_size': 'Urban, Growing',
                'description': 'Expanding middle class driving demand for quality services',
                'enablers': 'Quality standards, branding, location strategy'
            }
        ]
        
        self.opportunities = pd.DataFrame(opportunities)
        
        print("\n🎯 Market Opportunities:\n")
        print(self.opportunities[['opportunity', 'potential', 'target_sectors']])
        
        return self.opportunities
    
    def create_competitiveness_matrix(self):
        """
        Create competitiveness scoring matrix by sector and firm size
        Based on survey competitiveness grids
        """
        # Simplified from the detailed grids in the survey
        matrix_data = [
            # Agri-food
            {'sector': 'Agri-food', 'firm_size': 'Micro-Small', 'capability_score': 46, 'ecosystem_score': 58},
            {'sector': 'Agri-food', 'firm_size': 'Medium', 'capability_score': 55, 'ecosystem_score': 66},
            {'sector': 'Agri-food', 'firm_size': 'Large', 'capability_score': 63, 'ecosystem_score': 74},
            
            # Manufacturing
            {'sector': 'Manufacturing', 'firm_size': 'Micro-Small', 'capability_score': 51, 'ecosystem_score': 56},
            {'sector': 'Manufacturing', 'firm_size': 'Medium', 'capability_score': 63, 'ecosystem_score': 62},
            {'sector': 'Manufacturing', 'firm_size': 'Large', 'capability_score': 73, 'ecosystem_score': 78},
            
            # Services
            {'sector': 'Business Services', 'firm_size': 'Micro-Small', 'capability_score': 48, 'ecosystem_score': 54},
            {'sector': 'Business Services', 'firm_size': 'Medium', 'capability_score': 57, 'ecosystem_score': 51},
            {'sector': 'Business Services', 'firm_size': 'Large', 'capability_score': 71, 'ecosystem_score': 70},
        ]
        
        competitiveness_matrix = pd.DataFrame(matrix_data)
        
        print("\n📈 Competitiveness Matrix:\n")
        print(competitiveness_matrix)
        
        return competitiveness_matrix
    
    def save_all_data(self):
        """
        Save all extracted data
        """
        Path('data/processed').mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*70}")
        print("SAVING EXTRACTED DATA")
        print(f"{'='*70}\n")
        
        # Save sector insights
        if self.sector_data is not None:
            self.sector_data.to_csv('data/processed/sme_sector_insights.csv', index=False)
            print("✅ Saved: sme_sector_insights.csv")
        
        # Save challenges
        if self.challenges is not None:
            self.challenges.to_csv('data/processed/sme_challenges.csv', index=False)
            print("✅ Saved: sme_challenges.csv")
        
        # Save opportunities
        if self.opportunities is not None:
            self.opportunities.to_csv('data/processed/sme_opportunities.csv', index=False)
            print("✅ Saved: sme_opportunities.csv")
        
        # Create summary JSON for easy loading
        summary = {
            'survey_metadata': {
                'year': 2018,
                'total_firms': 242,
                'provinces': ['Lusaka', 'Copperbelt', 'Central'],
                'sme_percentage': 88,
                'exporter_percentage': 7,
                'importer_percentage': 43
            },
            'key_findings': {
                'sme_failure_rate': 70,  # Within 3 years (implied from doc)
                'gdp_contribution': 70,
                'employment_contribution': 88,
                'business_percentage': 97
            }
        }
        
        import json
        with open('data/processed/sme_survey_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        print("✅ Saved: sme_survey_summary.json")

def main():
    """
    Extract all SME survey data
    """
    print("\n" + "📋" * 35)
    print("SME SURVEY DATA EXTRACTOR")
    print("📋" * 35)
    
    extractor = SMESurveyExtractor()
    
    # Extract all data
    extractor.extract_sector_insights()
    extractor.extract_challenges()
    extractor.extract_opportunities()
    competitiveness = extractor.create_competitiveness_matrix()
    
    # Save everything
    extractor.save_all_data()
    
    # Save competitiveness matrix
    competitiveness.to_csv('data/processed/competitiveness_matrix.csv', index=False)
    print("✅ Saved: competitiveness_matrix.csv")
    
    print(f"\n{'='*70}")
    print("EXTRACTION COMPLETE!")
    print(f"{'='*70}")
    
    print("\n📁 Generated files:")
    print("   • sme_sector_insights.csv")
    print("   • sme_challenges.csv")
    print("   • sme_opportunities.csv")
    print("   • competitiveness_matrix.csv")
    print("   • sme_survey_summary.json")
    
    print("\n💡 Use these insights to:")
    print("   1. Inform business idea generation")
    print("   2. Identify sector-specific opportunities")
    print("   3. Understand SME challenges")
    print("   4. Tailor recommendations by firm size")
    
    print("\n")

if __name__ == "__main__":
    main()
