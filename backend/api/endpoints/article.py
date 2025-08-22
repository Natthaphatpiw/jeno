from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import asyncio
import logging
from pydantic import BaseModel
from models.schemas import ArticleRequest, ArticleResponse, GenerationContext, ImageSlot, ArticleLayout
from services.llm_service import LLMService
from services.web_scraper import WebScraperService
from services.pdf_processor import PDFProcessorService
from services.quality_checker import QualityCheckerService
from services.pdf_generator import PDFGeneratorService
from utils.helpers import parse_seo_keywords, validate_url
from config.settings import settings

router = APIRouter()

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize services
llm_service = LLMService()
web_scraper = WebScraperService()
pdf_processor = PDFProcessorService()
quality_checker = QualityCheckerService()
pdf_generator = PDFGeneratorService()

class PDFGenerationRequest(BaseModel):
    content: str
    include_quality_info: bool = True
    quality_score: float = 0.0
    iterations: int = 1

class PDFGenerationResponse(BaseModel):
    pdf_base64: str

@router.post("/generate-pdf", response_model=PDFGenerationResponse)
async def generate_pdf(request: PDFGenerationRequest):
    """Generate PDF from Markdown content using AI"""
    
    logger.info("PDF generation endpoint called")
    logger.info(f"Request content length: {len(request.content)}")
    logger.info(f"Include quality info: {request.include_quality_info}")
    logger.info(f"Quality score: {request.quality_score}")
    logger.info(f"Iterations: {request.iterations}")
    
    try:
        logger.info("Calling PDF generator service...")
        pdf_base64 = pdf_generator.generate_pdf_with_ai(
            content=request.content,
            include_quality_info=request.include_quality_info,
            quality_score=request.quality_score,
            iterations=request.iterations
        )
        
        logger.info(f"PDF generator returned result with length: {len(pdf_base64) if pdf_base64 else 0}")
        
        if not pdf_base64:
            logger.error("PDF generator returned empty content")
            raise HTTPException(status_code=500, detail="Failed to generate PDF content")
        
        logger.info("PDF generation successful, returning response")
        return PDFGenerationResponse(pdf_base64=pdf_base64)
        
    except HTTPException as e:
        logger.error(f"HTTP Exception in PDF generation: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in PDF generation: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@router.post("/generate-article", response_model=ArticleResponse)
async def generate_article(request: ArticleRequest):
    """Generate an article based on provided parameters"""
    
    logger.info("Article generation endpoint called")
    logger.info(f"Request parameters: topic={request.topic_category}, industry={request.industry}")
    logger.info(f"Has source URL: {bool(request.source_url)}")
    logger.info(f"Has PDF: {bool(request.pdf_base64)}")
    
    try:
        # Build generation context
        logger.info("Building generation context...")
        context = await _build_generation_context(request)
        logger.info("Generation context built successfully")
        
        # Generate article with quality loop
        logger.info("Starting article generation with quality loop...")
        article_data = await _generate_with_quality_loop(context)
        logger.info("Article generation completed successfully")
        
        return ArticleResponse(**article_data)
        
    except HTTPException as e:
        logger.error(f"HTTP Exception in article generation: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in article generation: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error generating article: {str(e)}")

async def _build_generation_context(request: ArticleRequest) -> GenerationContext:
    """Build generation context from request"""
    
    logger.info("Building generation context...")
    context_data = {
        "topic_category": request.topic_category,
        "industry": request.industry,
        "target_audience": request.target_audience,
        "seo_keywords": parse_seo_keywords(request.seo_keywords)
    }
    logger.info(f"Basic context data prepared: {list(context_data.keys())}")
    
    # Process source URL if provided
    if request.source_url:
        logger.info(f"Processing source URL: {request.source_url}")
        if not validate_url(request.source_url):
            logger.error(f"Invalid URL format: {request.source_url}")
            raise HTTPException(status_code=400, detail="Invalid source URL format")
        
        try:
            logger.info("Starting web scraping...")
            scraped_content = web_scraper.scrape_url(request.source_url)
            context_data["scraped_content"] = scraped_content
            logger.info(f"Web scraping completed. Content length: {len(scraped_content) if scraped_content else 0}")
        except Exception as e:
            logger.error(f"Web scraping failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error scraping URL: {str(e)}")
    
    # Process PDF if provided
    if request.pdf_base64:
        logger.info("Processing PDF content...")
        try:
            pdf_content = pdf_processor.process_pdf_base64(request.pdf_base64)
            context_data["pdf_content"] = pdf_content
            logger.info(f"PDF processing completed. Content length: {len(pdf_content) if pdf_content else 0}")
        except Exception as e:
            logger.error(f"PDF processing failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")
    
    logger.info("Generation context built successfully")
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