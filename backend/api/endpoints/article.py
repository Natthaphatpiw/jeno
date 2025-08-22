from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import asyncio
from models.schemas import ArticleRequest, ArticleResponse, GenerationContext, ImageSlot, ArticleLayout
from services.llm_service import LLMService
from services.web_scraper import WebScraperService
from services.pdf_processor import PDFProcessorService
from services.quality_checker import QualityCheckerService
from utils.helpers import parse_seo_keywords, validate_url
from config.settings import settings

router = APIRouter()

# Initialize services
llm_service = LLMService()
web_scraper = WebScraperService()
pdf_processor = PDFProcessorService()
quality_checker = QualityCheckerService()

@router.post("/generate-article", response_model=ArticleResponse)
async def generate_article(request: ArticleRequest):
    """Generate an article based on provided parameters"""
    
    try:
        # Build generation context
        context = await _build_generation_context(request)
        
        # Generate article with quality loop
        article_data = await _generate_with_quality_loop(context)
        
        return ArticleResponse(**article_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating article: {str(e)}")

async def _build_generation_context(request: ArticleRequest) -> GenerationContext:
    """Build generation context from request"""
    
    context_data = {
        "topic_category": request.topic_category,
        "industry": request.industry,
        "target_audience": request.target_audience,
        "seo_keywords": parse_seo_keywords(request.seo_keywords)
    }
    
    # Process source URL if provided
    if request.source_url:
        if not validate_url(request.source_url):
            raise HTTPException(status_code=400, detail="Invalid source URL format")
        
        try:
            scraped_content = web_scraper.scrape_url(request.source_url)
            context_data["scraped_content"] = scraped_content
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error scraping URL: {str(e)}")
    
    # Process PDF if provided
    if request.pdf_base64:
        try:
            pdf_content = pdf_processor.process_pdf_base64(request.pdf_base64)
            context_data["pdf_content"] = pdf_content
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")
    
    return GenerationContext(**context_data)

async def _generate_with_quality_loop(context: GenerationContext) -> Dict[str, Any]:
    """Generate article with quality checking and iterative improvement"""
    
    iteration = 0
    feedback = None
    
    while iteration < settings.MAX_QUALITY_ITERATIONS:
        iteration += 1
        
        # Generate article
        try:
            article_result = llm_service.generate_article(context, feedback)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in article generation: {str(e)}")
        
        # Extract content and layout
        content = article_result.get("content", "")
        layout_data = article_result.get("layout", {})
        
        if not content:
            raise HTTPException(status_code=500, detail="Generated article has no content")
        
        # Evaluate quality
        quality_context = {
            "topic_category": context.topic_category,
            "industry": context.industry,
            "target_audience": context.target_audience,
            "seo_keywords": ", ".join(context.seo_keywords) if context.seo_keywords else None
        }
        
        try:
            quality_feedback = quality_checker.evaluate_article_quality(content, quality_context)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in quality evaluation: {str(e)}")
        
        # Check if quality meets threshold
        if quality_feedback.score >= settings.QUALITY_THRESHOLD:
            # Quality is acceptable, return result
            return {
                "content": content,
                "layout": _parse_layout(layout_data),
                "quality_score": quality_feedback.score,
                "iterations": iteration
            }
        
        # Quality below threshold, prepare feedback for next iteration
        if iteration < settings.MAX_QUALITY_ITERATIONS:
            feedback = f"Quality score: {quality_feedback.score:.2f}. {quality_feedback.feedback} Suggestions: {'; '.join(quality_feedback.suggestions)}"
    
    # Max iterations reached, return best attempt
    return {
        "content": content,
        "layout": _parse_layout(layout_data),
        "quality_score": quality_feedback.score,
        "iterations": iteration
    }

def _parse_layout(layout_data: Dict[str, Any]) -> ArticleLayout:
    """Parse layout data into ArticleLayout model"""
    
    sections = layout_data.get("sections", [])
    image_slots_data = layout_data.get("image_slots", [])
    
    image_slots = []
    for slot_data in image_slots_data:
        if isinstance(slot_data, dict):
            image_slots.append(ImageSlot(
                id=slot_data.get("id", f"img_{len(image_slots)}"),
                description=slot_data.get("description", "Image placeholder"),
                position=slot_data.get("position", "article"),
                suggested_type=slot_data.get("suggested_type", "photo")
            ))
    
    return ArticleLayout(
        sections=sections,
        image_slots=image_slots
    )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "article-generator"}