# Jenosize Article Generator

An AI-powered content generation tool that creates high-quality business articles about trends and future ideas. Built with FastAPI backend and Next.js frontend, utilizing GPT-4o for intelligent content creation.

## 🚀 Features

### Backend (FastAPI)
- **Modular Architecture**: Clean separation of concerns with services, models, and utilities
- **GPT-4o Integration**: Advanced AI content generation with quality checking
- **Web Scraping**: Extract content from URLs using BeautifulSoup
- **PDF Processing**: OCR and text extraction from uploaded documents
- **Quality Loop**: Iterative content improvement with quality scoring
- **RESTful API**: Well-documented endpoints with proper error handling

### Frontend (Next.js)
- **Modern React**: Built with Next.js 14, TypeScript, and Tailwind CSS
- **Interactive Form**: Intuitive input form with drag-and-drop file upload
- **Real-time Progress**: Live updates during article generation
- **Image Management**: Upload and manage images for article enhancement
- **PDF Export**: Generate professional PDFs with custom layouts
- **Responsive Design**: Works seamlessly on desktop and mobile

### Key Capabilities
- Generate articles from various inputs (topics, URLs, PDFs, keywords)
- Quality assessment and iterative improvement
- Image placement suggestions and upload functionality
- Professional PDF export with custom styling
- Jenosize brand alignment and tone consistency

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **OpenAI API Key** (GPT-4o access required)
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
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

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
uvicorn main:app --reload --host 0.0.0.0 --port 8000
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
# Edit .env.local if needed (default API URL: http://localhost:8000)
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
│   │   ├── llm_service.py     # GPT-4o integration
│   │   ├── web_scraper.py     # URL content extraction
│   │   ├── pdf_processor.py   # PDF text extraction
│   │   └── quality_checker.py # Content quality evaluation
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
│   │   ├── InputForm.tsx     # Article generation form
│   │   ├── ArticleDisplay.tsx # Article viewing component
│   │   ├── ImageUploader.tsx  # Image upload component
│   │   └── PDFExporter.tsx    # PDF export functionality
│   ├── services/
│   │   └── api.ts            # API client
│   ├── types/
│   │   └── index.ts          # TypeScript definitions
│   ├── utils/
│   │   └── helpers.ts        # Utility functions
│   ├── package.json          # Node.js dependencies
│   └── Dockerfile           # Frontend Docker configuration
├── docker-compose.yml        # Multi-container setup
├── .env.example             # Environment variables template
└── README.md               # Documentation
```

## 🎯 Usage Guide

### 1. Article Generation

1. **Fill the Input Form** (all fields optional):
   - **Topic Category**: e.g., "Digital Transformation", "AI", "Sustainability"
   - **Industry**: Select from dropdown or specify custom
   - **Target Audience**: e.g., "C-level executives", "Small business owners"
   - **Source URL**: Provide URL for content scraping
   - **PDF Upload**: Drag and drop PDF documents
   - **SEO Keywords**: Comma-separated keywords for optimization

2. **Generate Article**: Click "Generate Article" to start the process

3. **Monitor Progress**: Watch real-time progress updates during generation

### 2. Quality Process

The system implements a quality loop:
- **Generation**: GPT-4o creates initial content
- **Evaluation**: Quality checker scores the article (0-1 scale)
- **Iteration**: If score < 0.85, feedback is provided for regeneration
- **Maximum 3 iterations** to ensure efficiency

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
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Customization Options

#### Backend Settings (backend/config/settings.py)
```python
MAX_QUALITY_ITERATIONS = 3     # Maximum regeneration attempts
QUALITY_THRESHOLD = 0.85       # Minimum quality score
REQUEST_TIMEOUT = 10           # Web scraping timeout
MAX_TOKENS = 4000             # GPT-4o token limit
TEMPERATURE = 0.7             # AI creativity setting
```

#### Frontend Styling
- Modify `frontend/app/globals.css` for custom styles
- Update `frontend/tailwind.config.js` for theme changes
- Customize components in `frontend/components/`

## 📡 API Documentation

### Endpoints

#### POST /api/generate-article
Generate an article based on provided parameters.

**Request Body:**
```json
{
  "topic_category": "Digital Transformation",
  "industry": "Technology",
  "target_audience": "Business leaders",
  "source_url": "https://example.com/article",
  "pdf_base64": "base64_encoded_pdf_content",
  "seo_keywords": "digital, transformation, business"
}
```

**Response:**
```json
{
  "content": "Generated article HTML content",
  "layout": {
    "sections": ["Introduction", "Main Content", "Conclusion"],
    "image_slots": [
      {
        "id": "img_1",
        "description": "Chart showing digital adoption trends",
        "position": "introduction",
        "suggested_type": "chart"
      }
    ]
  },
  "quality_score": 0.92,
  "iterations": 2
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

### Health Monitoring

Both services include health checks:
- **Backend**: `/api/health` endpoint monitoring
- **Frontend**: HTTP availability check
- **Auto-restart**: Services restart automatically on failure

## 🚨 Troubleshooting

### Common Issues

#### 1. OpenAI API Errors
```bash
# Check API key configuration
echo $OPENAI_API_KEY

# Verify API access
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

#### 2. CORS Issues
```bash
# Backend CORS is configured for localhost:3000
# For different domains, update main.py:
allow_origins=["http://your-domain.com"]
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

**Built with ❤️ for Jenosize** | Powered by GPT-4o