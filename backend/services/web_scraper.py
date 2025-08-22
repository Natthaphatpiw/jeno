import requests
from bs4 import BeautifulSoup
from typing import Optional
from config.settings import settings
import re
from urllib.parse import urljoin, urlparse

class WebScraperService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.USER_AGENT
        })
    
    def scrape_url(self, url: str) -> Optional[str]:
        """Scrape content from a given URL"""
        try:
            # Validate URL
            if not self._is_valid_url(url):
                raise ValueError("Invalid URL format")
            
            response = self.session.get(
                url,
                timeout=settings.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            self._remove_unwanted_elements(soup)
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Clean and format text
            cleaned_content = self._clean_text(content)
            
            return cleaned_content
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching URL: {str(e)}")
        except Exception as e:
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
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
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