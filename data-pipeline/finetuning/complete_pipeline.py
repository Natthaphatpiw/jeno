"""
Complete fine-tuning pipeline - runs all steps in sequence
From data checking to model training
"""

from together import Together
from together.utils import check_file
import os
import json
import time

# Hardcoded API key as requested
TOGETHER_API_KEY = "74cc536c6a77ccd61c6a09a89e8a36e97c66ebdf95bce95e541b67da5c5a9b97"

def run_complete_pipeline():
    """Run the complete fine-tuning pipeline"""
    
    print("=== Complete Fine-tuning Pipeline ===")
    print("This will check data, upload files, and start fine-tuning\n")
    
    client = Together(api_key=TOGETHER_API_KEY)
    
    # Step 1: Check data format
    print("Step 1: Checking data format...")
    train_file_path = "/Users/piw/Downloads/jetask/data-pipeline/output/clean_training_data_train.jsonl"
    validation_file_path = "/Users/piw/Downloads/jetask/data-pipeline/output/clean_training_data_validation.jsonl"
    
    # Check training data
    print("  Checking training data...")
    train_report = check_file(train_file_path)
    
    # Check validation data
    print("  Checking validation data...")
    validation_report = check_file(validation_file_path)
    
    if not (train_report["is_check_passed"] and validation_report["is_check_passed"]):
        print("❌ Data format check failed!")
        print("Training data check:", train_report["is_check_passed"])
        print("Validation data check:", validation_report["is_check_passed"])
        return
    
    print("✅ Data format check passed!")
    
    # Step 2: Upload data
    print("\nStep 2: Uploading data files...")
    
    try:
        # Upload training data
        print("  Uploading training data...")
        train_file_resp = client.files.upload(train_file_path, check=True)
        print(f"  Training file uploaded. ID: {train_file_resp.id}")
        
        # Upload validation data
        print("  Uploading validation data...")
        validation_file_resp = client.files.upload(validation_file_path, check=True)
        print(f"  Validation file uploaded. ID: {validation_file_resp.id}")
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return
    
    print("✅ Data upload completed!")
    
    # Step 3: Start fine-tuning
    print("\nStep 3: Starting fine-tuning...")
    
    # Fine-tuning configuration
    ft_config = {
        "training_file": train_file_resp.id,
        "validation_file": validation_file_resp.id,
        "model": 'meta-llama/Meta-Llama-3.1-8B-Instruct-Reference',
        "train_on_inputs": "auto",
        "n_epochs": 3,
        "n_checkpoints": 1,
        "lora": True,
        "warmup_ratio": 0,
        "learning_rate": 1e-5,
        "suffix": 'jetask_content_model',
    }
    
    try:
        ft_resp = client.fine_tuning.create(**ft_config)
        print(f"✅ Fine-tuning job started!")
        print(f"Job ID: {ft_resp.id}")
        print(f"Status: {ft_resp.status}")
        
    except Exception as e:
        print(f"❌ Fine-tuning start failed: {e}")
        return
    
    # Step 4: Save job information
    print("\nStep 4: Saving job information...")
    
    job_info = {
        "job_id": ft_resp.id,
        "status": ft_resp.status,
        "model": ft_config["model"],
        "training_file_id": train_file_resp.id,
        "validation_file_id": validation_file_resp.id,
        "config": ft_config,
        "created_at": time.time()
    }
    
    with open("/Users/piw/Downloads/jetask/data-pipeline/finetuning/current_job.json", "w") as f:
        json.dump(job_info, f, indent=2)
    
    print("✅ Job information saved to current_job.json")
    
    # Step 5: Basic monitoring
    print(f"\n🚀 Fine-tuning pipeline completed!")
    print(f"Job ID: {ft_resp.id}")
    print(f"Expected completion time: ~10-15 minutes")
    print(f"Use monitor_finetuning.py to track progress")
    print(f"Or check status with: python -c \"from together import Together; print(Together(api_key='{TOGETHER_API_KEY}').fine_tuning.retrieve('{ft_resp.id}').status)\"")

if __name__ == "__main__":
    run_complete_pipeline()