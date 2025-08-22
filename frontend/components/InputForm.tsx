'use client';

import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Link, Target, Building, Hash, Plus, X, MessageSquare } from 'lucide-react';
import toast from 'react-hot-toast';
import { ArticleRequest } from '../types';
import { convertFileToBase64, validateUrl } from '../utils/helpers';

interface InputFormProps {
  onSubmit: (request: ArticleRequest) => void;
  isGenerating: boolean;
}

export default function InputForm({ onSubmit, isGenerating }: InputFormProps) {
  const [formData, setFormData] = useState<ArticleRequest>({});
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [sourceUrls, setSourceUrls] = useState<string[]>(['']);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
    },
    multiple: false,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setUploadedFile(acceptedFiles[0]);
        toast.success('PDF uploaded successfully');
      }
    },
    onDropRejected: () => {
      toast.error('Please upload a valid PDF file');
    },
  });

  const handleInputChange = (field: keyof ArticleRequest, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value || undefined,
    }));
  };

  const handleUrlChange = (index: number, value: string) => {
    const newUrls = [...sourceUrls];
    newUrls[index] = value;
    setSourceUrls(newUrls);
  };

  const addUrlField = () => {
    if (sourceUrls.length < 5) {
      setSourceUrls([...sourceUrls, '']);
    } else {
      toast.error('Maximum 5 URLs allowed');
    }
  };

  const removeUrlField = (index: number) => {
    if (sourceUrls.length > 1) {
      const newUrls = sourceUrls.filter((_, i) => i !== index);
      setSourceUrls(newUrls);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate URLs
    const validUrls = sourceUrls.filter(url => url.trim() !== '');
    const invalidUrls = validUrls.filter(url => !validateUrl(url));
    
    if (invalidUrls.length > 0) {
      toast.error(`Please enter valid URLs. Invalid: ${invalidUrls.join(', ')}`);
      return;
    }

    let pdfBase64: string | undefined;
    if (uploadedFile) {
      try {
        pdfBase64 = await convertFileToBase64(uploadedFile);
      } catch (error) {
        toast.error('Failed to process PDF file');
        return;
      }
    }

    const request: ArticleRequest = {
      ...formData,
      pdfBase64,
      sourceUrls: validUrls.length > 0 ? validUrls : undefined,
    };

    onSubmit(request);
  };

  const clearForm = () => {
    setFormData({});
    setUploadedFile(null);
    setSourceUrls(['']);
  };

  return (
    <div className="card">
      <div className="mb-8">
        <div className="flex items-center space-x-4 mb-6">
          <div className="icon-wrapper w-14 h-14">
            <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
            </svg>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-dark-navy-800">
              Article Generation
            </h2>
            <p className="text-navy-600 font-medium">Configure your content parameters</p>
          </div>
        </div>
        <div className="bg-gradient-to-r from-sky-50 to-navy-50 rounded-2xl p-6 mb-8">
          <p className="text-gray-700 leading-relaxed">
            Fill in any combination of fields below to generate your article. All fields are optional, giving you complete flexibility in content creation.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Topic Category */}
          <div>
            <label className="flex items-center text-sm font-semibold text-dark-navy-700 mb-3">
              <div className="w-5 h-5 bg-sky-100 rounded-lg flex items-center justify-center mr-3">
                <Target className="w-3 h-3 text-sky-600" />
              </div>
              Topic Category
            </label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g., Digital Transformation, AI, Sustainability"
              value={formData.topicCategory || ''}
              onChange={(e) => handleInputChange('topicCategory', e.target.value)}
            />
          </div>

          {/* Industry */}
          <div>
            <label className="flex items-center text-sm font-semibold text-dark-navy-700 mb-3">
              <div className="w-5 h-5 bg-sky-100 rounded-lg flex items-center justify-center mr-3">
                <Building className="w-3 h-3 text-sky-600" />
              </div>
              Industry
            </label>
            <select
              className="input-field"
              value={formData.industry || ''}
              onChange={(e) => handleInputChange('industry', e.target.value)}
            >
              <option value="">Select industry (optional)</option>
              <option value="Technology">Technology</option>
              <option value="Healthcare">Healthcare</option>
              <option value="Finance">Finance</option>
              <option value="Retail">Retail</option>
              <option value="Manufacturing">Manufacturing</option>
              <option value="Education">Education</option>
              <option value="Real Estate">Real Estate</option>
              <option value="Energy">Energy</option>
              <option value="Transportation">Transportation</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>

        {/* Target Audience */}
        <div>
          <label className="flex items-center text-sm font-semibold text-dark-navy-700 mb-3">
            <div className="w-5 h-5 bg-sky-100 rounded-lg flex items-center justify-center mr-3">
              <Target className="w-3 h-3 text-sky-600" />
            </div>
            Target Audience
          </label>
          <input
            type="text"
            className="input-field"
            placeholder="e.g., C-level executives, Small business owners, Tech professionals"
            value={formData.targetAudience || ''}
            onChange={(e) => handleInputChange('targetAudience', e.target.value)}
          />
        </div>

        {/* Source URLs */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="flex items-center text-sm font-semibold text-dark-navy-700">
              <div className="w-5 h-5 bg-sky-100 rounded-lg flex items-center justify-center mr-3">
                <Link className="w-3 h-3 text-sky-600" />
              </div>
              Source URLs
              <span className="text-xs text-gray-500 ml-2">(Max 5)</span>
            </label>
            {sourceUrls.length < 5 && (
              <button
                type="button"
                onClick={addUrlField}
                className="flex items-center text-xs text-sky-600 hover:text-sky-700 transition-colors"
              >
                <Plus className="w-3 h-3 mr-1" />
                Add URL
              </button>
            )}
          </div>
          
          <div className="space-y-3">
            {sourceUrls.map((url, index) => (
              <div key={index} className="flex items-center gap-2">
                <input
                  type="url"
                  className="input-field flex-1"
                  placeholder={`https://example.com/source-${index + 1}`}
                  value={url}
                  onChange={(e) => handleUrlChange(index, e.target.value)}
                />
                {sourceUrls.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeUrlField(index)}
                    className="p-2 text-red-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
          
          <p className="text-xs text-gray-500 mt-2 ml-8">
            Provide URLs to scrape content from multiple sources. The AI will use different sources for different sections of the article.
          </p>
        </div>

        {/* PDF Upload */}
        <div>
          <label className="flex items-center text-sm font-semibold text-dark-navy-700 mb-3">
            <div className="w-5 h-5 bg-sky-100 rounded-lg flex items-center justify-center mr-3">
              <FileText className="w-3 h-3 text-sky-600" />
            </div>
            Upload Document (PDF)
          </label>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300 ${
              isDragActive
                ? 'border-sky-400 bg-sky-50 shadow-lg'
                : 'border-navy-300 hover:border-sky-400 hover:bg-sky-50/30'
            }`}
          >
            <input {...getInputProps()} />
            <div className={`w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center ${
              uploadedFile ? 'bg-sky-100' : 'bg-navy-100'
            }`}>
              <Upload className={`w-8 h-8 ${uploadedFile ? 'text-sky-600' : 'text-navy-400'}`} />
            </div>
            {uploadedFile ? (
              <div>
                <p className="text-lg font-semibold text-dark-navy-800 mb-1">{uploadedFile.name}</p>
                <p className="text-sm text-navy-500">
                  {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB • PDF Document
                </p>
              </div>
            ) : (
              <div>
                <p className="text-lg font-medium text-navy-700 mb-2">
                  {isDragActive
                    ? 'Drop the PDF here...'
                    : 'Drag & drop a PDF here, or click to select'}
                </p>
                <p className="text-sm text-navy-500">PDF files only • Advanced OCR processing</p>
              </div>
            )}
          </div>
        </div>

        {/* SEO Keywords */}
        <div>
          <label className="flex items-center text-sm font-semibold text-dark-navy-700 mb-3">
            <div className="w-5 h-5 bg-sky-100 rounded-lg flex items-center justify-center mr-3">
              <Hash className="w-3 h-3 text-sky-600" />
            </div>
            SEO Keywords
          </label>
          <input
            type="text"
            className="input-field"
            placeholder="future of work, digital transformation, business innovation"
            value={formData.seoKeywords || ''}
            onChange={(e) => handleInputChange('seoKeywords', e.target.value)}
          />
          <p className="text-xs text-gray-500 mt-2 ml-8">
            Comma-separated keywords to optimize the article for search engines
          </p>
        </div>

        {/* Custom Prompt */}
        <div>
          <label className="flex items-center text-sm font-semibold text-dark-navy-700 mb-3">
            <div className="w-5 h-5 bg-sky-100 rounded-lg flex items-center justify-center mr-3">
              <MessageSquare className="w-3 h-3 text-sky-600" />
            </div>
            Custom Instructions
            <span className="text-xs text-gray-500 ml-2">(Optional)</span>
          </label>
          <textarea
            className="input-field resize-y min-h-[100px]"
            placeholder="Add specific instructions for the AI, such as: focus on case studies, include more statistics, emphasize practical implementation steps..."
            value={formData.customPrompt || ''}
            onChange={(e) => handleInputChange('customPrompt', e.target.value)}
          />
          <p className="text-xs text-gray-500 mt-2 ml-8">
            Provide specific instructions to customize how the AI generates your article
          </p>
        </div>

        {/* Submit Buttons */}
        <div className="flex gap-4 pt-8">
          <button
            type="submit"
            disabled={isGenerating}
            className={`btn-primary flex-1 flex items-center justify-center gap-3 text-lg ${
              isGenerating ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {isGenerating ? (
              <>
                <div className="loading-spinner w-5 h-5 border-white" />
                Generating Article...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Generate Article
              </>
            )}
          </button>
          
          <button
            type="button"
            onClick={clearForm}
            disabled={isGenerating}
            className="btn-secondary"
          >
            Clear Form
          </button>
        </div>
      </form>
    </div>
  );
}