# Agentic AI Article Generation System - Technical Report

## System Overview

This project implements an Agentic AI system for automated article generation, combining multiple AI models, web scraping, and quality assessment to produce high-quality business content. The system is designed for Jenosize, a digital transformation consultancy, to create executive-level articles with strategic depth and actionable insights.

## System Architecture & Workflow

### 1. User Input Processing
The system accepts flexible user inputs through a web interface:
- **Topic Category**: Subject matter focus (e.g., Digital Transformation, AI, Sustainability)
- **Industry**: Target industry context (Technology, Healthcare, Finance, etc.)
- **Target Audience**: Specific reader demographics (C-level executives, SME owners)
- **Source URLs**: Up to 5 web sources for content enrichment (optional)
- **PDF Documents**: Document upload for reference material (optional)
- **SEO Keywords**: Search optimization terms
- **Custom Instructions**: Specific user requirements
- **Model Selection**: Choice between GPT Fine-tuned and Gemini 2.5 Pro
- **Thai Translation**: Optional bilingual output

All inputs are optional, providing maximum flexibility for content creators.

### 2. Content Enrichment Pipeline
When users provide URLs or PDF files:
- **Web Scraping**: Selenium-based scraper extracts clean content from multiple URLs
- **PDF Processing**: OCR and text extraction from uploaded documents
- **Content Validation**: URL format validation and content quality checks
- **Context Building**: Aggregated content feeds into the generation context

### 3. AI Article Generation
The core generation engine:
- **Model Selection**: Routes requests to either GPT-4.1-mini (fine-tuned) or Gemini 2.5 Pro
- **Context Integration**: Combines user inputs, scraped content, and system prompts
- **Current Date Injection**: Ensures articles reflect up-to-date information
- **Structured Output**: Generates markdown content with layout specifications

### 4. Quality Assessment Loop
Multi-layered quality control:
- **AI Analysis**: Secondary LLM evaluates content quality, structure, and business relevance
- **Quality Scoring**: Iterative improvement up to 3 cycles if quality threshold not met
- **Feedback Integration**: Failed quality checks generate specific improvement suggestions

### 5. Output Delivery
Final processing and presentation:
- **Bilingual Support**: Optional Thai translation using dedicated translation service
- **Layout Generation**: Image slot suggestions and content structure
- **PDF Export**: AI-enhanced PDF generation with quality metrics
- **UI Presentation**: Rich markdown rendering with interactive elements

## Data Engineering for Fine-tuning

### Data Pipeline Process
1. **Content Scraping**: Automated collection of 38 high-quality business articles from target websites
2. **HTML Processing**: Clean extraction using Selenium and BeautifulSoup
3. **Markdown Conversion**: Structured content formatting for training consistency  
4. **Quality Filtering**: Manual curation and validation of training examples
5. **Format Standardization**: Conversion to OpenAI fine-tuning JSON format
6. **Train/Validation Split**: 80/20 split for model training and evaluation

The fine-tuning dataset contains executive-level content specifically aligned with Jenosize's brand voice and strategic depth requirements.

## Technical Challenges & Solutions

### Model Selection Rationale
**Challenge**: Balancing model capability, cost-effectiveness, and fine-tuning flexibility.

**Solution**: Selected GPT-4.1-mini as the primary fine-tuned model based on:
- Superior fine-tuning capabilities among available GPT models
- Cost-effectiveness for prototype development
- Proven performance in business content generation
- **GPQA Score**: 65% (adequate for business content)

**Alternative Considered**: Open-source LLMs were evaluated but rejected due to:
- Hardware resource constraints
- Infrastructure complexity
- Development timeline limitations

### Data Scarcity
**Challenge**: Limited training data for fine-tuning due to budget constraints.

**Impact**: Reduced model specialization and potential for overfitting on small dataset.

**Mitigation**: Supplemented with Gemini 2.5 Pro as high-performance alternative.

## Current System Capabilities

### Core Features
- **Multi-Model Support**: Toggle between GPT Fine-tuned and Gemini 2.5 Pro
- **Flexible Input Handling**: All fields optional, supporting various content creation scenarios
- **Multi-Source Integration**: Concurrent processing of up to 5 URLs plus PDF documents
- **Quality Assurance**: Automated content evaluation and iterative improvement
- **Bilingual Output**: English-first with optional Thai translation
- **Export Functionality**: PDF generation with quality metrics

### Advanced Features
- **Content Enrichment**: Intelligent integration of external sources
- **SEO Optimization**: Keyword integration and search-friendly formatting
- **Executive Focus**: Content optimized for C-level decision makers
- **Layout Intelligence**: Strategic image placement suggestions

## Performance Benchmarks & Model Comparison

Based on evaluation criteria from [Vellum AI LLM Leaderboard](https://www.vellum.ai/llm-leaderboard):

### Gemini 2.5 Pro
- **GRIND Score**: 82.1% (Highest among all LLMs - Adaptive Reasoning Excellence)
- **GPQA Score**: 86.4% (3rd highest - Graduate-level expertise)
- **Strengths**: Superior reasoning, complex analysis, latest knowledge
- **Limitations**: No fine-tuning capability, higher per-token cost

### GPT-4.1-mini (Fine-tuned)
- **GPQA Score**: 65% (Adequate for business content)
- **Strengths**: Domain-specific training, cost-effective, customizable
- **Limitations**: Lower baseline performance, limited training data

## Recommendations for Future Improvements

### Short-term Enhancements
1. **Expanded Training Dataset**: Increase fine-tuning corpus to 500+ articles
2. **Few-shot Prompting**: Enhance Gemini performance with curated examples
3. **Content Caching**: Implement intelligent URL content caching
4. **Quality Metrics**: Add more granular quality assessment dimensions

### Long-term Strategic Improvements
1. **Llama 4 Integration**: When available, implement open-source alternative with:
   - Full fine-tuning capability
   - Cost independence
   - Enhanced customization options

2. **Multi-Agent Architecture**: Implement specialized agents for:
   - Research and data gathering
   - Content generation
   - Quality assessment and editing
   - SEO optimization

3. **Advanced Personalization**: User preference learning and content style adaptation

4. **Real-time Updates**: Integration with current events and market data APIs

## Conclusion

The Agentic AI Article Generation System successfully demonstrates the integration of multiple AI models, automated quality assessment, and flexible content creation workflows. While constrained by budget and data limitations, the system provides a robust foundation for automated content generation with clear pathways for enhancement.

The dual-model approach (GPT fine-tuned + Gemini 2.5 Pro) offers users choice between specialized performance and general intelligence, while the comprehensive input handling ensures adaptability to various content creation scenarios. Future improvements focusing on expanded training data and open-source model integration will further enhance system capabilities and cost-effectiveness.

---
*System developed for Jenosize Digital Transformation Consultancy*  
*Report generated: January 2025*