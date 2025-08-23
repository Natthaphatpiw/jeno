"""
LoRA Fine-tuning script for Together AI
Based on the Together AI documentation example
"""

from together import Together
import os
import json

# Load API key from environment
from dotenv import load_dotenv
load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
WANDB_API_KEY = os.getenv("WANDB_API_KEY")  # Optional, for logging fine-tuning to wandb

def start_lora_finetuning(train_file_id, validation_file_id=None, model_name='meta-llama/Meta-Llama-3.1-8B-Instruct-Reference'):
    """
    Start LoRA fine-tuning job with Together AI
    
    Args:
        train_file_id: ID of uploaded training file
        validation_file_id: ID of uploaded validation file (optional)
        model_name: Base model to fine-tune
    """
    
    client = Together(api_key=TOGETHER_API_KEY)
    
    print(f"Starting LoRA fine-tuning with model: {model_name}")
    print(f"Training file ID: {train_file_id}")
    if validation_file_id:
        print(f"Validation file ID: {validation_file_id}")
    
    # Fine-tuning configuration
    ft_config = {
        "training_file": train_file_id,
        "model": model_name,
        "train_on_inputs": "auto",
        "n_epochs": 3,
        "n_checkpoints": 1,
        "lora": True,  # Enable LoRA (default True)
        "warmup_ratio": 0,
        "learning_rate": 1e-5,
        "suffix": 'jetask_content_model',
    }
    
    # Add validation file if provided
    if validation_file_id:
        ft_config["validation_file"] = validation_file_id
    
    # Add wandb logging if API key is available
    if WANDB_API_KEY:
        ft_config["wandb_api_key"] = WANDB_API_KEY
    
    # Start fine-tuning job
    ft_resp = client.fine_tuning.create(**ft_config)
    
    print(f"\n✅ Fine-tuning job started!")
    print(f"Job ID: {ft_resp.id}")
    print(f"Status: {ft_resp.status}")
    print(f"\n📝 Save this job ID for monitoring: {ft_resp.id}")
    
    return ft_resp.id

def start_finetuning_with_file_ids():
    """Interactive function to start fine-tuning with file IDs"""
    
    print("=== Together AI LoRA Fine-tuning ===")
    print("This script will start a LoRA fine-tuning job.")
    print("Make sure you have already uploaded your data files using data_checker.py\n")
    
    # Get file IDs from user
    train_file_id = input("Enter training file ID: ").strip()
    validation_file_id = input("Enter validation file ID (optional, press Enter to skip): ").strip()
    
    if not validation_file_id:
        validation_file_id = None
    
    # Get model choice
    print("\nAvailable models:")
    print("1. meta-llama/Meta-Llama-3.1-8B-Instruct-Reference (default)")
    print("2. meta-llama/Meta-Llama-3.1-70B-Instruct-Reference")
    print("3. mistralai/Mixtral-8x7B-Instruct-v0.1")
    
    model_choice = input("Choose model (1-3, or press Enter for default): ").strip()
    
    model_map = {
        "1": "meta-llama/Meta-Llama-3.1-8B-Instruct-Reference",
        "2": "meta-llama/Meta-Llama-3.1-70B-Instruct-Reference", 
        "3": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "": "meta-llama/Meta-Llama-3.1-8B-Instruct-Reference"
    }
    
    model_name = model_map.get(model_choice, "meta-llama/Meta-Llama-3.1-8B-Instruct-Reference")
    
    # Start fine-tuning
    job_id = start_lora_finetuning(train_file_id, validation_file_id, model_name)
    
    print(f"\n🚀 Fine-tuning job is now running!")
    print(f"Expected completion time: ~10-15 minutes")
    print(f"Use monitor_finetuning.py with job ID: {job_id}")

if __name__ == "__main__":
    start_finetuning_with_file_ids()