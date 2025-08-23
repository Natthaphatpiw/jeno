"""
Prompt templates for fine-tuning based on analysis of llm_service.py
These prompts are designed to match the current production system's behavior.
"""

from typing import List, Dict, Optional
import random
from config.settings import CATEGORY_MAPPING

class JenosizePromptGenerator:
    """Generate training prompts that match the production LLM service"""
    
    def __init__(self):
        self.system_prompt_base = self._get_base_system_prompt()
        self.user_prompt_templates = self._get_user_prompt_templates()
        self.categories = list(CATEGORY_MAPPING.keys())
        self.industries = [
            "Technology", "Healthcare", "Finance", "Retail", "Manufacturing",
            "Education", "Transportation", "Real Estate", "Media", "Consulting"
        ]
        self.audiences = [
            "C-suite executives", "Business leaders", "Entrepreneurs",
            "Marketing professionals", "Operations managers", "Strategy consultants",
            "Digital transformation leaders", "Innovation directors"
        ]
    
    def _get_base_system_prompt(self) -> str:
        """Base system prompt matching production llm_service.py"""
        return """You are an expert content creator for Jenosize, a premier digital transformation consultancy. You are writing for C-level executives, business leaders, and decision-makers who need strategic insights to drive business transformation.

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
- Every claim must be supported by data, research, or expert analysis
- Include specific statistics, percentages, and quantifiable metrics
- Reference industry leaders, case studies, and best practices
- Provide actionable frameworks and implementation guidance
- Address both opportunities and potential pitfalls
- Include cost-benefit considerations where relevant

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
- Jenosize's consultative value is clearly positioned throughout

IMPORTANT: You must respond in JSON format only. Return your response as a valid JSON object with the structure specified above."""

    def _get_user_prompt_templates(self) -> List[str]:
        """User prompt templates matching different input scenarios"""
        return [
            # Basic article generation
            "Generate a comprehensive article with the following specifications:\n\nTopic Category: {topic_category}\nIndustry Focus: {industry}\nTarget Audience: {target_audience}\nSEO Keywords to incorporate: {seo_keywords}\n\nReturn your response as a JSON object with the specified format.",
            
            # With custom instructions
            "Generate a comprehensive article with the following specifications:\n\nTopic Category: {topic_category}\nIndustry Focus: {industry}\nTarget Audience: {target_audience}\nSEO Keywords to incorporate: {seo_keywords}\n\nCUSTOM USER INSTRUCTIONS: {custom_prompt}\n\nReturn your response as a JSON object with the specified format.",
            
            # With single source
            "Generate a comprehensive article with the following specifications:\n\nTopic Category: {topic_category}\nIndustry Focus: {industry}\nTarget Audience: {target_audience}\nSEO Keywords to incorporate: {seo_keywords}\n\nReference Content from provided source:\n{source_content}\n\nReturn your response as a JSON object with the specified format.",
            
            # With multiple sources
            "Generate a comprehensive article with the following specifications:\n\nTopic Category: {topic_category}\nIndustry Focus: {industry}\nTarget Audience: {target_audience}\nSEO Keywords to incorporate: {seo_keywords}\n\nMultiple Reference Sources:\n{multiple_sources}\n\nIMPORTANT: Use the source titles exactly as provided above in your source_mapping response. Distribute content usage across different article sections and clearly map which sections reference which sources.\n\nReturn your response as a JSON object with the specified format.",
            
            # Minimal input
            "Generate an article about {topic_category} for {target_audience}.\n\nReturn your response as a JSON object with the specified format.",
            
            # With feedback (quality improvement)
            "PREVIOUS FEEDBACK TO IMPROVE: {feedback}\n\nGenerate a comprehensive article with the following specifications:\n\nTopic Category: {topic_category}\nIndustry Focus: {industry}\nTarget Audience: {target_audience}\nSEO Keywords to incorporate: {seo_keywords}\n\nReturn your response as a JSON object with the specified format."
        ]
    
    def generate_system_prompt_variation(self) -> str:
        """Generate a variation of the system prompt"""
        # For fine-tuning, we mostly use the base prompt
        # but can add slight variations for robustness
        base = self.system_prompt_base
        
        # Occasionally add emphasis on certain aspects
        variations = [
            base,  # Use base most of the time
            base + "\n\nEMPHASIS: Pay special attention to creating actionable, practical advice that business leaders can immediately implement.",
            base + "\n\nEMPHASIS: Focus on forward-thinking insights that help businesses prepare for future challenges and opportunities.",
            base + "\n\nEMPHASIS: Ensure all recommendations are backed by concrete examples and real-world applications.",
        ]
        
        return random.choice(variations)
    
    def generate_user_prompt(self, 
                           article_content: str,
                           article_metadata: Dict,
                           source_content: Optional[str] = None,
                           custom_instructions: Optional[str] = None) -> str:
        """Generate user prompt based on article content and metadata"""
        
        # Extract parameters from metadata
        category = article_metadata.get('category', 'business-trends')
        title = article_metadata.get('title', '')
        
        # Map category to topic
        topic_category = CATEGORY_MAPPING.get(category, "Business Innovation")
        
        # Generate realistic parameters
        industry = random.choice(self.industries)
        target_audience = random.choice(self.audiences)
        seo_keywords = self._generate_seo_keywords(title, category)
        
        # Choose template based on available content
        if source_content and custom_instructions:
            template = random.choice(self.user_prompt_templates[1:3])  # With custom or source
        elif source_content:
            template = self.user_prompt_templates[2]  # With source
        elif len(title) < 50:
            template = self.user_prompt_templates[4]  # Minimal
        else:
            template = self.user_prompt_templates[0]  # Basic
        
        # Format template
        prompt = template.format(
            topic_category=topic_category,
            industry=industry,
            target_audience=target_audience,
            seo_keywords=seo_keywords,
            source_content=source_content[:2000] if source_content else "",
            custom_prompt=custom_instructions or "",
            multiple_sources="",
            feedback=""
        )
        
        return prompt
    
    def _generate_seo_keywords(self, title: str, category: str) -> str:
        """Generate realistic SEO keywords based on title and category"""
        
        # Extract key terms from title
        title_words = [word.lower().strip('.,!?()[]{}') for word in title.split() 
                      if len(word) > 3 and word.lower() not in ['the', 'and', 'for', 'with', 'that', 'this']]
        
        # Category-specific keywords
        category_keywords = {
            'futurist': ['future trends', 'innovation', 'digital transformation', 'emerging technology'],
            'understand-people-and-consumer': ['consumer behavior', 'customer insights', 'user experience', 'market research'],
            'transformation-and-technology': ['digital transformation', 'technology adoption', 'automation', 'AI integration'],
            'utility-for-our-world': ['sustainability', 'social impact', 'ESG', 'corporate responsibility'],
            'real-time-marketing': ['marketing strategy', 'real-time engagement', 'customer experience', 'brand strategy'],
            'experience-the-new-world': ['customer experience', 'user journey', 'experience design', 'digital experience']
        }
        
        # Combine title words with category keywords
        base_keywords = title_words[:3]  # Top 3 words from title
        category_keys = category_keywords.get(category, ['business strategy'])
        
        all_keywords = base_keywords + category_keys[:2]
        return ', '.join(all_keywords[:5])  # Limit to 5 keywords
    
    def create_training_example(self,
                               article_content: str,
                               article_metadata: Dict,
                               structured_content: Dict,
                               source_content: Optional[str] = None) -> Dict:
        """Create a complete training example in OpenAI format"""
        
        # Generate prompts
        system_prompt = self.generate_system_prompt_variation()
        user_prompt = self.generate_user_prompt(
            article_content, 
            article_metadata, 
            source_content
        )
        
        # Create realistic assistant response
        assistant_response = self._create_assistant_response(
            article_content,
            article_metadata,
            structured_content,
            source_content
        )
        
        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": assistant_response}
            ]
        }
    
    def _create_assistant_response(self,
                                  article_content: str,
                                  article_metadata: Dict,
                                  structured_content: Dict,
                                  source_content: Optional[str] = None) -> str:
        """Create realistic assistant response matching expected JSON format"""
        
        # Extract sections from structured content
        sections = []
        if 'headings' in structured_content:
            sections = [h['text'] for h in structured_content['headings'] 
                       if h['level'] <= 3][:5]  # Top level headings only
        
        if not sections:
            sections = ["Introduction", "Key Insights", "Practical Applications", "Future Implications", "Conclusion"]
        
        # Create image slots (3-5 strategic placements)
        image_slots = self._generate_image_slots(sections, article_metadata['category'])
        
        # Create source usage details if source provided
        source_usage = []
        if source_content:
            source_usage = [{
                "source_title": f"Source Article - {article_metadata['title']}",
                "source_url": article_metadata['url'],
                "content_used": source_content[:200] + "..." if len(source_content) > 200 else source_content,
                "usage_location": f"Referenced in {sections[1] if len(sections) > 1 else 'main content'} section",
                "usage_purpose": "To provide concrete examples and support key arguments with real-world data",
                "transformation": "Adapted the original insights to focus on actionable business strategies and aligned with Jenosize's consulting perspective"
            }]
        
        # Create response JSON
        response = {
            "content": self._format_content_as_markdown(article_content, sections, image_slots),
            "layout": {
                "sections": sections,
                "image_slots": [slot for slot in image_slots]
            },
            "source_usage_details": source_usage
        }
        
        import json
        return json.dumps(response, ensure_ascii=False)
    
    def _generate_image_slots(self, sections: List[str], category: str) -> List[Dict]:
        """Generate realistic image slot recommendations"""
        
        num_slots = min(random.randint(3, 5), len(sections))
        slots = []
        
        image_types = ['infographic', 'chart', 'illustration', 'photo']
        dimensions = ['1200x800px', '800x600px', '1000x600px', '1200x900px']
        ratios = ['16:9', '4:3', '3:2', '5:4']
        
        for i in range(num_slots):
            section = sections[i] if i < len(sections) else "conclusion"
            slot_id = f"img_{i+1}"
            
            slots.append({
                "id": slot_id,
                "description": f"Visual representation supporting the {section.lower()} discussion",
                "position": section.lower().replace(' ', '_'),
                "suggested_type": random.choice(image_types),
                "placement_rationale": f"Enhances understanding of key concepts in {section}",
                "content_guidance": f"Should illustrate main points discussed in {section} with clear, professional design",
                "dimensions": random.choice(dimensions),
                "aspect_ratio": random.choice(ratios),
                "alternatives": f"Could also use {random.choice(image_types)} or data visualization"
            })
        
        return slots
    
    def _format_content_as_markdown(self, content: str, sections: List[str], image_slots: List[Dict]) -> str:
        """Format content as proper Markdown with image placeholders"""
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        # Create markdown structure
        markdown_parts = []
        markdown_parts.append(f"# {sections[0] if sections else 'Article Title'}\n")
        
        # Add content with sections and image placeholders
        paragraphs_per_section = max(1, len(paragraphs) // max(1, len(sections)-1))  # -1 for intro
        
        for i, section in enumerate(sections[1:], 1):  # Skip first section (title)
            markdown_parts.append(f"\n## {section}\n")
            
            # Add paragraphs for this section
            start_idx = (i-1) * paragraphs_per_section
            end_idx = min(start_idx + paragraphs_per_section, len(paragraphs))
            
            section_paragraphs = paragraphs[start_idx:end_idx]
            for paragraph in section_paragraphs:
                markdown_parts.append(f"{paragraph}\n")
            
            # Add image placeholder if there's a slot for this section
            matching_slots = [slot for slot in image_slots if slot['position'] == section.lower().replace(' ', '_')]
            if matching_slots:
                slot = matching_slots[0]
                markdown_parts.append(f"\n\n![{{{{{slot['id']}}}}}](placeholder)\n\n")
        
        return '\n'.join(markdown_parts)  # Full content for executive-level articles