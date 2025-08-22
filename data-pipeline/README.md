# Jenosize Article Scraping & Fine-tuning Data Pipeline

A comprehensive data engineering pipeline that scrapes articles from the Jenosize Ideas website and prepares high-quality training data for fine-tuning GPT-4 models to match Jenosize's content style and expertise.

## 🎯 Project Overview

This pipeline automates the complete process of:

1. **Discovery**: Scraping all article links from 6 Jenosize Ideas category pages
2. **Collection**: Extracting full article content while preserving HTML structure
3. **Processing**: Cleaning and structuring content for training purposes
4. **Generation**: Creating training examples that match the production LLM service
5. **Validation**: Ensuring dataset quality and OpenAI fine-tuning compatibility

## 📁 Project Structure

```
data-pipeline/
├── main.py                    # Main pipeline orchestrator
├── config/
│   └── settings.py           # Configuration and URLs
├── scrapers/
│   ├── category_scraper.py   # Extract article links from category pages
│   └── article_scraper.py    # Scrape individual article content
├── processors/
│   ├── content_extractor.py  # Process and clean content for training
│   └── html_processor.py     # HTML processing utilities
├── generators/
│   ├── dataset_builder.py    # Build training/validation datasets
│   └── prompt_generator.py   # Generate prompts based on llm_service.py
├── prompts/
│   └── prompt.py             # Prompt templates and generation logic
├── models/
│   └── schemas.py            # Data models and structures
├── utils/
│   ├── logger.py             # Colored logging utilities
│   └── helpers.py            # Helper functions and utilities
├── output/
│   ├── raw/                  # Raw HTML files
│   ├── processed/            # Processed article JSON files
│   ├── train.jsonl           # Training dataset (JSONL format)
│   ├── validation.jsonl      # Validation dataset (JSONL format)
│   ├── dataset_metadata.json # Dataset statistics and metadata
│   └── pipeline_report.json  # Comprehensive pipeline report
└── requirements.txt
```

## 🚀 Quick Start

### 1. Installation

```bash
cd /Users/piw/Downloads/jetask/data-pipeline

# Install dependencies
pip install -r requirements.txt

# Make main.py executable
chmod +x main.py
```

### 2. Basic Usage

```bash
# Run the complete pipeline
python main.py

# Run with limited articles for testing (10 per category)
python main.py --limit 10

# Resume from a specific step (useful if pipeline was interrupted)
python main.py --resume scrape_articles

# Use custom output directory
python main.py --output-dir /path/to/custom/output
```

### 3. Expected Output

The pipeline will generate:
- `train.jsonl`: Training dataset in OpenAI format (80% of data)
- `validation.jsonl`: Validation dataset in OpenAI format (20% of data)
- `dataset_metadata.json`: Comprehensive statistics and metadata
- `pipeline_report.json`: Detailed execution report

## 🔧 Configuration

Edit `config/settings.py` to customize:

### Target URLs
```python
CATEGORY_URLS = [
    "https://www.jenosize.com/en/ideas/futurist",
    "https://www.jenosize.com/en/ideas/understand-people-and-consumer",
    "https://www.jenosize.com/en/ideas/transformation-and-technology",
    "https://www.jenosize.com/en/ideas/utility-for-our-world",
    "https://www.jenosize.com/en/ideas/real-time-marketing",
    "https://www.jenosize.com/en/ideas/experience-the-new-world"
]
```

### Scraping Parameters
```python
REQUEST_DELAY = 1.0              # Delay between requests (seconds)
MAX_RETRIES = 3                  # Retry failed requests
REQUEST_TIMEOUT = 15             # Request timeout (seconds)
MAX_ARTICLES_PER_CATEGORY = 50   # Limit for development
```

### Dataset Parameters
```python
TRAIN_SPLIT_RATIO = 0.8          # 80% training, 20% validation
MIN_CONTENT_LENGTH = 500         # Minimum article length
SYSTEM_PROMPT_VARIATIONS = 5     # Number of prompt variations
```

