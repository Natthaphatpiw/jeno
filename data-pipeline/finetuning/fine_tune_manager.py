#!/usr/bin/env python3
"""Fine-tuning job manager for OpenAI models"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import asdict

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fine_tune_config import config
from utils.logger import get_logger

logger = get_logger(__name__)

class FineTuneManager:
    """Manages OpenAI fine-tuning jobs"""
    
    def __init__(self):
        """Initialize the fine-tuning manager"""
        config.validate()
        self.api_key = config.api_key
        self.base_url = config.base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Ensure logs directory exists
        os.makedirs(config.logs_dir, exist_ok=True)
        
    def upload_training_file(self, file_path: str, purpose: str = "fine-tune") -> Optional[str]:
        """
        Upload training data file to OpenAI
        
        Args:
            file_path: Path to the training file
            purpose: Purpose of the file (default: "fine-tune")
            
        Returns:
            File ID if successful, None otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"Training file not found: {file_path}")
            return None
            
        logger.info(f"Uploading training file: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                files = {
                    'file': f,
                    'purpose': (None, purpose)
                }
                
                response = requests.post(
                    f"{self.base_url}/files",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files=files
                )
                
            if response.status_code == 200:
                file_data = response.json()
                file_id = file_data.get('id')
                logger.info(f"✅ File uploaded successfully. File ID: {file_id}")
                logger.info(f"File details: {file_data}")
                return file_id
            else:
                logger.error(f"Failed to upload file: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return None
    
    def create_fine_tuning_job(self, training_file_id: str, validation_file_id: Optional[str] = None) -> Optional[str]:
        """
        Create a fine-tuning job
        
        Args:
            training_file_id: ID of the uploaded training file
            validation_file_id: ID of the uploaded validation file (optional)
            
        Returns:
            Job ID if successful, None otherwise
        """
        logger.info(f"Creating fine-tuning job with model: {config.base_model}")
        
        job_data = {
            "training_file": training_file_id,
            "model": config.base_model
        }
        
        # Add optional parameters
        if validation_file_id:
            job_data["validation_file"] = validation_file_id
            
        if config.suffix:
            job_data["suffix"] = config.suffix
            
        if config.n_epochs:
            job_data["hyperparameters"] = {"n_epochs": config.n_epochs}
            
        if config.batch_size:
            if "hyperparameters" not in job_data:
                job_data["hyperparameters"] = {}
            job_data["hyperparameters"]["batch_size"] = config.batch_size
            
        if config.learning_rate_multiplier:
            if "hyperparameters" not in job_data:
                job_data["hyperparameters"] = {}
            job_data["hyperparameters"]["learning_rate_multiplier"] = config.learning_rate_multiplier
        
        try:
            response = requests.post(
                f"{self.base_url}/fine_tuning/jobs",
                headers=self.headers,
                json=job_data
            )
            
            if response.status_code == 200:
                job_info = response.json()
                job_id = job_info.get('id')
                logger.info(f"✅ Fine-tuning job created successfully. Job ID: {job_id}")
                logger.info(f"Job details: {job_info}")
                
                # Save job info
                self._save_job_info(job_info)
                return job_id
            else:
                logger.error(f"Failed to create fine-tuning job: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating fine-tuning job: {e}")
            return None
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """
        Get the status of a fine-tuning job
        
        Args:
            job_id: ID of the fine-tuning job
            
        Returns:
            Job status information if successful, None otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/fine_tuning/jobs/{job_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get job status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting job status: {e}")
            return None
    
    def list_jobs(self, limit: int = 20) -> Optional[List[Dict]]:
        """
        List fine-tuning jobs
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of job information if successful, None otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/fine_tuning/jobs?limit={limit}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"Failed to list jobs: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error listing jobs: {e}")
            return None
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a fine-tuning job
        
        Args:
            job_id: ID of the fine-tuning job
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/fine_tuning/jobs/{job_id}/cancel",
                headers=self.headers
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Job {job_id} cancelled successfully")
                return True
            else:
                logger.error(f"Failed to cancel job: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelling job: {e}")
            return False
    
    def run_complete_pipeline(self) -> Optional[str]:
        """
        Run the complete fine-tuning pipeline
        
        Returns:
            Fine-tuned model ID if successful, None otherwise
        """
        logger.info("🚀 Starting complete fine-tuning pipeline")
        
        # Step 1: Upload training file
        logger.info("Step 1: Uploading training file...")
        training_file_id = self.upload_training_file(config.training_file_path)
        if not training_file_id:
            logger.error("Failed to upload training file")
            return None
        
        # Step 2: Upload validation file if exists
        validation_file_id = None
        if os.path.exists(config.validation_file_path):
            logger.info("Step 2: Uploading validation file...")
            validation_file_id = self.upload_training_file(config.validation_file_path)
            if validation_file_id:
                logger.info("Validation file uploaded successfully")
            else:
                logger.warning("Failed to upload validation file, continuing without it")
        else:
            logger.info("Step 2: No validation file found, skipping...")
        
        # Step 3: Create fine-tuning job
        logger.info("Step 3: Creating fine-tuning job...")
        job_id = self.create_fine_tuning_job(training_file_id, validation_file_id)
        if not job_id:
            logger.error("Failed to create fine-tuning job")
            return None
        
        logger.info(f"✅ Pipeline initiated successfully!")
        logger.info(f"Job ID: {job_id}")
        logger.info("Use the monitor script to track progress: python fine_tune_monitor.py")
        
        return job_id
    
    def _save_job_info(self, job_info: Dict):
        """Save job information to file"""
        try:
            # Load existing jobs
            jobs = []
            if os.path.exists(config.jobs_file):
                with open(config.jobs_file, 'r') as f:
                    jobs = json.load(f)
            
            # Add new job
            job_record = {
                **job_info,
                'created_at_local': datetime.now().isoformat(),
                'config_used': asdict(config)
            }
            jobs.append(job_record)
            
            # Save updated jobs
            with open(config.jobs_file, 'w') as f:
                json.dump(jobs, f, indent=2)
                
            logger.info(f"Job info saved to {config.jobs_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save job info: {e}")

