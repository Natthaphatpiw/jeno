"""Fine-tuning configuration settings"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class FineTuningConfig:
    """Configuration for fine-tuning jobs"""
    
    # OpenAI API settings
    api_key: str = "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"
    base_url: str = "https://api.openai.com/v1"
    
    # Model settings
    base_model: str = "gpt-4.1-mini-2025-04-14"  # Using gpt-4o-mini as requested
    
    # Training settings
    training_file_path: str = "/Users/piw/Downloads/jetask/data-pipeline/output/clean_training_data_train.jsonl"
    validation_file_path: str = "/Users/piw/Downloads/jetask/data-pipeline/output/clean_training_data_validation.jsonl"
    
    # Fine-tuning parameters
    n_epochs: Optional[int] = None  # Auto-determined by OpenAI
    batch_size: Optional[int] = None  # Auto-determined by OpenAI  
    learning_rate_multiplier: Optional[float] = None  # Auto-determined by OpenAI
    
    # Job settings
    suffix: Optional[str] = "jenosize-content"  # Will be appended to model name
    
    # Output settings
    jobs_file: str = "/Users/piw/Downloads/jetask/data-pipeline/finetuning/jobs.json"
    logs_dir: str = "/Users/piw/Downloads/jetask/data-pipeline/finetuning/logs"
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        if not os.path.exists(self.training_file_path):
            raise ValueError(f"Training file not found: {self.training_file_path}")
            
        return True

# Global config instance
config = FineTuningConfig()