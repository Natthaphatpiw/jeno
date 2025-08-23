import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from utils.logger import get_logger
from utils.helpers import clean_text, calculate_content_stats
from services.html_to_markdown_service import HTMLToMarkdownService
from utils.markdown_validator import MarkdownValidator

logger = get_logger(__name__)

class ContentExtractor:
    """Extract and process article content for training data generation"""
    
    def __init__(self):
        self.min_paragraph_length = 50
        self.max_content_length = 10000
        self.html_to_markdown_service = HTMLToMarkdownService()
        self.markdown_validator = MarkdownValidator()
    
    def extract_training_content(self, article_content: Dict) -> Optional[Dict]:
        """Extract content suitable for training data"""
        try:
            # Get basic content
            html_content = article_content.get('html_content', '')
            text_content = article_content.get('text_content', '')
            structured_content = article_content.get('structured_content', {})
            metadata = article_content.get('metadata', {})
            
            # NEW: Convert HTML to Markdown using LLM
            logger.info("Converting HTML to Markdown using LLM...")
            markdown_result = self.html_to_markdown_service.convert_html_to_markdown(
                html_content, metadata
            )
            
            if not markdown_result['conversion_success']:
                logger.warning(f"HTML to Markdown conversion failed: {markdown_result.get('error', 'Unknown error')}")
                # Fallback to original text content
                markdown_content = text_content
            else:
                markdown_content = markdown_result['markdown_content']
                logger.info(f"Successfully converted HTML to Markdown ({len(markdown_content)} chars)")
                
                # Validate markdown quality
                validation_result = self.markdown_validator.validate_markdown_content(markdown_content)
                logger.info(f"Markdown validation: {self.markdown_validator.get_quality_summary(validation_result)}")
                
                if not validation_result['is_valid']:
                    logger.warning(f"Markdown validation failed. Issues: {validation_result['issues']}")
                    # Could fallback to original text or skip article
                    if validation_result['score'] < 0.5:
                        logger.warning("Markdown quality too poor, using fallback text content")
                        markdown_content = text_content
                
                # Update metadata with extracted information
                extracted_meta = markdown_result.get('extracted_metadata', {})
                if extracted_meta:
                    metadata.update(extracted_meta)
            
            # Validate content quality using markdown content
            if not self._is_content_suitable_for_training(markdown_content, metadata):
                return None
            
            # Clean and process markdown content
            cleaned_content = self._clean_content_for_training(markdown_content)
            processed_structure = self._process_structured_content(structured_content)
            enhanced_metadata = self._enhance_metadata(metadata, cleaned_content)
            
            # Extract key sections for training from markdown
            article_sections = self._extract_markdown_sections(markdown_content)
            
            return {
                'metadata': enhanced_metadata,
                'content': cleaned_content,
                'markdown_content': markdown_content,  # NEW: Include original markdown
                'structured_content': processed_structure,
                'sections': article_sections,
                'content_structure': markdown_result.get('content_structure', {}),
                'conversion_notes': markdown_result.get('processing_notes', []),
                'markdown_validation': validation_result if 'validation_result' in locals() else None,
                'training_ready': True
            }
            
        except Exception as e:
            logger.error(f"Error extracting training content: {e}")
            return None
    
    def _is_content_suitable_for_training(self, content: str, metadata: Dict) -> bool:
        """Check if content is suitable for training data"""
        if not content or not content.strip():
            return False
        
        stats = calculate_content_stats(content)
        
        # Content quality checks - adjusted for Next.js content
        checks = {
            'min_length': stats['chars'] >= 400,  # Lowered threshold
            'max_length': stats['chars'] <= 30000,  # Increased max
            'min_words': stats['words'] >= 80,  # Lowered threshold
            'has_title': bool(metadata.get('title', '').strip()),
            'reasonable_structure': stats['lines'] >= 3,  # Lowered threshold
            'not_too_repetitive': self._check_content_diversity(content)
        }
        
        passed_checks = sum(checks.values())
        logger.debug(f"Content quality checks: {passed_checks}/{len(checks)} passed")
        
        return passed_checks >= len(checks) - 1  # Allow 1 check to fail
    
    def _check_content_diversity(self, content: str) -> bool:
        """Check if content has good diversity (not too repetitive)"""
        words = content.lower().split()
        if len(words) < 50:
            return False
        
        # Check for excessive repetition
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Only check meaningful words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        if not word_freq:
            return False
        
        # If any word appears more than 5% of total words, it's too repetitive
        max_freq = max(word_freq.values())
        return max_freq / len(words) < 0.05
    
    def _clean_content_for_training(self, content: str) -> str:
        """Clean content specifically for training purposes"""
        if not content:
            return ""
        
        try:
            # Remove excessive whitespace
            content = re.sub(r'\s+', ' ', content)
            
            # Remove URLs (they're not useful for training)
            content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
            
            # Remove email addresses
            content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', content)
            
            # Remove excessive punctuation
            content = re.sub(r'[.]{3,}', '...', content)
            content = re.sub(r'[!]{2,}', '!', content)
            content = re.sub(r'[?]{2,}', '?', content)
            
            # Clean up quotes - use simpler approach
            content = content.replace('"', '"').replace('"', '"')
            content = content.replace(''', "'").replace(''', "'")
            
            # Remove standalone numbers that might be page numbers or artifacts
            content = re.sub(r'\b\d+\s*$', '', content, flags=re.MULTILINE)
            
        except re.error as e:
            logger.warning(f"Regex error in content cleaning: {e}, returning original content")
            # Return original content if regex fails
            return content.strip() if content else ""
        
        # Clean up sentence structure
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        # Remove very short sentences (likely artifacts)
        sentences = [s for s in sentences if len(s) >= 20]
        
        cleaned = '. '.join(sentences)
        if cleaned and not cleaned.endswith('.'):
            cleaned += '.'
        
        return cleaned.strip()
    
    def _process_structured_content(self, structured: Dict) -> Dict:
        """Process structured content for training"""
        processed = {
            'headings': [],
            'key_points': [],
            'sections': [],
            'content_type': 'article'
        }
        
        try:
            # Process headings
            if 'headings' in structured:
                headings = []
                for heading in structured['headings']:
                    if isinstance(heading, dict):
                        text = clean_text(heading.get('text', ''))
                        if text and len(text) > 3:
                            headings.append({
                                'level': heading.get('level', 1),
                                'text': text
                            })
                processed['headings'] = headings[:10]  # Limit to 10 headings
            
            # Process key points from lists
            if 'lists' in structured:
                key_points = []
                for list_item in structured['lists']:
                    if isinstance(list_item, dict) and 'items' in list_item:
                        for item in list_item['items']:
                            clean_item = clean_text(item)
                            if clean_item and len(clean_item) > 10:
                                key_points.append(clean_item)
                processed['key_points'] = key_points[:20]  # Limit key points
            
            # Create sections based on headings and paragraphs
            sections = []
            if processed['headings']:
                for heading in processed['headings']:
                    if heading['level'] <= 3:  # Only main sections
                        sections.append(heading['text'])
            
            if not sections:
                # Default sections if no clear structure
                sections = ['Introduction', 'Main Content', 'Conclusion']
            
            processed['sections'] = sections
            
        except Exception as e:
            logger.warning(f"Error processing structured content: {e}")
        
        return processed
    
    def _enhance_metadata(self, metadata: Dict, content: str) -> Dict:
        """Enhance metadata with additional information"""
        enhanced = metadata.copy()
        
        try:
            # Update content stats
            enhanced['content_stats'] = calculate_content_stats(content)
            
            # Extract keywords from content
            enhanced['extracted_keywords'] = self._extract_keywords(content)
            
            # Determine content complexity
            enhanced['complexity_level'] = self._assess_content_complexity(content)
            
            # Extract theme/topic
            enhanced['primary_theme'] = self._extract_primary_theme(content, metadata)
            
        except Exception as e:
            logger.warning(f"Error enhancing metadata: {e}")
        
        return enhanced
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract potential keywords from content"""
        if not content:
            return []
        
        try:
            # Simple keyword extraction (could be improved with NLP)
            words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        except re.error as e:
            logger.warning(f"Regex error in keyword extraction: {e}")
            return []
        
        # Common business/tech terms that are likely keywords
        business_terms = [
            'digital', 'transformation', 'innovation', 'strategy', 'technology',
            'business', 'customer', 'market', 'growth', 'future', 'trends',
            'analytics', 'automation', 'artificial', 'intelligence', 'data',
            'experience', 'optimization', 'efficiency', 'competitive', 'advantage'
        ]
        
        # Find business-relevant keywords
        keywords = []
        for term in business_terms:
            if term in words:
                keywords.append(term)
        
        return list(set(keywords))[:10]  # Unique keywords, max 10
    
    def _assess_content_complexity(self, content: str) -> str:
        """Assess the complexity level of the content"""
        if not content:
            return 'basic'
        
        words = content.split()
        sentences = content.split('.')
        
        # Calculate average word length and sentence length
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences) if sentences else 0
        
        # Count complex words (7+ characters)
        complex_words = sum(1 for word in words if len(word) >= 7)
        complex_word_ratio = complex_words / len(words) if words else 0
        
        # Determine complexity
        if avg_word_length >= 6 and avg_sentence_length >= 20 and complex_word_ratio >= 0.3:
            return 'advanced'
        elif avg_word_length >= 5 and avg_sentence_length >= 15 and complex_word_ratio >= 0.2:
            return 'intermediate'
        else:
            return 'basic'
    
    def _extract_primary_theme(self, content: str, metadata: Dict) -> str:
        """Extract the primary theme/topic of the article"""
        # Use category as base theme
        category = metadata.get('category', 'business')
        title = metadata.get('title', '').lower()
        content_lower = content.lower()
        
        # Theme keywords
        themes = {
            'digital_transformation': ['digital', 'transformation', 'digitization', 'technology adoption'],
            'artificial_intelligence': ['ai', 'artificial intelligence', 'machine learning', 'automation'],
            'customer_experience': ['customer', 'experience', 'user', 'service', 'satisfaction'],
            'innovation': ['innovation', 'innovative', 'breakthrough', 'creative', 'novel'],
            'strategy': ['strategy', 'strategic', 'planning', 'growth', 'competitive'],
            'future_trends': ['future', 'trends', 'emerging', 'tomorrow', 'next'],
            'sustainability': ['sustainable', 'sustainability', 'green', 'environment', 'eco'],
            'data_analytics': ['data', 'analytics', 'insights', 'analysis', 'metrics']
        }
        
        # Score each theme based on keyword presence
        theme_scores = {}
        for theme, keywords in themes.items():
            score = 0
            for keyword in keywords:
                score += content_lower.count(keyword)
                score += title.count(keyword) * 2  # Title keywords are more important
            theme_scores[theme] = score
        
        # Return highest scoring theme or default to category
        if theme_scores:
            best_theme = max(theme_scores, key=theme_scores.get)
            if theme_scores[best_theme] > 0:
                return best_theme
        
        return category
    
    def _extract_article_sections(self, html_content: str) -> Dict[str, str]:
        """Extract distinct sections from HTML content"""
        sections = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            # Extract introduction (first few paragraphs)
            paragraphs = soup.find_all('p')
            if paragraphs:
                intro_paras = []
                for p in paragraphs[:3]:  # First 3 paragraphs as intro
                    text = clean_text(p.get_text())
                    if text and len(text) > 50:
                        intro_paras.append(text)
                if intro_paras:
                    sections['introduction'] = ' '.join(intro_paras)
            
            # Extract sections based on headings
            headings = soup.find_all(['h1', 'h2', 'h3'])
            for heading in headings:
                heading_text = clean_text(heading.get_text())
                if not heading_text:
                    continue
                
                # Get content after heading until next heading
                content = []
                current = heading.next_sibling
                while current:
                    if current.name in ['h1', 'h2', 'h3']:
                        break
                    if current.name == 'p':
                        text = clean_text(current.get_text())
                        if text and len(text) > 30:
                            content.append(text)
                    current = current.next_sibling
                
                if content:
                    section_key = heading_text.lower().replace(' ', '_')[:50]
                    sections[section_key] = ' '.join(content)
            
        except Exception as e:
            logger.warning(f"Error extracting article sections: {e}")
        
        return sections
    
    def _extract_markdown_sections(self, markdown_content: str) -> Dict[str, str]:
        """Extract sections from markdown content"""
        sections = {}
        
        if not markdown_content:
            return sections
        
        try:
            lines = markdown_content.split('\n')
            current_section = ""
            current_content = []
            
            for line in lines:
                # Check if line is a heading
                if line.startswith('#'):
                    # Save previous section if exists
                    if current_section and current_content:
                        section_key = current_section.lower().replace(' ', '_')[:50]
                        sections[section_key] = '\n'.join(current_content).strip()
                    
                    # Start new section
                    current_section = line.lstrip('#').strip()
                    current_content = []
                else:
                    # Add line to current section content
                    if line.strip():  # Only add non-empty lines
                        current_content.append(line)
            
            # Don't forget the last section
            if current_section and current_content:
                section_key = current_section.lower().replace(' ', '_')[:50]
                sections[section_key] = '\n'.join(current_content).strip()
            
            logger.info(f"Extracted {len(sections)} sections from markdown content")
            
        except Exception as e:
            logger.warning(f"Error extracting markdown sections: {e}")
        
        return sections
    
    def convert_to_markdown(self, html_content: str) -> str:
        """Convert HTML content to clean Markdown"""
        try:
            # Clean HTML first
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            # Convert to markdown
            markdown = md(str(soup), heading_style="ATX")
            
            # Clean up markdown
            markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown)  # Remove excessive line breaks
            markdown = re.sub(r'^\s*\n', '', markdown, flags=re.MULTILINE)  # Remove empty lines at start
            
            return markdown.strip()
            
        except Exception as e:
            logger.warning(f"Error converting to markdown: {e}")
            return html_content