from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import article
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Jenosize Article Generator API",
    description="AI-powered content generation for business trends and future ideas",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(article.router, prefix="/api", tags=["articles"])

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Jenosize Article Generator API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "generate_article": "/api/generate-article",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "jetask-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)