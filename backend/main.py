from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import article

app = FastAPI(
    title="Jenosize Article Generator API",
    description="AI-powered content generation for business trends and future ideas",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:3000", "http://127.0.0.1:3000"],  # Support both frontend ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(article.router, prefix="/api", tags=["articles"])

@app.get("/")
async def root():
    return {
        "message": "Jenosize Article Generator API",
        "version": "1.0.0",
        "endpoints": {
            "generate_article": "/api/generate-article",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)