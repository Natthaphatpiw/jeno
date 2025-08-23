# URL Content Instructions Feature

## 🎯 Overview

ฟีเจอร์ใหม่ที่ให้ user สามารถระบุคำแนะนำเฉพาะสำหรับการใช้เนื้อหาจาก URL แต่ละตัว เพื่อให้ LLM สามารถดึงเนื้อหาและนำไปใช้ตามที่ต้องการได้อย่างแม่นยำ

## 🚀 Key Features

### 1. Content Focus (เนื้อหาที่สนใจ)
ระบุว่าต้องการเนื้อหาส่วนไหนจาก URL นั้น ๆ

**ตัวอย่าง:**
- "เอาเฉพาะสถิติและตัวเลขเกี่ยวกับ AI adoption"
- "สนใจแค่ case studies และ real-world examples"
- "ต้องการ methodology และ best practices"

### 2. Usage Instructions (วิธีการใช้)
ระบุว่าต้องการให้นำเนื้อหาไปใช้อย่างไร

**ตัวอย่าง:**
- "ใช้เป็น supporting evidence ใน main argument"  
- "แยกเป็น callout box หรือ sidebar"
- "สรุปเป็น bullet points ใน conclusion"
- "ทำเป็น step-by-step guide"

### 3. Section Target (ตำแหน่งที่ต้องการ)
ระบุ section ที่ต้องการให้วางเนื้อหา

**ตัวอย่าง:**
- "introduction" - วางในช่วงเริ่มต้น
- "market_analysis" - ใส่ในส่วนวิเคราะห์ตลาด
- "implementation_guide" - ไปอยู่ส่วน how-to
- "conclusion" - สรุปในตอนจบ

### 4. Extraction Type (ประเภทเนื้อหา)
ระบุประเภทของเนื้อหาที่ต้องการดึง

**ตัวอย่าง:**
- `statistics` - ตัวเลขและสถิติ
- `case_study` - ตัวอย่างองค์กร/บริษัท  
- `methodology` - วิธีการและกระบวนการ
- `quotes` - คำพูดจากผู้เชี่ยวชาญ
- `predictions` - การคาดการณ์แนวโน้ม

## 📋 API Usage

### Request Structure

```json
{
  "topic_category": "Digital Transformation",
  "industry": "Retail",
  "target_audience": "Business executives",
  "source_urls": ["https://example.com/article1", "https://example.com/article2"],
  "url_instructions": [
    {
      "url": "https://example.com/article1",
      "content_focus": "สถิติการ adopt digital technology ในธุรกิจ retail",
      "usage_instruction": "ใช้เป็น key statistics ใน introduction",
      "section_target": "introduction",
      "extraction_type": "statistics"
    },
    {
      "url": "https://example.com/article2", 
      "content_focus": "case study ของบริษัทที่ transform สำเร็จ",
      "usage_instruction": "ยกเป็นตัวอย่าง concrete example",
      "section_target": "success_stories",
      "extraction_type": "case_study"
    }
  ]
}
```

### Response Enhancement

LLM จะ return ข้อมูลเพิ่มเติมใน `source_usage_details`:

```json
{
  "source_usage_details": [
    {
      "source_title": "Digital Retail Transformation - McKinsey",
      "source_url": "https://example.com/article1",
      "content_used": "73% of retail executives report increased revenue",
      "usage_location": "Introduction, paragraph 1", 
      "usage_purpose": "Establish urgency of digital transformation",
      "transformation": "Paraphrased and contextualized for Jenosize audience",
      "instruction_compliance": "Used statistics in introduction as requested",
      "extraction_type_used": "statistics"
    }
  ]
}
```

## 💡 Use Cases

### 1. Research-Based Articles
```json
{
  "url_instructions": [
    {
      "url": "https://research-report.com",
      "content_focus": "ผลการวิจัยล่าสุดและ key findings",
      "usage_instruction": "ใช้เป็น evidence ใน main arguments", 
      "section_target": "research_findings",
      "extraction_type": "research_findings"
    }
  ]
}
```

### 2. How-to Guides
```json
{
  "url_instructions": [
    {
      "url": "https://best-practices.com",
      "content_focus": "step-by-step methodology",
      "usage_instruction": "แปลงเป็น numbered list ที่ actionable",
      "section_target": "implementation_steps", 
      "extraction_type": "methodology"
    }
  ]
}
```

