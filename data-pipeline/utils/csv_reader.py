import csv
from typing import List
from urllib.parse import urlparse
from models.schemas import ArticleLink
from utils.logger import get_logger

logger = get_logger(__name__)

class CSVReader:
    """Read article URLs from CSV file"""
    
    def __init__(self, csv_file: str = "url.csv"):
        self.csv_file = csv_file
    
    def read_urls(self) -> List[ArticleLink]:
        """Read URLs from CSV and convert to ArticleLink objects"""
        article_links = []
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    url = row.get('url', '').strip()
                    if not url:
                        continue
                    
                    # Extract category and title from URL
                    category = self._extract_category_from_url(url)
                    title = self._extract_title_from_url(url)
                    href = self._extract_href_from_url(url)
                    
                    article_link = ArticleLink(
                        url=url,
                        title=title,
                        category=category,
                        href=href
                    )
                    
                    article_links.append(article_link)
                    logger.debug(f"Added article: {title} ({category})")
            
            logger.info(f"Successfully loaded {len(article_links)} URLs from {self.csv_file}")
            return article_links
            
        except FileNotFoundError:
            logger.error(f"CSV file {self.csv_file} not found")
            return []
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return []
    
    def _extract_category_from_url(self, url: str) -> str:
        """Extract category from URL path"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            
            # Expected format: /en/ideas/category/article-slug
            if len(path_parts) >= 4 and path_parts[2] == 'ideas':
                return path_parts[3]
            
            return 'unknown'
        except Exception:
            return 'unknown'
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract title from URL slug"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            
            # Get the last part (article slug)
            if path_parts:
                slug = path_parts[-1]
                # Convert slug to title
                title = slug.replace('-', ' ').title()
                return title
            
            return 'Unknown Article'
        except Exception:
            return 'Unknown Article'
    
    def _extract_href_from_url(self, url: str) -> str:
        """Extract href (path) from full URL"""
        try:
            parsed = urlparse(url)
            return parsed.path
        except Exception:
            return url
    
    def get_category_stats(self, article_links: List[ArticleLink]) -> dict:
        """Get statistics about categories"""
        stats = {
            'total_articles': len(article_links),
            'by_category': {},
            'categories': set()
        }
        
        for link in article_links:
            category = link.category
            stats['categories'].add(category)
            
            if category not in stats['by_category']:
                stats['by_category'][category] = 0
            stats['by_category'][category] += 1
        
        stats['total_categories'] = len(stats['categories'])
        stats['categories'] = list(stats['categories'])
        
        return stats