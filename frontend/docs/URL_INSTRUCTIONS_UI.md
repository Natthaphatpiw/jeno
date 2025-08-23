# URL Instructions UI Documentation

## 🎯 Overview

Enhanced frontend interface to support detailed URL content instructions, allowing users to specify exactly what content they want from each URL and how it should be used in the generated article.

## 🆕 New Components

### 1. `UrlInstructionsForm.tsx`

Advanced form component for configuring URL content instructions.

**Features:**
- ✅ Collapsible interface to save space
- ✅ Auto-populates based on entered URLs
- ✅ Pre-defined extraction types with descriptions
- ✅ Common section targets dropdown
- ✅ Example fill functionality
- ✅ Individual instruction clearing
- ✅ Help documentation toggle
- ✅ Real-time preview of instructions

**Props:**
```typescript
interface UrlInstructionsFormProps {
  sourceUrls: string[];                    // URLs from main form
  urlInstructions: UrlContentInstruction[]; // Current instructions
  onInstructionsChange: (instructions: UrlContentInstruction[]) => void;
}
```

## 🔄 Updated Components

### 1. `InputForm.tsx`
- Added URL instructions state management
- Integrated `UrlInstructionsForm` component
- Updated form submission to include URL instructions
- Enhanced form clearing to reset instructions

### 2. `ArticleDisplay.tsx`
- Enhanced source usage details section
- Added URL instruction compliance display
- Shows extraction type used
- Displays instruction compliance feedback

## 📊 Enhanced Types

### New Interfaces

```typescript
interface UrlContentInstruction {
  url: string;
  contentFocus?: string;    // What specific content to extract
  usageInstruction?: string; // How to use the content
  sectionTarget?: string;   // Target section in article
  extractionType?: string;  // Type of content (statistics, case_study, etc.)
}
```

### Updated Interfaces

```typescript
interface ArticleRequest {
  // ... existing fields
  urlInstructions?: UrlContentInstruction[]; // New field
}

interface SourceUsageDetail {
  // ... existing fields
  instructionCompliance?: string;  // How instructions were followed
  extractionTypeUsed?: string;    // Type of content extracted
}
```

## 🎨 UI/UX Features

### Extraction Types Available
- **📊 Statistics & Data** - ตัวเลข สถิติ และข้อมูลเชิงปริมาณ
- **📝 Case Study** - ตัวอย่างองค์กร บริษัท หรือโครงการ  
- **⚙️ Methodology** - วิธีการ กระบวนการ หรือขั้นตอน
- **💬 Expert Quotes** - คำพูดจากผู้เชี่ยวชาญหรือบุคคลสำคัญ
- **🔮 Predictions** - การคาดการณ์แนวโน้มหรืออนาคต
- **🔬 Research Findings** - ผลการวิจัยและการค้นพบ

### Section Targets Available
- `introduction`
- `market_analysis`
- `current_trends`
- `case_studies`
- `implementation_guide`
- `best_practices`
- `challenges`
- `future_outlook`
- `conclusion`

## 💡 User Experience

### Collapsible Design
- Instructions form starts collapsed to avoid overwhelming users
- Clear indicators show how many URLs are ready for configuration
- One-click expand to access full configuration

### Progressive Enhancement
- Works with existing URL functionality (backward compatible)
- Instructions are optional - users can skip for AI auto-determination
- Visual feedback shows which URLs have instructions configured

### Smart Defaults
- Auto-creates instruction slots for all valid URLs
- Removes instruction slots when URLs are deleted
- Maintains instruction state during form interactions

## 🔧 API Integration

### Request Format
```json
{
  "source_urls": ["https://example1.com", "https://example2.com"],
  "url_instructions": [
    {
      "url": "https://example1.com",
      "content_focus": "เอาสถิติการ adopt AI ในองค์กร",
      "usage_instruction": "ใช้เป็น supporting evidence ใน introduction",
      "section_target": "introduction",
      "extraction_type": "statistics"
    }
  ]
}
```

