'use client';

import { useState } from 'react';
import { Download, Star, RotateCcw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
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

  const handleImageUpload = (slotId: string, image: UploadedImage) => {
    setUploadedImages(prev => new Map(prev.set(slotId, image)));
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
  };

  const downloadHTML = () => {
    const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Jenosize Article</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
    h1 { color: #1a202c; font-size: 2.5em; margin-bottom: 0.5em; }
    h2 { color: #2d3748; font-size: 1.8em; margin-top: 2em; margin-bottom: 0.5em; }
    h3 { color: #4a5568; font-size: 1.3em; margin-top: 1.5em; margin-bottom: 0.5em; }
    p { color: #2d3748; margin-bottom: 1em; }
    .image-placeholder { background: #f7fafc; border: 2px dashed #cbd5e0; padding: 20px; text-align: center; margin: 20px 0; }
    .quality-info { background: #edf2f7; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
  </style>
</head>
<body>
  <div class="quality-info">
    <strong>Article Quality Score: ${formatQualityScore(article.qualityScore)}</strong>
    (Generated in ${article.iterations} iteration${article.iterations !== 1 ? 's' : ''})
  </div>
  ${article.content}
  
  ${article.layout.imageSlots.map(slot => `
    <div class="image-placeholder">
      <strong>${slot.position}</strong><br>
      <em>${slot.description}</em><br>
      <small>Suggested type: ${slot.suggestedType}</small>
    </div>
  `).join('')}
</body>
</html>`;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'jenosize-article.html';
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
        <div 
          className="article-content"
          dangerouslySetInnerHTML={{ __html: article.content }}
        />
      </div>

      {/* Image Upload Section */}
      {article.layout.imageSlots.length > 0 && (
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
              </h3>
              <p className="text-gray-600 text-lg">
                Upload images for the suggested placements below to enhance your article visually and professionally.
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {article.layout.imageSlots.map(slot => (
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

      {/* PDF Exporter Modal */}
      {showPDFExporter && (
        <PDFExporter
          article={article}
          uploadedImages={uploadedImages}
          onClose={() => setShowPDFExporter(false)}
        />
      )}
    </div>
  );
}