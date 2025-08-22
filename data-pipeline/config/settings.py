import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Base URL and categories
    BASE_URL = "https://www.jenosize.com"
    CATEGORY_URLS = [
        "https://www.jenosize.com/en/ideas/futurist",
        "https://www.jenosize.com/en/ideas/understand-people-and-consumer",
        "https://www.jenosize.com/en/ideas/transformation-and-technology",
        "https://www.jenosize.com/en/ideas/utility-for-our-world",
        "https://www.jenosize.com/en/ideas/real-time-marketing",
        "https://www.jenosize.com/en/ideas/experience-the-new-world"
    ]
    
    # CSS Selectors (Updated for actual website structure)
    ARTICLE_GRID_SELECTOR = ".grid"  # More flexible selector
    ARTICLE_LINK_SELECTOR = "a[href*='/ideas/']"  # Links that contain /ideas/ in href
    
    # Request settings
    REQUEST_TIMEOUT = 15
    REQUEST_DELAY = 1.0  # Seconds between requests
    MAX_RETRIES = 3
    RETRY_BACKOFF_FACTOR = 2.0
    
    # User Agent
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # File paths
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
    RAW_DIR = os.path.join(OUTPUT_DIR, "raw")
    PROCESSED_DIR = os.path.join(OUTPUT_DIR, "processed")
    
    # Dataset settings
    TRAIN_SPLIT_RATIO = 0.8
    MIN_CONTENT_LENGTH = 500  # Minimum article content length
    MAX_ARTICLES_PER_CATEGORY = 50  # Limit for development
    
    # Fine-tuning settings
    SYSTEM_PROMPT_VARIATIONS = 5
    USER_PROMPT_VARIATIONS = 10
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

settings = Settings()

# Category mapping for better organization
CATEGORY_MAPPING = {
    "futurist": "Future Trends & Innovation",
    "understand-people-and-consumer": "Consumer Insights & Behavior",
    "transformation-and-technology": "Digital Transformation",
    "utility-for-our-world": "Social Impact & Sustainability",
    "real-time-marketing": "Marketing & Strategy",
    "experience-the-new-world": "Customer Experience"
}