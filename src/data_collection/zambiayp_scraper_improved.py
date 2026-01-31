"""
Project Kwacha - Zambia Business Directory Scraper (IMPROVED)
Better pagination handling and duplicate detection
Week 2: Enhanced Data Collection
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from pathlib import Path
import hashlib

class ZambiaBusinessScraper:
    """
    Scrapes business listings from zambiayp.com with improved pagination
    """
    
    def __init__(self):
        self.base_url = "https://www.zambiayp.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.businesses = []
        self.seen_businesses = set()  # Track duplicates in real-time
        
    def scrape_city(self, city_name, max_pages=20):
        """
        Scrape all businesses in a specific city with smart duplicate detection
        """
        print(f"\n{'='*70}")
        print(f"SCRAPING: {city_name.upper()}")
        print(f"{'='*70}")
        
        # Try different URL patterns that zambiayp might use
        url_patterns = [
            f"{self.base_url}/location/{city_name.lower()}",
            f"{self.base_url}/browse-business-cities/{city_name.lower()}",
            f"{self.base_url}/city/{city_name.lower()}"
        ]
        
        successful_pattern = None
        
        # Find which URL pattern works
        for pattern in url_patterns:
            try:
                response = requests.get(pattern, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    cards = soup.find_all('div', class_='company_header')
                    if cards:
                        successful_pattern = pattern
                        print(f"✅ Found working URL pattern: {pattern}")
                        break
            except:
                continue
        
        if not successful_pattern:
            print(f"❌ Could not find businesses for {city_name}")
            return
        
        consecutive_duplicates = 0
        page = 1
        
        while page <= max_pages:
            print(f"\n📄 Page {page}/{max_pages}...")
            
            try:
                # Try different pagination patterns
                url_variations = [
                    f"{successful_pattern}?page={page}",
                    f"{successful_pattern}/page/{page}",
                    f"{successful_pattern}?p={page}"
                ]
                
                response = None
                for url in url_variations:
                    try:
                        r = requests.get(url, headers=self.headers, timeout=10)
                        if r.status_code == 200:
                            response = r
                            break
                    except:
                        continue
                
                if not response or response.status_code != 200:
                    print(f"   ⚠️  Could not load page {page}")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                business_cards = soup.find_all('div', class_='company_header')
                
                if not business_cards:
                    print(f"   ℹ️  No businesses found on page {page} - end of results")
                    break
                
                new_businesses = 0
                for card in business_cards:
                    business = self.extract_business_info(card, city_name)
                    if business:
                        # Create unique hash for this business
                        business_hash = self.get_business_hash(business)
                        
                        if business_hash not in self.seen_businesses:
                            self.businesses.append(business)
                            self.seen_businesses.add(business_hash)
                            new_businesses += 1
                
                print(f"   Found {len(business_cards)} listings, {new_businesses} new, {len(business_cards)-new_businesses} duplicates")
                
                # Stop if we're getting all duplicates (pagination not working)
                if new_businesses == 0:
                    consecutive_duplicates += 1
                    if consecutive_duplicates >= 2:
                        print(f"\n   ⚠️  Getting only duplicates for {consecutive_duplicates} consecutive pages")
                        print(f"   Pagination may not be working - stopping here")
                        break
                else:
                    consecutive_duplicates = 0
                
                page += 1
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Error on page {page}: {str(e)}")
                break
        
        city_total = len([b for b in self.businesses if b.get('city') == city_name])
        print(f"\n✅ Total unique businesses from {city_name}: {city_total}")
    
    def get_business_hash(self, business):
        """
        Create unique hash for a business to detect duplicates
        """
        # Use name + city + address to create unique identifier
        unique_string = f"{business.get('name', '')}_{business.get('city', '')}_{business.get('address', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def extract_business_info(self, card, city):
        """
        Extract business information from HTML card
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
            
            # Fix URL
            if relative_url.startswith('/'):
                business_url = f"{self.base_url}{relative_url}"
            else:
                business_url = relative_url
            
            # Get other info
            address_div = card.find('div', class_='address')
            address = address_div.text.strip() if address_div else None
            
            phone_div = card.find('div', class_='s')
            phone = phone_div.text.strip() if phone_div else None
            
            # Look for category in the card itself
            category = None
            category_span = card.find('span', class_='category')
            if category_span:
                category = category_span.text.strip()
            
            business = {
                'name': business_name,
                'address': address,
                'phone': phone,
                'category': category,
                'city': city,
                'url': business_url,
                'source': 'zambiayp.com'
            }
            
            return business
            
        except Exception as e:
            return None
    
    def scrape_all_listings(self):
        """
        Alternative: Scrape the main business directory without city filter
        This might get more businesses
        """
        print(f"\n{'='*70}")
        print("SCRAPING ALL BUSINESSES (NO CITY FILTER)")
        print(f"{'='*70}")
        
        base_url = f"{self.base_url}/companies"
        
        for page in range(1, 50):  # Try up to 50 pages
            print(f"\n📄 Page {page}...")
            
            try:
                url = f"{base_url}?page={page}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"   Status {response.status_code} - stopping")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                cards = soup.find_all('div', class_='company_header')
                
                if not cards:
                    print(f"   No more businesses found")
                    break
                
                new_count = 0
                for card in cards:
                    business = self.extract_business_info(card, 'Unknown')
                    if business:
                        biz_hash = self.get_business_hash(business)
                        if biz_hash not in self.seen_businesses:
                            self.businesses.append(business)
                            self.seen_businesses.add(biz_hash)
                            new_count += 1
                
                print(f"   Found {len(cards)} listings, {new_count} new")
                
                if new_count == 0:
                    print(f"   All duplicates - stopping")
                    break
                
                time.sleep(2)
                
            except Exception as e:
                print(f"   Error: {str(e)}")
                break
        
        print(f"\n✅ Total businesses: {len(self.businesses)}")
    
    def save_data(self):
        """
        Save collected data to CSV
        """
        if not self.businesses:
            print("\n⚠️  No data to save!")
            return None
        
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
        print(f"   • Total businesses: {len(df)}")
        print(f"   • Cities: {df['city'].nunique()}")
        
        if 'city' in df.columns:
            print(f"\n🏙️  Businesses by city:")
            city_counts = df['city'].value_counts()
            for city, count in city_counts.items():
                print(f"   • {city.title()}: {count}")
        
        if 'category' in df.columns and df['category'].notna().any():
            print(f"\n🏢 Top 15 categories:")
            cat_counts = df['category'].value_counts().head(15)
            for cat, count in cat_counts.items():
                print(f"   • {cat}: {count}")
        
        # Data quality report
        print(f"\n📋 Data Quality:")
        print(f"   • With phone: {df['phone'].notna().sum()} ({df['phone'].notna().sum()/len(df)*100:.1f}%)")
        print(f"   • With address: {df['address'].notna().sum()} ({df['address'].notna().sum()/len(df)*100:.1f}%)")
        print(f"   • With category: {df['category'].notna().sum()} ({df['category'].notna().sum()/len(df)*100:.1f}%)")
        
        return df

