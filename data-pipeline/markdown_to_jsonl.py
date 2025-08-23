#!/usr/bin/env python3
"""
Convert clean markdown files to JSONL format for fine-tuning
"""

import os
import json
import glob
from pathlib import Path
import random
from typing import List, Dict
import jsonlines

# System prompt matching the current llm_service.py
SYSTEM_PROMPT = """You are an expert content creator for Jenosize, a premier digital transformation consultancy. You are writing for C-level executives, business leaders, and decision-makers who need strategic insights to drive business transformation.

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

ARTICLE STRUCTURE AND REQUIREMENTS:

**Length**: 2000-3500 words (executive-level depth)

**Mandatory Structure**:
1. **Executive Summary** (150-200 words)
2. **Introduction** (200-300 words)
3. **Main Analysis Sections** (4-6 sections, 400-600 words each)
4. **Strategic Recommendations** (300-400 words)
5. **Future Outlook** (200-300 words)
6. **Conclusion** (150-200 words)

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
  "source_usage_details": []
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

IMPORTANT: You must respond in JSON format only. Return your response as a valid JSON object with the structure specified above."""

# Categories and topics for generating realistic user prompts
CATEGORIES = {
    'Digital Transformation': ['Technology', 'Healthcare', 'Finance', 'Manufacturing'],
    'Customer Experience': ['Retail', 'Technology', 'Healthcare', 'Finance'], 
    'Business Innovation': ['Technology', 'Manufacturing', 'Consulting', 'Media'],
    'Social Impact & Sustainability': ['Real Estate', 'Manufacturing', 'Energy', 'Transportation'],
    'Consumer Insights & Behavior': ['Retail', 'Media', 'Healthcare', 'Finance'],
    'Marketing Strategy': ['Technology', 'Retail', 'Media', 'Education']
}

AUDIENCES = [
    'C-suite executives', 'Business leaders', 'Entrepreneurs', 
    'Marketing professionals', 'Operations managers', 'Strategy consultants',
    'Digital transformation leaders', 'Innovation directors'
]

def extract_title_from_markdown(content: str) -> str:
    """Extract title from markdown content"""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return "Business Strategy Article"

def generate_keywords_from_title(title: str) -> str:
    """Generate realistic SEO keywords from title"""
    words = title.lower().replace('-', ' ').replace(':', ' ').split()
    # Filter out common words
    stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 'when', 'where'}
    keywords = [word for word in words if len(word) > 3 and word not in stop_words]
    return ', '.join(keywords[:5])  # Take first 5 keywords

def generate_user_prompt(title: str) -> str:
    """Generate realistic user prompt"""
    category = random.choice(list(CATEGORIES.keys()))
    industry = random.choice(CATEGORIES[category])
    audience = random.choice(AUDIENCES)
    keywords = generate_keywords_from_title(title)
    
    templates = [
        f"Generate a comprehensive article with the following specifications:\n\nTopic Category: {category}\nIndustry Focus: {industry}\nTarget Audience: {audience}\nSEO Keywords to incorporate: {keywords}\n\nReturn your response as a JSON object with the specified format.",
        
        f"Generate a comprehensive article with the following specifications:\n\nTopic Category: {category}\nIndustry Focus: {industry}\nTarget Audience: {audience}\nSEO Keywords to incorporate: {keywords}\n\nCUSTOM USER INSTRUCTIONS: Include more statistical data and concrete examples from real companies; Focus on actionable implementation steps; Keep explanations accessible to business leaders\n\nReturn your response as a JSON object with the specified format.",
        
        f"Generate an article about {category.lower()} for {audience.lower()}.\n\nReturn your response as a JSON object with the specified format."
    ]
    
    return random.choice(templates)

