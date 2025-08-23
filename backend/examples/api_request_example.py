#!/usr/bin/env python3
"""
API Request Examples for URL Content Instructions

Shows how to structure API requests with URL content instructions
"""

import json
from models.schemas import ArticleRequest, UrlContentInstruction

def example_api_request_json():
    """Example of how API request JSON should be structured"""
    
    # Example 1: Single URL with instructions
    request1 = {
        "topic_category": "Digital Transformation",
        "industry": "Retail",
        "target_audience": "Retail executives", 
        "source_urls": ["https://www.mckinsey.com/industries/retail/our-insights/retail-digital-transformation"],
        "url_instructions": [
            {
                "url": "https://www.mckinsey.com/industries/retail/our-insights/retail-digital-transformation",
                "content_focus": "สถิติการ adopt digital technology ในธุรกิจ retail และ impact ต่อ revenue",
                "usage_instruction": "ใช้เป็น key statistics ใน introduction เพื่อ establish ความสำคัญของหัวข้อ",
                "section_target": "introduction",
                "extraction_type": "statistics"
            }
        ],
        "seo_keywords": "digital transformation retail, retail technology adoption",
        "custom_prompt": "เขียนบทความเกี่ยวกับ digital transformation ในธุรกิจ retail โดยเน้นที่ practical implementation"
    }
    
    # Example 2: Multiple URLs with different instructions
    request2 = {
        "topic_category": "Artificial Intelligence",
        "industry": "Healthcare",
        "target_audience": "Healthcare administrators and IT directors",
        "source_urls": [
            "https://www.who.int/news/item/28-06-2023-who-calls-for-safe-and-ethical-ai-for-health", 
            "https://www.nejm.org/doi/full/10.1056/NEJMra2302726",
            "https://www.healthcarefinancenews.com/news/ai-healthcare-roi-study"
        ],
        "url_instructions": [
            {
                "url": "https://www.who.int/news/item/28-06-2023-who-calls-for-safe-and-ethical-ai-for-health",
                "content_focus": "WHO guidelines และ ethical considerations สำหรับการใช้ AI ใน healthcare",
                "usage_instruction": "ใช้เป็น regulatory framework ใน section เกี่ยวกับ compliance",
                "section_target": "regulatory_compliance",
                "extraction_type": "guidelines"
            },
            {
                "url": "https://www.nejm.org/doi/full/10.1056/NEJMra2302726",
                "content_focus": "Clinical evidence และ research findings จาก AI implementations",
                "usage_instruction": "สร้างเป็น evidence-based arguments ใน main content sections",
                "section_target": "clinical_applications", 
                "extraction_type": "research_findings"
            },
            {
                "url": "https://www.healthcarefinancenews.com/news/ai-healthcare-roi-study",
                "content_focus": "ROI data และ cost-benefit analysis ของ AI ใน healthcare",
                "usage_instruction": "ทำเป็น financial justification table ใน business case section",
                "section_target": "business_case",
                "extraction_type": "statistics"
            }
        ],
        "custom_prompt": "สร้างบทความที่ balance ระหว่าง clinical benefits และ business considerations ของ AI ใน healthcare"
    }
    
    return request1, request2

def example_with_validation():
    """Example showing how to validate the request using Pydantic models"""
    
    print("=== API Request Validation Example ===\n")
    
    # Create URL instructions using Pydantic models
    url_instructions = [
        UrlContentInstruction(
            url="https://www.gartner.com/en/newsroom/press-releases/2024-01-15-gartner-says-ai-augmentation",
            content_focus="Gartner predictions เกี่ยวกับ AI augmentation trends",
            usage_instruction="ใช้เป็น future outlook ใน conclusion section", 
            section_target="future_outlook",
            extraction_type="predictions"
        )
    ]
    
    # Create full request
    article_request = ArticleRequest(
        topic_category="Future of Work",
        industry="Technology",
        target_audience="HR Directors and Business Leaders",
        source_urls=["https://www.gartner.com/en/newsroom/press-releases/2024-01-15-gartner-says-ai-augmentation"],
        url_instructions=url_instructions,
        seo_keywords="AI augmentation, future of work, human AI collaboration",
        custom_prompt="เน้นที่ how AI will augment rather than replace human workers"
    )
    
    # Convert to dict for API sending
    request_dict = article_request.dict()
    
    print("Validated Request Structure:")
    print(json.dumps(request_dict, indent=2, ensure_ascii=False))
    
    return request_dict

