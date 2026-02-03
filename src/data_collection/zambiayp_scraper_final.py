"""
Project Kwacha - Zambia Business Directory Scraper (FINAL FIX)
Fixed: Doesn't count businesses from previous runs as duplicates
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
    Scrapes business listings from zambiayp.com
    """
    
    def __init__(self):
        self.base_url = "https://www.zambiayp.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.businesses = []
        self.seen_businesses = set()  # Only for THIS scraping session
        
    def scrape_city(self, city_name, max_pages=380):
        """
        Scrape all businesses in a specific city
        """
        print(f"\n{'='*70}")
        print(f"SCRAPING: {city_name.upper()}")
        print(f"{'='*70}")
        
        # Try different URL patterns
        url_patterns = [
            f"{self.base_url}/location/{city_name.lower()}",
            f"{self.base_url}/browse-business-cities/{city_name.lower()}",
        ]
        
        successful_pattern = None
        
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
        
        page = 1
        consecutive_duplicates_within_page = 0
        
        while page <= max_pages:
            print(f"\n📄 Page {page}/{max_pages}...")
            
            # Build URL
            if page == 1:
                url = successful_pattern
            else:
                url = f"{successful_pattern}/{page}"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"   ⚠️  Status {response.status_code} - stopping")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                business_cards = soup.find_all('div', class_='company_header')
                
                if not business_cards:
                    print(f"   ℹ️  No businesses found - end of results")
                    break
                
                new_businesses = 0
                page_hashes = set()  # Track within this page only
                
                for card in business_cards:
                    business = self.extract_business_info(card, city_name)
                    if business:
                        business_hash = self.get_business_hash(business)
                        
                        # Check if we've seen this business IN THIS SCRAPING SESSION
                        if business_hash not in self.seen_businesses:
                            self.businesses.append(business)
                            self.seen_businesses.add(business_hash)
                            page_hashes.add(business_hash)
                            new_businesses += 1
                
                duplicates_within_page = len(business_cards) - new_businesses
                print(f"   Found {len(business_cards)} listings: {new_businesses} new, {duplicates_within_page} duplicates")
                
                # If ALL businesses on this page are duplicates (pagination returning same page)
                if new_businesses == 0:
                    consecutive_duplicates_within_page += 1
                    if consecutive_duplicates_within_page >= 2:
                        print(f"\n   ⚠️  Pagination not working - getting same page repeatedly")
                        print(f"   Stopping here")
                        break
                else:
                    consecutive_duplicates_within_page = 0
                
                page += 1
                time.sleep(2)  # Be polite
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                break
        
        city_total = len([b for b in self.businesses if b.get('city') == city_name])
        print(f"\n✅ Total unique businesses from {city_name}: {city_total}")
    
    def get_business_hash(self, business):
        """
        Create unique hash for a business
        """
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
            business_url = f"{self.base_url}{relative_url}" if relative_url.startswith('/') else relative_url
            
            # Get address
            address_div = card.find('div', class_='address')
            address = address_div.text.strip() if address_div else None
            
            # Get phone
            phone = None
            phone_icon = card.find('i', class_='fa-phone')
            if phone_icon:
                phone_parent = phone_icon.find_parent()
                if phone_parent:
                    phone_span = phone_parent.find('span')
                    phone = phone_span.text.strip() if phone_span else None
            
            # Get category if available
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
    
    def save_data(self, merge_with_existing=False):
        """
        Save collected data to CSV
        """
        if not self.businesses:
            print("\n⚠️  No data to save!")
            return None
        
        df_new = pd.DataFrame(self.businesses)
        
        # Check if we should merge with existing data
        output_file = Path('data/raw/zambiayp_businesses.csv')
        
        if merge_with_existing and output_file.exists():
            print("\n📊 Merging with existing data...")
            df_old = pd.read_csv(output_file)
            print(f"   • Old data: {len(df_old)} businesses")
            print(f"   • New data: {len(df_new)} businesses")
            
            # Combine and remove duplicates
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
            df_final = df_combined.drop_duplicates(subset=['name', 'city', 'address'], keep='first')
            
            print(f"   • Combined: {len(df_final)} unique businesses")
            print(f"   • Removed: {len(df_combined) - len(df_final)} duplicates")
        else:
            df_final = df_new
        
        # Save
        Path('data/raw').mkdir(parents=True, exist_ok=True)
        df_final.to_csv(output_file, index=False)
        
        print(f"\n{'='*70}")
        print("SCRAPING COMPLETE")
        print(f"{'='*70}")
        print(f"\n✅ Saved {len(df_final)} businesses to {output_file}")
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   • Total businesses: {len(df_final)}")
        print(f"   • Cities: {df_final['city'].nunique()}")
        
        if 'city' in df_final.columns:
            print(f"\n🏙️  Businesses by city:")
            for city, count in df_final['city'].value_counts().items():
                print(f"   • {city.title()}: {count}")
        
        if 'category' in df_final.columns and df_final['category'].notna().any():
            print(f"\n🏢 Top 10 categories:")
            for cat, count in df_final['category'].value_counts().head(10).items():
                print(f"   • {cat}: {count}")
        
        # Data quality
        print(f"\n📋 Data Quality:")
        print(f"   • With phone: {df_final['phone'].notna().sum()} ({df_final['phone'].notna().sum()/len(df_final)*100:.1f}%)")
        print(f"   • With address: {df_final['address'].notna().sum()} ({df_final['address'].notna().sum()/len(df_final)*100:.1f}%)")
        if 'category' in df_final.columns:
            print(f"   • With category: {df_final['category'].notna().sum()} ({df_final['category'].notna().sum()/len(df_final)*100:.1f}%)")
        
        return df_final

