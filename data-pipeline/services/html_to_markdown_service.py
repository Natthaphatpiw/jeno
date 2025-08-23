"""
HTML to Markdown conversion service using LLM
Converts scraped HTML content to clean, structured Markdown for fine-tuning data preparation
"""

import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class HTMLToMarkdownService:
    """Service for converting HTML content to Markdown using LLM"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')  # Use cheaper model for conversion
        
    def convert_html_to_markdown(self, html_content: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        Convert HTML content to clean Markdown format using LLM
        
        Args:
            html_content: Raw HTML content from scraping
            metadata: Optional metadata about the article (title, url, etc.)
            
        Returns:
            Dict containing converted markdown and processing info
        """
        
        logger.info("Starting HTML to Markdown conversion with LLM")
        
        if not html_content or not html_content.strip():
            logger.warning("Empty HTML content provided")
            return {
                'markdown_content': '',
                'conversion_success': False,
                'error': 'Empty HTML content'
            }
        
        try:
            system_prompt = self._get_conversion_system_prompt()
            user_prompt = self._build_conversion_user_prompt(html_content, metadata)
            
            logger.info(f"Converting HTML content (length: {len(html_content)} chars)")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2500,  # Increased since we have cleaner input
                temperature=0.1,  # Low temperature for consistent formatting
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            
            if not content:
                logger.error("OpenAI returned empty content for HTML conversion")
                return {
                    'markdown_content': '',
                    'conversion_success': False,
                    'error': 'Empty response from LLM'
                }
            
            result = json.loads(content)
            logger.info("HTML to Markdown conversion completed successfully")
            
            return {
                'markdown_content': result.get('markdown_content', ''),
                'conversion_success': True,
                'extracted_metadata': result.get('extracted_metadata', {}),
                'content_structure': result.get('content_structure', {}),
                'processing_notes': result.get('processing_notes', [])
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in HTML conversion: {str(e)}")
            return {
                'markdown_content': '',
                'conversion_success': False,
                'error': f'Invalid JSON response: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error in HTML to Markdown conversion: {str(e)}")
            return {
                'markdown_content': '',
                'conversion_success': False,
                'error': f'Conversion failed: {str(e)}'
            }
    
    def _get_conversion_system_prompt(self) -> str:
        """Get the system prompt for HTML to Markdown conversion"""
        return """You are an expert content processor. Convert HTML to clean, concise Markdown format optimized for training data.

OBJECTIVES:
- Extract ONLY the main article content
- Create clean, readable Markdown
- Keep output concise and focused
- Remove all non-content elements

MARKDOWN RULES:
- Use proper heading hierarchy (# ## ###)
- Convert lists to Markdown format (- or 1.)
- Convert emphasis: <b>/<strong> to **bold**, <i>/<em> to *italic*
- Convert links: <a href="url">text</a> to [text](url)
- Use blockquotes (>) for important quotes
- Remove all HTML tags and inline styles

CONTENT FILTERING - REMOVE:
- Navigation, headers, footers, sidebars
- Ads, social widgets, comments
- "Share", "Related articles", promotional content
- Cookie notices, popups, UI elements
- Empty paragraphs and excessive whitespace

KEEP CONCISE:
- Focus on main points and key information
- Combine similar paragraphs when appropriate
- Remove redundant or filler content
- Keep only essential details

RESPONSE FORMAT (JSON):
{
  "markdown_content": "Clean, concise Markdown content",
  "extracted_metadata": {
    "title": "Article title",
    "word_count": estimated_count,
    "main_topics": ["topic1", "topic2"]
  },
  "content_structure": {
    "has_headings": true/false,
    "paragraph_count": number
  },
  "processing_notes": ["brief notes about processing"]
}

IMPORTANT: 
- Keep markdown_content under 2000 characters when possible
- Focus on quality over quantity
- Ensure content is suitable for training data"""

    def _build_conversion_user_prompt(self, html_content: str, metadata: Dict = None) -> str:
        """Build the user prompt for HTML conversion"""
        
        prompt_parts = [
            "Convert the following HTML content to clean Markdown format:",
        ]
        
        if metadata:
            prompt_parts.append(f"\nPage Metadata:")
            if metadata.get('title'):
                prompt_parts.append(f"Title: {metadata['title']}")
            if metadata.get('url'):
                prompt_parts.append(f"URL: {metadata['url']}")
            if metadata.get('description'):
                prompt_parts.append(f"Description: {metadata['description']}")
        
        # CRITICAL: Remove base64 images first (saves 99%+ tokens)
        import re
        logger.info(f"Original HTML: {len(html_content):,} chars")
        
        # Remove base64 image data completely
        base64_pattern = r'data:image/[^"\'>\s]*'
        html_without_images = re.sub(base64_pattern, '[IMAGE_REMOVED]', html_content)
        logger.info(f"After removing images: {len(html_without_images):,} chars")
        
        # Pre-process HTML to reduce size before sending to LLM
        cleaned_html = self._preprocess_html_for_conversion(html_without_images)
        
        # Increase limit since we removed images (more content can fit)
        truncated_html = cleaned_html[:8000]  # Increased from 4000
        if len(cleaned_html) > 8000:
            truncated_html += "\n... [Content truncated for processing]"
        
        prompt_parts.append(f"\nHTML Content to Convert:\n{truncated_html}")
        prompt_parts.append("\nReturn the conversion result in the specified JSON format.")
        
        return "\n".join(prompt_parts)
    
    def batch_convert_articles(self, articles: list) -> list:
        """Convert multiple articles in batch"""
        
        logger.info(f"Starting batch conversion of {len(articles)} articles")
        converted_articles = []
        
        for i, article in enumerate(articles):
            logger.info(f"Converting article {i+1}/{len(articles)}")
            
            html_content = article.get('html_content', '')
            metadata = article.get('metadata', {})
            
            conversion_result = self.convert_html_to_markdown(html_content, metadata)
            
            # Add conversion result to article data
            article_with_markdown = article.copy()
            article_with_markdown.update({
                'markdown_content': conversion_result['markdown_content'],
                'conversion_success': conversion_result['conversion_success'],
                'extracted_metadata': conversion_result.get('extracted_metadata', {}),
                'content_structure': conversion_result.get('content_structure', {}),
                'conversion_error': conversion_result.get('error', None)
            })
            
            converted_articles.append(article_with_markdown)
            
            # Small delay to avoid rate limiting
            if i < len(articles) - 1:
                import time
                time.sleep(0.5)
        
        logger.info(f"Batch conversion completed: {len(converted_articles)} articles processed")
        return converted_articles
    
    def _preprocess_html_for_conversion(self, html_content: str) -> str:
        """
        Pre-process HTML to reduce size and focus on main content before LLM conversion
        This reduces input tokens significantly
        """
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove elements that don't contribute to main content
            unwanted_tags = [
                'script', 'style', 'nav', 'header', 'footer', 'aside',
                'iframe', 'noscript', 'form', 'input', 'button',
                'meta', 'link', 'title', 'head'
            ]
            
            for tag in unwanted_tags:
                for element in soup.find_all(tag):
                    element.decompose()
            
            # Remove elements with common non-content classes/ids
            unwanted_selectors = [
                '[class*="nav"]', '[class*="menu"]', '[class*="sidebar"]',
                '[class*="footer"]', '[class*="header"]', '[class*="banner"]',
                '[class*="ad"]', '[class*="advertisement"]', '[class*="social"]',
                '[class*="share"]', '[class*="comment"]', '[class*="related"]',
                '[id*="nav"]', '[id*="menu"]', '[id*="sidebar"]',
                '[id*="footer"]', '[id*="header"]'
            ]
            
            for selector in unwanted_selectors:
                try:
                    for element in soup.select(selector):
                        element.decompose()
                except:
                    continue  # Skip if selector fails
            
            # Focus on main content areas
            main_content_selectors = [
                'main', 'article', '[role="main"]', '.content', '.post',
                '.entry', '.article-content', '.post-content'
            ]
            
            main_content = None
            for selector in main_content_selectors:
                try:
                    main_content = soup.select_one(selector)
                    if main_content and len(main_content.get_text().strip()) > 200:
                        break
                except:
                    continue
            
            # If we found main content, use only that
            if main_content:
                soup = main_content
            
            # Remove empty elements and whitespace-only elements
            for element in soup.find_all():
                if not element.get_text().strip():
                    element.decompose()
            
            # Convert back to string and clean up whitespace
            cleaned_html = str(soup)
            
            # Remove excessive whitespace
            import re
            cleaned_html = re.sub(r'\s+', ' ', cleaned_html)
            cleaned_html = re.sub(r'>\s+<', '><', cleaned_html)
            
            logger.info(f"HTML preprocessing: {len(html_content)} → {len(cleaned_html)} chars ({len(cleaned_html)/len(html_content)*100:.1f}%)")
            
            return cleaned_html
            
        except Exception as e:
            logger.warning(f"HTML preprocessing failed: {e}, using original content")
            return html_content[:4000]  # Fallback with truncation