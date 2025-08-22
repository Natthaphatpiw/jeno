from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl

class ArticleRequest(BaseModel):
    topic_category: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    source_url: Optional[str] = None
    pdf_base64: Optional[str] = None
    seo_keywords: Optional[str] = None

class ImageSlot(BaseModel):
    id: str
    description: str
    position: str
    suggested_type: str

class ArticleLayout(BaseModel):
    sections: List[str]
    image_slots: List[ImageSlot]

class ArticleResponse(BaseModel):
    content: str
    layout: ArticleLayout
    quality_score: float
    iterations: int

class QualityFeedback(BaseModel):
    score: float
    feedback: str
    suggestions: List[str]

class GenerationContext(BaseModel):
    topic_category: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    scraped_content: Optional[str] = None
    pdf_content: Optional[str] = None
    seo_keywords: List[str] = []