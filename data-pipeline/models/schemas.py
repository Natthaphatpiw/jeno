from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ArticleLink:
    """Represents a link to an article found on category pages"""
    url: str
    title: str
    category: str
    href: str  # Original href attribute
    
    def __post_init__(self):
        if not self.url.startswith(('http://', 'https://')):
            from config.settings import settings
            from urllib.parse import urljoin
            self.url = urljoin(settings.BASE_URL, self.href)

@dataclass
class ArticleMetadata:
    """Metadata extracted from an article"""
    url: str
    title: str
    category: str
    author: Optional[str] = None
    publish_date: Optional[str] = None
    tags: List[str] = None
    description: Optional[str] = None
    image_count: int = 0
    content_stats: Dict[str, int] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.content_stats is None:
            self.content_stats = {}

@dataclass
class ArticleContent:
    """Processed article content"""
    metadata: ArticleMetadata
    html_content: str
    text_content: str
    structured_content: Dict[str, Any]  # Headings, paragraphs, lists, etc.
    images: List[Dict[str, str]] = None  # Image metadata
    
    def __post_init__(self):
        if self.images is None:
            self.images = []

@dataclass
class ProcessingStats:
    """Statistics from processing pipeline"""
    total_categories: int = 0
    total_links_found: int = 0
    total_articles_scraped: int = 0
    successful_scrapes: int = 0
    failed_scrapes: int = 0
    total_content_chars: int = 0
    total_content_words: int = 0
    categories_breakdown: Dict[str, int] = None
    processing_time_seconds: float = 0.0
    
    def __post_init__(self):
        if self.categories_breakdown is None:
            self.categories_breakdown = {}
    
    @property
    def success_rate(self) -> float:
        if self.total_articles_scraped == 0:
            return 0.0
        return self.successful_scrapes / self.total_articles_scraped * 100
    
    @property
    def average_content_length(self) -> int:
        if self.successful_scrapes == 0:
            return 0
        return self.total_content_chars // self.successful_scrapes

@dataclass
class TrainingExample:
    """Training example for fine-tuning"""
    system_prompt: str
    user_input: str
    assistant_response: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_openai_format(self) -> Dict[str, List[Dict[str, str]]]:
        """Convert to OpenAI fine-tuning format"""
        return {
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_input},
                {"role": "assistant", "content": self.assistant_response}
            ]
        }

@dataclass
class DatasetStats:
    """Statistics about generated dataset"""
    total_examples: int = 0
    train_examples: int = 0
    validation_examples: int = 0
    system_prompt_variations: int = 0
    user_prompt_variations: int = 0
    categories_covered: List[str] = None
    avg_system_prompt_length: int = 0
    avg_user_input_length: int = 0
    avg_assistant_response_length: int = 0
    
    def __post_init__(self):
        if self.categories_covered is None:
            self.categories_covered = []

@dataclass
class ScrapingResult:
    """Result of scraping operation"""
    success: bool
    url: str
    content: Optional[ArticleContent] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    
    @property
    def is_valid(self) -> bool:
        """Check if result has valid content"""
        return self.success and self.content is not None and len(self.content.text_content) >= 100