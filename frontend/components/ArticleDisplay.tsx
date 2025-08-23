'use client';

import { useState } from 'react';
import { Download, Star, RotateCcw, FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { marked } from 'marked';
import { ArticleResponse, UploadedImage } from '../types';
import { formatQualityScore, getQualityColor } from '../utils/helpers';
import ImageUploader from './ImageUploader';
import PDFExporter from './PDFExporter';

interface ArticleDisplayProps {
  article: ArticleResponse;
  onRegenerateRequest: () => void;
}

export default function ArticleDisplay({ article, onRegenerateRequest }: ArticleDisplayProps) {
  const [uploadedImages, setUploadedImages] = useState<Map<string, UploadedImage>>(new Map());
  const [showPDFExporter, setShowPDFExporter] = useState(false);
  const [contentKey, setContentKey] = useState(0); // Force re-render when images change
  const [showThai, setShowThai] = useState(false); // Toggle between EN/TH

  // Debug: Log if Thai content exists
  console.log('ArticleDisplay - Has Thai content:', !!article.thaiContent);
  console.log('ArticleDisplay - Thai content length:', article.thaiContent?.length || 0);

  const handleImageUpload = (slotId: string, image: UploadedImage) => {
    setUploadedImages(prev => new Map(prev.set(slotId, image)));
    setContentKey(prev => prev + 1); // Force re-render
  };

  const handleImageRemove = (slotId: string) => {
    setUploadedImages(prev => {
      const newMap = new Map(prev);
      const removedImage = newMap.get(slotId);
      if (removedImage) {
        URL.revokeObjectURL(removedImage.preview);
      }
      newMap.delete(slotId);
      return newMap;
    });
    setContentKey(prev => prev + 1); // Force re-render
  };

  const downloadHTML = () => {
    // Get current content based on language selection
    const currentContent = showThai && article.thaiContent ? article.thaiContent : article.content;
    
    // Process Markdown and handle image placeholders
    const processedContent = currentContent.replace(/!\{\{([^}]+)\}\}\(placeholder\)/g, (match, imageId) => {
      const uploadedImage = uploadedImages.get(imageId);
      const currentLayout = showThai && article.thaiLayout ? article.thaiLayout : article.layout;
      const imageSlot = currentLayout.imageSlots.find(slot => slot.id === imageId);
      
      if (uploadedImage) {
        return `<div class="uploaded-image">
          <img src="${uploadedImage.preview}" alt="${uploadedImage.file.name}" />
          <p class="image-caption">${imageSlot?.description || uploadedImage.file.name}</p>
        </div>`;
      }
      
      return `<div class="image-placeholder">
        <div class="placeholder-icon">🖼️</div>
        <strong>${imageSlot?.position || 'Image Placeholder'}</strong><br>
        <em>${imageSlot?.description || 'Upload an image for this position'}</em><br>
        <small>Suggested type: ${imageSlot?.suggestedType || 'image'}</small>
      </div>`;
    });

    // Convert Markdown to HTML
    const htmlContent = marked(processedContent, {
      gfm: true,
      breaks: true,
    });

    const fullHtmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Jenosize Article</title>
  <style>
    body { 
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
      max-width: 800px; 
      margin: 0 auto; 
      padding: 40px 20px; 
      line-height: 1.6; 
      color: #2d3748; 
      background-color: #ffffff;
    }
    h1 { 
      color: #1a202c; 
      font-size: 2.5em; 
      margin-bottom: 0.8em; 
      font-weight: 700; 
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 0.5em;
    }
    h2 { 
      color: #2d3748; 
      font-size: 1.8em; 
      margin-top: 2em; 
      margin-bottom: 0.8em; 
      font-weight: 600; 
    }
    h3 { 
      color: #4a5568; 
      font-size: 1.4em; 
      margin-top: 1.5em; 
      margin-bottom: 0.6em; 
      font-weight: 600; 
    }
    h4 { 
      color: #4a5568; 
      font-size: 1.2em; 
      margin-top: 1.2em; 
      margin-bottom: 0.5em; 
      font-weight: 600; 
    }
    p { 
      margin-bottom: 1.2em; 
      text-align: justify;
    }
    strong { 
      font-weight: 600; 
      color: #1a202c; 
    }
    em { 
      font-style: italic; 
      color: #4a5568; 
    }
    ul, ol { 
      margin-bottom: 1.2em; 
      padding-left: 1.5em; 
    }
    li { 
      margin-bottom: 0.5em; 
    }
    table { 
      width: 100%; 
      border-collapse: collapse; 
      margin: 1.5em 0; 
      border: 1px solid #e2e8f0;
    }
    th, td { 
      padding: 12px; 
      text-align: left; 
      border-bottom: 1px solid #e2e8f0; 
    }
    th { 
      background-color: #f8fafc; 
      font-weight: 600; 
      color: #2d3748; 
    }
    blockquote { 
      border-left: 4px solid #0ea5e9; 
      padding: 1em 1.5em; 
      margin: 1.5em 0; 
      background-color: #f0f9ff; 
      font-style: italic; 
      color: #0c4a6e;
    }
    .image-placeholder { 
      background: #f7fafc; 
      border: 2px dashed #cbd5e0; 
      padding: 20px; 
      text-align: center; 
      margin: 20px 0; 
      border-radius: 8px; 
    }
    .placeholder-icon {
      font-size: 2em;
      margin-bottom: 10px;
    }
    .uploaded-image {
      text-align: center;
      margin: 20px 0;
    }
    .uploaded-image img {
      max-width: 100%;
      height: auto;
      border-radius: 8px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .image-caption {
      margin-top: 8px;
      font-size: 0.9em;
      color: #64748b;
      font-style: italic;
    }
    .quality-info { 
      background: #edf2f7; 
      padding: 15px; 
      border-radius: 8px; 
      margin-bottom: 30px; 
      border-left: 4px solid #0ea5e9; 
    }
    code {
      background-color: #f1f5f9;
      padding: 2px 4px;
      border-radius: 4px;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
      font-size: 0.9em;
    }
    pre {
      background-color: #f1f5f9;
      padding: 16px;
      border-radius: 8px;
      overflow-x: auto;
      margin: 1.5em 0;
    }
    pre code {
      background-color: transparent;
      padding: 0;
    }
  </style>
</head>
<body>
  <div class="quality-info">
    <strong>Article Quality Score: ${formatQualityScore(article.qualityScore)}</strong><br>
    <small>Generated in ${article.iterations} iteration${article.iterations !== 1 ? 's' : ''} using GPT-4o</small>
  </div>
  ${htmlContent}
</body>
</html>`;

    const blob = new Blob([fullHtmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `jenosize-article${showThai && article.thaiContent ? '-thai' : ''}.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const downloadText = () => {
    // Get current content based on language selection
    const currentContent = showThai && article.thaiContent ? article.thaiContent : article.content;
    const currentLayout = showThai && article.thaiLayout ? article.thaiLayout : article.layout;
    
    // Convert Markdown to plain text
    const textContent = currentContent
      .replace(/!\{\{([^}]+)\}\}\(placeholder\)/g, (match, imageId) => {
        const imageSlot = currentLayout.imageSlots.find(slot => slot.id === imageId);
        return `[Image: ${imageSlot?.description || 'Image placeholder'}]`;
      })
      .replace(/#{1,6}\s+/g, '') // Remove heading markers
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold markers
      .replace(/\*(.*?)\*/g, '$1') // Remove italic markers
      .replace(/`(.*?)`/g, '$1') // Remove code markers
      .replace(/>\s+/g, '') // Remove blockquote markers
      .replace(/^\s*[-*+]\s+/gm, '• ') // Convert list markers
      .replace(/^\s*\d+\.\s+/gm, (match) => `${match.trim()} `) // Keep numbered lists
      .trim();

    const fullTextContent = `
Jenosize Article
Quality Score: ${formatQualityScore(article.qualityScore)}
Generated in ${article.iterations} iteration${article.iterations !== 1 ? 's' : ''} using GPT-4o

================================================================================

${textContent}

================================================================================
Generated by Jenosize AI Article Generator
`.trim();

    const blob = new Blob([fullTextContent], { type: 'text/plain; charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `jenosize-article${showThai && article.thaiContent ? '-thai' : ''}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Article Header */}
      <div className="card-navy">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-8">
          <div className="flex flex-col lg:flex-row lg:items-center gap-8">
            <div className="flex items-center gap-4">
              <div className="icon-wrapper bg-gradient-to-br from-yellow-500 to-orange-500 w-16 h-16">
                <Star className="w-8 h-8" />
              </div>
              <div>
                <div className="text-sm font-medium text-sky-300 mb-1">Quality Score</div>
                <div className={`text-3xl font-bold text-white`}>
                  {formatQualityScore(article.qualityScore)}
                </div>
              </div>
            </div>
            <div className="text-sky-200">
              <div className="text-sm font-semibold mb-1">Generation Stats</div>
              <div className="text-sm">
                {article.iterations} iteration{article.iterations !== 1 ? 's' : ''} • AI-optimized content
              </div>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-3">
            {/* Thai/English Toggle */}
            {article.thaiContent && (
              <div className="flex bg-white/10 rounded-lg p-1">
                <button
                  onClick={() => setShowThai(false)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    !showThai 
                      ? 'bg-white text-navy-700 shadow-sm' 
                      : 'text-white hover:bg-white/10'
                  }`}
                >
                  🇺🇸 EN
                </button>
                <button
                  onClick={() => setShowThai(true)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    showThai 
                      ? 'bg-white text-navy-700 shadow-sm' 
                      : 'text-white hover:bg-white/10'
                  }`}
                >
                  🇹🇭 TH
                </button>
              </div>
            )}
            
            <button
              onClick={onRegenerateRequest}
              className="btn-secondary flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 16h4.01M12 12h-4.01M8 16H4.01M12 12v-4.01M12 12V8.01" />
              </svg>
              Create New Article
            </button>
            <button
              onClick={downloadText}
              className="btn-secondary flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              Download Text
            </button>
            <button
              onClick={downloadHTML}
              className="btn-secondary flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Download HTML
            </button>
            <button
              onClick={() => setShowPDFExporter(true)}
              className="btn-primary flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export PDF
            </button>
          </div>
        </div>
      </div>

      {/* Article Content */}
      <div className="card">
        <div className="article-content prose prose-lg max-w-none">
          <ReactMarkdown 
            key={contentKey}
            remarkPlugins={[remarkGfm]}
            children={showThai && article.thaiContent ? article.thaiContent : article.content}
            components={{
              img: ({ node, ...props }) => {
                const { src, alt } = props;
                // Handle image placeholders
                if (src === 'placeholder' && alt?.startsWith('{{') && alt?.endsWith('}}')) {
                  const imageId = alt.slice(2, -2);
                  const uploadedImage = uploadedImages.get(imageId);
                  const currentLayout = showThai && article.thaiLayout ? article.thaiLayout : article.layout;
                  const imageSlot = currentLayout.imageSlots.find(slot => slot.id === imageId);
                  
                  if (uploadedImage) {
                    return (
                      <div className="my-8 text-center">
                        <img
                          src={uploadedImage.preview}
                          alt={uploadedImage.file.name}
                          className="mx-auto max-w-full h-auto rounded-lg shadow-lg"
                        />
                        <p className="text-sm text-gray-500 mt-2 italic">{imageSlot?.description || uploadedImage.file.name}</p>
                        <div className="mt-2 flex justify-center">
                          <button
                            onClick={() => handleImageRemove(imageId)}
                            className="text-red-500 hover:text-red-700 text-xs px-2 py-1 rounded hover:bg-red-50 transition-colors"
                          >
                            Remove Image
                          </button>
                        </div>
                      </div>
                    );
                  }
                  
                  // Show placeholder if no image uploaded
                  return (
                    <div className="my-8 p-6 border-2 border-dashed border-sky-300 rounded-lg text-center bg-sky-50 hover:bg-sky-100 transition-colors cursor-pointer">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) {
                            const preview = URL.createObjectURL(file);
                            handleImageUpload(imageId, {
                              id: imageId,
                              file,
                              preview,
                              slotId: imageId
                            });
                          }
                        }}
                        className="hidden"
                        id={`inline-upload-${imageId}`}
                      />
                      <label
                        htmlFor={`inline-upload-${imageId}`}
                        className="cursor-pointer block text-sky-600 hover:text-sky-700 transition-colors"
                      >
                        <svg className="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        <p className="font-medium text-sky-700">Click to Upload Image</p>
                        <p className="text-sm text-sky-600 mt-1">{imageSlot?.description || 'Upload an image for this position'}</p>
                        <p className="text-xs text-sky-500 mt-2">Suggested: {imageSlot?.suggestedType || 'image'}</p>
                      </label>
                    </div>
                  );
                }
                
                return <img {...props} className="mx-auto max-w-full h-auto rounded-lg shadow-lg" />;
              },
              table: ({ children }) => (
                <div className="overflow-x-auto my-6">
                  <table className="min-w-full divide-y divide-gray-200 border border-gray-300">
                    {children}
                  </table>
                </div>
              ),
              th: ({ children }) => (
                <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 border-b border-gray-200">
                  {children}
                </td>
              ),
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-sky-500 pl-6 py-2 my-6 bg-sky-50 italic text-sky-800">
                  {children}
                </blockquote>
              ),
            }}
          >
            {article.content}
          </ReactMarkdown>
        </div>
      </div>

      {/* Image Upload Section */}
      {((showThai && article.thaiLayout ? article.thaiLayout : article.layout).imageSlots.length > 0) && (
        <div className="card">
          <div className="flex items-center space-x-4 mb-8">
            <div className="icon-wrapper w-16 h-16">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h3 className="text-3xl font-bold text-dark-navy-800 mb-2">
                Enhance with Images
                {showThai && article.thaiContent && (
                  <span className="ml-3 text-xl text-orange-600 font-medium">(Thai Version)</span>
                )}
              </h3>
              <p className="text-gray-600 text-lg">
                Upload images for the suggested placements below to enhance your article visually and professionally.
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {(showThai && article.thaiLayout ? article.thaiLayout : article.layout).imageSlots.map(slot => (
              <ImageUploader
                key={slot.id}
                imageSlot={slot}
                onImageUpload={handleImageUpload}
                onImageRemove={handleImageRemove}
                uploadedImage={uploadedImages.get(slot.id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Source Usage Details - Only show if there are actual sources with URLs */}
      {article.sourceUsageDetails && 
       article.sourceUsageDetails.length > 0 && 
       article.sourceUsageDetails.some(detail => detail.sourceUrl && detail.sourceUrl.trim() !== '') && (
        <div className="card">
          <div className="flex items-center space-x-4 mb-8">
            <div className="icon-wrapper w-16 h-16">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
            </div>
            <div>
              <h3 className="text-3xl font-bold text-dark-navy-800 mb-2">
                Source Content Usage
              </h3>
              <p className="text-gray-600 text-lg">
                Detailed breakdown of how content from each source was integrated into the article.
              </p>
            </div>
          </div>
          
          <div className="space-y-6">
            {article.sourceUsageDetails.map((detail, index) => (
              <div key={index} className="bg-gray-50 border border-gray-200 rounded-xl p-6">
                <div className="flex items-start justify-between mb-4">
                  <h4 className="text-lg font-bold text-dark-navy-800">{detail.sourceTitle}</h4>
                  <a 
                    href={detail.sourceUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sky-600 hover:text-sky-700 text-sm"
                  >
                    View Source →
                  </a>
                </div>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h5 className="font-semibold text-navy-700 mb-2">Content Used:</h5>
                    <p className="text-sm text-gray-700 bg-white p-3 rounded-lg border">
                      "{detail.contentUsed}"
                    </p>
                  </div>
                  
                  <div>
                    <h5 className="font-semibold text-navy-700 mb-2">Usage Location:</h5>
                    <p className="text-sm text-gray-700 bg-white p-3 rounded-lg border">
                      {detail.usageLocation}
                    </p>
                  </div>
                </div>
                
                <div className="mt-4">
                  <h5 className="font-semibold text-navy-700 mb-2">Purpose & Transformation:</h5>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Why this content was selected:</p>
                      <p className="text-sm text-gray-700">{detail.usagePurpose}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">How it was adapted:</p>
                      <p className="text-sm text-gray-700">{detail.transformation}</p>
                    </div>
                  </div>
                </div>
                
                {/* URL Instruction Compliance */}
                {(detail.instructionCompliance || detail.extractionTypeUsed) && (
                  <div className="mt-4 bg-amber-50 border border-amber-200 rounded-lg p-4">
                    <h5 className="font-semibold text-amber-700 mb-3 flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      URL Instructions Compliance
                    </h5>
                    <div className="space-y-3">
                      {detail.extractionTypeUsed && (
                        <div>
                          <p className="text-xs text-amber-600 mb-1">Content Type Extracted:</p>
                          <div className="flex items-center gap-2">
                            <span className="bg-amber-100 text-amber-700 px-2 py-1 rounded-full text-xs font-medium">
                              {detail.extractionTypeUsed.replace('_', ' ').toUpperCase()}
                            </span>
                          </div>
                        </div>
                      )}
                      {detail.instructionCompliance && (
                        <div>
                          <p className="text-xs text-amber-600 mb-1">How instructions were followed:</p>
                          <p className="text-sm text-amber-700">{detail.instructionCompliance}</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Article Analysis */}
      {article.analysis && (
        <div className="card">
          <div className="flex items-center space-x-4 mb-8">
            <div className="icon-wrapper w-16 h-16">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h3 className="text-3xl font-bold text-dark-navy-800 mb-2">
                Article Analysis & Feedback
              </h3>
              <p className="text-gray-600 text-lg">
                AI-generated assessment of strengths, weaknesses, and recommendations for improvement.
              </p>
            </div>
          </div>
          
          {/* Summary */}
          <div className="bg-navy-50 border border-navy-200 rounded-xl p-6 mb-6">
            <h4 className="text-lg font-bold text-dark-navy-800 mb-3">Overall Assessment</h4>
            <p className="text-navy-700 leading-relaxed">{article.analysis.summary}</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            {/* Strengths */}
            <div className="bg-green-50 border border-green-200 rounded-xl p-6">
              <h4 className="text-lg font-bold text-green-800 mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Strengths
              </h4>
              <ul className="space-y-2">
                {article.analysis.strengths.map((strength, index) => (
                  <li key={index} className="text-sm text-green-700 flex items-start">
                    <span className="text-green-500 mr-2">•</span>
                    {strength}
                  </li>
                ))}
              </ul>
            </div>
            
            {/* Weaknesses */}
            <div className="bg-orange-50 border border-orange-200 rounded-xl p-6">
              <h4 className="text-lg font-bold text-orange-800 mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                Areas for Improvement
              </h4>
              <ul className="space-y-2">
                {article.analysis.weaknesses.map((weakness, index) => (
                  <li key={index} className="text-sm text-orange-700 flex items-start">
                    <span className="text-orange-500 mr-2">•</span>
                    {weakness}
                  </li>
                ))}
              </ul>
            </div>
            
            {/* Recommendations */}
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <h4 className="text-lg font-bold text-blue-800 mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                Recommendations
              </h4>
              <ul className="space-y-2">
                {article.analysis.recommendations.map((recommendation, index) => (
                  <li key={index} className="text-sm text-blue-700 flex items-start">
                    <span className="text-blue-500 mr-2">•</span>
                    {recommendation}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* PDF Exporter Modal */}
      {showPDFExporter && (
        <PDFExporter
          article={article}
          uploadedImages={uploadedImages}
          onClose={() => setShowPDFExporter(false)}
          showThai={showThai}
        />
      )}
    </div>
  );
}