import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
    
    # Article generation settings
    MAX_QUALITY_ITERATIONS = 3
    QUALITY_THRESHOLD = 0.85
    
    # Web scraping settings
    REQUEST_TIMEOUT = 10
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # OpenAI settings
    # OPENAI_MODEL = "ft:gpt-4.1-mini-2025-04-14:codelabdev:jenosize-content:C7LDOFr7"  # Fine-tuned model
    # OPENAI_MODEL = "gpt-4o-mini"  # Base model (backup)
    # OPENAI_MODEL = "gpt-4.1-mini"
    OPENAI_MODEL = "ft:gpt-4.1-mini-2025-04-14:codelabdev:jenosize-content:C7SVORLy"
    MAX_TOKENS = 8000  # Increased for executive-level content depth
    TEMPERATURE = 0.7

settings = Settings()