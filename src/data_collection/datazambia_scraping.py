'''
Kip
This code aims at scraping the datazambia website to obtain the stated information on all the 10 provinces
'''

from os import mkdir
import pandas as pd
import os
from bs4 import BeautifulSoup
import time
import requests
from pathlib import Path

from sqlalchemy.sql.operators import exists


class DataZambia_scraper:
    # initialize neccessary variables
    def __init__(self):
        self.base_url = "https://datazambia.com/explore"
        self.headers = {
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def scrap_province(self):
        province_url = self.base_url
        response = requests.get(province_url, headers=self.headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            province_cards = soup.find_all('div', class_="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-all duration-300 cursor-pointer")

            if province_cards:
                 print("Url Working")
        print(f"status code: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        for province in province_cards:
            provinces = self.extract_prov_info(province)

    def extract_prov_info(self, province):
        # extract information from each province card
        h2_tag = province.find('h2', class_="text-2x1 font-bold")
        province_name = h2_tag.text.strip() if h2_tag else None
        #           get population and capital city
        population_tag = province.find('p', class_="flex items-center")
        population = population_tag.find('span', class_="mr-2").text.strip()
        capital_tag = province.find('p', class_="flex items-center").find('span')
        capital_city = capital_tag.text.strip()
        #             key industries
        industry_tag = province.find('span',
                                     class_="inline-block bg-blue-100 dark:bg-blue-800 dark:text-blue-100 text-xs px-2 py-1 rounded")
        industries = list(industry_tag.text.strip() if industry_tag else None)
        exports_tag = province.find('span',
                                    class_="inline-block bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-100 text-xs px-2 py-1 rounded")
        exports = list(exports_tag.text.strip() if exports_tag else None)

        provinces = {
            "Name": province_name,
            "Population": population,
            "Capital City": capital_city,
            "Key industries": industries,
            "Key exports": exports
        }

        return provinces

    def save_data(self):
        # output_file = Path("data/scraped_zambia_info/datazambia.csv")
        output_file = Path("data/scrap/datazambia.csv").mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(self.provinces)
        df.to_csv(output_file, index=False)


def main():
    print("="*60)
    print("\n Program initialized...")
    scraper = DataZambia_scraper()
    scraper.scrap_province()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")