'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { Plus, X, Settings, Target, FileText, BarChart3, MessageCircle, Lightbulb, ChevronDown, ChevronUp, Info } from 'lucide-react';
import toast from 'react-hot-toast';
import { UrlContentInstruction } from '../types';

interface UrlInstructionsFormProps {
  sourceUrls: string[];
  urlInstructions: UrlContentInstruction[];
  onInstructionsChange: (instructions: UrlContentInstruction[]) => void;
}

const EXTRACTION_TYPES = [
  { value: 'statistics', label: '📊 Statistics & Data', icon: BarChart3, description: 'ตัวเลข สถิติ และข้อมูลเชิงปริมาณ' },
  { value: 'case_study', label: '📝 Case Study', icon: FileText, description: 'ตัวอย่างองค์กร บริษัท หรือโครงการ' },
  { value: 'methodology', label: '⚙️ Methodology', icon: Settings, description: 'วิธีการ กระบวนการ หรือขั้นตอน' },
  { value: 'quotes', label: '💬 Expert Quotes', icon: MessageCircle, description: 'คำพูดจากผู้เชี่ยวชาญหรือบุคคลสำคัญ' },
  { value: 'predictions', label: '🔮 Predictions', icon: Lightbulb, description: 'การคาดการณ์แนวโน้มหรืออนาคต' },
  { value: 'research_findings', label: '🔬 Research Findings', icon: Target, description: 'ผลการวิจัยและการค้นพบ' }
];

const COMMON_SECTIONS = [
  'introduction',
  'market_analysis', 
  'current_trends',
  'case_studies',
  'implementation_guide',
  'best_practices',
  'challenges',
  'future_outlook',
  'conclusion'
];

