#!/usr/bin/env python3
"""Fine-tuning job monitor and status checker"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich import print as rprint

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fine_tune_config import config
from utils.logger import get_logger

logger = get_logger(__name__)
console = Console()

class FineTuneMonitor:
    """Monitor fine-tuning jobs with real-time updates"""
    
    def __init__(self):
        """Initialize the monitor"""
        config.validate()
        self.api_key = config.api_key
        self.base_url = config.base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get detailed job status"""
        try:
            response = requests.get(
                f"{self.base_url}/fine_tuning/jobs/{job_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get job status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting job status: {e}")
            return None
    
    def get_job_events(self, job_id: str) -> Optional[List[Dict]]:
        """Get job events/logs"""
        try:
            response = requests.get(
                f"{self.base_url}/fine_tuning/jobs/{job_id}/events",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"Failed to get job events: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting job events: {e}")
            return None
    
    def format_status_display(self, job_status: Dict) -> Table:
        """Format job status for display"""
        table = Table(title=f"Fine-tuning Job Status: {job_status.get('id', 'N/A')}")
        
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        
        # Basic info
        table.add_row("Status", job_status.get('status', 'Unknown'))
        table.add_row("Model", job_status.get('model', 'N/A'))
        table.add_row("Fine-tuned Model", job_status.get('fine_tuned_model', 'N/A'))
        
        # Training details
        if 'training_file' in job_status:
            table.add_row("Training File", job_status['training_file'])
        if 'validation_file' in job_status:
            table.add_row("Validation File", job_status['validation_file'])
        
        # Timestamps
        created_at = job_status.get('created_at')
        if created_at:
            created_time = datetime.fromtimestamp(created_at)
            table.add_row("Created At", created_time.strftime('%Y-%m-%d %H:%M:%S'))
        
        finished_at = job_status.get('finished_at')
        if finished_at:
            finished_time = datetime.fromtimestamp(finished_at)
            table.add_row("Finished At", finished_time.strftime('%Y-%m-%d %H:%M:%S'))
            
            # Calculate duration
            if created_at:
                duration = finished_time - created_time
                table.add_row("Duration", str(duration))
        
        # Hyperparameters
        hyperparams = job_status.get('hyperparameters', {})
        if hyperparams:
            table.add_row("Epochs", str(hyperparams.get('n_epochs', 'Auto')))
            table.add_row("Batch Size", str(hyperparams.get('batch_size', 'Auto')))
            table.add_row("Learning Rate Multiplier", str(hyperparams.get('learning_rate_multiplier', 'Auto')))
        
        # Results
        if 'result_files' in job_status and job_status['result_files']:
            table.add_row("Result Files", str(len(job_status['result_files'])))
        
        # Error info
        if job_status.get('error'):
            error_info = job_status['error']
            table.add_row("Error", f"{error_info.get('code', 'N/A')}: {error_info.get('message', 'N/A')}")
        
        return table
    
    def display_job_events(self, events: List[Dict], limit: int = 10):
        """Display recent job events"""
        if not events:
            console.print("No events found", style="yellow")
            return
        
        table = Table(title="Recent Job Events")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Level", style="green")
        table.add_column("Message", style="white")
        
        # Sort events by timestamp (newest first) and limit
        sorted_events = sorted(events, key=lambda x: x.get('created_at', 0), reverse=True)[:limit]
        
        for event in sorted_events:
            timestamp = datetime.fromtimestamp(event.get('created_at', 0)).strftime('%H:%M:%S')
            level = event.get('level', 'info')
            message = event.get('message', '')
            
            # Color code by level
            level_style = "green" if level == "info" else "yellow" if level == "warn" else "red"
            table.add_row(timestamp, f"[{level_style}]{level}[/{level_style}]", message)
        
        console.print(table)
    
    def monitor_job(self, job_id: str, refresh_interval: int = 30, show_events: bool = True):
        """Monitor a job with live updates"""
        console.print(f"🔍 Monitoring job: {job_id}")
        console.print(f"Refresh interval: {refresh_interval} seconds")
        console.print("Press Ctrl+C to stop monitoring\n")
        
        try:
            while True:
                # Get current status
                status = self.get_job_status(job_id)
                if not status:
                    console.print("❌ Failed to get job status", style="red")
                    break
                
                # Clear screen and display status
                console.clear()
                console.print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                console.print(self.format_status_display(status))
                
                # Display events if requested
                if show_events:
                    events = self.get_job_events(job_id)
                    if events:
                        console.print("\n")
                        self.display_job_events(events)
                
                # Check if job is finished
                job_status = status.get('status', '')
                if job_status in ['succeeded', 'failed', 'cancelled']:
                    console.print(f"\n🎯 Job {job_status.upper()}!", style="green" if job_status == "succeeded" else "red")
                    
                    if job_status == 'succeeded':
                        fine_tuned_model = status.get('fine_tuned_model')
                        if fine_tuned_model:
                            console.print(f"✅ Fine-tuned model ID: {fine_tuned_model}", style="green bold")
                            console.print(f"You can now use this model in your API calls!", style="green")
                    
                    break
                
                # Wait before next refresh
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            console.print("\n👋 Monitoring stopped by user")
    
    def list_all_jobs(self, limit: int = 20):
        """List all fine-tuning jobs"""
        try:
            response = requests.get(
                f"{self.base_url}/fine_tuning/jobs?limit={limit}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                jobs = response.json().get('data', [])
                
                if not jobs:
                    console.print("No fine-tuning jobs found", style="yellow")
                    return
                
                table = Table(title="Fine-tuning Jobs")
                table.add_column("ID", style="cyan", no_wrap=True)
                table.add_column("Status", style="magenta")
                table.add_column("Model", style="green")
                table.add_column("Fine-tuned Model", style="blue")
                table.add_column("Created", style="yellow")
                
                for job in jobs:
                    job_id = job.get('id', 'N/A')
                    status = job.get('status', 'Unknown')
                    model = job.get('model', 'N/A')
                    fine_tuned_model = job.get('fine_tuned_model', 'N/A')
                    created_at = job.get('created_at', 0)
                    created_time = datetime.fromtimestamp(created_at).strftime('%m/%d %H:%M')
                    
                    # Style status with colors
                    if status == 'succeeded':
                        status = f"[green]{status}[/green]"
                    elif status == 'failed':
                        status = f"[red]{status}[/red]"
                    elif status == 'running':
                        status = f"[yellow]{status}[/yellow]"
                    
                    table.add_row(job_id, status, model, fine_tuned_model, created_time)
                
                console.print(table)
            else:
                console.print(f"❌ Failed to list jobs: {response.status_code}", style="red")
                
        except Exception as e:
            console.print(f"❌ Error listing jobs: {e}", style="red")
    
    def save_job_logs(self, job_id: str):
        """Save job logs to file"""
        events = self.get_job_events(job_id)
        if not events:
            console.print("No events to save", style="yellow")
            return
        
        log_file = os.path.join(config.logs_dir, f"job_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        try:
            with open(log_file, 'w') as f:
                json.dump(events, f, indent=2)
            
            console.print(f"✅ Logs saved to: {log_file}", style="green")
        except Exception as e:
            console.print(f"❌ Failed to save logs: {e}", style="red")

def main():
    """Main function"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor fine-tuning jobs")
    parser.add_argument("command", choices=["monitor", "status", "list", "events", "save-logs"], 
                       help="Command to execute")
    parser.add_argument("job_id", nargs="?", help="Job ID (required for monitor, status, events, save-logs)")
    parser.add_argument("--refresh", "-r", type=int, default=30, 
                       help="Refresh interval in seconds for monitoring (default: 30)")
    parser.add_argument("--no-events", action="store_true", 
                       help="Don't show events during monitoring")
    parser.add_argument("--limit", "-l", type=int, default=20, 
                       help="Limit number of results (default: 20)")
    
    args = parser.parse_args()
    
    monitor = FineTuneMonitor()
    
    if args.command == "monitor":
        if not args.job_id:
            console.print("❌ Job ID is required for monitoring", style="red")
            return
        monitor.monitor_job(args.job_id, args.refresh, not args.no_events)
        
    elif args.command == "status":
        if not args.job_id:
            console.print("❌ Job ID is required for status", style="red")
            return
        status = monitor.get_job_status(args.job_id)
        if status:
            console.print(monitor.format_status_display(status))
        
    elif args.command == "list":
        monitor.list_all_jobs(args.limit)
        
    elif args.command == "events":
        if not args.job_id:
            console.print("❌ Job ID is required for events", style="red")
            return
        events = monitor.get_job_events(args.job_id)
        if events:
            monitor.display_job_events(events, args.limit)
        
    elif args.command == "save-logs":
        if not args.job_id:
            console.print("❌ Job ID is required for save-logs", style="red")
            return
        monitor.save_job_logs(args.job_id)

if __name__ == "__main__":
    main()