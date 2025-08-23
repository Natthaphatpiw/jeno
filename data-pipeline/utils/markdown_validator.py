"""
Markdown content validation utilities
Validates quality and structure of LLM-generated Markdown content
"""

import re
from typing import Dict, List, Tuple, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class MarkdownValidator:
    """Validator for Markdown content quality and structure"""
    
    def __init__(self):
        self.min_word_count = 100
        self.min_paragraph_count = 3
        self.max_heading_level = 6
    
    def validate_markdown_content(self, markdown_content: str) -> Dict[str, any]:
        """
        Comprehensive validation of Markdown content
        
        Returns:
            Dict with validation results and quality metrics
        """
        
        if not markdown_content or not markdown_content.strip():
            return {
                'is_valid': False,
                'score': 0.0,
                'issues': ['Empty content'],
                'metrics': {},
                'recommendations': ['Content is empty or whitespace only']
            }
        
        # Run all validation checks
        structure_check = self._validate_structure(markdown_content)
        content_check = self._validate_content_quality(markdown_content)
        format_check = self._validate_formatting(markdown_content)
        
        # Combine results
        all_issues = structure_check['issues'] + content_check['issues'] + format_check['issues']
        all_recommendations = structure_check['recommendations'] + content_check['recommendations'] + format_check['recommendations']
        
        # Calculate overall score (0.0 to 1.0)
        structure_score = structure_check['score']
        content_score = content_check['score']
        format_score = format_check['score']
        
        # Weighted average: structure 40%, content 50%, format 10%
        overall_score = (structure_score * 0.4) + (content_score * 0.5) + (format_score * 0.1)
        
        # Determine if valid (score >= 0.7)
        is_valid = overall_score >= 0.7 and len(all_issues) <= 2
        
        return {
            'is_valid': is_valid,
            'score': round(overall_score, 2),
            'issues': all_issues,
            'metrics': {
                'structure_score': round(structure_score, 2),
                'content_score': round(content_score, 2),
                'format_score': round(format_score, 2),
                **structure_check['metrics'],
                **content_check['metrics'],
                **format_check['metrics']
            },
            'recommendations': all_recommendations
        }
    
    def _validate_structure(self, content: str) -> Dict:
        """Validate Markdown structure and organization"""
        
        issues = []
        recommendations = []
        metrics = {}
        
        # Extract headings
        headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        metrics['heading_count'] = len(headings)
        
        # Check heading hierarchy
        if not headings:
            issues.append('No headings found')
            recommendations.append('Add section headings to improve structure')
        else:
            # Check for proper hierarchy
            heading_levels = [len(h[0]) for h in headings]
            metrics['heading_levels'] = list(set(heading_levels))
            
            # Check if headings skip levels (e.g., # then ###)
            for i in range(1, len(heading_levels)):
                if heading_levels[i] - heading_levels[i-1] > 1:
                    issues.append('Heading hierarchy skips levels')
                    recommendations.append('Use consecutive heading levels (# ## ### instead of # ###)')
                    break
        
        # Check for paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
        metrics['paragraph_count'] = len(paragraphs)
        
        if len(paragraphs) < self.min_paragraph_count:
            issues.append(f'Too few paragraphs ({len(paragraphs)} < {self.min_paragraph_count})')
            recommendations.append('Add more content paragraphs')
        
        # Check for lists
        list_items = re.findall(r'^[\s]*[-*+]\s+.+$', content, re.MULTILINE)
        numbered_items = re.findall(r'^[\s]*\d+\.\s+.+$', content, re.MULTILINE)
        metrics['list_items'] = len(list_items) + len(numbered_items)
        
        # Calculate structure score
        score = 1.0
        if not headings:
            score -= 0.4
        if len(paragraphs) < self.min_paragraph_count:
            score -= 0.3
        if len(issues) > 0:
            score -= 0.1 * len(issues)
        
        score = max(0.0, score)
        
        return {
            'score': score,
            'issues': issues,
            'recommendations': recommendations,
            'metrics': metrics
        }
    
    def _validate_content_quality(self, content: str) -> Dict:
        """Validate content quality and readability"""
        
        issues = []
        recommendations = []
        metrics = {}
        
        # Word count
        words = re.findall(r'\b\w+\b', content.lower())
        metrics['word_count'] = len(words)
        
        if len(words) < self.min_word_count:
            issues.append(f'Content too short ({len(words)} words < {self.min_word_count})')
            recommendations.append('Expand content with more detailed information')
        
        # Character count
        metrics['char_count'] = len(content)
        
        # Check for repetitive content
        if len(words) > 50:
            word_freq = {}
            for word in words:
                if len(word) > 4:  # Only check meaningful words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            if word_freq:
                max_freq = max(word_freq.values())
                repetition_ratio = max_freq / len(words)
                metrics['repetition_ratio'] = round(repetition_ratio, 3)
                
                if repetition_ratio > 0.05:
                    issues.append('Content appears repetitive')
                    recommendations.append('Reduce repetitive words and phrases')
        
        # Check for meaningful sentences
        sentences = re.split(r'[.!?]+', content)
        meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        metrics['sentence_count'] = len(meaningful_sentences)
        
        if len(meaningful_sentences) < 5:
            issues.append('Too few meaningful sentences')
            recommendations.append('Add more detailed explanations and examples')
        
        # Calculate content score
        score = 1.0
        if len(words) < self.min_word_count:
            score -= 0.4
        if len(meaningful_sentences) < 5:
            score -= 0.3
        if metrics.get('repetition_ratio', 0) > 0.05:
            score -= 0.2
        
        score = max(0.0, score)
        
        return {
            'score': score,
            'issues': issues,
            'recommendations': recommendations,
            'metrics': metrics
        }
    
    def _validate_formatting(self, content: str) -> Dict:
        """Validate Markdown formatting and syntax"""
        
        issues = []
        recommendations = []
        metrics = {}
        
        # Check for HTML remnants
        html_tags = re.findall(r'<[^>]+>', content)
        metrics['html_tags_found'] = len(html_tags)
        
        if html_tags:
            issues.append(f'HTML tags found in Markdown ({len(html_tags)} instances)')
            recommendations.append('Remove or convert HTML tags to Markdown syntax')
        
        # Check for proper link formatting
        markdown_links = re.findall(r'\[([^\]]+)\]\([^)]+\)', content)
        broken_links = re.findall(r'\[([^\]]*)\]\(\s*\)', content)  # Empty href
        metrics['markdown_links'] = len(markdown_links)
        metrics['broken_links'] = len(broken_links)
        
        if broken_links:
            issues.append(f'Broken links found ({len(broken_links)} instances)')
            recommendations.append('Fix or remove broken links')
        
        # Check for excessive whitespace
        excessive_newlines = re.findall(r'\n{4,}', content)
        if excessive_newlines:
            issues.append('Excessive whitespace/newlines found')
            recommendations.append('Clean up excessive whitespace')
        
        # Check for proper emphasis formatting
        bold_text = re.findall(r'\*\*[^*]+\*\*', content)
        italic_text = re.findall(r'\*[^*]+\*', content)
        metrics['bold_text'] = len(bold_text)
        metrics['italic_text'] = len(italic_text)
        
        # Calculate format score
        score = 1.0
        if html_tags:
            score -= 0.5
        if broken_links:
            score -= 0.3
        if excessive_newlines:
            score -= 0.2
        
        score = max(0.0, score)
        
        return {
            'score': score,
            'issues': issues,
            'recommendations': recommendations,
            'metrics': metrics
        }
    
    def get_quality_summary(self, validation_result: Dict) -> str:
        """Generate a human-readable quality summary"""
        
        score = validation_result['score']
        is_valid = validation_result['is_valid']
        issues_count = len(validation_result['issues'])
        
        if score >= 0.9:
            quality = "Excellent"
        elif score >= 0.8:
            quality = "Good"
        elif score >= 0.7:
            quality = "Fair"
        elif score >= 0.5:
            quality = "Poor"
        else:
            quality = "Very Poor"
        
        summary = f"Quality: {quality} (Score: {score}/1.0)"
        
        if is_valid:
            summary += " ✅ Valid for training"
        else:
            summary += " ❌ Needs improvement"
        
        if issues_count > 0:
            summary += f" | {issues_count} issues found"
        
        return summary