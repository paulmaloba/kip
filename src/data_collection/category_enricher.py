"""
Project Kwacha - Category Enrichment Script
Extracts categories from business profile pages and updates CSV
Week 2: Data Enhancement
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path
from datetime import datetime

class CategoryEnricher:
    """
    Enriches business data with categories from profile pages
    """
    
    def __init__(self, csv_file='data/raw/zambiayp_businesses.csv'):
        self.csv_file = csv_file
        self.df = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.enriched_count = 0
        self.failed_count = 0
        
    def load_data(self):
        """Load the existing CSV"""
        print("=" * 70)
        print("LOADING BUSINESS DATA")
        print("=" * 70 + "\n")
        
        self.df = pd.read_csv(self.csv_file)
        
        print(f"✅ Loaded {len(self.df)} businesses")
        
        # Check how many already have categories
        has_category = self.df['category'].notna().sum()
        needs_category = self.df['category'].isna().sum()
        
        print(f"\n📊 Category Status:")
        print(f"   • Already have categories: {has_category}")
        print(f"   • Need categories: {needs_category}")
        
        return needs_category
    
    def extract_categories_from_url(self, url):
        """
        Extract categories from a business profile page
        Based on the screenshot: categories are in div.tags > a
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the tags div (from your screenshot inspection)
            tags_div = soup.find('div', class_='tags')
            
            if not tags_div:
                return None
            
            # Extract all category links
            category_links = tags_div.find_all('a')
            categories = [a.text.strip() for a in category_links if a.text.strip()]
            
            if categories:
                # Return as comma-separated string
                return ', '.join(categories)
            
            return None
            
        except Exception as e:
            return None
    
    def enrich_categories(self, start_index=0, batch_size=100, delay=2):
        """
        Enrich businesses with categories
        
        Args:
            start_index: Which row to start from (for resuming)
            batch_size: Save progress every N businesses
            delay: Seconds to wait between requests (be polite!)
        """
        print(f"\n{'='*70}")
        print("ENRICHING CATEGORIES")
        print(f"{'='*70}\n")
        
        # Get businesses that need categories
        needs_enrichment = self.df[self.df['category'].isna()].copy()
        
        if len(needs_enrichment) == 0:
            print("✅ All businesses already have categories!")
            return
        
        # Start from specified index
        if start_index > 0:
            needs_enrichment = needs_enrichment.iloc[start_index:]
            print(f"📍 Resuming from index {start_index}")
        
        total = len(needs_enrichment)
        print(f"🎯 Will process {total} businesses")
        print(f"⏱️  Estimated time: {total * delay / 60:.1f} minutes")
        print(f"💾 Will save progress every {batch_size} businesses\n")
        
        input("Press Enter to start, or Ctrl+C to cancel...")
        
        start_time = datetime.now()
        
        for i, (idx, row) in enumerate(needs_enrichment.iterrows(), 1):
            url = row['url']
            business_name = row['name']
            
            # Progress indicator
            if i % 10 == 0 or i == 1:
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = i / elapsed if elapsed > 0 else 0
                remaining = (total - i) / rate if rate > 0 else 0
                print(f"[{i}/{total}] Processing {business_name[:50]}... (ETA: {remaining/60:.1f} min)")
            
            # Extract categories
            categories = self.extract_categories_from_url(url)
            
            if categories:
                self.df.at[idx, 'category'] = categories
                self.enriched_count += 1
            else:
                self.failed_count += 1
            
            # Save progress periodically
            if i % batch_size == 0:
                self.save_progress()
                print(f"   💾 Progress saved! ({self.enriched_count} enriched, {self.failed_count} failed)")
            
            # Be polite - wait between requests
            time.sleep(delay)
        
        # Final save
        self.save_progress()
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n{'='*70}")
        print("ENRICHMENT COMPLETE!")
        print(f"{'='*70}")
        print(f"\n⏱️  Total time: {elapsed/60:.1f} minutes")
        print(f"✅ Successfully enriched: {self.enriched_count}")
        print(f"❌ Failed to enrich: {self.failed_count}")
        print(f"📊 Success rate: {self.enriched_count/(self.enriched_count+self.failed_count)*100:.1f}%")
    
    def save_progress(self):
        """Save current progress"""
        # Backup original first time
        backup_file = Path(self.csv_file).parent / f"{Path(self.csv_file).stem}_backup.csv"
        if not backup_file.exists():
            original_df = pd.read_csv(self.csv_file)
            original_df.to_csv(backup_file, index=False)
            print(f"\n💾 Backup created: {backup_file}")
        
        # Save current state
        self.df.to_csv(self.csv_file, index=False)
    
    def show_sample_results(self, n=10):
        """Show sample enriched results"""
        print(f"\n{'='*70}")
        print("SAMPLE ENRICHED RESULTS")
        print(f"{'='*70}\n")
        
        enriched = self.df[self.df['category'].notna()].sample(min(n, len(self.df)))
        
        for _, row in enriched.iterrows():
            print(f"📍 {row['name']}")
            print(f"   City: {row['city']}")
            print(f"   Categories: {row['category']}")
            print()
    
    def generate_report(self):
        """Generate enrichment report"""
        print(f"\n{'='*70}")
        print("ENRICHMENT REPORT")
        print(f"{'='*70}\n")
        
        total = len(self.df)
        has_category = self.df['category'].notna().sum()
        
        print(f"📊 Overall Statistics:")
        print(f"   • Total businesses: {total}")
        print(f"   • With categories: {has_category} ({has_category/total*100:.1f}%)")
        print(f"   • Without categories: {total - has_category}")
        
        if has_category > 0:
            # Category distribution
            print(f"\n🏢 Top 15 Categories:")
            
            # Flatten categories (since some businesses have multiple)
            all_categories = []
            for cats in self.df['category'].dropna():
                all_categories.extend([c.strip() for c in str(cats).split(',')])
            
            from collections import Counter
            cat_counts = Counter(all_categories)
            
            for cat, count in cat_counts.most_common(15):
                print(f"   • {cat}: {count} businesses")
            
            # Save category report
            cat_df = pd.DataFrame(cat_counts.most_common(), columns=['category', 'count'])
            cat_df.to_csv('data/processed/category_distribution.csv', index=False)
            print(f"\n✅ Saved detailed report to: data/processed/category_distribution.csv")