## 📊 Features

### Intelligent Content Extraction
- **HTML Structure Preservation**: Maintains layout information for training
- **Content Quality Validation**: Filters articles based on length, structure, and diversity
- **Metadata Extraction**: Captures titles, authors, categories, tags, and images
- **Multiple Format Support**: Generates both HTML and Markdown versions

### Advanced Prompt Engineering
- **Production Matching**: Prompts based on analysis of `/Users/piw/Downloads/jetask/backend/services/llm_service.py`
- **Multiple Variations**: Generates diverse training examples per article
- **Realistic Parameters**: Creates authentic business scenarios and requirements
- **Custom Instructions**: Simulates user-provided custom prompts

### Robust Data Pipeline
- **Error Handling**: Comprehensive retry logic and graceful failure handling
- **Caching**: Resume capability from any step using cached intermediate results
- **Progress Tracking**: Real-time progress bars and detailed logging
- **Rate Limiting**: Respectful scraping with configurable delays

### Quality Assurance
- **Content Validation**: Multi-layered validation of scraped content
- **Dataset Verification**: Automatic validation of JSONL format compatibility
- **Statistics Generation**: Comprehensive reporting on data quality and coverage
- **OpenAI Compatibility**: Ensures datasets meet fine-tuning requirements

## 🎛️ Command Line Options

### Basic Options
```bash
python main.py [OPTIONS]

Options:
  --limit INTEGER          Maximum articles per category (useful for development)
  --resume STEP           Resume from specific step [discover_articles|scrape_articles|process_content|build_datasets|finalize]
  --output-dir PATH       Custom output directory (overrides config)
  --help                  Show help message
```

### Resume Steps
- `discover_articles`: Scrape category pages for article links
- `scrape_articles`: Download and parse individual articles
- `process_content`: Clean and structure content for training
- `build_datasets`: Generate training and validation JSONL files
- `finalize`: Validate datasets and create final report

### Examples
```bash
# Development run with limited articles
python main.py --limit 5

# Resume after network interruption
python main.py --resume scrape_articles

# Full production run with custom output
python main.py --output-dir /data/jenosize-training

# Resume with limits (useful for testing changes)
python main.py --limit 3 --resume build_datasets
```

## 📈 Output Datasets

### Training Data Format
Each JSONL entry follows OpenAI's fine-tuning format:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are an expert content creator for Jenosize..."
    },
    {
      "role": "user", 
      "content": "Generate a comprehensive article with the following specifications:\n\nTopic Category: Digital Transformation\nIndustry Focus: Healthcare\n..."
    },
    {
      "role": "assistant",
      "content": "{\"content\": \"# The Future of Healthcare Digital Transformation\\n\\n...\", \"layout\": {...}, \"source_usage_details\": [...]}"
    }
  ]
}
```

### Dataset Variations
The pipeline generates diverse training examples:
- **Basic Generation**: Standard article requests with topic, industry, audience
- **With Source Content**: Examples that reference scraped material
- **Custom Instructions**: Simulated user-specific requirements
- **Multiple Categories**: Balanced coverage across all 6 Jenosize categories

### Quality Metrics
- **Content Length**: 500-20,000 characters per article
- **Diversity Check**: Prevents repetitive content
- **Structure Validation**: Ensures proper headings and organization
- **Business Relevance**: Focuses on actionable business insights

## 🔍 Monitoring and Logging

### Log Levels
The pipeline provides comprehensive logging with color coding:
- **🔍 DEBUG**: Detailed operation information
- **✅ INFO**: General progress and success messages
- **⚠️  WARNING**: Non-critical issues and fallbacks
- **❌ ERROR**: Critical failures requiring attention

### Progress Tracking
- Real-time progress bars for long-running operations
- Category-by-category breakdown of scraping progress
- Success/failure rates with detailed error reporting
- Processing time measurements for performance monitoring

### Output Reports
- **Pipeline Report**: Complete execution summary with statistics
- **Dataset Metadata**: Detailed breakdown of training data characteristics
- **Validation Results**: Quality checks and OpenAI compatibility verification

## 🛠️ Development and Customization

### Adding New Categories
1. Add URLs to `CATEGORY_URLS` in `config/settings.py`
2. Update `CATEGORY_MAPPING` for proper categorization
3. Test with `--limit 1` to verify scraping works

### Modifying Prompts
1. Edit prompt templates in `prompts/prompt.py`
2. Adjust the `JenosizePromptGenerator` class methods
3. Test with `--resume build_datasets` to regenerate training data

### Content Processing
1. Modify extraction logic in `processors/content_extractor.py`
2. Adjust quality validation criteria
3. Update structured content processing as needed

### Extending Output Formats
1. Add new dataset builders in `generators/dataset_builder.py`
2. Implement additional validation methods
3. Update the main pipeline to support new formats

## 📋 Troubleshooting

### Common Issues

**Network Errors**
```bash
# Reduce request frequency
# Edit settings.py: REQUEST_DELAY = 2.0

