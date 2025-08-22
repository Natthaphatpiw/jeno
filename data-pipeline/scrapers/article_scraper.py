import time
import os
from typing import List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from config.settings import settings
from models.schemas import ArticleLink, ArticleContent, ArticleMetadata, ScrapingResult
from utils.logger import get_logger
from utils.helpers import (
    create_session,
    fetch_with_retry,
    sanitize_filename,
    get_url_hash,
    save_json,
    ensure_dir_exists,
    extract_text_content,
    calculate_content_stats,
    validate_article_content,
    format_url_for_display
)

logger = get_logger(__name__)

class ArticleScraper:
    """Scrapes individual article pages and extracts content"""
    
    def __init__(self, use_selenium=True):
        self.session = create_session()
        self.use_selenium = use_selenium
        self.driver = None
        
        if use_selenium:
            self._setup_selenium()
        
        ensure_dir_exists(settings.RAW_DIR)
        ensure_dir_exists(settings.PROCESSED_DIR)
    
    def scrape_articles(self, article_links: List[ArticleLink], max_workers: int = 3) -> List[ScrapingResult]:
        """Scrape multiple articles with thread pool"""
        logger.info(f"Starting to scrape {len(article_links)} articles with {max_workers} workers")
        
        results = []
        
        # Limit articles per category if configured
        if settings.MAX_ARTICLES_PER_CATEGORY:
            article_links = self._limit_articles_per_category(article_links, settings.MAX_ARTICLES_PER_CATEGORY)
            logger.info(f"Limited to {len(article_links)} articles total")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scraping tasks
            future_to_link = {
                executor.submit(self.scrape_single_article, link): link 
                for link in article_links
            }
            
            # Process completed tasks with progress bar
            for future in tqdm(as_completed(future_to_link), total=len(article_links), desc="Scraping articles"):
                link = future_to_link[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result.success:
                        logger.debug(f"✓ Scraped: {format_url_for_display(link.url)}")
                    else:
                        logger.warning(f"✗ Failed: {format_url_for_display(link.url)} - {result.error}")
                        
                except Exception as e:
                    logger.error(f"Exception scraping {link.url}: {e}")
                    results.append(ScrapingResult(
                        success=False,
                        url=link.url,
                        error=str(e)
                    ))
        
        # Log summary
        successful = sum(1 for r in results if r.success)
        logger.info(f"Scraping completed: {successful}/{len(results)} articles successful")
        
        return results
    
    def scrape_single_article(self, article_link: ArticleLink) -> ScrapingResult:
        """Scrape a single article"""
        start_time = time.time()
        
        try:
            logger.debug(f"Scraping article: {article_link.title}")
            
            # Fetch article page
            response = None
            html_content = None
            
            if self.use_selenium and self.driver:
                html_content = self._fetch_with_selenium(article_link.url)
                if not html_content:
                    # Fallback to requests
                    response = fetch_with_retry(self.session, article_link.url)
                    soup = BeautifulSoup(response.content, 'html.parser')
                else:
                    soup = BeautifulSoup(html_content, 'html.parser')
            else:
                response = fetch_with_retry(self.session, article_link.url)
                soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content
            content = self._extract_article_content(soup, article_link)
            
            if not content:
                # Try to extract from Next.js script tags as fallback
                logger.debug("Trying to extract from script tags")
                content = self._extract_from_nextjs_scripts(soup, article_link)
            
            if not content:
                return ScrapingResult(
                    success=False,
                    url=article_link.url,
                    error="Failed to extract article content",
                    processing_time=time.time() - start_time
                )
            
            # Save raw HTML
            if response:
                self._save_raw_html(article_link.url, response.content)
            elif html_content:
                self._save_raw_html(article_link.url, html_content.encode('utf-8'))
            
            # Save processed content
            self._save_processed_content(content)
            
            return ScrapingResult(
                success=True,
                url=article_link.url,
                content=content,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Error scraping {article_link.url}: {e}")
            return ScrapingResult(
                success=False,
                url=article_link.url,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def _extract_article_content(self, soup: BeautifulSoup, article_link: ArticleLink) -> Optional[ArticleContent]:
        """Extract and structure article content"""
        try:
            # Extract metadata
            metadata = self._extract_metadata(soup, article_link)
            
            # Extract main content
            html_content = self._extract_html_content(soup)
            text_content = extract_text_content(BeautifulSoup(html_content, 'html.parser'))
            
            # Validate content
            validation = validate_article_content(text_content, metadata.title)
            if not all(validation.values()):
                logger.warning(f"Content validation failed for {article_link.url}: {validation}")
            
            # Extract structured content
            structured_content = self._extract_structured_content(soup)
            
            # Extract images
            images = self._extract_images(soup, article_link.url)
            
            return ArticleContent(
                metadata=metadata,
                html_content=html_content,
                text_content=text_content,
                structured_content=structured_content,
                images=images
            )
            
        except Exception as e:
            logger.error(f"Error extracting content from {article_link.url}: {e}")
            return None
    
    def _extract_metadata(self, soup: BeautifulSoup, article_link: ArticleLink) -> ArticleMetadata:
        """Extract article metadata"""
        # Title - try multiple selectors
        title = article_link.title
        title_selectors = [
            'h1',
            '.article-title', 
            '.post-title',
            'h1.font-gtrm',  # Specific to Jenosize
            '[class*="txt-web-title"]',
            'title'
        ]
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text(strip=True):
                title = title_elem.get_text(strip=True)
                break
        
        # Author
        author = None
        author_selectors = ['.author', '.by-author', '[rel="author"]', '.post-author']
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                author = author_elem.get_text(strip=True)
                break
        
        # Publish date
        publish_date = None
        date_selectors = ['time', '.publish-date', '.post-date', '[datetime]']
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                publish_date = date_elem.get('datetime') or date_elem.get_text(strip=True)
                break
        
        # Description/excerpt
        description = None
        desc_selectors = ['meta[name="description"]', '.excerpt', '.summary', '.article-excerpt']
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                description = desc_elem.get('content') or desc_elem.get_text(strip=True)
                break
        
        # Tags
        tags = []
        tag_selectors = ['.tags a', '.post-tags a', '.article-tags a', '.categories a']
        for selector in tag_selectors:
            tag_elements = soup.select(selector)
            tags.extend([tag.get_text(strip=True) for tag in tag_elements])
        
        # Calculate content stats (will be updated with actual content)
        content_stats = {'chars': 0, 'words': 0, 'lines': 0}
        
        return ArticleMetadata(
            url=article_link.url,
            title=title,
            category=article_link.category,
            author=author,
            publish_date=publish_date,
            description=description,
            tags=list(set(tags)),  # Remove duplicates
            content_stats=content_stats
        )
    
    def _extract_html_content(self, soup: BeautifulSoup) -> str:
        """Extract main article HTML content"""
        # For Next.js/React apps, content might be in script tags or specific divs
        # Try to find content in dangerouslySetInnerHTML divs first
        content_div = soup.find('div', {'class': lambda x: x and 'content-detail' in x})
        if content_div:
            logger.debug("Found content in content-detail div")
            return str(content_div)
        
        # Try to find main content container
        content_selectors = [
            'article',
            '.article-content',
            '.post-content', 
            '.entry-content',
            '.content',
            'main',
            '.main-content',
            '.content-detail-en',  # Specific to Jenosize
            '[class*="content-detail"]'  # Any class containing content-detail
        ]
        
        main_content = None
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                main_content = element
                break
        
        # For Next.js apps, try to extract from script tags
        if not main_content:
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and 'dangerouslySetInnerHTML' in script.string:
                    logger.debug("Found content in script tag")
                    # Extract the actual HTML content from the script
                    import re
                    match = re.search(r'"__html":"([^"]+)"', script.string)
                    if match:
                        html_content = match.group(1)
                        # Decode escaped HTML
                        html_content = html_content.encode().decode('unicode_escape')
                        return html_content
        
        if not main_content:
            # Fallback to body content
            main_content = soup.find('body')
        
        if main_content:
            # Remove unwanted elements
            for unwanted in main_content.find_all(['script', 'style', 'nav', 'header', 'footer', '.sidebar']):
                unwanted.decompose()
            
            return str(main_content)
        
        return str(soup)
    
    def _extract_structured_content(self, soup: BeautifulSoup) -> Dict:
        """Extract structured content elements"""
        structured = {
            'headings': [],
            'paragraphs': [],
            'lists': [],
            'quotes': [],
            'code_blocks': []
        }
        
        try:
            # Find main content area
            main_content = soup.select_one('article, .article-content, .post-content, .entry-content, main')
            if not main_content:
                main_content = soup
            
            # Extract headings
            for i in range(1, 7):
                headings = main_content.find_all(f'h{i}')
                for heading in headings:
                    structured['headings'].append({
                        'level': i,
                        'text': heading.get_text(strip=True),
                        'id': heading.get('id', '')
                    })
            
            # Extract paragraphs
            paragraphs = main_content.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text:  # Skip empty paragraphs
                    structured['paragraphs'].append(text)
            
            # Extract lists
            lists = main_content.find_all(['ul', 'ol'])
            for lst in lists:
                list_items = [li.get_text(strip=True) for li in lst.find_all('li')]
                if list_items:
                    structured['lists'].append({
                        'type': lst.name,
                        'items': list_items
                    })
            
            # Extract quotes
            quotes = main_content.find_all('blockquote')
            for quote in quotes:
                text = quote.get_text(strip=True)
                if text:
                    structured['quotes'].append(text)
            
            # Extract code blocks
            code_blocks = main_content.find_all(['pre', 'code'])
            for code in code_blocks:
                text = code.get_text()
                if text.strip():
                    structured['code_blocks'].append(text)
        
        except Exception as e:
            logger.warning(f"Error extracting structured content: {e}")
        
        return structured
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract image information"""
        images = []
        
        try:
            img_elements = soup.find_all('img')
            for img in img_elements:
                src = img.get('src')
                if src:
                    # Make absolute URL
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = 'https://www.jenosize.com' + src
                    
                    images.append({
                        'src': src,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', ''),
                        'width': img.get('width', ''),
                        'height': img.get('height', '')
                    })
        
        except Exception as e:
            logger.warning(f"Error extracting images: {e}")
        
        return images
    
    def _save_raw_html(self, url: str, content: bytes) -> None:
        """Save raw HTML content to file"""
        try:
            filename = f"{get_url_hash(url)}.html"
            filepath = os.path.join(settings.RAW_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(content)
                
        except Exception as e:
            logger.warning(f"Failed to save raw HTML for {url}: {e}")
    
    def _save_processed_content(self, content: ArticleContent) -> None:
        """Save processed content to JSON file"""
        try:
            filename = f"{get_url_hash(content.metadata.url)}.json"
            filepath = os.path.join(settings.PROCESSED_DIR, filename)
            
            # Convert to dict for JSON serialization
            content_dict = {
                'metadata': {
                    'url': content.metadata.url,
                    'title': content.metadata.title,
                    'category': content.metadata.category,
                    'author': content.metadata.author,
                    'publish_date': content.metadata.publish_date,
                    'description': content.metadata.description,
                    'tags': content.metadata.tags,
                    'image_count': len(content.images),
                    'content_stats': calculate_content_stats(content.text_content)
                },
                'html_content': content.html_content,
                'text_content': content.text_content,
                'structured_content': content.structured_content,
                'images': content.images
            }
            
            save_json(content_dict, filepath)
            
        except Exception as e:
            logger.warning(f"Failed to save processed content for {content.metadata.url}: {e}")
    
    def _limit_articles_per_category(self, article_links: List[ArticleLink], max_per_category: int) -> List[ArticleLink]:
        """Limit number of articles per category"""
        category_counts = {}
        limited_links = []
        
        for link in article_links:
            category = link.category
            if category not in category_counts:
                category_counts[category] = 0
            
            if category_counts[category] < max_per_category:
                limited_links.append(link)
                category_counts[category] += 1
        
        return limited_links
    
    def _extract_from_nextjs_scripts(self, soup: BeautifulSoup, article_link: ArticleLink) -> Optional[ArticleContent]:
        """Extract content from Next.js script tags"""
        try:
            import json
            import re
            
            # Look for script tags with content
            script_tags = soup.find_all('script')
            html_content = ""
            
            for script in script_tags:
                if script.string and 'dangerouslySetInnerHTML' in script.string:
                    # Extract HTML from script
                    match = re.search(r'"__html":"([^"]+)"', script.string)
                    if match:
                        escaped_html = match.group(1)
                        # Decode Unicode escapes
                        html_content = escaped_html.encode('utf-8').decode('unicode_escape')
                        break
            
            if not html_content:
                return None
            
            # Parse the extracted HTML
            content_soup = BeautifulSoup(html_content, 'html.parser')
            text_content = content_soup.get_text(separator=' ', strip=True)
            
            # Extract metadata
            metadata = self._extract_metadata(soup, article_link)
            
            # Extract structured content from the parsed HTML
            structured_content = self._extract_structured_content(content_soup)
            
            # Extract images
            images = self._extract_images(soup, article_link.url)
            
            return ArticleContent(
                metadata=metadata,
                html_content=html_content,
                text_content=text_content,
                structured_content=structured_content,
                images=images
            )
            
        except Exception as e:
            logger.error(f"Error extracting from Next.js scripts: {e}")
            return None
    
    def _setup_selenium(self):
        """Setup Selenium Chrome driver"""
        try:
            options = Options()
            options.add_argument('--headless')  # Run in background
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            logger.info("Selenium Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            logger.info("Falling back to requests-based scraping")
            self.use_selenium = False
    
    def _fetch_with_selenium(self, url: str) -> Optional[str]:
        """Fetch page content using Selenium"""
        try:
            logger.debug(f"Loading page with Selenium: {url}")
            self.driver.get(url)
            
            # Wait for content to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "main"))
                )
            except:
                # If main tag not found, wait for body
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            return self.driver.page_source
            
        except Exception as e:
            logger.error(f"Error fetching with Selenium: {e}")
            return None
    
    def close(self):
        """Close the session and driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Chrome driver closed")
        self.session.close()