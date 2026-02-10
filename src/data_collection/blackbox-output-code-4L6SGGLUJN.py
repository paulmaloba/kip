import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path

class DataZambia_scraper:
    def __init__(self):
        self.base_url = "https://datazambia.com/explore"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.provinces = []  # Initialize list to store province data

    def scrap_province(self):
        province_url = self.base_url
        try:
            response = requests.get(province_url, headers=self.headers, timeout=10)
            print(f"Status Code: {response.status_code}")  # Debug
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                province_cards = soup.find_all('div', class_="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-all duration-300 cursor-pointer")
                
                if province_cards:
                    print("Url Working - Found province cards")
                else:
                    print("No province cards found. Check HTML structure.")
                    return  # Exit early if no cards
                
                for province in province_cards:
                    province_data = self.extract_prov_info(province)
                    if province_data:
                        self.provinces.append(province_data)
                    time.sleep(1)  # Polite delay to avoid rate-limiting
            else:
                print(f"Failed to fetch page: {response.status_code}")
        except Exception as e:
            print(f"Error during scraping: {e}")

    def extract_prov_info(self, province):
        try:
            # Extract province name
            h2_tag = province.find('h2', class_="text-2x1 font-bold")
            province_name = h2_tag.text.strip() if h2_tag else None
            
            # Extract population and capital city (assuming <p> has two <span> elements)
            population_tag = province.find('p', class_="flex items-center")
            if population_tag:
                spans = population_tag.find_all('span')
                if len(spans) >= 2:
                    population = spans[0].text.strip() if spans[0] else None
                    capital_city = spans[1].text.strip() if spans[1] else None
                else:
                    population = None
                    capital_city = None
            else:
                population = None
                capital_city = None
            
            # Extract key industries
            industry_tag = province.find('span', class_="inline-block bg-blue-100 dark:bg-blue-800 dark:text-blue-100 text-xs px-2 py-1 rounded")
            industries = industry_tag.text.strip() if industry_tag else None
            
            # Extract key exports
            exports_tag = province.find('span', class_="inline-block bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-100 text-xs px-2 py-1 rounded")
            exports = exports_tag.text.strip() if exports_tag else None
            
            return {
                "Name": province_name,
                "Population": population,
                "Capital City": capital_city,
                "Key industries": industries,
                "Key exports": exports
            }
        except Exception as e:
            print(f"Error extracting info for a province: {e}")
            return None

    def save_data(self):
        if not self.provinces:
            print("No data to save.")
            return
        
        # Create directory if it doesn't exist
        Path("data/scrap").mkdir(parents=True, exist_ok=True)
        output_file = Path("data/scrap/datazambia.csv")
        
        df = pd.DataFrame(self.provinces)
        df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")

def main():
    print("="*60)
    print("\nProgram initialized...")
    scraper = DataZambia_scraper()
    scraper.scrap_province()
    scraper.save_data()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")