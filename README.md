# Agentic AI Article Generation System

![System Architecture](https://img.shields.io/badge/Architecture-Agentic%20AI-blue) ![Models](https://img.shields.io/badge/Models-GPT%20%2B%20Gemini-green) ![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

An intelligent article generation system that combines multiple AI models, web scraping, and quality assessment to produce high-quality business content. Built for Jenosize Digital Transformation Consultancy with agentic AI architecture for self-improving content generation.

## 🚀 Features

- **Multi-Model AI**: Choose between GPT-4.1-mini (fine-tuned) and Gemini 2.5 Pro
- **Agentic Architecture**: Self-improving content with quality assessment loops
- **Flexible Inputs**: All fields optional - topic, industry, URLs, PDFs, custom prompts
- **Web Content Integration**: Scrape and integrate up to 5 web sources
- **PDF Processing**: Upload and extract content from PDF documents
- **Bilingual Support**: Optional Thai translation with layout preservation
- **Quality Assessment**: AI-powered content evaluation and iterative improvement
- **Export Capabilities**: PDF generation with quality metrics
- **Fine-tuning Pipeline**: Complete data engineering workflow for model customization
- **Production Ready**: Scalable architecture with comprehensive error handling

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **OpenAI API Key** (GPT-4.1-mini fine-tuned access)
- **Gemini API Key** (hardcoded in system)
- **Docker & Docker Compose** (optional, for containerized deployment)

## 🛠️ Installation & Setup

### Method 1: Docker Compose (Recommended)

1. **Clone and Setup**
```bash
git clone <repository-url>
cd jetask
cp .env.example .env
```

2. **Configure Environment**
```bash
# Edit .env file with your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

3. **Run with Docker**
```bash
docker-compose up --build
```

4. **Access the Application**
- Frontend: http://localhost:3001
- Backend API: http://localhost:8003
- API Documentation: http://localhost:8003/docs

### Method 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

5. **Run the backend**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8003
```

#### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
cp .env.local.example .env.local
# Edit .env.local if needed (default API URL: http://localhost:8003)
```

4. **Run the frontend**
```bash
npm run dev
```

## 🏗️ Project Structure

```
jetask/
├── backend/                    # FastAPI Backend
│   ├── config/
│   │   └── settings.py        # Application configuration
│   ├── api/
│   │   └── endpoints/
│   │       └── article.py     # Article generation endpoints
│   ├── services/
│   │   ├── llm_service.py     # GPT-4.1-mini integration
│   │   ├── llm_service_gemini.py # Gemini 2.5 Pro integration
│   │   ├── web_scraper.py     # URL content extraction
│   │   ├── pdf_processor.py   # PDF text extraction
│   │   ├── quality_checker.py # Content quality evaluation
│   │   └── translation_service.py # Thai translation
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── utils/
│   │   └── helpers.py         # Utility functions
│   ├── main.py               # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Backend Docker configuration
├── frontend/                  # Next.js Frontend
│   ├── app/
│   │   ├── layout.tsx        # Root layout
│   │   ├── page.tsx          # Homepage
│   │   └── globals.css       # Global styles
│   ├── components/
│   │   ├── InputForm.tsx     # Article generation form with model selection
│   │   ├── ArticleDisplay.tsx # Article viewing component
│   │   ├── ImageUploader.tsx  # Image upload component
│   │   ├── PDFExporter.tsx    # PDF export functionality
│   │   └── UrlInstructionsForm.tsx # URL content instruction form
│   ├── services/
│   │   └── api.ts            # API client
│   ├── types/
│   │   └── index.ts          # TypeScript definitions
│   ├── utils/
│   │   └── helpers.ts        # Utility functions
│   ├── package.json          # Node.js dependencies
│   └── Dockerfile           # Frontend Docker configuration
├── data-pipeline/             # Data Engineering Pipeline
│   ├── finetuning/           # Fine-tuning scripts and tools
│   │   ├── data_checker.py   # Data validation and upload
│   │   ├── start_finetuning.py # LoRA fine-tuning
│   │   ├── monitor_finetuning.py # Training monitoring
│   │   └── complete_pipeline.py # End-to-end pipeline
│   ├── scrapers/             # Web scraping tools
│   ├── processors/           # Content processing
│   └── output/              # Training data and results
├── docker-compose.yml        # Multi-container setup
├── .env.example             # Environment variables template
├── SYSTEM_REPORT.md         # Technical documentation
└── README.md               # Setup documentation
```

## 🎯 Usage Guide

### 1. Article Generation

1. **Select AI Model**: Choose between GPT Fine-tuned or Gemini 2.5 Pro
2. **Fill the Input Form** (all fields optional):
   - **Topic Category**: e.g., "Digital Transformation", "AI", "Sustainability"
   - **Industry**: Select from dropdown or specify custom
   - **Target Audience**: e.g., "C-level executives", "Small business owners"
   - **Source URLs**: Up to 5 URLs for content scraping
   - **PDF Upload**: Drag and drop PDF documents
   - **SEO Keywords**: Comma-separated keywords for optimization
   - **Custom Instructions**: Specific requirements for content generation
   - **Thai Translation**: Optional bilingual output

3. **Generate Article**: Click "Generate Article" to start the agentic process

4. **Monitor Progress**: Watch real-time progress through quality assessment loops

### 2. Agentic Quality Process

The system implements an intelligent quality loop:
- **Generation**: Selected AI model creates initial content with current date context
- **Evaluation**: Secondary AI evaluates and scores the article (0-1 scale)
- **Self-Improvement**: If score < 0.85, specific feedback guides regeneration
- **Iterative Enhancement**: Maximum 3 cycles for optimal quality/efficiency balance
- **Multi-source Integration**: Intelligent blending of web content, PDFs, and user inputs

### 3. Image Management

1. **View Suggestions**: System suggests strategic image placements
2. **Upload Images**: Drag and drop images for each suggested slot
3. **Preview**: See images in context before export

### 4. Export Options

- **HTML Download**: Export as styled HTML file
- **PDF Export**: Generate professional PDF with:
  - Custom styling and layout
  - Embedded images
  - Quality score information
  - Proper page breaks

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
OPENAI_API_KEY=your_openai_api_key_here
# Gemini API key is hardcoded in settings.py
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8003
```

### Customization Options

#### Backend Settings (backend/config/settings.py)
```python
MAX_QUALITY_ITERATIONS = 3     # Maximum regeneration attempts
QUALITY_THRESHOLD = 0.85       # Minimum quality score
REQUEST_TIMEOUT = 10           # Web scraping timeout
MAX_TOKENS = 8000             # Token limit for generation
TEMPERATURE = 0.7             # AI creativity setting
OPENAI_MODEL = "ft:gpt-4.1-mini-2025-04-14:codelabdev:jenosize-content:C7SVORLy"
GEMINI_API_KEY = "hardcoded_in_settings"  # Gemini API key
```

#### Frontend Styling
- Modify `frontend/app/globals.css` for custom styles
- Update `frontend/tailwind.config.js` for theme changes
- Customize components in `frontend/components/`

## 📡 API Documentation

### Primary Endpoint

#### POST /api/generate-article
Generate articles with agentic AI and multi-model support.

**Request Body (all fields optional):**
```json
{
  "topicCategory": "Digital Transformation",
  "industry": "Technology",
  "targetAudience": "C-level executives",
  "sourceUrls": [
    "https://example.com/article1",
    "https://example.com/article2"
  ],
  "pdfBase64": "base64_encoded_pdf_content",
  "seoKeywords": "AI, automation, business transformation",
  "customPrompt": "Focus on implementation strategies",
  "includeThaiTranslation": false,
  "selectedModel": "gpt-finetune"
}
```

**Response:**
```json
{
  "content": "# Article Title\n\nGenerated markdown content...",
  "layout": {
    "sections": ["Executive Summary", "Introduction", "Analysis"],
    "imageSlots": [
      {
        "id": "img_1",
        "description": "Strategic framework diagram",
        "position": "introduction",
        "suggestedType": "infographic"
      }
    ]
  },
  "qualityScore": 0.87,
  "iterations": 2,
  "analysis": {
    "strengths": ["Clear structure", "Data-driven insights"],
    "weaknesses": ["Needs more examples"],
    "recommendations": ["Add case studies"],
    "summary": "High-quality strategic analysis"
  },
  "thaiContent": "# หัวข้อบทความ..."
}
```

#### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "article-generator"
}
```

## 🐳 Docker Deployment

### Production Deployment

1. **Build and run services**
```bash
docker-compose -f docker-compose.yml up --build -d
```

2. **View logs**
```bash
docker-compose logs -f
```

3. **Scale services**
```bash
docker-compose up --scale backend=2 --scale frontend=2
```

### Fine-tuning Pipeline

The system includes complete data engineering tools:

```bash
cd data-pipeline/finetuning

