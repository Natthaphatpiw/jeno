"""
Data format checker and uploader for Together AI fine-tuning
Based on CoQA dataset example from Together AI documentation
"""

from together import Together
from together.utils import check_file
import os
import json

# Load API key from environment
from dotenv import load_dotenv
load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

def check_training_data():
    """Check if the training data files are properly formatted"""
    
    client = Together(api_key=TOGETHER_API_KEY)
    
    # Check training data
    train_file_path = "/Users/piw/Downloads/jetask/data-pipeline/output/clean_training_data_train.jsonl"
    print("Checking training data format...")
    train_report = check_file(train_file_path)
    print("Training data report:")
    print(json.dumps(train_report, indent=2))
    
    # Check validation data
    validation_file_path = "/Users/piw/Downloads/jetask/data-pipeline/output/clean_training_data_validation.jsonl"
    print("\nChecking validation data format...")
    validation_report = check_file(validation_file_path)
    print("Validation data report:")
    print(json.dumps(validation_report, indent=2))
    
    return train_report["is_check_passed"] and validation_report["is_check_passed"]

def upload_training_data():
    """Upload training and validation data to Together AI"""
    
    client = Together(api_key=TOGETHER_API_KEY)
    
    # Upload training data
    train_file_path = "/Users/piw/Downloads/jetask/data-pipeline/output/clean_training_data_train.jsonl"
    print("Uploading training data...")
    train_file_resp = client.files.upload(train_file_path, check=True)
    print(f"Training file uploaded. ID: {train_file_resp.id}")
    
    # Upload validation data
    validation_file_path = "/Users/piw/Downloads/jetask/data-pipeline/output/clean_training_data_validation.jsonl"
    print("Uploading validation data...")
    validation_file_resp = client.files.upload(validation_file_path, check=True)
    print(f"Validation file uploaded. ID: {validation_file_resp.id}")
    
    return train_file_resp.id, validation_file_resp.id

if __name__ == "__main__":
    print("=== Data Format Checker ===")
    
    # Check data format first
    if check_training_data():
        print("\n✅ All data files are properly formatted!")
        
        # Upload data
        print("\n=== Uploading Data ===")
        train_id, validation_id = upload_training_data()
        
        print(f"\n📝 Save these IDs for fine-tuning:")
        print(f"Training file ID: {train_id}")
        print(f"Validation file ID: {validation_id}")
        
    else:
        print("\n❌ Data format check failed. Please fix the data format before proceeding.")