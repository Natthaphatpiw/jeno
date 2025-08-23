#!/usr/bin/env python3
"""
Example script demonstrating URL content instructions functionality

This shows how users can provide detailed instructions for how to extract
and use content from specific URLs when generating articles.
"""

from models.schemas import UrlContentInstruction, GenerationContext
from services.llm_service import LLMService

def example_basic_url_instruction():
    """Basic example: Single URL with content focus"""
    
    url_instruction = UrlContentInstruction(
        url="https://www.mckinsey.com/featured-insights/artificial-intelligence",
        content_focus="เอาสถิติและตัวเลขเกี่ยวกับ AI adoption ในองค์กร",
        usage_instruction="ใช้สถิติเหล่านี้เป็น supporting evidence ในการพูดถึงแนวโน้ม AI",
        section_target="introduction",
        extraction_type="statistics"
    )
    
    context = GenerationContext(
        topic_category="Digital Transformation",
        industry="Technology",
        target_audience="Business executives",
        url_instructions=[url_instruction],
        # Note: In real usage, scraped_sources would contain the actual scraped content
        scraped_sources=[{
            "title": "AI Insights - McKinsey",
            "url": "https://www.mckinsey.com/featured-insights/artificial-intelligence",
            "content": "Sample content with AI adoption statistics showing 70% of companies are exploring AI..."
        }]
    )
    
    return context

def example_multiple_url_instructions():
    """Advanced example: Multiple URLs with different instructions"""
    
    url_instructions = [
        UrlContentInstruction(
            url="https://www.gartner.com/en/newsroom/press-releases/2024-ai-trends",
            content_focus="Gartner's predictions สำหรับ AI trends ในปี 2024-2025",
            usage_instruction="ใช้เป็น main argument ใน section เกี่ยวกับ future outlook",
            section_target="future_trends_section",
            extraction_type="predictions"
        ),
        UrlContentInstruction(
            url="https://hbr.org/2024/01/ai-implementation-case-study",
            content_focus="Case study ของบริษัทที่ implement AI successfully",
            usage_instruction="ยกเป็นตัวอย่าง concrete example และแยกเป็น box/callout",
            section_target="implementation_examples",
            extraction_type="case_study"
        ),
        UrlContentInstruction(
            url="https://www.bcg.com/publications/2024/ai-roi-methodology",
            content_focus="Methodology สำหรับการวัด ROI จาก AI projects",
            usage_instruction="สรุปเป็น step-by-step guide และทำเป็น numbered list",
            section_target="measurement_framework",
            extraction_type="methodology"
        )
    ]
    
    context = GenerationContext(
        topic_category="Artificial Intelligence",
        industry="Business Strategy", 
        target_audience="C-level executives",
        seo_keywords=["AI ROI", "artificial intelligence implementation", "business AI strategy"],
        custom_prompt="เขียนบทความเชิงลึกเกี่ยวกับการวัดผลลัพธ์ของ AI projects ในองค์กร",
        url_instructions=url_instructions,
        # In real usage, this would contain actual scraped content
        scraped_sources=[
            {
                "title": "AI Trends 2024 - Gartner",
                "url": "https://www.gartner.com/en/newsroom/press-releases/2024-ai-trends",
                "content": "Gartner predicts that by 2025, 80% of enterprises will have implemented AI in some form..."
            },
            {
                "title": "AI Implementation Case Study - Harvard Business Review",
                "url": "https://hbr.org/2024/01/ai-implementation-case-study",
                "content": "Company XYZ successfully implemented AI across 3 departments, resulting in 25% efficiency gains..."
            },
            {
                "title": "AI ROI Methodology - Boston Consulting Group", 
                "url": "https://www.bcg.com/publications/2024/ai-roi-methodology",
                "content": "BCG's framework for measuring AI ROI involves 5 key steps: 1) Baseline establishment, 2) KPI definition..."
            }
        ]
    )
    
    return context

def demonstrate_usage():
    """Demonstrate how the URL instructions would be used"""
    
    print("=== URL Content Instructions Example ===\n")
    
    # Example 1: Basic usage
    print("1. Basic URL Instruction:")
    context1 = example_basic_url_instruction()
    
    print(f"   URL: {context1.url_instructions[0].url}")
    print(f"   Content Focus: {context1.url_instructions[0].content_focus}")
    print(f"   Usage: {context1.url_instructions[0].usage_instruction}")
    print(f"   Target Section: {context1.url_instructions[0].section_target}")
    print(f"   Extraction Type: {context1.url_instructions[0].extraction_type}")
    print()
    
    # Example 2: Multiple URLs
    print("2. Multiple URL Instructions:")
    context2 = example_multiple_url_instructions()
    
    for i, instruction in enumerate(context2.url_instructions, 1):
        print(f"   URL {i}: {instruction.url}")
        print(f"   Focus: {instruction.content_focus}")
        print(f"   Usage: {instruction.usage_instruction}")
        print(f"   Target: {instruction.section_target}")
        print(f"   Type: {instruction.extraction_type}")
        print()
    
    print("=== How LLM Service Would Process This ===\n")
    
    # Show how the prompt would be built
    llm_service = LLMService()
    user_prompt = llm_service._build_user_prompt(context2, None)
    
    print("Generated User Prompt:")
    print("-" * 50)
    print(user_prompt)
    print("-" * 50)
    print()
    
    print("=== Expected LLM Behavior ===")
    print("The LLM will:")
    print("- Extract Gartner predictions and place them in 'future_trends_section'")
    print("- Create a case study callout from HBR content in 'implementation_examples'") 
    print("- Build a numbered methodology list from BCG content in 'measurement_framework'")
    print("- Document exact compliance with instructions in source_usage_details")
    print("- Include instruction_compliance and extraction_type_used fields")

if __name__ == "__main__":
    demonstrate_usage()

"""
USAGE PATTERNS:

1. **Content Focus Examples:**
   - "เอาเฉพาะส่วน statistics และ research findings"
   - "สนใจแค่ methodology และ best practices"  
   - "เอา case studies และ real-world examples"
   - "ต้องการ quotes จาก expert interviews"

2. **Usage Instruction Examples:**
   - "ใช้เป็น supporting evidence ใน main argument"
   - "แยกเป็น callout box หรือ sidebar"
   - "สรุปเป็น bullet points ใน conclusion"
   - "ทำเป็น comparison table กับ competitors"
   - "เขียนเป็น step-by-step guide"

3. **Section Target Examples:**
   - "introduction" - วางไว้ในช่วงเริ่มต้น
   - "market_analysis" - ใส่ในส่วนวิเคราะห์ตลาด
   - "implementation_guide" - ไปอยู่ส่วน how-to
   - "conclusion" - สรุปในตอนจบ
   - "case_studies" - ส่วนตัวอย่างองค์กร

4. **Extraction Type Examples:**
   - "statistics" - ตัวเลขและสถิติ
   - "case_study" - ตัวอย่างองค์กร/บริษัท
   - "methodology" - วิธีการและกระบวนการ
   - "quotes" - คำพูดจากผู้เชี่ยวชาญ
   - "predictions" - การคาดการณ์แนวโน้ม
   - "research_findings" - ผลการวิจัย
"""