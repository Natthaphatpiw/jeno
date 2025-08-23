from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl

class UrlContentInstruction(BaseModel):
    """Instructions for specific URL content extraction and usage"""
    url: str
    content_focus: Optional[str] = None  # What specific content to extract from this URL
    usage_instruction: Optional[str] = None  # How to use the content from this URL
    section_target: Optional[str] = None  # Which section of the article should use this URL's content
    extraction_type: Optional[str] = None  # e.g., "statistics", "case_study", "methodology", "quotes"

class ArticleRequest(BaseModel):
    topic_category: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    source_url: Optional[str] = None  # Keep for backward compatibility
    source_urls: Optional[List[str]] = None  # New field for multiple URLs (max 5)
    url_instructions: Optional[List[UrlContentInstruction]] = None  # Detailed instructions for URL content
    pdf_base64: Optional[str] = None
    seo_keywords: Optional[str] = None
    custom_prompt: Optional[str] = None  # User's custom instructions
    include_thai_translation: Optional[bool] = False  # Whether to generate Thai translation

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
    thai_content: Optional[str] = None  # Thai translated content
    thai_layout: Optional[ArticleLayout] = None  # Thai translated layout

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
    url_instructions: Optional[List[UrlContentInstruction]] = None  # Detailed instructions for URL content usage
    pdf_content: Optional[str] = None
    seo_keywords: List[str] = []
    custom_prompt: Optional[str] = None