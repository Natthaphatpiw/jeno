import os
import re
import json
import hashlib
import time
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlparse
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from bs4 import BeautifulSoup

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system storage"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove extra spaces and limit length
    filename = re.sub(r'\s+', '_', filename).strip('_')
    return filename[:200]  # Limit filename length

def get_url_hash(url: str) -> str:
    """Generate short hash for URL to use in filenames"""
    return hashlib.md5(url.encode()).hexdigest()[:12]

def extract_category_from_url(url: str) -> str:
    """Extract category name from article URL"""
    # Example: /en/ideas/futurist/article-name -> futurist
    path_parts = urlparse(url).path.split('/')
    if len(path_parts) >= 4 and path_parts[3] in ['futurist', 'understand-people-and-consumer', 
                                                   'transformation-and-technology', 'utility-for-our-world',
                                                   'real-time-marketing', 'experience-the-new-world']:
        return path_parts[3]
    return 'unknown'

def save_json(data: Any, filepath: str) -> None:
    """Save data as JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.debug(f"Saved JSON to {filepath}")

def load_json(filepath: str) -> Optional[Dict]:
    """Load JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load JSON from {filepath}: {e}")
        return None

def ensure_dir_exists(directory: str) -> None:
    """Ensure directory exists"""
    os.makedirs(directory, exist_ok=True)

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    return text

def extract_text_content(soup: BeautifulSoup) -> str:
    """Extract clean text content from BeautifulSoup object"""
    # Remove unwanted elements
    for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
        element.decompose()
    
    # Get text content
    text = soup.get_text(separator=' ', strip=True)
    return clean_text(text)

def is_valid_article_url(url: str) -> bool:
    """Check if URL is a valid article URL"""
    if not url or not url.startswith(('http://', 'https://')):
        return False
    
    # Must be from jenosize.com domain
    parsed = urlparse(url)
    if 'jenosize.com' not in parsed.netloc:
        return False
    
    # Must contain article path pattern
    path = parsed.path
    return '/en/ideas/' in path and len(path.split('/')) >= 5

def create_session() -> requests.Session:
    """Create configured requests session"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': settings.USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    return session

@retry(
    stop=stop_after_attempt(settings.MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_with_retry(session: requests.Session, url: str) -> requests.Response:
    """Fetch URL with retry logic"""
    logger.debug(f"Fetching {url}")
    
    response = session.get(url, timeout=settings.REQUEST_TIMEOUT)
    response.raise_for_status()
    
    # Add delay to be respectful to the server
    time.sleep(settings.REQUEST_DELAY)
    
    return response

def calculate_content_stats(content: str) -> Dict[str, int]:
    """Calculate content statistics"""
    if not content:
        return {'chars': 0, 'words': 0, 'lines': 0}
    
    return {
        'chars': len(content),
        'words': len(content.split()),
        'lines': len(content.splitlines())
    }

def validate_article_content(content: str, title: str = "") -> Dict[str, bool]:
    """Validate article content quality"""
    stats = calculate_content_stats(content)
    
    return {
        'has_title': bool(title.strip()),
        'min_length': stats['chars'] >= settings.MIN_CONTENT_LENGTH,
        'reasonable_word_count': 50 <= stats['words'] <= 10000,
        'not_empty': bool(content.strip()),
        'has_paragraphs': stats['lines'] >= 3
    }

def format_url_for_display(url: str, max_length: int = 50) -> str:
    """Format URL for display in logs"""
    if len(url) <= max_length:
        return url
    return url[:max_length-3] + "..."