#!/usr/bin/env python3
"""Test script for fine-tuned models"""

import json
import requests
from typing import Dict, List, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fine_tune_config import config
from utils.logger import get_logger

logger = get_logger(__name__)

class ModelTester:
    """Test fine-tuned models"""
    
    def __init__(self):
        """Initialize the model tester"""
        config.validate()
        self.api_key = config.api_key
        self.base_url = config.base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def test_model(self, model_id: str, messages: List[Dict], max_tokens: int = 500) -> Optional[str]:
        """
        Test a fine-tuned model with chat completion
        
        Args:
            model_id: ID of the fine-tuned model
            messages: List of messages for chat completion
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response if successful, None otherwise
        """
        try:
            data = {
                "model": model_id,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"API request failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error testing model: {e}")
            return None
    
    def run_test_suite(self, model_id: str):
        """Run a comprehensive test suite"""
        print(f"🧪 Testing fine-tuned model: {model_id}\n")
        
        # Test cases based on Jenosize content types
        test_cases = [
            {
                "name": "Content Creation - Futurist Topic",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert content creator for Jenosize, a leading digital transformation consultancy. Create engaging, professional content that showcases thought leadership in business innovation."
                    },
                    {
                        "role": "user", 
                        "content": "Write about the future of AI in business transformation. Focus on practical applications and real-world impact."
                    }
                ]
            },
            {
                "name": "Content Creation - Consumer Insights",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert content creator for Jenosize, a leading digital transformation consultancy. Create engaging, professional content that showcases thought leadership in business innovation."
                    },
                    {
                        "role": "user",
                        "content": "Explain how consumer behavior has changed in the digital age and what this means for businesses."
                    }
                ]
            },
            {
                "name": "Content Creation - Digital Transformation",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert content creator for Jenosize, a leading digital transformation consultancy. Create engaging, professional content that showcases thought leadership in business innovation."
                    },
                    {
                        "role": "user",
                        "content": "Describe the key challenges organizations face when implementing digital transformation initiatives."
                    }
                ]
            },
            {
                "name": "Content Summarization",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert content creator for Jenosize, a leading digital transformation consultancy. Create engaging, professional content that showcases thought leadership in business innovation."
                    },
                    {
                        "role": "user",
                        "content": "Summarize the key trends in real-time marketing and their impact on customer engagement."
                    }
                ]
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i}: {test_case['name']}")
            print("=" * 50)
            
            response = self.test_model(model_id, test_case['messages'])
            
            if response:
                print(f"✅ Success!\n")
                print("Response:")
                print("-" * 30)
                print(response)
                print("\n" + "="*80 + "\n")
                
                results.append({
                    "test_name": test_case['name'],
                    "status": "success",
                    "response": response,
                    "response_length": len(response)
                })
            else:
                print(f"❌ Failed!\n")
                results.append({
                    "test_name": test_case['name'],
                    "status": "failed",
                    "response": None,
                    "response_length": 0
                })
        
        # Print summary
        successful = sum(1 for r in results if r['status'] == 'success')
        total = len(results)
        
        print(f"📊 Test Summary: {successful}/{total} tests passed")
        
        if successful > 0:
            avg_response_length = sum(r['response_length'] for r in results if r['status'] == 'success') / successful
            print(f"📝 Average response length: {avg_response_length:.0f} characters")
        
        # Save results
        self._save_test_results(model_id, results)
        
        return results
    
    def _save_test_results(self, model_id: str, results: List[Dict]):
        """Save test results to file"""
        try:
            results_file = f"/Users/piw/Downloads/jetask/data-pipeline/finetuning/test_results_{model_id.replace(':', '_')}_{int(time.time())}.json"
            
            test_data = {
                "model_id": model_id,
                "test_date": datetime.now().isoformat(),
                "results": results,
                "summary": {
                    "total_tests": len(results),
                    "successful_tests": sum(1 for r in results if r['status'] == 'success'),
                    "success_rate": sum(1 for r in results if r['status'] == 'success') / len(results) * 100
                }
            }
            
            with open(results_file, 'w') as f:
                json.dump(test_data, f, indent=2)
            
            print(f"💾 Test results saved to: {results_file}")
            
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")

def main():
    """Main function"""
    import sys
    from datetime import datetime
    import time
    
    if len(sys.argv) < 2:
        print("Usage: python test_model.py <fine_tuned_model_id>")
        print("Example: python test_model.py ft:gpt-4o-mini-2024-07-18:openai::abc123")
        return
    
    model_id = sys.argv[1]
    tester = ModelTester()
    tester.run_test_suite(model_id)

if __name__ == "__main__":
    main()