# Increase timeout
# Edit settings.py: REQUEST_TIMEOUT = 30
```

**Memory Issues with Large Datasets**
```bash
# Limit articles for testing
python main.py --limit 10

# Process in batches using resume
python main.py --limit 20 --resume process_content
```

**Invalid JSONL Output**
```bash
# The pipeline includes automatic validation
# Check pipeline_report.json for detailed error information
# Re-run with: python main.py --resume build_datasets
```

### Performance Tuning

**Speed up Development**
- Use `--limit 5` for quick iterations
- Use `--resume` to skip completed steps
- Adjust `MAX_ARTICLES_PER_CATEGORY` in settings

**Production Optimization**
- Increase `max_workers` in `ArticleScraper` (default: 3)
- Adjust `REQUEST_DELAY` based on server tolerance
- Use SSD storage for better I/O performance

## 🎯 Fine-tuning Integration

### Using Generated Datasets

1. **Upload to OpenAI**:
   ```bash
   openai api fine_tuning.jobs.create \
     -t train.jsonl \
     -v validation.jsonl \
     -m gpt-4.1-mini
   ```

2. **Validate Before Upload**:
   The pipeline automatically validates datasets, but you can also use:
   ```bash
   openai tools fine_tuning.jobs.prepare_data -f train.jsonl
   ```

3. **Monitor Training**:
   Check `dataset_metadata.json` for expected training characteristics and token counts.

### Integration with Production System

The generated fine-tuned model can replace the base model in:
```python
# /Users/piw/Downloads/jetask/backend/services/llm_service.py
# Update the model name after fine-tuning completion
OPENAI_MODEL = "ft:gpt-4.1-mini:organization:model-name:job-id"
```

## 📊 Expected Results

### Dataset Size (Typical Run)
- **Articles Discovered**: ~200-300 per category (1200+ total)
- **Successfully Scraped**: ~80-90% success rate
- **Training Examples**: ~2000-4000 examples (3-4 per article)
- **File Sizes**: 50-100MB for complete datasets

### Quality Metrics
- **Content Diversity**: Multiple categories, complexity levels, and themes
- **Prompt Variations**: 5+ system prompt variations, 10+ user scenarios
- **Business Relevance**: Focus on actionable insights and Jenosize expertise
- **Production Alignment**: Prompts match current llm_service.py implementation

## 🤝 Contributing

### Code Style
- Follow existing patterns and logging conventions
- Add comprehensive error handling
- Include progress tracking for long operations
- Document any new configuration options

### Testing Changes
- Always test with `--limit 5` first
- Use `--resume` to test specific pipeline stages
- Verify JSONL output with OpenAI's validation tools
- Check pipeline_report.json for any warnings or errors

---

## 📝 License

This pipeline is designed specifically for Jenosize's internal use and fine-tuning needs. The scraped content remains subject to Jenosize's original terms and conditions.

---

*Generated by Claude Code Pipeline Generator*