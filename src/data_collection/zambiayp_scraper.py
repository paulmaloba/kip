"""
kip - Zambia Business Directory Scraper
Scrapes businesses from zambiayp.com by city and category
Week 2: Enhanced Data Collection
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from pathlib import Path
import json

class ZambiaBusinessScraper:
    """
    Scrapes business listings from zambiayp.com
    """
    
    def __init__(self):
        self.base_url = "https://www.zambiayp.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.businesses = []
        
    def scrape_city(self, city_name, max_pages=5):
        """
        Scrape all businesses in a specific city
        """
        print(f"\n{'='*70}")
        print(f"SCRAPING: {city_name.upper()}")
        print(f"{'='*70}")
        
        city_url = f"{self.base_url}/browse-business-cities/{city_name.lower()}"
        
        for page in range(1, max_pages + 1):
            print(f"\n📄 Page {page}/{max_pages}...")
            
            try:
                # Add page parameter
                url = f"{city_url}?page={page}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"   ⚠️  Status code: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find business listings (adjust selectors based on actual HTML)
                # This is a template - you'll need to inspect the actual page
                business_cards = soup.find_all('div', class_='company_header')  # Example selector
                
                if not business_cards:
                    print(f"   ℹ️  No businesses found on page {page}")
                    break
                
                for card in business_cards:
                    business = self.extract_business_info(card, city_name)
                    if business:
                        self.businesses.append(business)
                
                print(f"   ✅ Found {len(business_cards)} businesses")
                
                # Be polite - wait between requests
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                continue
        
        print(f"\n✅ Total collected from {city_name}: {len([b for b in self.businesses if b['city'] == city_name])}")
    
    def extract_business_info(self, card, city):
        """
        Extract business information from HTML card
        Adjust selectors based on actual website structure
        """
        try:
            business = {
                'name': card.find('h3').find('a', href=True).text.strip() if card.find('h3') else None,
                'category': card.find('span', class_='category').text.strip() if card.find('span', class_='category') else None,
                'address': card.find('div', class_='address').text.strip() if card.find('div', class_='address') else None,
                'phone': card.find('div', class_='s').text.strip() if card.find('div', class_='s') else None,
                'email': card.find('a', class_='email').text.strip() if card.find('a', class_='email') else None,
                'city': city,
                'url': card.find('a', href=True)['href'] if card.find('a', href=True) else None,
                'source': 'zambiayp.com'
            }
            
            return business if business['name'] else None
            
        except Exception as e:
            print(f"   ⚠️  Error extracting business: {str(e)}")
            return None
    
    def scrape_category(self, category_name, city=None):
        """
        Scrape businesses by category (optional: filter by city)
        """
        print(f"\n{'='*70}")
        print(f"SCRAPING CATEGORY: {category_name.upper()}")
        print(f"{'='*70}")
        
        # Implement category-specific scraping
        # URL pattern might be: /browse-business-category/{category}
        pass
    
    def save_data(self):
        """
        Save collected data to CSV
        """
        if not self.businesses:
            print("\n⚠️  No data to save!")
            return
        
        df = pd.DataFrame(self.businesses)
        
        # Create output directory
        Path('data/raw').mkdir(parents=True, exist_ok=True)
        
        output_file = 'data/raw/zambiayp_businesses.csv'
        df.to_csv(output_file, index=False)
        
        print(f"\n{'='*70}")
        print("SCRAPING COMPLETE")
        print(f"{'='*70}")
        print(f"\n✅ Saved {len(df)} businesses to {output_file}")
        
        # Summary statistics
        print(f"\n📊 Summary:")
        print(f"   • Cities: {df['city'].nunique()}")
        print(f"   • Categories: {df['category'].nunique()}")
        print(f"\n🏙️  Businesses by city:")
        print(df['city'].value_counts())
        print(f"\n🏢 Top 10 categories:")
        print(df['category'].value_counts().head(10))
        
        return df

def main():
    """
    Run business directory scraping
    """
    print("\n" + "🔍" * 35)
    print("ZAMBIA BUSINESS DIRECTORY SCRAPER")
    print("🔍" * 35)
    
    scraper = ZambiaBusinessScraper()
    
    # Target cities (based on SME survey)
    cities = [
        'lusaka',
        'kitwe',
        'ndola',
        'livingstone',
        'kabwe'
    ]
    
    # Scrape each city
    for city in cities:
        scraper.scrape_city(city, max_pages=10)
        time.sleep(3)  # Wait between cities
    
    # Save data
    df = scraper.save_data()
    
    print("\n📋 Next steps:")
    print("   1. Review data/raw/zambiayp_businesses.csv")
    print("   2. Run market saturation analysis")
    print("   3. Identify market gaps")
    
    print("\n")

if __name__ == "__main__":
    # IMPORTANT NOTE:
    # This is a TEMPLATE scraper. You need to:
    # 1. Inspect zambiayp.com HTML structure
    # 2. Update CSS selectors in extract_business_info()
    # 3. Test with one city first
    # 4. Respect robots.txt and rate limits
    
    print("\n⚠️  BEFORE RUNNING:")
    print("   1. Inspect zambiayp.com with browser DevTools")
    print("   2. Update CSS selectors in extract_business_info()")
    print("   3. Test with small sample first")
    print("   4. Check site's robots.txt")
    print("\n   Ready to proceed? (Press Ctrl+C to cancel)")
    
    input("\nPress Enter to continue...")
    
    main()
