import re
from typing import List, Optional

def parse_seo_keywords(keywords_string: Optional[str]) -> List[str]:
    """Parse comma-separated SEO keywords string into list"""
    if not keywords_string:
        return []
    
    keywords = [kw.strip() for kw in keywords_string.split(',')]
    return [kw for kw in keywords if kw]

def validate_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def clean_html_content(html_content: str) -> str:
    """Clean HTML content for processing"""
    # Remove HTML tags
    import re
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', html_content)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def truncate_text(text: str, max_length: int = 5000) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    
    # Try to truncate at sentence boundary
    truncated = text[:max_length]
    last_period = truncated.rfind('.')
    
    if last_period > max_length * 0.8:  # If we can keep at least 80% of content
        return truncated[:last_period + 1]
    
    return truncated + '...'