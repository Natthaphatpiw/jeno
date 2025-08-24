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
from services.translation_service import TranslationService
from utils.helpers import parse_seo_keywords, validate_url
from config.settings import settings

router = APIRouter()

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize services
llm_service = LLMService()
from services.llm_service_gemini import LLMServiceGemini
llm_service_gemini = LLMServiceGemini()
web_scraper = WebScraperService()
pdf_processor = PDFProcessorService()
quality_checker = QualityCheckerService()
pdf_generator = PDFGeneratorService()
translation_service = TranslationService()

class PDFGenerationRequest(BaseModel):
    content: str
    include_quality_info: bool = True
    quality_score: float = 0.0
    iterations: int = 1

class PDFGenerationResponse(BaseModel):
    pdf_base64: str

class TranslationRequest(BaseModel):
    markdown_content: str
    layout: dict = {}
    source_usage_details: list = []

class TranslationResponse(BaseModel):
    markdown_content: str
    layout: dict
    source_usage_details: list
    translation_success: bool
    translation_notes: list = []
    error: str = None

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
    logger.info(f"Raw include_thai_translation: {repr(request.include_thai_translation)}")
    logger.info(f"Type of include_thai_translation: {type(request.include_thai_translation)}")
    
    try:
        # Build generation context
        logger.info("Building generation context...")
        context = await _build_generation_context(request)
        logger.info("Generation context built successfully")
        
        # Generate article with quality loop
        logger.info("Starting article generation with quality loop...")
        logger.info(f"Request include_thai_translation: {request.include_thai_translation}")
        logger.info(f"Selected model: {request.selected_model}")
        article_data = await _generate_with_quality_loop(context, request.include_thai_translation, request.selected_model)
        logger.info("Article generation completed successfully")
        
        # Generate article analysis
        logger.info("Starting article analysis...")
        try:
            # Use the same model for analysis as for generation
            selected_llm = llm_service_gemini if request.selected_model == 'gemini-pro' else llm_service
            analysis_result = selected_llm.analyze_article(article_data["content"], context)
            article_data["analysis"] = {
                "strengths": analysis_result.get("strengths", []),
                "weaknesses": analysis_result.get("weaknesses", []),
                "recommendations": analysis_result.get("recommendations", []),
                "summary": analysis_result.get("summary", "")
            }
            logger.info("Article analysis completed successfully")
        except Exception as e:
            logger.error(f"Article analysis failed: {str(e)}")
            # Continue without analysis if it fails
            article_data["analysis"] = None
        
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
        "seo_keywords": parse_seo_keywords(request.seo_keywords),
        "custom_prompt": request.custom_prompt
    }
    logger.info(f"Basic context data prepared: {list(context_data.keys())}")
    
    # Process source URLs if provided
    urls_to_process = []
    
    # Handle backward compatibility with single source_url
    if request.source_url:
        urls_to_process.append(request.source_url)
    
    # Handle new multiple source_urls
    if request.source_urls:
        urls_to_process.extend(request.source_urls)
    
    # Remove duplicates and limit to 5
    urls_to_process = list(dict.fromkeys(urls_to_process))[:5]
    
    if urls_to_process:
        logger.info(f"Processing {len(urls_to_process)} source URLs")
        
        # Validate all URLs
        for url in urls_to_process:
            if not validate_url(url):
                logger.error(f"Invalid URL format: {url}")
                raise HTTPException(status_code=400, detail=f"Invalid URL format: {url}")
        
        try:
            logger.info("Starting web scraping for multiple URLs...")
            if len(urls_to_process) == 1:
                # Single URL - use backward compatible method
                scraped_content = web_scraper.scrape_url(urls_to_process[0])
                context_data["scraped_content"] = scraped_content
                logger.info(f"Web scraping completed. Content length: {len(scraped_content) if scraped_content else 0}")
            else:
                # Multiple URLs - use new method
                scraped_sources = web_scraper.scrape_multiple_urls(urls_to_process, max_urls=5)
                context_data["scraped_sources"] = scraped_sources
                logger.info(f"Multiple URL scraping completed. Sources scraped: {len(scraped_sources)}")
                for i, source in enumerate(scraped_sources, 1):
                    logger.info(f"Source {i}: {source['title']} - {len(source['content'])} characters")
        except Exception as e:
            logger.error(f"Web scraping failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error scraping URLs: {str(e)}")
    
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

