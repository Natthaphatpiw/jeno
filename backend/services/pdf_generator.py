import base64
import json
import logging
from openai import OpenAI
from config.settings import settings

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
    logger.info("WeasyPrint is available")
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger.warning("WeasyPrint is not available")

class PDFGeneratorService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_pdf_with_ai(self, content: str, include_quality_info: bool = True, 
                           quality_score: float = 0.0, iterations: int = 1) -> str:
        """Generate PDF using AI-enhanced HTML formatting"""
        
        logger.info(f"Starting AI PDF generation for content length: {len(content)}")
        logger.info(f"Parameters: include_quality_info={include_quality_info}, quality_score={quality_score}, iterations={iterations}")
        
        try:
            # First, get AI-enhanced HTML
            system_prompt = self._get_html_system_prompt()
            user_prompt = self._build_html_user_prompt(content, include_quality_info, quality_score, iterations)
            
            logger.info(f"System prompt length: {len(system_prompt)}")
            logger.info(f"User prompt length: {len(user_prompt)}")
            
            logger.info("Calling OpenAI API for HTML generation...")
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=settings.MAX_TOKENS,
                temperature=0.1,  # Lower temperature for consistent formatting
                response_format={"type": "json_object"}
            )
            
            logger.info("OpenAI API call successful")
            
            response_content = response.choices[0].message.content
            logger.info(f"Response content length: {len(response_content) if response_content else 0}")
            
            if not response_content:
                raise Exception("OpenAI returned empty response")
            
            logger.info("Parsing JSON response...")
            result = json.loads(response_content)
            logger.info(f"JSON parsed successfully. Keys: {list(result.keys())}")
            
            enhanced_html = result.get("html_content", "")
            logger.info(f"Enhanced HTML length: {len(enhanced_html)}")
            
            if not enhanced_html:
                logger.error("AI did not generate HTML content")
                raise Exception("AI did not generate HTML content")
            
            # For now, return the enhanced HTML as base64 for client-side processing
            # This allows better control over PDF generation on the frontend
            logger.info("Converting HTML to base64...")
            html_base64 = base64.b64encode(enhanced_html.encode('utf-8')).decode('utf-8')
            logger.info(f"Base64 encoding successful. Length: {len(html_base64)}")
            
            return html_base64
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.error(f"Raw response content: {response_content[:500]}...")
            raise Exception(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"Error in AI PDF generation: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            raise Exception(f"Error generating PDF with AI: {str(e)}")
    
    def _convert_html_to_pdf_weasyprint(self, html_content: str) -> str:
        """Convert HTML to PDF using WeasyPrint"""
        try:
            # Create PDF from HTML
            pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
            
            # Convert to base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            return pdf_base64
            
        except Exception as e:
            raise Exception(f"Error converting HTML to PDF: {str(e)}")
    
    def _get_html_system_prompt(self) -> str:
        """Get system prompt for HTML generation"""
        return """You are a professional HTML document generator for Jenosize business consultancy. Your task is to create high-quality, professionally formatted HTML documents from Markdown content that will be converted to PDF.

FORMATTING REQUIREMENTS:
- Use professional business document layout with CSS styling
- Proper typography hierarchy (h1, h2, h3, p tags)
- Clean margins and spacing using CSS
- Professional color scheme (dark navy #1a202c, blues #2d3748, sky blue #0ea5e9, whites)
- Tables with proper borders and headers using CSS
- Image placeholders with clear descriptions
- Page break styles for PDF conversion
- Jenosize branding elements

CONTENT PROCESSING:
- Convert Markdown formatting to semantic HTML
- Handle image placeholders appropriately
- Maintain readability and professional appearance
- Ensure consistent spacing and alignment
- Include quality information if requested
- Use inline CSS for PDF compatibility

OUTPUT FORMAT:
You must return a JSON object with:
{
  "html_content": "complete_html_document_with_inline_css"
}

IMPORTANT: 
- Return only valid JSON format
- Generate complete HTML document with DOCTYPE and inline CSS
- Ensure PDF-compatible HTML/CSS
- Handle all Markdown elements properly
- Create visually appealing layout similar to business reports
- Use print-friendly CSS styles"""

    def _build_html_user_prompt(self, content: str, include_quality_info: bool, 
                             quality_score: float, iterations: int) -> str:
        """Build user prompt for HTML generation"""
        
        prompt_parts = []
        
        if include_quality_info:
            prompt_parts.append(f"""QUALITY INFORMATION:
- Article Quality Score: {quality_score:.1%}
- Generated in {iterations} iteration{'s' if iterations != 1 else ''}
- Powered by GPT-4o AI

Include this information in a professional header section.""")
        
        prompt_parts.append(f"""MARKDOWN CONTENT TO CONVERT:
{content}

INSTRUCTIONS:
1. Convert the above Markdown content to a professional PDF document
2. Use proper typography and spacing
3. Handle image placeholders appropriately 
4. Maintain business document standards
5. Return the complete PDF as base64 encoded content

Return your response as a JSON object with the pdf_base64 field containing the base64 encoded PDF content.""")
        
        return "\n\n".join(prompt_parts)