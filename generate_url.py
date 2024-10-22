import requests
from bs4 import BeautifulSoup
import concurrent.futures
import json
from urllib.parse import urljoin, urlparse
import os
import time
from tqdm import tqdm
import logging
from collections import defaultdict
import re

class DMOZScraper:
    def __init__(self, output_dir="urls_dataset"):
        self.base_url = "https://odp.org/"
        self.output_dir = output_dir
        self.urls = defaultdict(set)
        self.processed_pages = set()
        
        # Create output directory first
        self.create_directories()
        
        # Then setup logging
        self.setup_logging()
        
        # Categories we're interested in for UI patterns
        self.target_categories = {
            'business': [
                'Business', 'E-Commerce', 'Financial_Services', 'Shopping',
                'Business_Services', 'Marketing', 'Consulting'
            ],
            'technology': [
                'Computers', 'Software', 'Internet', 'Web_Design',
                'Programming', 'Hardware', 'Security'
            ],
            'education': [
                'Education', 'Distance_Learning', 'Online_Education',
                'Universities', 'Courses', 'Training'
            ],
            'entertainment': [
                'Entertainment', 'Games', 'Music', 'Movies', 'Television',
                'Streaming_Media', 'Radio'
            ],
            'lifestyle': [
                'Health', 'Home', 'Food', 'Fashion', 'Travel', 'Sports',
                'Recreation'
            ],
            'social': [
                'Society', 'Community', 'Social_Networks', 'Forums',
                'Blogs', 'News', 'Media'
            ],
            'services': [
                'Web_Services', 'Cloud_Computing', 'Hosting',
                'Email_Services', 'Communication', 'Productivity'
            ],
            'reference': [
                'Reference', 'Libraries', 'Documentation', 'Science',
                'Research', 'Academic'
            ]
        }

    def create_directories(self):
        """Create necessary directories"""
        try:
            # Create main output directory
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Create subdirectories for different types of output
            os.makedirs(os.path.join(self.output_dir, 'categories'), exist_ok=True)
            os.makedirs(os.path.join(self.output_dir, 'logs'), exist_ok=True)
            os.makedirs(os.path.join(self.output_dir, 'stats'), exist_ok=True)
            
        except Exception as e:
            print(f"Error creating directories: {str(e)}")
            raise

    def setup_logging(self):
        """Setup logging configuration"""
        try:
            log_file = os.path.join(self.output_dir, 'logs', 'scraper.log')
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler()
                ]
            )
            
            # Test logging
            logging.info("Logging initialized successfully")
            
        except Exception as e:
            print(f"Error setting up logging: {str(e)}")
            raise

    # ... (rest of the methods remain the same)

    def save_urls(self):
        """Save URLs to files"""
        try:
            # Save categorized URLs
            categories_dir = os.path.join(self.output_dir, 'categories')
            for category, urls in self.urls.items():
                filename = os.path.join(categories_dir, f"{category}_urls.txt")
                with open(filename, 'w') as f:
                    for url in sorted(urls):
                        f.write(f"{url}\n")
            
            # Save all URLs in a single file
            all_urls_file = os.path.join(self.output_dir, "all_urls.txt")
            with open(all_urls_file, 'w') as f:
                for category, urls in self.urls.items():
                    for url in sorted(urls):
                        f.write(f"{url}\n")
            
            # Save statistics
            stats = {
                'total_urls': sum(len(urls) for urls in self.urls.values()),
                'urls_per_category': {cat: len(urls) for cat, urls in self.urls.items()},
                'timestamp': int(time.time())
            }
            
            stats_file = os.path.join(self.output_dir, 'stats', "statistics.json")
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error saving URLs: {str(e)}")
            raise

    def run(self):
        """Main execution method"""
        try:
            logging.info("Starting URL scraping")
            
            # Start with main categories
            for category in self.target_categories:
                category_url = urljoin(self.base_url, category)
                self.get_category_urls(category_url)
            
            # Scrape additional sources
            self.scrape_additional_sources()
            
            # Verify URLs are accessible
            self.verify_urls()
            
            # Save results
            self.save_urls()
            
            # Print summary
            total_urls = sum(len(urls) for urls in self.urls.values())
            logging.info(f"Scraping completed. Total URLs collected: {total_urls}")
            for category, urls in self.urls.items():
                logging.info(f"{category}: {len(urls)} URLs")
                
        except Exception as e:
            logging.error(f"Error during scraping: {str(e)}")
            raise

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="URL Scraper for UI Dataset"
    )
    parser.add_argument(
        "--output-dir",
        default="urls_dataset",
        help="Output directory for dataset"
    )
    
    args = parser.parse_args()
    
    try:
        scraper = DMOZScraper(output_dir=args.output_dir)
        scraper.run()
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()