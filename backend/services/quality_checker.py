import json
from typing import Dict, Any
from openai import OpenAI
from config.settings import settings
from models.schemas import QualityFeedback

class QualityCheckerService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def evaluate_article_quality(self, article_content: str, context: Dict[str, Any]) -> QualityFeedback:
        """Evaluate article quality and provide feedback"""
        
        system_prompt = self._get_quality_system_prompt()
        user_prompt = self._build_quality_user_prompt(article_content, context)
        
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            return QualityFeedback(
                score=result.get("score", 0.0),
                feedback=result.get("feedback", ""),
                suggestions=result.get("suggestions", [])
            )
            
        except Exception as e:
            raise Exception(f"Error evaluating article quality: {str(e)}")
    
    def _get_quality_system_prompt(self) -> str:
        """Get system prompt for quality evaluation"""
        return """You are a quality evaluator for Jenosize business articles. Your role is to assess article quality based on specific criteria and provide actionable feedback.

EVALUATION CRITERIA (each worth equal weight):

1. JENOSIZE BRAND ALIGNMENT (0-1 scale)
   - Professional yet approachable tone
   - Forward-thinking perspective
   - Business-focused insights
   - Authoritative but not academic

2. CONTENT QUALITY (0-1 scale)
   - Depth of insights
   - Practical actionability
   - Relevance to business audience
   - Logical structure and flow

3. ENGAGEMENT FACTOR (0-1 scale)
   - Compelling introduction
   - Clear value proposition
   - Engaging examples and stories
   - Strong conclusion with call-to-action

4. TECHNICAL EXCELLENCE (0-1 scale)
   - Proper formatting and structure
   - SEO optimization (if keywords provided)
   - Appropriate length (1500-2500 words)
   - Error-free grammar and clarity

SCORING:
- 0.9-1.0: Exceptional, publish-ready
- 0.85-0.89: High quality, minor improvements
- 0.75-0.84: Good, needs moderate improvements
- Below 0.75: Requires significant revision

IMPORTANT: You must respond in JSON format only. Provide a JSON object with the following structure:
{
  "score": 0.0-1.0,
  "feedback": "Detailed explanation of strengths and weaknesses",
  "suggestions": ["specific", "actionable", "improvement", "recommendations"]
}"""
    
    def _build_quality_user_prompt(self, article_content: str, context: Dict[str, Any]) -> str:
        """Build user prompt for quality evaluation"""
        
        prompt_parts = [
            "Evaluate the following article for Jenosize:\n",
            f"ARTICLE CONTENT:\n{article_content}\n",
            "CONTEXT:",
        ]
        
        if context.get("topic_category"):
            prompt_parts.append(f"- Topic: {context['topic_category']}")
        
        if context.get("industry"):
            prompt_parts.append(f"- Industry: {context['industry']}")
        
        if context.get("target_audience"):
            prompt_parts.append(f"- Audience: {context['target_audience']}")
        
        if context.get("seo_keywords"):
            prompt_parts.append(f"- SEO Keywords: {context['seo_keywords']}")
        
        prompt_parts.extend([
            "\nProvide a comprehensive quality assessment with:",
            "1. Overall score (0-1 scale)",
            "2. Detailed feedback on strengths and weaknesses",
            "3. Specific suggestions for improvement",
            "\nFocus on Jenosize brand alignment, content quality, engagement, and technical excellence.",
            "\nReturn your evaluation as a JSON object with the specified format."
        ])
        
        return "\n".join(prompt_parts)