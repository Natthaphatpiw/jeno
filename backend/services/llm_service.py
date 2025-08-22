import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from config.settings import settings
from models.schemas import GenerationContext, ArticleResponse, ArticleLayout, ImageSlot

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_article(self, context: GenerationContext, feedback: Optional[str] = None) -> Dict[str, Any]:
        """Generate article content using GPT-4o"""
        
        logger.info("Starting article generation with LLM")
        logger.info(f"Context: topic={context.topic_category}, industry={context.industry}")
        logger.info(f"Has feedback: {feedback is not None}")
        
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_user_prompt(context, feedback)
        
        logger.info(f"System prompt length: {len(system_prompt)}")
        logger.info(f"User prompt length: {len(user_prompt)}")
        
        try:
            logger.info("Calling OpenAI API for article generation...")
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            logger.info("OpenAI API call successful for article generation")
            
            content = response.choices[0].message.content
            logger.info(f"Response content length: {len(content) if content else 0}")
            
            if not content:
                logger.error("OpenAI returned empty content for article generation")
                raise Exception("OpenAI returned empty response")
            
            logger.info("Parsing JSON response...")
            result = json.loads(content)
            logger.info(f"JSON parsed successfully. Keys: {list(result.keys())}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in article generation: {str(e)}")
            logger.error(f"Raw response: {content[:500]}..." if content else "No content")
            raise Exception(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Error in article generation: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Error generating article: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for article generation"""
        return """You are an expert content creator for Jenosize, a forward-thinking business consultancy. Your task is to generate high-quality, insightful articles about trends and future ideas for businesses.

JENOSIZE TONE AND STYLE:
- Professional yet approachable
- Data-driven insights with practical applications
- Forward-looking perspective on business trends
- Actionable advice for business leaders
- Engaging storytelling with concrete examples
- Balance of optimism and realism about future trends

ARTICLE REQUIREMENTS:
- Length: 1500-2500 words
- Structure: Introduction, 3-5 main sections, conclusion
- Include relevant statistics and examples
- Focus on actionable insights
- SEO-optimized when keywords provided
- Professional formatting with clear headings

RESPONSE FORMAT:
Return a JSON object with:
{
  "content": "Full article content in Markdown format with proper headings, structure, and image placeholders",
  "layout": {
    "sections": ["array", "of", "section", "titles"],
    "image_slots": [
      {
        "id": "unique_id",
        "description": "Description of suggested image",
        "position": "section_name_or_introduction",
        "suggested_type": "chart/photo/infographic/illustration"
      }
    ]
  }
}

MARKDOWN FORMATTING GUIDELINES:
- Use proper heading hierarchy (# ## ### ####)
- Include tables where appropriate for data presentation
- Use bullet points and numbered lists for clarity
- Add emphasis with **bold** and *italic* text
- Include image placeholders as: ![{{image_id}}](placeholder) where {{image_id}} matches the slot id
- Use proper paragraph spacing and line breaks
- Include blockquotes for key insights: > Important insight here

IMAGE PLACEMENT:
- Suggest 3-5 strategic image placements within the article content
- Place images logically within sections to enhance understanding
- Include specific image placeholders in the Markdown content
- Ensure image slots enhance rather than interrupt the reading flow

IMPORTANT: You must respond in JSON format only. Return your response as a valid JSON object with the structure specified above."""
    
    def _build_user_prompt(self, context: GenerationContext, feedback: Optional[str] = None) -> str:
        """Build the user prompt based on context and feedback"""
        
        prompt_parts = []
        
        if feedback:
            prompt_parts.append(f"PREVIOUS FEEDBACK TO IMPROVE: {feedback}\n")
        
        prompt_parts.append("Generate a comprehensive article with the following specifications:\n")
        
        if context.topic_category:
            prompt_parts.append(f"Topic Category: {context.topic_category}")
        
        if context.industry:
            prompt_parts.append(f"Industry Focus: {context.industry}")
        
        if context.target_audience:
            prompt_parts.append(f"Target Audience: {context.target_audience}")
        
        if context.seo_keywords:
            prompt_parts.append(f"SEO Keywords to incorporate: {', '.join(context.seo_keywords)}")
        
        if context.scraped_content:
            prompt_parts.append(f"\nReference Content from provided source:\n{context.scraped_content[:2000]}...")
        
        if context.pdf_content:
            prompt_parts.append(f"\nReference Content from uploaded document:\n{context.pdf_content[:2000]}...")
        
        if not any([context.topic_category, context.industry, context.scraped_content, context.pdf_content]):
            prompt_parts.append("Generate an article about emerging business trends and future opportunities.")
        
        prompt_parts.append("\nReturn your response as a JSON object with the specified format.")
        
        return "\n".join(prompt_parts)