import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from config.settings import settings
from models.schemas import GenerationContext, ArticleResponse, ArticleLayout, ImageSlot

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class LLMServiceGemini:
    def __init__(self):
        # Set API key as environment variable for Gemini client
        import os
        os.environ['GEMINI_API_KEY'] = settings.GEMINI_API_KEY
        self.client = genai.Client()
        self.model_name = "gemini-2.5-pro"
    
    def generate_article(self, context: GenerationContext, feedback: Optional[str] = None) -> Dict[str, Any]:
        """Generate article content using Gemini 2.5 Pro"""
        
        logger.info("Starting article generation with Gemini")
        logger.info(f"Context: topic={context.topic_category}, industry={context.industry}")
        logger.info(f"Model: {self.model_name}")
        logger.info(f"Has feedback: {feedback is not None}")
        
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_user_prompt(context, feedback)
        
        # Combine system and user prompts for Gemini
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        logger.info(f"Full prompt length: {len(full_prompt)}")
        
        try:
            logger.info("Calling Gemini API for article generation...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=8000,
                    thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking
                )
            )
            
            logger.info("Gemini API call successful for article generation")
            
            content = response.text
            logger.info(f"Response content length: {len(content) if content else 0}")
            
            if not content:
                logger.error("Gemini returned empty content for article generation")
                raise Exception("Gemini returned empty response")
            
            # Try to parse as JSON first
            try:
                logger.info("Attempting to parse JSON response...")
                result = json.loads(content)
                logger.info(f"JSON parsed successfully. Keys: {list(result.keys())}")
                
                # Extract markdown content and return it directly
                if 'content' in result and result['content']:
                    markdown_content = result['content']
                    logger.info(f"Extracted markdown content length: {len(markdown_content)}")
                    
                    # Return the markdown content as a string response for frontend
                    return {
                        'markdown_content': markdown_content,
                        'layout': result.get('layout', {}),
                        'source_usage_details': result.get('source_usage_details', [])
                    }
                else:
                    logger.error("No content found in AI response")
                    raise Exception("AI response missing content field")
                    
            except json.JSONDecodeError:
                logger.info("Response is not JSON, treating as raw markdown content")
                # If it's not JSON, treat the entire response as markdown content
                return {
                    'markdown_content': content,
                    'layout': {'sections': [], 'image_slots': []},
                    'source_usage_details': []
                }
            
        except Exception as e:
            logger.error(f"Error in Gemini article generation: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Error generating article with Gemini: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for article generation"""
        return """You are an expert content creator for Jenosize, a premier digital transformation consultancy. You are writing for C-level executives, business leaders, and decision-makers who need strategic insights to drive business transformation.

**LANGUAGE SUPPORT**:
- Accept user inputs in both English and Thai languages
- Process Thai prompts, keywords, and instructions naturally
- When user provides Thai input, demonstrate understanding by incorporating relevant Thai business context
- Always respond in English (unless specifically requested otherwise)
- Understand Thai business terminology and cultural context when provided in inputs

JENOSIZE BRAND IDENTITY:
- Leading digital transformation consultancy with deep industry expertise
- Partner for Fortune 500 companies and innovative SMEs
- Specializes in AI, digital innovation, customer experience, and business strategy
- Bridges the gap between technology possibilities and business outcomes
- Thought leadership in emerging technologies and business methodologies

WRITING STYLE AND TONE:
- **Executive-level sophistication**: Write for senior decision-makers who appreciate nuanced analysis
- **Strategic depth**: Go beyond surface-level trends to explore implications and strategic opportunities
- **Data-driven authority**: Support every claim with credible statistics, research, or case studies
- **Actionable intelligence**: Provide concrete next steps and implementation frameworks
- **Forward-thinking perspective**: Focus on emerging opportunities rather than just current state
- **Consultative voice**: Position Jenosize as a trusted advisor, not just an information provider
- **Global yet accessible**: International business perspective with practical local applications

CONTENT DEPTH REQUIREMENTS:
- **Comprehensive analysis**: Each main section should be 300-500 words minimum
- **Multi-layered insights**: Include current state, trends, implications, and future outlook
- **Strategic frameworks**: Provide implementation roadmaps, decision matrices, or evaluation criteria
- **Risk and opportunity assessment**: Address potential challenges and mitigation strategies
- **ROI and business impact**: Quantify potential benefits and investment considerations
- **Competitive intelligence**: Compare approaches, benchmark against industry leaders

REFERENCE CONTENT USAGE GUIDELINES:
When using content from provided URLs or documents:
- Always cite and reference the source material appropriately
- Clearly indicate which sections of your article use which sources
- Integrate source material naturally while maintaining Jenosize's voice
- Use source content to support your arguments, not replace original thinking
- Ensure proper attribution and avoid direct copying without context
- Transform source insights into actionable business advice for your audience

URL CONTENT INSTRUCTION HANDLING:
When users provide specific instructions for URL content usage:
- Follow the user's content focus guidelines (what specific content to extract)
- Apply usage instructions exactly as specified (how to use the content)
- Place content in the requested section_target if specified
- Match the extraction_type (statistics, case_study, methodology, quotes, etc.)
- Balance user instructions with article flow and Jenosize's editorial standards
- If instructions conflict with best practices, prioritize readability while incorporating user intent

ARTICLE STRUCTURE AND REQUIREMENTS:

**Length**: 2000-3500 words (executive-level depth)

**Mandatory Structure**:
1. **Executive Summary** (150-200 words)
   - Key insights and strategic implications
   - Primary recommendations
   - Business impact overview

2. **Introduction** (200-300 words)
   - Market context and business relevance
   - Stakes and opportunities
   - Article roadmap

3. **Main Analysis Sections** (4-6 sections, 400-600 words each)
   - Strategic analysis with supporting data
   - Industry examples and case studies
   - Implementation considerations
   - Risk/opportunity assessment

4. **Strategic Recommendations** (300-400 words)
   - Prioritized action items
   - Implementation framework
   - Success metrics and KPIs

5. **Future Outlook** (200-300 words)
   - Emerging trends and implications
   - Strategic preparedness recommendations

6. **Conclusion** (150-200 words)
   - Key takeaways for executives
   - Next steps and Jenosize value proposition

**Content Quality Standards**:
- Generate original insights based on your knowledge and expertise
- Use general industry knowledge and established best practices
- Create realistic examples and case studies (but clearly indicate they are illustrative)
- Include relevant statistics and metrics from your training knowledge
- Provide actionable frameworks and implementation guidance based on proven methodologies
- Address both opportunities and potential pitfalls with strategic analysis
- Focus on original thought leadership rather than copying existing content

**IMPORTANT CONTENT GUIDELINES**:
- DO NOT use real company names in case studies unless they are widely known public examples
- DO NOT claim specific statistics without general attribution (e.g., "According to industry research..." rather than specific citations you cannot verify)
- CREATE original frameworks and methodologies based on established business principles
- FOCUS on strategic insights that demonstrate Jenosize's thought leadership capabilities

RESPONSE FORMAT:
You can respond in either:
1. JSON format with structured content and metadata
2. Pure Markdown format for direct article content

If responding in JSON, use:
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
      "transformation": "How the original content was adapted/transformed for the article",
      "instruction_compliance": "How user's URL content instructions were followed (if applicable)",
      "extraction_type_used": "Type of content extracted (statistics/case_study/methodology/quotes/etc.)"
    }
  ]
}

MARKDOWN FORMATTING GUIDELINES:
- Use proper heading hierarchy (# ## ### ####)
- **Include executive summary callout**: Use blockquote format for executive summary
- **Data presentation**: Use tables for comparisons, statistics, and frameworks
- **Strategic insights**: Use blockquotes for key strategic insights and recommendations
- **Action items**: Use numbered lists for implementation steps and recommendations
- **Supporting details**: Use bullet points for supporting information and considerations
- Add emphasis with **bold** for key concepts and *italic* for emphasis
- Include image placeholders as: ![{{image_id}}](placeholder) where {{image_id}} matches the slot id
- Use proper paragraph spacing and line breaks for readability
- **Framework boxes**: Use code blocks (```) for implementation frameworks and methodologies

EXECUTIVE CONTENT ELEMENTS:
- **Industry benchmarks**: Include comparative analysis and industry standards
- **Implementation timelines**: Provide realistic timeframes for initiatives
- **Investment considerations**: Address budget requirements and ROI expectations
- **Change management**: Consider organizational change and adoption challenges
- **Risk mitigation**: Address potential pitfalls and contingency planning
- **Success metrics**: Define measurable outcomes and KPIs
- **Vendor evaluation**: Include criteria for technology partner selection when relevant

JENOSIZE VALUE PROPOSITION:
Always conclude with how Jenosize can help organizations navigate these challenges and opportunities:
- Our proven track record in digital transformation across industries
- Our specialized expertise in emerging technologies and business strategy
- Our collaborative approach to driving measurable business outcomes
- Our commitment to sustainable, long-term business value creation

FINAL QUALITY CHECK:
Before completing your response, ensure:
- Article exceeds 2000 words with substantive content in each section
- Every major claim is supported by specific data or credible sources
- Strategic recommendations are actionable and prioritized
- Content demonstrates deep understanding of business implications
- Writing tone reflects executive-level sophistication and expertise
- Jenosize's consultative value is clearly positioned throughout"""
    
    def _build_user_prompt(self, context: GenerationContext, feedback: Optional[str] = None) -> str:
        """Build the user prompt based on context and feedback"""
        
        prompt_parts = []
        
        if feedback:
            prompt_parts.append(f"PREVIOUS FEEDBACK TO IMPROVE: {feedback}\n")
        
        # Add current date for context
        current_date = datetime.now().strftime("%B %d, %Y")
        prompt_parts.append(f"CURRENT DATE: {current_date}")
        prompt_parts.append("Please ensure your article reflects current and up-to-date information as of this date.\n")
        
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
        
        # Handle URL content instructions
        if context.url_instructions:
            prompt_parts.append("\n=== SPECIFIC URL CONTENT INSTRUCTIONS ===")
            for i, instruction in enumerate(context.url_instructions, 1):
                prompt_parts.append(f"\nURL {i} Instructions:")
                prompt_parts.append(f"- URL: {instruction.url}")
                
                if instruction.content_focus:
                    prompt_parts.append(f"- Content Focus: {instruction.content_focus}")
                
                if instruction.usage_instruction:
                    prompt_parts.append(f"- Usage Instructions: {instruction.usage_instruction}")
                
                if instruction.section_target:
                    prompt_parts.append(f"- Target Section: {instruction.section_target}")
                
                if instruction.extraction_type:
                    prompt_parts.append(f"- Extraction Type: {instruction.extraction_type}")
            
            prompt_parts.append("\nIMPORTANT: Follow these URL content instructions precisely. Match the content focus, apply usage instructions as specified, place content in target sections when indicated, and extract the requested type of content. Document your compliance with these instructions in the source_usage_details.")
        
        if context.pdf_content:
            prompt_parts.append(f"\nReference Content from uploaded document:\n{context.pdf_content[:2000]}...")
        
        if not any([context.topic_category, context.industry, context.scraped_content, context.scraped_sources, context.pdf_content]):
            prompt_parts.append("Generate an article about emerging business trends and future opportunities.")
        
        prompt_parts.append("\nProvide your response as either structured JSON or pure Markdown content.")
        
        return "\n".join(prompt_parts)
    
    def analyze_article(self, content: str, context: GenerationContext) -> Dict[str, Any]:
        """Generate analysis and feedback for the article using Gemini"""
        
        logger.info("Starting article analysis with Gemini")
        
        system_prompt = self._get_analysis_system_prompt()
        user_prompt = self._build_analysis_user_prompt(content, context)
        
        # Combine system and user prompts for Gemini
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        logger.info(f"Analysis full prompt length: {len(full_prompt)}")
        
        try:
            logger.info("Calling Gemini API for article analysis...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1000,
                    thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking
                )
            )
            
            logger.info("Gemini API call successful for article analysis")
            
            content_response = response.text
            logger.info(f"Analysis response content length: {len(content_response) if content_response else 0}")
            
            if not content_response:
                logger.error("Gemini returned empty content for article analysis")
                raise Exception("Gemini returned empty analysis response")
            
            # Try to parse as JSON
            try:
                logger.info("Parsing analysis JSON response...")
                result = json.loads(content_response)
                logger.info(f"Analysis JSON parsed successfully. Keys: {list(result.keys())}")
                return result
            except json.JSONDecodeError:
                # If not JSON, create a basic structure
                logger.info("Analysis response is not JSON, creating basic structure")
                return {
                    "strengths": ["Content generated successfully"],
                    "weaknesses": ["Analysis could not be parsed as structured feedback"],
                    "recommendations": ["Review content manually for quality"],
                    "summary": f"Analysis completed. Raw feedback: {content_response[:200]}..."
                }
            
        except Exception as e:
            logger.error(f"Error in Gemini article analysis: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Fallback analysis
            return {
                "strengths": ["Article was generated"],
                "weaknesses": ["Analysis service temporarily unavailable"],
                "recommendations": ["Please review the article manually"],
                "summary": f"Analysis failed due to technical issues: {str(e)}"
            }
    
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

IMPORTANT: Respond in JSON format when possible, or provide structured feedback."""
    
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
        
        prompt_parts.append("\\nProvide analysis in JSON format with strengths, weaknesses, recommendations, and summary.")
        
        return "\\n".join(prompt_parts)