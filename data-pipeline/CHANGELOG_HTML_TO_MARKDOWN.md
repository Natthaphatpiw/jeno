# HTML to Markdown Conversion Enhancement

## การเปลี่ยนแปลงใหม่ในระบบ Data Pipeline

### 📋 สรุปการเปลี่ยนแปลง

ปรับปรุง data pipeline ให้มีขั้นตอนการแปลง HTML เป็น Markdown ด้วย LLM ก่อนสร้าง JSONL สำหรับ fine-tuning

### 🔄 กระบวนการใหม่

**เดิม:**
```
HTML Scraping → Text Extraction → JSONL Creation
```

**ใหม่:**
```
HTML Scraping → LLM HTML-to-Markdown → Quality Validation → JSONL Creation
```

### 🆕 ไฟล์ใหม่ที่เพิ่มเข้ามา

#### 1. `services/html_to_markdown_service.py`
- **HTMLToMarkdownService**: ใช้ OpenAI GPT-4o-mini แปลง HTML เป็น Markdown
- **Features:**
  - แปลง HTML เป็น clean Markdown format
  - ลบ navigation, ads, footers ออก
  - สกัดเนื้อหาหลักเท่านั้น
  - ปรับปรุง metadata และ structure
  - รองรับ batch processing

#### 2. `utils/markdown_validator.py`
- **MarkdownValidator**: ตรวจสอบคุณภาพ Markdown ที่สร้างขึ้น
- **Validation Areas:**
  - โครงสร้าง (headings, paragraphs, lists)
  - คุณภาพเนื้อหา (word count, repetition, readability)
  - การจัดรูปแบบ (HTML remnants, links, formatting)
- **Scoring System:** 0.0-1.0 (≥0.7 = valid for training)

### 🔧 ไฟล์ที่แก้ไข

#### 1. `processors/content_extractor.py`
- เพิ่ม HTML to Markdown conversion ด้วย LLM
- เพิ่ม Markdown quality validation
- เพิ่ม fallback mechanism ถ้าการแปลงล้มเหลว
- เพิ่ม `_extract_markdown_sections()` method

#### 2. `main.py`
- ปรับปรุง Step 3: Content Processing
- เพิ่มการบันทึก processed articles เป็น JSON
- เพิ่มการบันทึก individual Markdown files
- เพิ่ม detailed logging สำหรับ conversion process

#### 3. `requirements.txt`
- เพิ่ม `openai>=1.0.0`

#### 4. `config/settings.py`
- เพิ่ม `OPENAI_API_KEY` และ `OPENAI_MODEL` settings

### 🎯 ประโยชน์ของการเปลี่ยนแปลง

1. **คุณภาพเนื้อหาดีขึ้น**: LLM ช่วยทำความสะอาดและจัดโครงสร้าง HTML
2. **Markdown Format**: เหมาะสำหรับ fine-tuning มากกว่า plain text
3. **Quality Control**: มีระบบตรวจสอบคุณภาพอัตโนมัติ
4. **Flexibility**: สามารถปรับ prompt ให้เหมาะกับแต่ละประเภทเนื้อหา
5. **Traceability**: บันทึก conversion notes และ validation results

### 🚀 วิธีใช้งาน

#### 1. Setup Environment Variables
```bash
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_MODEL="gpt-4o-mini"  # Optional, defaults to gpt-4o-mini
```

#### 2. Install Dependencies
```bash
cd /Users/piw/Downloads/jetask/data-pipeline
pip install -r requirements.txt
```

#### 3. Run Pipeline
```bash
python main.py
```

### 📁 Output Structure

```
output/
├── processed_articles.json          # All processed articles with metadata
├── markdown/                       # Individual Markdown files
│   ├── article-title-1.md
│   ├── article-title-2.md
│   └── ...
├── train.jsonl                     # Training dataset
├── validation.jsonl                # Validation dataset
└── ...
```

### 🔍 การตรวจสอบผลลัพธ์

#### 1. ตรวจสอบ Markdown Files
```bash
ls -la output/markdown/
cat output/markdown/article-title-1.md
```

#### 2. ตรวจสอบ Conversion Quality
```bash
grep -A 5 "markdown_validation" output/processed_articles.json
```

#### 3. ตรวจสอบ Logs
- ดู conversion success rate
- ตรวจสอบ validation scores
- ตรวจสอบ fallback cases

### ⚙️ การปรับแต่ง

#### 1. ปรับ Conversion Prompt
แก้ไขใน `services/html_to_markdown_service.py`:
- `_get_conversion_system_prompt()`
- ปรับ temperature และ max_tokens

#### 2. ปรับ Validation Criteria
แก้ไขใน `utils/markdown_validator.py`:
- `min_word_count`
- `min_paragraph_count`
- Scoring weights

#### 3. ปรับ Quality Thresholds
แก้ไขใน `processors/content_extractor.py`:
- Fallback threshold (currently 0.5)
- Validation requirements

### 🐛 Troubleshooting

#### 1. OpenAI API Errors
- ตรวจสอบ API key
- ตรวจสอบ rate limits
- ตรวจสอบ model availability

#### 2. Poor Conversion Quality
- ตรวจสอบ source HTML quality
- ปรับ conversion prompt
- ลด validation threshold

#### 3. Performance Issues
- ใช้ batch processing
- ปรับ request delays
- ใช้ cheaper model (gpt-4o-mini)

### 📊 Expected Results

- **Conversion Success Rate**: >90%
- **Validation Pass Rate**: >80%
- **Average Quality Score**: >0.75
- **Processing Time**: ~2-5 seconds per article

### 🔮 Future Enhancements

1. **Custom Model**: Train specialized HTML-to-Markdown model
2. **Multi-language Support**: Support non-English content
3. **Advanced Validation**: Add semantic validation
4. **Parallel Processing**: Process multiple articles simultaneously
5. **Quality Feedback Loop**: Use validation results to improve conversion