def main():
    """
    Main enrichment workflow
    """
    print("\n" + "🏷️" * 35)
    print("CATEGORY ENRICHMENT TOOL")
    print("🏷️" * 35)
    
    enricher = CategoryEnricher('data/raw/zambiayp_businesses.csv')
    
    # Load data
    needs_enrichment = enricher.load_data()
    
    if needs_enrichment == 0:
        print("\n✅ No enrichment needed!")
        enricher.show_sample_results()
        return
    
    print(f"\n📋 Enrichment Options:")
    print(f"   1. Full enrichment ({needs_enrichment} businesses)")
    print(f"   2. Test run (first 50 businesses)")
    print(f"   3. Resume from checkpoint")
    print(f"   4. Custom range")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '2':
        # Test run
        print("\n🧪 Test run: First 50 businesses")
        enricher.enrich_categories(start_index=0, batch_size=10, delay=2)
        
    elif choice == '3':
        # Resume
        start_idx = int(input("Resume from index: ").strip())
        enricher.enrich_categories(start_index=start_idx, batch_size=100, delay=2)
        
    elif choice == '4':
        # Custom range
        start_idx = int(input("Start index: ").strip())
        end_idx = int(input("End index: ").strip())
        # Filter to range
        enricher.df = enricher.df.iloc[start_idx:end_idx]
        enricher.enrich_categories(start_index=0, batch_size=50, delay=2)
        
    else:
        # Full enrichment
        print(f"\n⚠️  WARNING: This will make ~{needs_enrichment} HTTP requests")
        print(f"   Estimated time: {needs_enrichment * 2 / 60:.0f} minutes ({needs_enrichment * 2 / 3600:.1f} hours)")
        print(f"   Progress will be saved every 100 businesses")
        
        confirm = input("\nProceed? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            enricher.enrich_categories(start_index=0, batch_size=100, delay=2)
        else:
            print("\n❌ Cancelled")
            return
    
    # Show results
    enricher.show_sample_results()
    enricher.generate_report()
    
    print("\n📋 Next steps:")
    print("   1. Review updated data/raw/zambiayp_businesses.csv")
    print("   2. Check data/processed/category_distribution.csv")
    print("   3. Run market saturation analysis")
    print("   4. Generate business scenarios")
    
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("   Progress has been saved")
        print("   Run again and choose 'Resume from checkpoint'")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