def main():
    """
    Run business directory scraping
    """
    print("\n" + "🔍" * 35)
    print("ZAMBIA BUSINESS DIRECTORY SCRAPER (FINAL)")
    print("🔍" * 35)
    
    scraper = ZambiaBusinessScraper()
    
    print("\n📋 Scraping Options:")
    print("   1. Fresh scrape (replace existing data)")
    print("   2. Add to existing data (merge)")
    print("   3. Test - Lusaka only, 5 pages")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    merge_existing = False
    
    if choice == '3':
        # Test
        print("\n🧪 Test run: Lusaka, 5 pages")
        scraper.scrape_city('lusaka', max_pages=5)
        
    elif choice == '2':
        # Merge mode
        merge_existing = True
        cities = ['lusaka', 'kitwe', 'ndola', 'livingstone', 'kabwe']
        
        print(f"\n📍 Will scrape {len(cities)} cities and MERGE with existing data")
        input("Press Enter to start...")
        
        for i, city in enumerate(cities, 1):
            print(f"\n[{i}/{len(cities)}] Processing {city.title()}...")
            scraper.scrape_city(city, max_pages=50)
            if i < len(cities):
                time.sleep(5)
                
    else:
        # Fresh scrape
        cities = ['chambeshi', 'chadiza', 'chama',
                  'chibombo', 'chiengi', 'chilubi', 'chingola', 'chipata', 'chinsali', 'chembe',
                  'chavuma', 'chilanga', 'chisamba', 'choma', 'chirundu', 'gwembe', 'isoka',
                  'kabwe', 'kafue', 'kalabo', 'kalomo', 'kalulushi', 'kitwe', 'chililabombwe', 'kaoma', 'kapiri mposhi',
                  'kasama', 'kasempa', 'katete','kawambwa', 'kazembe', 'kazungula', 'livingstone',
                  'luangwa', 'lukulu', 'luanshya', 'lukulu', 'lundazi', 'lusaka', 'makeni', 'mansa', 'mazabuka',
                  'mbala', 'mbereshi', 'mfuwe', 'milenge', 'mkushi', 'mongu', 'monze', 'mpika', 'mporokoso',
                  'mpulungu', 'mufulira', 'mumbwa', 'muyombe', 'mwinilunga', 'nakonde', 'nchelenge', 'ndola',
                  'nseluka', 'pemba', 'petauke', 'samfya', 'senanga', 'serenje', 'sesheke', 'siavonga',
                  'sinazongwe', 'solwezi', 'zambezi', 'zimba']
        
        print(f"\n📍 Will scrape {len(cities)} cities (FRESH - replaces existing)")
        input("Press Enter to start...")
        
        for i, city in enumerate(cities, 1):
            print(f"\n[{i}/{len(cities)}] Processing {city.title()}...")
            scraper.scrape_city(city, max_pages=50)
            if i < len(cities):
                time.sleep(5)
    
    # Save
    df = scraper.save_data(merge_with_existing=merge_existing)
    
    if df is not None:
        print("\n📋 Next steps:")
        print("   1. Review data/raw/zambiayp_businesses.csv")
        print("   2. Run: python src/data_processing/market_saturation_analyzer_fixed.py")
        print("   3. Run: python src/data_processing/sme_survey_extractor.py")
    
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
