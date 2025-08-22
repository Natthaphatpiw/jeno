from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl

class ArticleRequest(BaseModel):
    topic_category: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    source_url: Optional[str] = None  # Keep for backward compatibility
    source_urls: Optional[List[str]] = None  # New field for multiple URLs (max 5)
    pdf_base64: Optional[str] = None
    seo_keywords: Optional[str] = None
    custom_prompt: Optional[str] = None  # User's custom instructions

class ImageSlot(BaseModel):
    id: str
    description: str
    position: str
    suggested_type: str
    placement_rationale: Optional[str] = None
    content_guidance: Optional[str] = None
    dimensions: Optional[str] = None
    aspect_ratio: Optional[str] = None
    alternatives: Optional[str] = None

class ArticleLayout(BaseModel):
    sections: List[str]
    image_slots: List[ImageSlot]

class ArticleAnalysis(BaseModel):
    strengths: List[str]
    weaknesses: List[str] 
    recommendations: List[str]
    summary: str

class ArticleResponse(BaseModel):
    content: str
    layout: ArticleLayout
    quality_score: float
    iterations: int
    source_usage_details: Optional[List[Dict[str, str]]] = None
    analysis: Optional[ArticleAnalysis] = None

class QualityFeedback(BaseModel):
    score: float
    feedback: str
    suggestions: List[str]

class GenerationContext(BaseModel):
    topic_category: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    scraped_content: Optional[str] = None
    scraped_sources: Optional[List[Dict[str, str]]] = None  # [{"url": "...", "content": "...", "title": "..."}]
    pdf_content: Optional[str] = None
    seo_keywords: List[str] = []
    custom_prompt: Optional[str] = None