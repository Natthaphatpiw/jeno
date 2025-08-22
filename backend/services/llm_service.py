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

REFERENCE CONTENT USAGE GUIDELINES:
When using content from provided URLs or documents:
- Always cite and reference the source material appropriately
- Clearly indicate which sections of your article use which sources
- Integrate source material naturally while maintaining Jenosize's voice
- Use source content to support your arguments, not replace original thinking
- Ensure proper attribution and avoid direct copying without context
- Transform source insights into actionable business advice for your audience

ARTICLE REQUIREMENTS:
- Length: 1500-2500 words
- Structure: Introduction, 3-5 main sections, conclusion
- Include relevant statistics and examples
- Focus on actionable insights
- SEO-optimized when keywords provided
- Professional formatting with clear headings
- Strategic image placement with detailed recommendations for users

RESPONSE FORMAT:
Return a JSON object with:
{
  "content": "Full article content in Markdown format with proper headings, structure, and image placeholders",
  "layout": {
    "sections": ["array", "of", "section", "titles"],
    "image_slots": [
      {
        "id": "unique_id",
        "description": "Detailed description of what image should show",
        "position": "section_name_or_introduction",
        "suggested_type": "chart/photo/infographic/illustration",
        "placement_rationale": "Why this image belongs in this specific location",
        "content_guidance": "Specific visual elements, data, or concepts to include",
        "dimensions": "Recommended width x height (e.g., 800x400px)",
        "aspect_ratio": "Recommended ratio (e.g., 16:9, 4:3, 1:1)",
        "alternatives": "Alternative image options if primary isn't available"
      }
    ]
  },
  "source_usage_details": [
    {
      "source_title": "Name of the source",
      "source_url": "URL of the source",
      "content_used": "Specific content/data/quotes extracted from this source",
      "usage_location": "Exact section and paragraph where this content appears",
      "usage_purpose": "Why this specific content was chosen and how it supports the argument",
      "transformation": "How the original content was adapted/transformed for the article"
    }
  ]
}

