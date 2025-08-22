import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
from config.settings import settings
import re
import logging
from urllib.parse import urljoin, urlparse

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class WebScraperService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.USER_AGENT
        })
    
    def scrape_url(self, url: str) -> Optional[str]:
        """Scrape content from a given URL"""
        logger.info(f"Starting to scrape URL: {url}")
        
        try:
            # Validate URL
            logger.info("Validating URL format...")
            if not self._is_valid_url(url):
                logger.error(f"Invalid URL format: {url}")
                raise ValueError("Invalid URL format")
            
            logger.info("URL format valid, making HTTP request...")
            response = self.session.get(
                url,
                timeout=settings.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            logger.info(f"HTTP response status: {response.status_code}")
            response.raise_for_status()
            
            # Parse HTML content
            logger.info("Parsing HTML content...")
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"HTML parsed successfully, content length: {len(response.content)}")
            
            # Remove unwanted elements
            logger.info("Removing unwanted HTML elements...")
            self._remove_unwanted_elements(soup)
            
            # Extract main content
            logger.info("Extracting main content...")
            content = self._extract_main_content(soup)
            logger.info(f"Extracted content length: {len(content)}")
            
            # Clean and format text
            logger.info("Cleaning and formatting text...")
            cleaned_content = self._clean_text(content)
            logger.info(f"Cleaned content length: {len(cleaned_content)}")
            
            return cleaned_content
            
        except requests.RequestException as e:
            logger.error(f"Network error fetching URL {url}: {str(e)}")
            raise Exception(f"Error fetching URL: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing content from {url}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Error processing content: {str(e)}")
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate if the URL is properly formatted"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _remove_unwanted_elements(self, soup: BeautifulSoup) -> None:
        """Remove unwanted HTML elements"""
        unwanted_tags = [
            'script', 'style', 'nav', 'header', 'footer', 
            'aside', 'menu', 'form', 'button', 'input',
            'iframe', 'embed', 'object', 'applet'
        ]
        
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove elements with unwanted classes/ids
        unwanted_selectors = [
            '[class*="ad"]', '[class*="advertisement"]',
            '[class*="sidebar"]', '[class*="menu"]',
            '[class*="navigation"]', '[class*="footer"]',
            '[class*="header"]', '[id*="ad"]'
        ]
        
        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the page"""
        
        # Priority order for content extraction
        content_selectors = [
            'article',
            '[class*="content"]',
            '[class*="article"]',
            '[class*="post"]',
            '[class*="entry"]',
            'main',
            '.main-content',
            '#content',
            '#main'
        ]
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                return content_element.get_text(separator=' ', strip=True)
        
        # Fallback: extract from body
        body = soup.find('body')
        if body:
            return body.get_text(separator=' ', strip=True)
        
        # Last resort: entire document
        return soup.get_text(separator=' ', strip=True)
    
    def _clean_text(self, text: str) -> str:
        """Clean and format extracted text"""
        if not text:
            return ""
        
        # Remove problematic characters and normalize whitespace
        text = re.sub(r'[^\x20-\x7E\s]', '', text)  # Keep only printable ASCII and whitespace
        text = re.sub(r'\s+', ' ', text)  # Normalize all whitespace to single spaces
        
        # Remove very short lines (likely navigation/ads)
        lines = text.split('.')
        meaningful_lines = [
            line.strip() for line in lines 
            if len(line.strip()) > 20
        ]
        
        cleaned_text = '. '.join(meaningful_lines)
        
        # Limit content length
        if len(cleaned_text) > 5000:
            sentences = cleaned_text.split('. ')
            truncated = '. '.join(sentences[:50])  # First 50 sentences
            cleaned_text = truncated + '...'
        
        return cleaned_text.strip()
    
    def scrape_url_with_metadata(self, url: str) -> Optional[Dict[str, str]]:
        """Scrape content from a URL and return with metadata"""
        logger.info(f"Starting to scrape URL with metadata: {url}")
        
        try:
            # Validate URL
            logger.info("Validating URL format...")
            if not self._is_valid_url(url):
                logger.error(f"Invalid URL format: {url}")
                raise ValueError("Invalid URL format")
            
            logger.info("URL format valid, making HTTP request...")
            response = self.session.get(
                url,
                timeout=settings.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            logger.info(f"HTTP response status: {response.status_code}")
            response.raise_for_status()
            
            # Parse HTML content
            logger.info("Parsing HTML content...")
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"HTML parsed successfully, content length: {len(response.content)}")
            
            # Extract title
            title = self._extract_title(soup)
            logger.info(f"Extracted title: {title}")
            
            # Remove unwanted elements
            logger.info("Removing unwanted HTML elements...")
            self._remove_unwanted_elements(soup)
            
            # Extract main content
            logger.info("Extracting main content...")
            content = self._extract_main_content(soup)
            logger.info(f"Extracted content length: {len(content)}")
            
            # Clean and format text
            logger.info("Cleaning and formatting text...")
            cleaned_content = self._clean_text(content)
            logger.info(f"Cleaned content length: {len(cleaned_content)}")
            
            return {
                "url": url,
                "title": title,
                "content": cleaned_content
            }
            
        except requests.RequestException as e:
            logger.error(f"Network error fetching URL {url}: {str(e)}")
            raise Exception(f"Error fetching URL: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing content from {url}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Error processing content: {str(e)}")
    
    def scrape_multiple_urls(self, urls: List[str], max_urls: int = 5) -> List[Dict[str, str]]:
        """Scrape multiple URLs with metadata"""
        logger.info(f"Starting to scrape {len(urls)} URLs (max: {max_urls})")
        
        # Limit to max_urls
        urls_to_process = urls[:max_urls]
        logger.info(f"Processing {len(urls_to_process)} URLs")
        
        results = []
        for i, url in enumerate(urls_to_process, 1):
            try:
                logger.info(f"Processing URL {i}/{len(urls_to_process)}: {url}")
                result = self.scrape_url_with_metadata(url)
                if result:
                    results.append(result)
                    logger.info(f"Successfully scraped URL {i}: {result['title']}")
            except Exception as e:
                logger.error(f"Failed to scrape URL {i} ({url}): {str(e)}")
                # Continue with other URLs even if one fails
                continue
        
        logger.info(f"Successfully scraped {len(results)} out of {len(urls_to_process)} URLs")
        return results
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try different title sources in order of preference
        title_sources = [
            soup.find('title'),
            soup.find('h1'),
            soup.find('meta', {'property': 'og:title'}),
            soup.find('meta', {'name': 'title'})
        ]
        
        for source in title_sources:
            if source:
                if source.name == 'meta':
                    title = source.get('content', '').strip()
                else:
                    title = source.get_text().strip()
                
                if title and len(title) > 0:
                    # Clean and truncate title
                    title = re.sub(r'\s+', ' ', title)
                    return title[:100] + '...' if len(title) > 100 else title
        
        return "Untitled"