# Validate and upload training data
python data_checker.py

# Start LoRA fine-tuning with Together AI
python start_finetuning.py

# Monitor training progress
python monitor_finetuning.py

# Run complete pipeline
python complete_pipeline.py
```

### Production Server Deployment

**Current Deployment:** http://43.209.0.15:8003

1. **Manual Setup on Server:**
   ```bash
   # Backend setup
   cd ~/jib_db/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Run backend as background process
   nohup python main.py > app.log 2>&1 &
   
   # Check if running
   ps aux | grep python
   curl http://localhost:8003/api/health
   ```

2. **Docker Deployment:**
   ```bash
   # Backend on port 8003
   docker-compose up --build -d
   ```

3. **Frontend Deployment:**
   - **Vercel:** Set `NEXT_PUBLIC_API_URL=http://43.209.0.15:8003`
   - **Local:** Frontend connects to server backend automatically

2. **Health monitoring**:
   - Backend: `/api/health` endpoint
   - Auto-restart on failure

## 🚨 Troubleshooting

### Common Issues

#### 1. AI Model API Errors
```bash
# Check OpenAI API key
echo $OPENAI_API_KEY

# Test Gemini API (key is hardcoded)
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: YOUR_GEMINI_KEY' \
  -X POST -d '{"contents":[{"parts":[{"text":"Test"}]}]}'
```