def show_curl_examples():
    """Show curl command examples for API requests"""
    
    print("\n=== cURL Command Examples ===\n")
    
    request1, request2 = example_api_request_json()
    
    print("1. Single URL with Instructions:")
    print("curl -X POST http://localhost:8000/api/generate \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '" + json.dumps(request1, ensure_ascii=False) + "'")
    print()
    
    print("2. Multiple URLs with Different Instructions:")
    print("curl -X POST http://localhost:8000/api/generate \\") 
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '" + json.dumps(request2, ensure_ascii=False) + "'")
    print()

def show_expected_response():
    """Show what the expected response format looks like"""
    
    print("\n=== Expected Response Format ===\n")
    
    expected_response = {
        "content": "# Digital Transformation in Retail: A Strategic Imperative\n\n## Introduction\n\nAccording to McKinsey research, 73% of retail executives report...",
        "layout": {
            "sections": ["Introduction", "Current State", "Implementation Strategy", "Success Metrics", "Conclusion"],
            "image_slots": [
                {
                    "id": "retail_stats_chart",
                    "description": "Chart showing digital adoption rates in retail",
                    "position": "introduction",
                    "suggested_type": "chart"
                }
            ]
        },
        "source_usage_details": [
            {
                "source_title": "Retail Digital Transformation - McKinsey",
                "source_url": "https://www.mckinsey.com/industries/retail/our-insights/retail-digital-transformation",
                "content_used": "73% of retail executives report increased revenue from digital transformation initiatives",
                "usage_location": "Introduction, paragraph 1",
                "usage_purpose": "Establish urgency and importance of digital transformation",
                "transformation": "Paraphrased statistic and contextualized for Jenosize audience",
                "instruction_compliance": "Used statistics as key data points in introduction as requested",
                "extraction_type_used": "statistics"
            }
        ]
    }
    
    print("Response JSON Structure:")
    print(json.dumps(expected_response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    print("=== URL Content Instructions API Examples ===\n")
    
    # Show different request examples
    request1, request2 = example_api_request_json()
    
    print("Example 1: Single URL Request")
    print(json.dumps(request1, indent=2, ensure_ascii=False))
    print("\n" + "="*60 + "\n")
    
    print("Example 2: Multiple URLs Request") 
    print(json.dumps(request2, indent=2, ensure_ascii=False))
    print("\n" + "="*60 + "\n")
    
    # Show validation
    example_with_validation()
    
    # Show curl examples
    show_curl_examples()
    
    # Show expected response
    show_expected_response()

"""
PRACTICAL USAGE SCENARIOS:

1. **Research Article Creation:**
   - URL 1: Industry report → Extract key statistics for introduction
   - URL 2: Case study → Use as concrete example in implementation section  
   - URL 3: Expert interview → Pull quotes for authority/credibility

2. **Competitive Analysis:**
   - URL 1: Competitor A → Extract their strategy for comparison table
   - URL 2: Competitor B → Get their pricing model for analysis
   - URL 3: Market research → Use overall trends for context

3. **How-to Guide Creation:**
   - URL 1: Best practices guide → Extract methodology for step-by-step section
   - URL 2: Implementation case → Use as success story example
   - URL 3: Common pitfalls article → Extract warnings for "what to avoid" section

4. **Trend Analysis:**
   - URL 1: Recent research → Get latest statistics for current state
   - URL 2: Future predictions → Use for trend forecasting section
   - URL 3: Expert opinion → Pull insights for expert perspective boxes
"""