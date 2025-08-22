import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
    
    # Article generation settings
    MAX_QUALITY_ITERATIONS = 3
    QUALITY_THRESHOLD = 0.85
    
    # Web scraping settings
    REQUEST_TIMEOUT = 10
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # OpenAI settings
    OPENAI_MODEL = "gpt-4.1-mini"
    MAX_TOKENS = 4000
    TEMPERATURE = 0.7

settings = Settings()