#### 2. CORS Issues
```bash
# Backend CORS is configured for all origins (*)
# For production, update main.py:
allow_origins=["https://your-vercel-app.vercel.app", "http://43.209.0.15:3001"]
```

#### 3. PDF Processing Errors
```bash
# Install system dependencies for PDF processing
# Ubuntu/Debian:
apt-get update && apt-get install -y poppler-utils

# macOS:
brew install poppler
```

#### 4. Memory Issues
```bash
# Increase Docker memory allocation
# Docker Desktop > Settings > Resources > Memory > 4GB+
```

### Debug Mode

#### Backend Debug
```bash
# Enable debug logging
export PYTHONPATH=/app
python -m uvicorn main:app --reload --log-level debug
```

#### Frontend Debug
```bash
# Enable debug mode
export NODE_ENV=development
npm run dev
```

## 🔒 Security Considerations

### API Security
- API keys are handled securely through environment variables
- No API keys are logged or exposed in client-side code
- Input validation and sanitization for all user inputs

### File Upload Security
- PDF files are processed in isolated environment
- Base64 encoding prevents direct file system access
- File size limits prevent DoS attacks

### CORS Configuration
- Restricted to specific domains in production
- Configure `allow_origins` in `main.py` for your domain

## 📈 Performance Optimization

### Backend Optimization
- Async/await patterns for concurrent operations
- Request timeouts to prevent hanging
- Efficient memory usage with streaming

### Frontend Optimization
- Image lazy loading and optimization
- Component-level code splitting
- Efficient state management

### Scaling Considerations
- Horizontal scaling with Docker Compose
- Load balancing for multiple instances
- Caching strategies for improved performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

### Development Guidelines
- Follow TypeScript/Python type annotations
- Write comprehensive error handling
- Include unit tests for new features
- Update documentation for API changes

## 📄 License

This project is proprietary software developed for Jenosize. All rights reserved.

## 📞 Support

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Check the troubleshooting section above

---

**Built with ❤️ for Jenosize** | Powered by GPT-4.1-mini Fine-tuned + Gemini 2.5 Pro

### 🌐 Current Deployment
- **Backend API:** http://43.209.0.15:8003
- **Status:** Running on Ubuntu server with nohup
- **Frontend:** Can be deployed on Vercel pointing to backend API
- **Models:** GPT-4.1-mini (fine-tuned) + Gemini 2.5 Pro available