def main():
    """
    Run business directory scraping
    """
    print("\n" + "🔍" * 35)
    print("ZAMBIA BUSINESS DIRECTORY SCRAPER (IMPROVED)")
    print("🔍" * 35)
    
    scraper = ZambiaBusinessScraper()
    
    print("\n📋 Scraping Options:")
    print("   1. By city (Lusaka, Kitwe, Ndola, Livingstone, Kabwe)")
    print("   2. All businesses (no city filter)")
    print("   3. Test - Single city, 3 pages")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '3':
        # Test
        print("\n🧪 Test run: Lusaka, 3 pages")
        scraper.scrape_city('lusaka', max_pages=3)
        
    elif choice == '2':
        # All businesses
        scraper.scrape_all_listings()
        
    else:
        # By city
        cities = ['lusaka', 'kitwe', 'ndola', 'livingstone', 'kabwe']
        
        print(f"\n📍 Will scrape {len(cities)} cities")
        input("Press Enter to start...")
        
        for i, city in enumerate(cities, 1):
            print(f"\n[{i}/{len(cities)}] Processing {city.title()}...")
            scraper.scrape_city(city, max_pages=20)
            
            if i < len(cities):
                time.sleep(5)
    
    # Save
    df = scraper.save_data()
    
    if df is not None:
        print("\n📋 Next steps:")
        print("   1. Review data/raw/zambiayp_businesses.csv")
        print("   2. If count is still low, try option 2 (all businesses)")
        print("   3. Run market saturation analysis")
    
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