### 3. Industry Analysis
```json
{
  "url_instructions": [
    {
      "url": "https://market-trends.com",
      "content_focus": "แนวโน้มตลาดและ future predictions", 
      "usage_instruction": "ใช้ใน conclusion เป็น future outlook",
      "section_target": "future_outlook",
      "extraction_type": "predictions"
    }
  ]
}
```

## 🔧 Implementation Details

### Schema Changes

#### New Model: `UrlContentInstruction`
```python
class UrlContentInstruction(BaseModel):
    url: str
    content_focus: Optional[str] = None
    usage_instruction: Optional[str] = None  
    section_target: Optional[str] = None
    extraction_type: Optional[str] = None
```

#### Updated Models
- `ArticleRequest`: Added `url_instructions` field
- `GenerationContext`: Added `url_instructions` field

### LLM Service Changes

#### Enhanced System Prompt
- Added URL content instruction handling guidelines
- Enhanced source usage documentation requirements

#### Enhanced User Prompt Generation
- Processes URL instructions into detailed prompts
- Ensures LLM follows user specifications precisely

## 📊 Benefits

### 1. **Precision Control** 
ผู้ใช้สามารถควบคุมได้ว่าต้องการเนื้อหาส่วนไหนจาก URL ไหน

### 2. **Better Content Integration**
เนื้อหาจาก source จะถูกนำไปใช้ในตำแหน่งและลักษณะที่เหมาะสม

### 3. **Improved Traceability** 
สามารถ track ได้ว่า LLM ทำตามคำแนะนำหรือไม่

### 4. **Flexible Usage Patterns**
รองรับการใช้งานหลากหลายรูปแบบตามความต้องการ

## 🎓 Best Practices

### 1. Content Focus Guidelines
- **Be Specific**: "สถิติการ adopt AI ใน healthcare" ดีกว่า "เนื้อหาเกี่ยวกับ AI"
- **Match Content Type**: ระบุประเภทเนื้อหาที่ต้องการให้ชัดเจน
- **Consider Context**: เลือกเนื้อหาที่เข้ากับ topic และ audience

### 2. Usage Instructions
- **Be Actionable**: "ทำเป็น comparison table" ชัดเจนกว่า "เปรียบเทียบ"
- **Specify Format**: ระบุรูปแบบที่ต้องการ (list, table, callout, etc.)
- **Consider Flow**: คิดถึงการไหลของเนื้อหาใน article

### 3. Section Targeting
- **Use Descriptive Names**: "market_analysis" ดีกว่า "section2"
- **Plan Article Structure**: วางแผน section ก่อนระบุ target
- **Allow Flexibility**: LLM อาจปรับตำแหน่งเล็กน้อยเพื่อความเหมาะสม

### 4. Extraction Types
- **Match Content**: ใช้ extraction type ที่ตรงกับเนื้อหาจริงใน URL
- **Be Consistent**: ใช้คำศัพท์เดียวกันสำหรับ type เดียวกัน
- **Document Standards**: มี standard list ของ extraction types

## ⚠️ Limitations & Considerations

### 1. **Content Availability**
URL อาจไม่มีเนื้อหาประเภทที่ request หรือเนื้อหาอาจเปลี่ยนแปลง

### 2. **LLM Interpretation**
LLM อาจตีความคำแนะนำแตกต่างจากที่ผู้ใช้ตั้งใจ

### 3. **Token Limitations** 
การส่งคำแนะนำมากเกินไปอาจเกิน token limit

### 4. **Quality Dependence**
คุณภาพของผลลัพธ์ขึ้นอยู่กับคุณภาพของ source content

## 🔍 Monitoring & Debugging

### 1. Check `source_usage_details`
ใช้ field `instruction_compliance` เพื่อเช็คว่า LLM ทำตามคำแนะนำหรือไม่

### 2. Validate `extraction_type_used`
เช็คว่า LLM ใช้ extraction type ที่ถูกต้องหรือไม่

### 3. Review `usage_location`
ตรวจสอบว่าเนื้อหาถูกวางในตำแหน่งที่เหมาะสมหรือไม่

## 🚀 Future Enhancements

### 1. **Smart Content Detection**
Auto-detect ประเภทเนื้อหาใน URL และแนะนำ extraction type

### 2. **Template Instructions**
Pre-defined instruction templates สำหรับ use cases ทั่วไป

### 3. **Visual Content Mapping**
แสดงการใช้เนื้อหาจาก source ใน visual format

### 4. **Quality Scoring**
Score ว่า LLM ทำตามคำแนะนำได้ดีแค่ไหน