### Response Enhancement
```json
{
  "source_usage_details": [
    {
      "source_title": "AI Report 2024",
      "content_used": "73% of organizations are adopting AI",
      "instruction_compliance": "Used statistics in introduction as requested",
      "extraction_type_used": "statistics"
    }
  ]
}
```

## 🎯 Example Usage Flows

### 1. Basic Usage
1. User enters URLs in main form
2. URL Instructions section automatically appears
3. User clicks "Configure" to expand instructions
4. Fills in desired instructions for specific URLs
5. Submits form with enhanced instructions

### 2. Quick Start with Examples
1. User enters URLs
2. Expands URL instructions
3. Clicks "Example" button for quick fill
4. Modifies example as needed
5. Submits enhanced request

### 3. Advanced Configuration
1. User enters multiple URLs
2. Configures different extraction types for each URL
3. Targets different sections for different URLs
4. Reviews instruction preview
5. Submits comprehensive configuration

## 🔍 Validation & Feedback

### Client-Side Validation
- Instructions automatically sync with URL changes
- Invalid URLs are filtered out from instructions
- Clear visual indicators for configured vs unconfigured URLs

### Server Response Processing
- Compliance feedback displayed prominently
- Extraction type badges show what was actually extracted
- Clear mapping between instructions and results

## 🎨 Visual Design

### Color Scheme
- **Amber/Yellow** theme for instructions (indicates "advanced/optional")
- **Green checkmarks** for compliance indicators
- **Blue accents** for action buttons
- **Gray** for secondary information

### Icons
- ⚙️ Settings icon for main instructions
- 🎯 Target for content focus
- 📝 Document for usage instructions
- 📍 Location pin for section targets
- 🔖 Bookmark for extraction types

## 🚀 Performance Considerations

- **Lazy Loading**: Instructions only created when URLs are present
- **Memoization**: Component re-renders optimized
- **State Management**: Efficient state updates without full re-renders
- **Bundle Size**: New component adds ~15KB to bundle

## 📱 Responsive Design

- **Desktop**: Full 2-column layout for instruction fields
- **Tablet**: Single column with adequate spacing
- **Mobile**: Stacked layout with touch-friendly controls

## 🔧 Customization Options

### Theme Integration
- Uses existing Tailwind classes for consistency
- Amber color scheme distinguishes from main form
- Responsive breakpoints match existing design

### Content Customization
- Extraction types easily configurable via constants
- Section targets can be modified per use case
- Help text and examples easily updatable

## 🐛 Error Handling

- **Empty URLs**: Instructions automatically cleaned up
- **Invalid Instructions**: Graceful fallbacks to AI defaults
- **Network Errors**: Clear error messages for failed submissions
- **Type Mismatches**: TypeScript ensures type safety

## 🔮 Future Enhancements

### Planned Features
- **Template Instructions** - Pre-saved instruction sets
- **Smart Suggestions** - AI-powered instruction recommendations
- **Visual Preview** - Show how instructions will be applied
- **Bulk Operations** - Apply same instructions to multiple URLs

### Potential Improvements
- **Drag & Drop** reordering of URL priorities
- **Custom Extraction Types** - User-defined content types
- **Section Preview** - Visual article structure mapping
- **Instruction History** - Save frequently used patterns

## 📖 Usage Examples

### Research Article
```typescript
{
  url: "https://research-report.com/ai-trends",
  contentFocus: "ผลการวิจัยล่าสุดและ key findings เกี่ยวกับ AI adoption",
  usageInstruction: "ใช้เป็น evidence-based arguments ใน main content",
  sectionTarget: "current_trends",
  extractionType: "research_findings"
}
```

### Case Study Integration
```typescript
{
  url: "https://company-success.com/digital-transformation",
  contentFocus: "case study ของบริษัทที่ transform สำเร็จ",
  usageInstruction: "ยกเป็น concrete example และแยกเป็น callout box",
  sectionTarget: "case_studies", 
  extractionType: "case_study"
}
```

This enhanced UI provides users with granular control over content extraction while maintaining ease of use through progressive enhancement and smart defaults.