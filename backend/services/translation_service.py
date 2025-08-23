import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from config.settings import settings

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class TranslationService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def translate_to_thai(self, markdown_content: str, layout_data: Dict = None, 
                         source_usage_details: list = None) -> Dict[str, Any]:
        """
        Translate article content from English to Thai
        
        Args:
            markdown_content: English markdown content
            layout_data: Article layout information
            source_usage_details: Source usage information
            
        Returns:
            Dict containing translated content and preserved layout
        """
        
        logger.info(f"Starting translation to Thai for content length: {len(markdown_content)}")
        
        if not markdown_content or not markdown_content.strip():
            logger.warning("Empty content provided for translation")
            return {
                'markdown_content': '',
                'layout': layout_data or {},
                'source_usage_details': source_usage_details or [],
                'translation_success': False,
                'error': 'Empty content'
            }
        
        try:
            system_prompt = self._get_translation_system_prompt()
            user_prompt = self._build_translation_user_prompt(markdown_content, layout_data, source_usage_details)
            
            logger.info("Calling OpenAI API for Thai translation...")
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",  # Use GPT-4o for better Thai translation
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=8000,  # Sufficient for long articles
                temperature=0.2,  # Low temperature for consistent translation
                response_format={"type": "json_object"}
            )
            
            logger.info("OpenAI API call successful for translation")
            
            response_content = response.choices[0].message.content
            logger.info(f"Translation response length: {len(response_content) if response_content else 0}")
            
            if not response_content:
                logger.error("OpenAI returned empty content for translation")
                raise Exception("OpenAI returned empty translation response")
            
            logger.info("Parsing translation JSON response...")
            result = json.loads(response_content)
            logger.info(f"Translation JSON parsed successfully. Keys: {list(result.keys())}")
            
            thai_content = result.get("thai_content", "")
            logger.info(f"Thai content length: {len(thai_content)}")
            
            return {
                'markdown_content': thai_content,
                'layout': result.get('layout', layout_data or {}),
                'source_usage_details': result.get('source_usage_details', source_usage_details or []),
                'translation_success': True,
                'translation_notes': result.get('translation_notes', [])
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in translation: {str(e)}")
            logger.error(f"Raw response content: {response_content[:500]}..." if response_content else "No content")
            return {
                'markdown_content': '',
                'layout': layout_data or {},
                'source_usage_details': source_usage_details or [],
                'translation_success': False,
                'error': f'Invalid JSON response: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error in Thai translation: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            return {
                'markdown_content': '',
                'layout': layout_data or {},
                'source_usage_details': source_usage_details or [],
                'translation_success': False,
                'error': f'Translation failed: {str(e)}'
            }
    
    def _get_translation_system_prompt(self) -> str:
        """Get system prompt for Thai translation"""
        return """You are an expert Thai translator specializing in business and technology content. Your task is to translate English business articles into natural, professional Thai while maintaining the exact formatting and structure.

TRANSLATION REQUIREMENTS:
- Translate to professional Thai suitable for business executives
- Maintain all Markdown formatting (headings, lists, tables, emphasis)
- Preserve image placeholders exactly as they are
- Keep technical terms appropriately (some may remain in English if commonly used)
- Use formal, professional Thai tone suitable for C-level executives
- Maintain business terminology accuracy

CONTENT HANDLING:
- Translate headings while keeping hierarchy (# ## ### ####)
- Translate all text content including quotes, lists, tables
- Keep URLs and links intact
- Preserve blockquotes and code blocks formatting
- Maintain proper spacing and line breaks
- Keep image placeholder syntax: ![{{image_id}}](placeholder)

BUSINESS TERMINOLOGY:
- Use appropriate Thai business terms
- Keep commonly used English terms when appropriate (e.g., "AI", "CEO", "ROI")
- Maintain professional consulting tone
- Ensure cultural appropriateness for Thai business context

LAYOUT PRESERVATION:
- Preserve all structural elements
- Maintain section organization
- Keep image slot information intact
- Preserve source usage details structure

OUTPUT FORMAT:
Return a JSON object with:
{
  "thai_content": "Complete article in Thai with preserved Markdown formatting",
  "layout": {
    "sections": ["translated", "section", "titles"],
    "image_slots": [
      {
        "id": "unchanged_id",
        "description": "translated description in Thai",
        "position": "unchanged_position",
        "suggested_type": "unchanged",
        "placement_rationale": "translated rationale in Thai", 
        "content_guidance": "translated guidance in Thai",
        "dimensions": "unchanged",
        "aspect_ratio": "unchanged",
        "alternatives": "translated alternatives in Thai"
      }
    ]
  },
  "source_usage_details": [
    {
      "source_title": "translated if needed",
      "source_url": "unchanged",
      "content_used": "translated content description",
      "usage_location": "translated location description",
      "usage_purpose": "translated purpose description", 
      "transformation": "translated transformation description",
      "instruction_compliance": "translated compliance description",
      "extraction_type_used": "unchanged or translated"
    }
  ],
  "translation_notes": ["any important translation decisions or notes"]
}

IMPORTANT:
- Maintain exact Markdown structure
- Translate content naturally while preserving business meaning
- Keep all technical formatting intact
- Ensure readability in Thai
- Preserve professional tone throughout
- Return only valid JSON format"""

    def _build_translation_user_prompt(self, content: str, layout_data: Dict = None, 
                                     source_usage_details: list = None) -> str:
        """Build user prompt for translation"""
        
        prompt_parts = [
            "Translate the following English business article to professional Thai:",
            "",
            "ENGLISH CONTENT TO TRANSLATE:",
            content
        ]
        
        if layout_data:
            prompt_parts.extend([
                "",
                "LAYOUT DATA TO PRESERVE AND TRANSLATE:",
                json.dumps(layout_data, indent=2, ensure_ascii=False)
            ])
        
        if source_usage_details:
            prompt_parts.extend([
                "",
                "SOURCE USAGE DETAILS TO TRANSLATE:",
                json.dumps(source_usage_details, indent=2, ensure_ascii=False)
            ])
        
        prompt_parts.extend([
            "",
            "INSTRUCTIONS:",
            "1. Translate all text content to professional Thai",
            "2. Preserve all Markdown formatting exactly",
            "3. Maintain business terminology appropriateness", 
            "4. Keep image placeholders unchanged",
            "5. Translate layout descriptions and metadata",
            "6. Ensure natural Thai readability",
            "",
            "Return the complete translation in the specified JSON format."
        ])
        
        return "\n".join(prompt_parts)