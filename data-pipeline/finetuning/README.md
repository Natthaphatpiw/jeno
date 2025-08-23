# Fine-tuning Documentation

This directory contains tools for fine-tuning OpenAI models using the scraped Jenosize content data.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Or create a .env file in the project root:
echo "OPENAI_API_KEY=your-api-key-here" >> .env
```

### 2. Install Dependencies

```bash
pip install rich requests python-dotenv
```

### 3. Run Complete Pipeline

```bash
cd /Users/piw/Downloads/jetask/data-pipeline/finetuning
python fine_tune_manager.py run
```

This will:
- ✅ Upload training data (`/output/train.jsonl`)
- ✅ Upload validation data (`/output/validation.jsonl`) 
- ✅ Create fine-tuning job with `gpt-4o-mini`
- ✅ Return job ID for monitoring

### 4. Monitor Progress

```bash
python fine_tune_monitor.py monitor <job-id>
```

## 📁 Files Overview

### Core Scripts

- **`fine_tune_config.py`** - Configuration settings for fine-tuning
- **`fine_tune_manager.py`** - Main script for managing fine-tuning jobs
- **`fine_tune_monitor.py`** - Real-time monitoring and status checking
- **`test_model.py`** - Test suite for evaluating fine-tuned models

### Data Files

- **`jobs.json`** - History of all fine-tuning jobs created
- **`logs/`** - Directory containing job logs and events

## 🛠️ Detailed Usage

### Fine-tuning Manager Commands

```bash
# Run complete pipeline (recommended)
python fine_tune_manager.py run

# Individual commands:
python fine_tune_manager.py upload <file_path>
python fine_tune_manager.py create <training_file_id> [validation_file_id]
python fine_tune_manager.py status <job_id>
python fine_tune_manager.py list
python fine_tune_manager.py cancel <job_id>
```

### Monitor Commands

```bash
# Real-time monitoring with live updates
python fine_tune_monitor.py monitor <job_id>

# Check status once
python fine_tune_monitor.py status <job_id>

# List all jobs
python fine_tune_monitor.py list

# View job events/logs
python fine_tune_monitor.py events <job_id>

# Save logs to file
python fine_tune_monitor.py save-logs <job_id>

# Options:
--refresh 10          # Refresh every 10 seconds (default: 30)
--no-events          # Don't show events during monitoring
--limit 50           # Limit number of results (default: 20)
```

## 🧪 Testing Fine-tuned Models

After your fine-tuning job completes successfully:

```bash
# Test the fine-tuned model
python test_model.py ft:gpt-4o-mini-2024-07-18:openai::abc123

# This will run test cases for:
# - Content creation (various topics)
# - Content summarization
# - Domain-specific writing
```

## ⚙️ Configuration

Edit `fine_tune_config.py` to customize:

```python
@dataclass
class FineTuningConfig:
    # Model settings
    base_model: str = "gpt-4o-mini"  # Base model to fine-tune
    
    # Training parameters (optional - OpenAI auto-optimizes)
    n_epochs: Optional[int] = None
    batch_size: Optional[int] = None  
    learning_rate_multiplier: Optional[float] = None
    
    # Job settings
    suffix: Optional[str] = "jenosize-content"  # Model name suffix
```

## 📊 Understanding Training Data

The pipeline creates training data in the format:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are an expert content creator for Jenosize..."
    },
    {
      "role": "user", 
      "content": "Write about digital transformation trends..."
    },
    {
      "role": "assistant",
      "content": "Digital transformation has become..."
    }
  ]
}
```

### Data Statistics (from latest run)

- **Total Examples**: 110 training examples
- **Train/Validation Split**: 88/22 (80/20)
- **Categories Covered**: 5 different Jenosize content categories
- **Average Lengths**:
  - System prompts: ~5,518 characters
  - User inputs: ~676 characters  
  - Assistant responses: ~4,580 characters

## 🔍 Monitoring Job Progress

### Job States

- **`validating_files`** - Checking uploaded files
- **`queued`** - Job queued for processing
- **`running`** - Training in progress
- **`succeeded`** - Training completed successfully ✅
- **`failed`** - Training failed ❌
- **`cancelled`** - Job cancelled by user

### Typical Timeline

1. **File Upload**: ~30 seconds
2. **Job Creation**: ~5 seconds
3. **Validation**: ~1-2 minutes
4. **Training**: ~10-60 minutes (depending on data size)

## 🎯 Using Fine-tuned Models

Once training completes, use your model ID:

```python
import openai

response = openai.ChatCompletion.create(
    model="ft:gpt-4o-mini-2024-07-18:your-org::abc123",  # Your fine-tuned model ID
    messages=[
        {"role": "system", "content": "You are an expert content creator for Jenosize..."},
        {"role": "user", "content": "Write about AI trends in 2024"}
    ]
)
```

## 🚨 Troubleshooting

### Common Issues

**1. API Key Error**
```bash
export OPENAI_API_KEY="your-actual-api-key"
```

**2. Training File Not Found**
```bash
# Make sure you ran the data pipeline first:
cd /Users/piw/Downloads/jetask/data-pipeline
python main.py
```

**3. Job Failed**
```bash
# Check job events for details:
python fine_tune_monitor.py events <job_id>
```

**4. Model Testing Fails**
```bash
# Verify model ID format:
# Should be: ft:gpt-4o-mini-2024-07-18:org::suffix
```

### Getting Help

1. Check job events: `python fine_tune_monitor.py events <job_id>`
2. View detailed status: `python fine_tune_monitor.py status <job_id>`
3. Save logs for analysis: `python fine_tune_monitor.py save-logs <job_id>`

## 💡 Best Practices

### Data Quality
- ✅ Use high-quality, diverse training examples
- ✅ Maintain consistent formatting
- ✅ Include various content types and styles

### Training Settings
- ✅ Let OpenAI auto-optimize hyperparameters
- ✅ Use validation data to prevent overfitting
- ✅ Monitor training progress regularly

### Testing
- ✅ Test with different prompt styles
- ✅ Evaluate on diverse content types
- ✅ Compare with base model performance

## 📈 Costs

Fine-tuning costs depend on:
- **Training tokens**: $8.00 per 1M tokens (gpt-4o-mini)
- **Usage**: Same as base model rates
- **Storage**: Free for model storage

Estimate for current dataset (~110 examples):
- Training cost: ~$2-5 USD
- Ongoing usage: Standard API rates

## 🔗 Additional Resources

- [OpenAI Fine-tuning Guide](https://platform.openai.com/docs/guides/fine-tuning)
- [Fine-tuning Best Practices](https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset)
- [Model Pricing](https://openai.com/pricing)