MARKDOWN FORMATTING GUIDELINES:
- Use proper heading hierarchy (# ## ### ####)
- Include tables where appropriate for data presentation
- Use bullet points and numbered lists for clarity
- Add emphasis with **bold** and *italic* text
- Include image placeholders as: ![{{image_id}}](placeholder) where {{image_id}} matches the slot id
- Use proper paragraph spacing and line breaks
- Include blockquotes for key insights: > Important insight here

IMAGE PLACEMENT GUIDELINES:
- Suggest 3-5 strategic image placements within the article content
- Place images logically within sections to enhance understanding
- Include specific image placeholders in the Markdown content with proper spacing
- Ensure image slots enhance rather than interrupt the reading flow

IMAGE RECOMMENDATIONS FOR USERS:
For each image slot, provide detailed guidance including:
- Exact placement rationale (why this image belongs here)
- Specific visual content recommendations (charts, photos, diagrams, etc.)
- Ideal image dimensions and aspect ratio suggestions
- How the image should relate to the surrounding text content
- Alternative image options if the primary suggestion isn't available

SPACING AND FORMATTING:
- Add 2-3 empty lines before and after each image placeholder
- Include clear section breaks where images naturally fit
- Ensure adequate white space around images for professional appearance
- Place images at natural content breaks, not mid-paragraph

MULTIPLE SOURCE INTEGRATION:
When multiple reference sources are provided:
- Use different sources to support different sections or arguments
- Document exactly which content from each source is used and where
- Vary your source usage to avoid over-reliance on a single reference
- Combine insights from multiple sources to create comprehensive sections
- Use source titles as they appear in the reference material for mapping
- Ensure each source contributes meaningfully to at least one section
- Balance source usage across the article structure

DETAILED SOURCE USAGE DOCUMENTATION:
For each source used, provide in source_usage_details:
- **content_used**: Quote or paraphrase the specific content/data/statistics extracted
- **usage_location**: Specify exact section, paragraph, or sentence where content appears
- **usage_purpose**: Explain why this content was selected and how it supports your argument
- **transformation**: Describe how you adapted/rephrased/contextualized the original content
- Be specific about data points, statistics, quotes, or insights used
- Include any modifications made to fit Jenosize's tone and business focus

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
        
        if context.custom_prompt:
            prompt_parts.append(f"\\nCUSTOM USER INSTRUCTIONS: {context.custom_prompt}")
        
        # Handle single source (backward compatibility)
        if context.scraped_content:
            prompt_parts.append(f"\nReference Content from provided source:\n{context.scraped_content[:2000]}...")
        
        # Handle multiple sources
        if context.scraped_sources:
            prompt_parts.append("\nMultiple Reference Sources:")
            for i, source in enumerate(context.scraped_sources, 1):
                title = source.get('title', f'Source {i}')
                url = source.get('url', 'Unknown URL')
                content = source.get('content', '')[:1500]  # Limit each source to 1500 chars to fit within token limits
                
                prompt_parts.append(f"\nSource {i} - {title}")
                prompt_parts.append(f"URL: {url}")
                prompt_parts.append(f"Content: {content}...")
                
            prompt_parts.append("\nIMPORTANT: Use the source titles exactly as provided above in your source_mapping response. Distribute content usage across different article sections and clearly map which sections reference which sources.")
        
        if context.pdf_content:
            prompt_parts.append(f"\nReference Content from uploaded document:\n{context.pdf_content[:2000]}...")
        
        if not any([context.topic_category, context.industry, context.scraped_content, context.scraped_sources, context.pdf_content]):
            prompt_parts.append("Generate an article about emerging business trends and future opportunities.")
        
        prompt_parts.append("\nReturn your response as a JSON object with the specified format.")
        
        return "\n".join(prompt_parts)
    
    def analyze_article(self, content: str, context: GenerationContext) -> Dict[str, Any]:
        """Generate analysis and feedback for the article"""
        
        logger.info("Starting article analysis with LLM")
        
        system_prompt = self._get_analysis_system_prompt()
        user_prompt = self._build_analysis_user_prompt(content, context)
        
        logger.info(f"Analysis system prompt length: {len(system_prompt)}")
        logger.info(f"Analysis user prompt length: {len(user_prompt)}")
        
        try:
            logger.info("Calling OpenAI API for article analysis...")
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,  # Shorter response for analysis
                temperature=0.3,  # Lower temperature for more consistent analysis
                response_format={"type": "json_object"}
            )
            
            logger.info("OpenAI API call successful for article analysis")
            
            content_response = response.choices[0].message.content
            logger.info(f"Analysis response content length: {len(content_response) if content_response else 0}")
            
            if not content_response:
                logger.error("OpenAI returned empty content for article analysis")
                raise Exception("OpenAI returned empty analysis response")
            
            logger.info("Parsing analysis JSON response...")
            result = json.loads(content_response)
            logger.info(f"Analysis JSON parsed successfully. Keys: {list(result.keys())}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in article analysis: {str(e)}")
            logger.error(f"Raw response: {content_response[:500]}..." if content_response else "No content")
            raise Exception(f"Invalid JSON response from analysis AI: {str(e)}")
        except Exception as e:
            logger.error(f"Error in article analysis: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Error analyzing article: {str(e)}")
    
    def _get_analysis_system_prompt(self) -> str:
        """Get the system prompt for article analysis"""
        return """You are an expert content analyst for Jenosize, a business consultancy. Your task is to analyze generated articles and provide constructive feedback.

ANALYSIS FOCUS:
- Content quality and business relevance
- Structure and readability
- Use of source materials and data
- Actionability for business leaders
- Areas for improvement

RESPONSE FORMAT:
Return a JSON object with:
{
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2"],
  "recommendations": ["recommendation1", "recommendation2"],
  "summary": "2-3 sentence overall assessment focusing on pros, cons, and key suggestions"
}

ANALYSIS GUIDELINES:
- Be constructive and specific in feedback
- Focus on business value and practical application
- Consider the target audience and industry context
- Evaluate source integration and data usage
- Suggest concrete improvements
- Keep summary concise but insightful

IMPORTANT: You must respond in JSON format only."""
    
    def _build_analysis_user_prompt(self, content: str, context: GenerationContext) -> str:
        """Build the user prompt for article analysis"""
        
        prompt_parts = [
            "Analyze the following article and provide detailed feedback:",
            f"\\nTarget Audience: {context.target_audience or 'General business leaders'}",
            f"Industry: {context.industry or 'General business'}",
            f"Topic Category: {context.topic_category or 'Business trends'}"
        ]
        
        if context.seo_keywords:
            prompt_parts.append(f"SEO Keywords: {', '.join(context.seo_keywords)}")
        
        # Include article content (truncated to fit token limits)
        prompt_parts.append(f"\\nARTICLE CONTENT:\\n{content[:3000]}...")
        
        prompt_parts.append("\\nProvide analysis in the specified JSON format.")
        
        return "\\n".join(prompt_parts)