#!/usr/bin/env python3
"""
Script to switch between fine-tuned and base models
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

SETTINGS_PATH = Path(__file__).parent.parent / "config" / "settings.py"

FINE_TUNED_MODEL = "ft:gpt-4.1-mini-2025-04-14:codelabdev:jenosize-content:C7LDOFr7"
BASE_MODEL = "gpt-4o-mini"

def switch_to_finetuned():
    """Switch to fine-tuned model"""
    content = SETTINGS_PATH.read_text()
    
    # Replace base model with fine-tuned model
    content = content.replace(
        f'OPENAI_MODEL = "{BASE_MODEL}"', 
        f'OPENAI_MODEL = "{FINE_TUNED_MODEL}"  # Fine-tuned model'
    )
    content = content.replace(
        f'# OPENAI_MODEL = "{FINE_TUNED_MODEL}"',
        f'OPENAI_MODEL = "{FINE_TUNED_MODEL}"  # Fine-tuned model'
    )
    content = content.replace(
        f'OPENAI_MODEL = "{FINE_TUNED_MODEL}"',
        f'OPENAI_MODEL = "{FINE_TUNED_MODEL}"  # Fine-tuned model'
    )
    
    # Comment out base model
    if f'OPENAI_MODEL = "{BASE_MODEL}"' in content:
        content = content.replace(
            f'OPENAI_MODEL = "{BASE_MODEL}"',
            f'# OPENAI_MODEL = "{BASE_MODEL}"  # Base model (backup)'
        )
    
    SETTINGS_PATH.write_text(content)
    print(f"✅ Switched to fine-tuned model: {FINE_TUNED_MODEL}")

def switch_to_base():
    """Switch to base model"""
    content = SETTINGS_PATH.read_text()
    
    # Replace fine-tuned model with base model
    content = content.replace(
        f'OPENAI_MODEL = "{FINE_TUNED_MODEL}"  # Fine-tuned model',
        f'OPENAI_MODEL = "{BASE_MODEL}"'
    )
    content = content.replace(
        f'OPENAI_MODEL = "{FINE_TUNED_MODEL}"',
        f'OPENAI_MODEL = "{BASE_MODEL}"'
    )
    
    # Comment out fine-tuned model
    if f'OPENAI_MODEL = "{BASE_MODEL}"' in content and f'# OPENAI_MODEL = "{FINE_TUNED_MODEL}"' not in content:
        content = content.replace(
            f'OPENAI_MODEL = "{BASE_MODEL}"',
            f'OPENAI_MODEL = "{BASE_MODEL}"\n    # OPENAI_MODEL = "{FINE_TUNED_MODEL}"  # Fine-tuned model (backup)'
        )
    
    SETTINGS_PATH.write_text(content)
    print(f"✅ Switched to base model: {BASE_MODEL}")

def show_current():
    """Show current model configuration"""
    content = SETTINGS_PATH.read_text()
    
    for line in content.split('\n'):
        if 'OPENAI_MODEL = ' in line and not line.strip().startswith('#'):
            model = line.split('=')[1].strip().strip('"').split('#')[0].strip().strip('"')
            if model == FINE_TUNED_MODEL:
                print(f"🎯 Current model: Fine-tuned ({model})")
            elif model == BASE_MODEL:
                print(f"🔧 Current model: Base ({model})")
            else:
                print(f"❓ Current model: {model}")
            break
    else:
        print("❌ Could not determine current model")

def compare_models():
    """Compare fine-tuned vs base model capabilities"""
    print("\n📊 Model Comparison:")
    print("="*60)
    
    print("🎯 Fine-tuned Model Benefits:")
    print("  • Specialized for Jenosize content style")
    print("  • Better understanding of business consulting context")
    print("  • Improved Thai-English mixed content handling")
    print("  • Optimized for URL content instruction following")
    print("  • Higher quality business article generation")
    
    print("\n🔧 Base Model Benefits:")
    print("  • More general knowledge coverage")
    print("  • Better for diverse content types")
    print("  • Potentially better for non-business topics")
    print("  • Lower cost (if pricing differs)")
    print("  • More predictable behavior")
    
    print("\n💡 Recommendation:")
    print("  • Use fine-tuned model for Jenosize-style business content")
    print("  • Use base model for testing or diverse content needs")

def main():
    parser = argparse.ArgumentParser(description="Switch between OpenAI models")
    parser.add_argument("action", choices=["finetuned", "base", "status", "compare"], 
                       help="Action to perform")
    
    args = parser.parse_args()
    
    if args.action == "finetuned":
        switch_to_finetuned()
    elif args.action == "base":
        switch_to_base()
    elif args.action == "status":
        show_current()
    elif args.action == "compare":
        compare_models()

if __name__ == "__main__":
    main()