async def _generate_with_quality_loop(context: GenerationContext, include_thai_translation: bool = False, selected_model: str = 'gpt-finetune') -> Dict[str, Any]:
    """Generate article with quality checking and iterative improvement"""
    
    iteration = 0
    feedback = None
    
    while iteration < settings.MAX_QUALITY_ITERATIONS:
        iteration += 1
        
        # Generate article using selected model
        try:
            logger.info(f"Using model: {selected_model}")
            if selected_model == 'gemini-pro':
                article_result = llm_service_gemini.generate_article(context, feedback)
            else:
                article_result = llm_service.generate_article(context, feedback)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in article generation: {str(e)}")
        
        # Extract content and layout
        if selected_model == 'gemini-pro':
            content = article_result.get("html_content", "") or article_result.get("content", "")
        else:
            content = article_result.get("markdown_content", "") or article_result.get("content", "")
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
            # Quality is acceptable, prepare result
            result = {
                "content": content,
                "layout": _parse_layout(layout_data),
                "quality_score": quality_feedback.score,
                "iterations": iteration,
                "source_usage_details": article_result.get("source_usage_details", [])
            }
            
            # Generate Thai translation if requested
            logger.info(f"Include Thai translation flag: {include_thai_translation}")
            if include_thai_translation:
                try:
                    logger.info("Generating Thai translation...")
                    logger.info(f"Content length for translation: {len(content)}")
                    thai_result = translation_service.translate_to_thai(
                        markdown_content=content,
                        layout_data=layout_data,
                        source_usage_details=article_result.get("source_usage_details", [])
                    )
                    
                    logger.info(f"Thai translation result keys: {list(thai_result.keys())}")
                    logger.info(f"Translation success: {thai_result.get('translation_success', False)}")
                    
                    if thai_result.get('translation_success', False):
                        result["thai_content"] = thai_result["markdown_content"]
                        result["thai_layout"] = _parse_layout(thai_result["layout"])
                        logger.info(f"Thai translation completed successfully. Thai content length: {len(thai_result['markdown_content'])}")
                    else:
                        logger.warning(f"Thai translation failed: {thai_result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    logger.error(f"Error generating Thai translation: {str(e)}")
                    # Don't fail the whole request if translation fails
                    pass
            
            logger.info(f"Final result keys: {list(result.keys())}")
            if 'thai_content' in result:
                logger.info(f"Returning result with Thai content. Thai content length: {len(result['thai_content'])}")
            else:
                logger.info("Returning result without Thai content")
            
            return result
        
        # Quality below threshold, prepare feedback for next iteration
        if iteration < settings.MAX_QUALITY_ITERATIONS:
            feedback = f"Quality score: {quality_feedback.score:.2f}. {quality_feedback.feedback} Suggestions: {'; '.join(quality_feedback.suggestions)}"
    
    # Max iterations reached, return best attempt
    final_result = {
        "content": content,
        "layout": _parse_layout(layout_data),
        "quality_score": quality_feedback.score,
        "iterations": iteration,
        "source_usage_details": article_result.get("source_usage_details", [])
    }
    
    # Generate Thai translation if requested (even for lower quality articles)
    if include_thai_translation:
        try:
            logger.info("Generating Thai translation for final result...")
            thai_result = translation_service.translate_to_thai(
                markdown_content=content,
                layout_data=layout_data,
                source_usage_details=article_result.get("source_usage_details", [])
            )
            
            if thai_result.get('translation_success', False):
                final_result["thai_content"] = thai_result["markdown_content"]
                final_result["thai_layout"] = _parse_layout(thai_result["layout"])
                logger.info("Final Thai translation completed successfully")
            else:
                logger.warning(f"Final Thai translation failed: {thai_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error generating final Thai translation: {str(e)}")
            # Don't fail the whole request if translation fails
            pass
    
    return final_result

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
                suggested_type=slot_data.get("suggested_type", "photo"),
                placement_rationale=slot_data.get("placement_rationale"),
                content_guidance=slot_data.get("content_guidance"),
                dimensions=slot_data.get("dimensions"),
                aspect_ratio=slot_data.get("aspect_ratio"),
                alternatives=slot_data.get("alternatives")
            ))
    
    return ArticleLayout(
        sections=sections,
        image_slots=image_slots
    )

@router.post("/translate-to-thai", response_model=TranslationResponse)
async def translate_to_thai(request: TranslationRequest):
    """Translate article content to Thai"""
    
    logger.info("Translation to Thai endpoint called")
    logger.info(f"Content length: {len(request.markdown_content)}")
    logger.info(f"Has layout data: {bool(request.layout)}")
    logger.info(f"Has source usage details: {bool(request.source_usage_details)}")
    
    try:
        logger.info("Calling translation service...")
        translation_result = translation_service.translate_to_thai(
            markdown_content=request.markdown_content,
            layout_data=request.layout,
            source_usage_details=request.source_usage_details
        )
        
        logger.info(f"Translation completed. Success: {translation_result.get('translation_success', False)}")
        
        if not translation_result.get('translation_success', False):
            logger.error(f"Translation failed: {translation_result.get('error', 'Unknown error')}")
            raise HTTPException(status_code=500, detail=f"Translation failed: {translation_result.get('error', 'Unknown error')}")
        
        return TranslationResponse(
            markdown_content=translation_result['markdown_content'],
            layout=translation_result['layout'],
            source_usage_details=translation_result['source_usage_details'],
            translation_success=translation_result['translation_success'],
            translation_notes=translation_result.get('translation_notes', [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "article-generator"}