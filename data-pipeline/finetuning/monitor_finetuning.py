"""
Monitor fine-tuning job status and logs
Based on Together AI documentation example
"""

from together import Together
import time
import json

# Hardcoded API key as requested
TOGETHER_API_KEY = "74cc536c6a77ccd61c6a09a89e8a36e97c66ebdf95bce95e541b67da5c5a9b97"

def check_job_status(job_id):
    """Check the status of a fine-tuning job"""
    
    client = Together(api_key=TOGETHER_API_KEY)
    
    try:
        resp = client.fine_tuning.retrieve(job_id)
        return resp
    except Exception as e:
        print(f"Error retrieving job status: {e}")
        return None

def get_job_logs(job_id):
    """Get logs from a fine-tuning job"""
    
    client = Together(api_key=TOGETHER_API_KEY)
    
    try:
        events = client.fine_tuning.list_events(id=job_id).data
        return events
    except Exception as e:
        print(f"Error retrieving job logs: {e}")
        return []

def monitor_job(job_id, check_interval=30):
    """Monitor a fine-tuning job until completion"""
    
    print(f"Monitoring fine-tuning job: {job_id}")
    print(f"Checking status every {check_interval} seconds...")
    print("Press Ctrl+C to stop monitoring (job will continue running)\n")
    
    try:
        while True:
            # Check job status
            status_resp = check_job_status(job_id)
            
            if status_resp:
                print(f"Status: {status_resp.status}")
                
                if status_resp.status in ['completed', 'failed', 'cancelled']:
                    print(f"\n🏁 Job finished with status: {status_resp.status}")
                    
                    if status_resp.status == 'completed':
                        print(f"✅ Fine-tuned model ready!")
                        if hasattr(status_resp, 'fine_tuned_model'):
                            print(f"Model ID: {status_resp.fine_tuned_model}")
                    
                    break
                
                # Show recent logs
                print("Recent logs:")
                logs = get_job_logs(job_id)
                for event in logs[-5:]:  # Show last 5 log entries
                    print(f"  {event.message}")
                print("-" * 50)
            
            else:
                print("Failed to get job status")
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print(f"\n⏸️  Stopped monitoring job {job_id}")
        print("Job will continue running in the background")
        print("Run this script again to resume monitoring")

def show_job_details(job_id):
    """Show detailed information about a fine-tuning job"""
    
    status_resp = check_job_status(job_id)
    
    if not status_resp:
        print("Failed to get job details")
        return
    
    print("=== Job Details ===")
    print(f"Job ID: {job_id}")
    print(f"Status: {status_resp.status}")
    print(f"Model: {status_resp.model}")
    
    if hasattr(status_resp, 'created_at'):
        print(f"Created: {status_resp.created_at}")
    
    if hasattr(status_resp, 'fine_tuned_model') and status_resp.fine_tuned_model:
        print(f"Fine-tuned Model: {status_resp.fine_tuned_model}")
    
    if hasattr(status_resp, 'training_file'):
        print(f"Training File: {status_resp.training_file}")
    
    if hasattr(status_resp, 'validation_file') and status_resp.validation_file:
        print(f"Validation File: {status_resp.validation_file}")
    
    print("\n=== Recent Logs ===")
    logs = get_job_logs(job_id)
    
    if logs:
        for event in logs[-10:]:  # Show last 10 log entries
            print(f"  {event.message}")
    else:
        print("  No logs available")

def main():
    """Main function for interactive monitoring"""
    
    print("=== Fine-tuning Job Monitor ===")
    
    job_id = input("Enter fine-tuning job ID: ").strip()
    
    if not job_id:
        print("Job ID is required!")
        return
    
    print("\nChoose an option:")
    print("1. Monitor job continuously")
    print("2. Check job status once")
    print("3. Show detailed job information")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        interval = input("Check interval in seconds (default 30): ").strip()
        try:
            interval = int(interval) if interval else 30
        except ValueError:
            interval = 30
        
        monitor_job(job_id, interval)
    
    elif choice == "2":
        status_resp = check_job_status(job_id)
        if status_resp:
            print(f"\nJob Status: {status_resp.status}")
        else:
            print("Failed to get job status")
    
    elif choice == "3":
        show_job_details(job_id)
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()