export default function UrlInstructionsForm({ sourceUrls, urlInstructions, onInstructionsChange }: UrlInstructionsFormProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

  // Filter out empty URLs with useMemo for performance
  const validUrls = useMemo(() => 
    sourceUrls.filter(url => url.trim() !== ''), 
    [sourceUrls]
  );

  // Sync instructions with URL changes - only when URLs change
  useEffect(() => {
    if (validUrls.length === 0) {
      if (urlInstructions.length > 0) {
        onInstructionsChange([]);
      }
      return;
    }

    const currentUrls = urlInstructions.map(inst => inst.url);
    const needsSync = 
      validUrls.some(url => !currentUrls.includes(url)) || 
      currentUrls.some(url => !validUrls.includes(url));

    if (!needsSync) return;

    const newInstructions: UrlContentInstruction[] = [];
    
    // Keep existing instructions for URLs that still exist
    validUrls.forEach(url => {
      const existing = urlInstructions.find(inst => inst.url === url);
      if (existing) {
        newInstructions.push(existing);
      } else {
        newInstructions.push({
          url,
          contentFocus: '',
          usageInstruction: '',
          sectionTarget: '',
          extractionType: ''
        });
      }
    });

    onInstructionsChange(newInstructions);
  }, [validUrls.join(',')]); // Use string join to avoid reference changes

  const updateInstruction = (url: string, field: keyof UrlContentInstruction, value: string) => {
    const updated = urlInstructions.map(inst => 
      inst.url === url ? { ...inst, [field]: value } : inst
    );
    onInstructionsChange(updated);
  };

  const clearInstruction = (url: string) => {
    const updated = urlInstructions.map(inst =>
      inst.url === url ? {
        url,
        contentFocus: '',
        usageInstruction: '',
        sectionTarget: '',
        extractionType: ''
      } : inst
    );
    onInstructionsChange(updated);
    toast.success('Instructions cleared for this URL');
  };

  const fillExampleInstruction = (url: string) => {
    const examples = [
      {
        contentFocus: 'เอาสถิติและตัวเลขเกี่ยวกับการ adopt AI ในองค์กร',
        usageInstruction: 'ใช้เป็น supporting evidence ใน introduction section',
        sectionTarget: 'introduction',
        extractionType: 'statistics'
      },
      {
        contentFocus: 'case study ของบริษัทที่ implement digital transformation สำเร็จ',
        usageInstruction: 'ยกเป็นตัวอย่าง concrete example และแยกเป็น callout box',
        sectionTarget: 'case_studies',
        extractionType: 'case_study'
      },
      {
        contentFocus: 'methodology สำหรับการวัด ROI ของ technology projects',
        usageInstruction: 'สรุปเป็น step-by-step guide และทำเป็น numbered list',
        sectionTarget: 'implementation_guide',
        extractionType: 'methodology'
      }
    ];

    const randomExample = examples[Math.floor(Math.random() * examples.length)];
    const updated = urlInstructions.map(inst =>
      inst.url === url ? { url, ...randomExample } : inst
    );
    onInstructionsChange(updated);
    toast.success('Example filled!');
  };

  if (validUrls.length === 0) {
    return null;
  }

  return (
    <div className="border-2 border-dashed border-amber-200 rounded-2xl bg-amber-50/30 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 bg-amber-100 rounded-lg flex items-center justify-center">
            <Settings className="w-4 h-4 text-amber-600" />
          </div>
          <h3 className="text-lg font-semibold text-amber-800">
            URL Content Instructions
          </h3>
          <span className="text-xs bg-amber-200 text-amber-700 px-2 py-1 rounded-full font-medium">
            Advanced
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowHelp(!showHelp)}
            className="p-2 text-amber-600 hover:text-amber-700 hover:bg-amber-100 rounded-lg transition-all"
          >
            <Info className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center text-amber-700 hover:text-amber-800 transition-colors"
          >
            <span className="text-sm font-medium mr-1">
              {isExpanded ? 'Collapse' : 'Configure'}
            </span>
            {isExpanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {showHelp && (
        <div className="bg-amber-100 border border-amber-200 rounded-xl p-4 mb-4">
          <h4 className="font-semibold text-amber-800 mb-2">🎯 How URL Instructions Work</h4>
          <div className="text-sm text-amber-700 space-y-2">
            <p><strong>Content Focus:</strong> ระบุเนื้อหาที่ต้องการจาก URL (เช่น "เอาแค่สถิติ" หรือ "สนใจ case studies")</p>
            <p><strong>Usage Instruction:</strong> บอกวิธีการใช้เนื้อหา (เช่น "ทำเป็น bullet points" หรือ "ใช้เป็น supporting evidence")</p>
            <p><strong>Section Target:</strong> ระบุส่วนของบทความที่ต้องการวางเนื้อหา</p>
            <p><strong>Extraction Type:</strong> ประเภทเนื้อหาที่ต้องการดึง</p>
          </div>
        </div>
      )}

      {!isExpanded && (
        <p className="text-sm text-amber-700 leading-relaxed">
          ให้คำแนะนำเฉพาะสำหรับแต่ละ URL ว่าต้องการเนื้อหาส่วนไหน และนำไปใช้อย่างไร
          <span className="ml-2 text-amber-600">
            ({validUrls.length} URL{validUrls.length !== 1 ? 's' : ''} ready for configuration)
          </span>
        </p>
      )}

      {isExpanded && (
        <div className="space-y-6 mt-6">
          {urlInstructions.map((instruction, index) => (
            <div key={instruction.url} className="bg-white rounded-xl border border-amber-200 p-5">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="bg-amber-100 text-amber-700 text-xs font-medium px-2 py-1 rounded-full">
                      URL {index + 1}
                    </span>
                    <span className="text-xs text-gray-500">
                      {instruction.url.length > 50 
                        ? `${instruction.url.substring(0, 47)}...` 
                        : instruction.url}
                    </span>
                  </div>
                </div>
                <div className="flex gap-1">
                  <button
                    type="button"
                    onClick={() => fillExampleInstruction(instruction.url)}
                    className="text-xs bg-sky-100 text-sky-700 px-3 py-1 rounded-full hover:bg-sky-200 transition-colors"
                  >
                    Example
                  </button>
                  <button
                    type="button"
                    onClick={() => clearInstruction(instruction.url)}
                    className="text-xs bg-gray-100 text-gray-600 px-3 py-1 rounded-full hover:bg-gray-200 transition-colors"
                  >
                    Clear
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Content Focus */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Content Focus 🎯
                  </label>
                  <textarea
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 resize-none"
                    placeholder="เช่น: เอาแค่สถิติและตัวเลขเกี่ยวกับ AI adoption ในองค์กร"
                    rows={2}
                    value={instruction.contentFocus || ''}
                    onChange={(e) => updateInstruction(instruction.url, 'contentFocus', e.target.value)}
                  />
                </div>

                {/* Usage Instruction */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Usage Instruction 📝
                  </label>
                  <textarea
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 resize-none"
                    placeholder="เช่น: ใช้เป็น supporting evidence ใน introduction section"
                    rows={2}
                    value={instruction.usageInstruction || ''}
                    onChange={(e) => updateInstruction(instruction.url, 'usageInstruction', e.target.value)}
                  />
                </div>

                {/* Section Target */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Section 📍
                  </label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                    value={instruction.sectionTarget || ''}
                    onChange={(e) => updateInstruction(instruction.url, 'sectionTarget', e.target.value)}
                  >
                    <option value="">Select section (optional)</option>
                    {COMMON_SECTIONS.map(section => (
                      <option key={section} value={section}>
                        {section.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Extraction Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Extraction Type 🔖
                  </label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                    value={instruction.extractionType || ''}
                    onChange={(e) => updateInstruction(instruction.url, 'extractionType', e.target.value)}
                  >
                    <option value="">Select type (optional)</option>
                    {EXTRACTION_TYPES.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                  {instruction.extractionType && (
                    <p className="text-xs text-gray-500 mt-1">
                      {EXTRACTION_TYPES.find(t => t.value === instruction.extractionType)?.description}
                    </p>
                  )}
                </div>
              </div>

              {/* Instruction Preview */}
              {(instruction.contentFocus || instruction.usageInstruction) && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs font-medium text-gray-600 mb-1">Preview:</p>
                  <p className="text-sm text-gray-700">
                    {instruction.contentFocus && `Focus: "${instruction.contentFocus}"`}
                    {instruction.contentFocus && instruction.usageInstruction && ' • '}
                    {instruction.usageInstruction && `Usage: "${instruction.usageInstruction}"`}
                    {instruction.sectionTarget && ` → ${instruction.sectionTarget}`}
                  </p>
                </div>
              )}
            </div>
          ))}

          <div className="border-t border-amber-200 pt-4">
            <p className="text-xs text-amber-600 leading-relaxed">
              💡 <strong>Pro Tip:</strong> เว้นว่างไว้ได้หากต้องการให้ AI ใช้วิจารณญาณเอง 
              หรือกรอกเฉพาะส่วนที่ต้องการควบคุมเป็นพิเศษ
            </p>
          </div>
        </div>
      )}
    </div>
  );
}