def main():
    """Main function to run fine-tuning"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        manager = FineTuneManager()
        
        if command == "upload":
            if len(sys.argv) < 3:
                print("Usage: python fine_tune_manager.py upload <file_path>")
                return
            file_id = manager.upload_training_file(sys.argv[2])
            if file_id:
                print(f"File uploaded successfully. ID: {file_id}")
                
        elif command == "create":
            if len(sys.argv) < 3:
                print("Usage: python fine_tune_manager.py create <training_file_id> [validation_file_id]")
                return
            validation_id = sys.argv[3] if len(sys.argv) > 3 else None
            job_id = manager.create_fine_tuning_job(sys.argv[2], validation_id)
            if job_id:
                print(f"Fine-tuning job created successfully. ID: {job_id}")
                
        elif command == "status":
            if len(sys.argv) < 3:
                print("Usage: python fine_tune_manager.py status <job_id>")
                return
            status = manager.get_job_status(sys.argv[2])
            if status:
                print(json.dumps(status, indent=2))
                
        elif command == "list":
            jobs = manager.list_jobs()
            if jobs:
                for job in jobs:
                    print(f"ID: {job['id']}, Status: {job['status']}, Model: {job.get('fine_tuned_model', 'N/A')}")
                    
        elif command == "cancel":
            if len(sys.argv) < 3:
                print("Usage: python fine_tune_manager.py cancel <job_id>")
                return
            success = manager.cancel_job(sys.argv[2])
            if success:
                print("Job cancelled successfully")
                
        elif command == "run":
            job_id = manager.run_complete_pipeline()
            if job_id:
                print(f"Pipeline started successfully. Job ID: {job_id}")
        else:
            print("Available commands: upload, create, status, list, cancel, run")
    else:
        # Run complete pipeline by default
        manager = FineTuneManager()
        job_id = manager.run_complete_pipeline()
        if job_id:
            print(f"Pipeline started successfully. Job ID: {job_id}")

if __name__ == "__main__":
    main()