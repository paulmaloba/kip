"""
Project Kwacha - Zambia Business Directory Scraper (FIXED)
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
        
        city_url = f"{self.base_url}/location/{city_name.lower()}"
        
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
                
                # Find business listings
                business_cards = soup.find_all('div', class_='company_header')
                
                if not business_cards:
                    print(f"   ℹ️  No businesses found on page {page}")
                    break
                
                for card in business_cards:
                    business = self.extract_business_info(card, city_name)
                    if business:
                        self.businesses.append(business)
                
                print(f"   ✅ Found {len(business_cards)} businesses (extracted {len([b for b in self.businesses if b.get('city') == city_name])} valid)")
                
                # Be polite - wait between requests
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                continue
        
        total = len([b for b in self.businesses if b.get('city') == city_name])
        print(f"\n✅ Total collected from {city_name}: {total}")

    def extract_business_info(self, card, city):
        """
        Extract business information from HTML card
        FIXED: Properly handles relative URLs and nested elements
        """
        try:
            # Get business name and URL
            h3_tag = card.find('h3')
            if not h3_tag:
                return None
            
            a_tag = h3_tag.find('a', href=True)
            if not a_tag:
                return None
            
            business_name = a_tag.text.strip()
            relative_url = a_tag['href']
            
            # Fix URL - prepend base URL if relative
            if relative_url.startswith('/'):
                business_url = f"{self.base_url}{relative_url}"
            else:
                business_url = relative_url
            
            # Get other basic info from card
            address_div = card.find('div', class_='address')
            address = address_div.text.strip() if address_div else None
            
            phone_div = card.find('div', class_='s')
            phone = phone_div.text.strip() if phone_div else None
            
            # Create basic business object
            business = {
                'name': business_name,
                'address': address,
                'phone': phone,
                'city': city,
                'url': business_url,
                'source': 'zambiayp.com',
                'category': None,  # Will try to get from detail page
                'email': None
            }
            
            # Try to get detailed info from business page (optional - slower)
            # Comment this out for faster scraping
            # business = self.enrich_business_details(business, business_url)
            
            return business
            
        except Exception as e:
            # Silently skip problematic businesses
            return None
    
    def enrich_business_details(self, business, detail_url):
        """
        Optional: Get additional details from business detail page
        WARNING: This makes scraping slower (one extra request per business)
        """
        try:
            response = requests.get(detail_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return business
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract categories
            categories_div = soup.find('div', class_='tags')
            if categories_div:
                category_links = categories_div.find_all('a')
                categories = [a.text.strip() for a in category_links]
                business['category'] = ', '.join(categories) if categories else None
            
            # Extract email if available
            email_link = soup.find('a', href=lambda href: href and 'mailto:' in href)
            if email_link:
                business['email'] = email_link['href'].replace('mailto:', '')
            
            return business
            
        except Exception as e:
            # If enrichment fails, return basic business info
            return business
    
    def scrape_category(self, category_name, city=None):
        """
        Scrape businesses by category (optional: filter by city)
        """
        print(f"\n{'='*70}")
        print(f"SCRAPING CATEGORY: {category_name.upper()}")
        print(f"{'='*70}")
        
        # Implement category-specific scraping if needed
        category_url = f"{self.base_url}/category/{category_name.lower()}"
        # Similar logic to scrape_city
        pass
    
    def save_data(self):
        """
        Save collected data to CSV
        """
        if not self.businesses:
            print("\n⚠️  No data to save!")
            return None
        
        df = pd.DataFrame(self.businesses)
        
        # Remove duplicates based on name and city
        df_unique = df.drop_duplicates(subset=['name', 'city'], keep='first')
        
        # Create output directory
        Path('data/raw').mkdir(parents=True, exist_ok=True)
        
        output_file = 'data/raw/zambiayp_businesses.csv'
        df_unique.to_csv(output_file, index=False)
        
        print(f"\n{'='*70}")
        print("SCRAPING COMPLETE")
        print(f"{'='*70}")
        print(f"\n✅ Saved {len(df_unique)} unique businesses to {output_file}")
        print(f"   (Removed {len(df) - len(df_unique)} duplicates)")
        
        # Summary statistics
        print(f"\n📊 Summary:")
        print(f"   • Total businesses: {len(df_unique)}")
        print(f"   • Cities: {df_unique['city'].nunique()}")
        
        print(f"\n🏙️  Businesses by city:")
        city_counts = df_unique['city'].value_counts()
        for city, count in city_counts.items():
            print(f"   • {city.title()}: {count}")
        
        if df_unique['category'].notna().any():
            print(f"\n🏢 Top 10 categories:")
            # Handle comma-separated categories
            all_categories = []
            for cats in df_unique['category'].dropna():
                if isinstance(cats, str):
                    all_categories.extend([c.strip() for c in cats.split(',')])
            
            if all_categories:
                from collections import Counter
                category_counts = Counter(all_categories)
                for cat, count in category_counts.most_common(10):
                    print(f"   • {cat}: {count}")
        
        return df_unique

def main():
    """
    Run business directory scraping
    """
    print("\n" + "🔍" * 35)
    print("ZAMBIA BUSINESS DIRECTORY SCRAPER")
    print("🔍" * 35)
    
    scraper = ZambiaBusinessScraper()
    
    print("\n📋 Scraping Options:")
    print("   1. Quick scrape (basic info only, fast)")
    print("   2. Detailed scrape (with categories, slow)")
    print("   3. Test run (1 page of Lusaka)")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '3':
        # Test run
        print("\n🧪 Running test scrape...")
        scraper.scrape_city('lusaka', max_pages=1)
        scraper.save_data()
        return
    
    # Full scraping
    cities = ['lusaka', 'kitwe', 'ndola', 'livingstone', 'kabwe']
    
    pages_per_city = 10
    print(f"\n📍 Will scrape {len(cities)} cities, {pages_per_city} pages each")
    print(f"   Estimated time: {len(cities) * pages_per_city * 3 / 60:.0f} minutes")
    
    input("\nPress Enter to start, or Ctrl+C to cancel...")
    
    # Scrape each city
    for i, city in enumerate(cities, 1):
        print(f"\n[{i}/{len(cities)}] Processing {city.title()}...")
        scraper.scrape_city(city, max_pages=pages_per_city)
        
        if i < len(cities):
            print(f"\n⏸️  Waiting 5 seconds before next city...")
            time.sleep(5)
    
    # Save data
    df = scraper.save_data()
    
    if df is not None:
        print("\n📋 Next steps:")
        print("   1. Review data/raw/zambiayp_businesses.csv")
        print("   2. Run market saturation analysis")
        print("   3. Identify market gaps")
    
    print("\n")

if __name__ == "__main__":
    print("\n⚠️  WEB SCRAPING GUIDELINES:")
    print("   • Be respectful of server resources")
    print("   • Use reasonable delays between requests")
    print("   • Check robots.txt compliance")
    print("   • Use data responsibly")
    print("\n   This scraper includes 2-5 second delays to be polite")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping cancelled by user")
        print("   Partial data may be available")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        print("   Check your internet connection and try again")
