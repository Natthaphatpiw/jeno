import time
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from models.schemas import ArticleLink
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)

class SeleniumScraper:
    """Scraper using Selenium for JavaScript-heavy websites"""
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with options"""
        try:
            options = Options()
            options.add_argument('--headless')  # Run in background
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            logger.info("Falling back to requests-based scraping")
    
    def scrape_category_page_selenium(self, url: str, category: str) -> List[ArticleLink]:
        """Scrape category page using Selenium"""
        if not self.driver:
            return []
        
        links = []
        try:
            logger.info(f"Loading page with Selenium: {url}")
            self.driver.get(url)
            
            # Wait for content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find article links
            article_links = soup.find_all('a', class_='hover:underline')
            logger.info(f"Found {len(article_links)} article links with Selenium")
            
            for link in article_links:
                href = link.get('href')
                title = link.get_text(strip=True)
                
                if href and f'/ideas/{category}' in href and len(href.split('/')) > 4:
                    full_url = f"https://www.jenosize.com{href}" if href.startswith('/') else href
                    
                    links.append(ArticleLink(
                        url=full_url,
                        title=title,
                        category=category,
                        href=href
                    ))
                    logger.debug(f"Found article: {title}")
            
        except Exception as e:
            logger.error(f"Error scraping with Selenium: {e}")
        
        return links
    
    def scrape_article_selenium(self, url: str) -> Optional[str]:
        """Scrape article content using Selenium"""
        if not self.driver:
            return None
        
        try:
            logger.info(f"Loading article with Selenium: {url}")
            self.driver.get(url)
            
            # Wait for content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "content-detail"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            return self.driver.page_source
            
        except Exception as e:
            logger.error(f"Error scraping article with Selenium: {e}")
            return None
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Chrome driver closed")