def create_response_from_markdown(markdown_content: str, title: str) -> str:
    """Create JSON response from markdown content"""
    
    # Extract sections from markdown
    sections = []
    lines = markdown_content.split('\n')
    current_section = ""
    
    for line in lines:
        if line.startswith('# '):
            current_section = line[2:].strip()
            if current_section and current_section not in sections:
                sections.append(current_section)
        elif line.startswith('## ') and not line.startswith('### '):
            current_section = line[3:].strip()
            if current_section and current_section not in sections:
                sections.append(current_section)
    
    if not sections:
        sections = [title, "Introduction", "Key Insights", "Strategic Recommendations", "Conclusion"]
    
    # Generate image slots (3-5 strategic placements)
    num_slots = min(random.randint(3, 5), len(sections))
    image_slots = []
    
    image_types = ['infographic', 'chart', 'illustration', 'photo']
    dimensions = ['1200x800px', '800x600px', '1000x600px', '1200x900px']
    ratios = ['16:9', '4:3', '3:2', '5:4']
    
    for i in range(num_slots):
        section = sections[i] if i < len(sections) else "conclusion"
        slot_id = f"img_{i+1}"
        
        image_slots.append({
            "id": slot_id,
            "description": f"Professional {random.choice(image_types)} supporting {section.lower()} section",
            "position": section.lower().replace(' ', '_').replace('&', 'and').replace(':', ''),
            "suggested_type": random.choice(image_types),
            "placement_rationale": f"Strategic placement to enhance understanding of {section.lower()} concepts",
            "content_guidance": f"Visual elements that illustrate key points from {section.lower()} section with executive-level design",
            "dimensions": random.choice(dimensions),
            "aspect_ratio": random.choice(ratios),
            "alternatives": f"Could also use {random.choice(image_types)} or data visualization"
        })
    
    # Create the response object
    response = {
        "content": markdown_content,
        "layout": {
            "sections": sections,
            "image_slots": image_slots
        },
        "source_usage_details": []
    }
    
    return json.dumps(response, ensure_ascii=False)

def convert_markdown_to_jsonl(markdown_dir: str, output_file: str):
    """Convert all markdown files to JSONL format"""
    
    markdown_files = glob.glob(os.path.join(markdown_dir, "*.md"))
    print(f"Found {len(markdown_files)} markdown files")
    
    if not markdown_files:
        print("No markdown files found!")
        return
    
    training_examples = []
    
    for md_file in markdown_files:
        try:
            # Read markdown content
            with open(md_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Skip if content is too short
            if len(markdown_content) < 500:
                print(f"Skipping {md_file} - content too short")
                continue
            
            # Extract title
            title = extract_title_from_markdown(markdown_content)
            print(f"Processing: {title}")
            
            # Generate user prompt
            user_prompt = generate_user_prompt(title)
            
            # Create assistant response
            assistant_response = create_response_from_markdown(markdown_content, title)
            
            # Create training example
            example = {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": assistant_response}
                ]
            }
            
            training_examples.append(example)
            
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
            continue
    
    # Save to JSONL
    print(f"Generated {len(training_examples)} training examples")
    
    if training_examples:
        with jsonlines.open(output_file, 'w') as writer:
            for example in training_examples:
                writer.write(example)
        
        print(f"Saved training data to {output_file}")
        
        # Also create validation split (20%)
        random.shuffle(training_examples)
        split_point = int(len(training_examples) * 0.8)
        
        train_examples = training_examples[:split_point]
        val_examples = training_examples[split_point:]
        
        # Save train/validation splits
        train_file = output_file.replace('.jsonl', '_train.jsonl')
        val_file = output_file.replace('.jsonl', '_validation.jsonl')
        
        with jsonlines.open(train_file, 'w') as writer:
            for example in train_examples:
                writer.write(example)
        
        with jsonlines.open(val_file, 'w') as writer:
            for example in val_examples:
                writer.write(example)
        
        print(f"Split dataset: {len(train_examples)} train, {len(val_examples)} validation")
        print(f"Train file: {train_file}")
        print(f"Validation file: {val_file}")

if __name__ == "__main__":
    # Convert markdown files to JSONL
    markdown_dir = "output/markdown"
    output_file = "output/clean_training_data.jsonl"
    
    convert_markdown_to_jsonl(markdown_dir, output_file)