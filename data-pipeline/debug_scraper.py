#!/usr/bin/env python3
"""Debug script to test individual article scraping"""

import sys
import traceback
from scrapers.article_scraper import ArticleScraper  
from models.schemas import ArticleLink
from utils.logger import get_logger

logger = get_logger(__name__)

def test_single_article():
    """Test scraping a single article"""
    
    # Create a test article link
    test_link = ArticleLink(
        url="https://www.jenosize.com/en/ideas/futurist/digital-twin-business-model",
        title="Digital Twin Business Model Test",
        category="futurist",
        href="/en/ideas/futurist/digital-twin-business-model"
    )
    
    logger.info(f"Testing article scraping: {test_link.url}")
    
    try:
        scraper = ArticleScraper()
        
        # Test individual steps
        logger.info("Step 1: Fetching page...")
        response = scraper.session.get(test_link.url, timeout=15)
        logger.info(f"Response status: {response.status_code}")
        
        logger.info("Step 2: Parsing HTML...")
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        logger.info(f"HTML parsed, title: {soup.title.string if soup.title else 'No title'}")
        
        logger.info("Step 3: Extracting metadata...")
        try:
            metadata = scraper._extract_metadata(soup, test_link)
            logger.info(f"Metadata extracted: {metadata.title}")
        except Exception as e:
            logger.error(f"Error in metadata extraction: {e}")
            traceback.print_exc()
            return None
        
        logger.info("Step 4: Full scrape...")
        result = scraper.scrape_single_article(test_link)
        
        logger.info(f"Result success: {result.success}")
        if result.error:
            logger.error(f"Error: {result.error}")
        if result.content:
            logger.info(f"Content length: {len(result.content.text_content)}")
        
        scraper.close()
        return result
        
    except Exception as e:
        logger.error(f"Exception in test: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_single_article()