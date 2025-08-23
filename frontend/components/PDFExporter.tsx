'use client';

import { useState } from 'react';
import { X, Download, FileText } from 'lucide-react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import toast from 'react-hot-toast';
import { marked } from 'marked';
import { ArticleResponse, UploadedImage } from '../types';
import { formatQualityScore } from '../utils/helpers';

interface PDFExporterProps {
  article: ArticleResponse;
  uploadedImages: Map<string, UploadedImage>;
  onClose: () => void;
  showThai?: boolean;  // Whether to use Thai content
}

export default function PDFExporter({ article, uploadedImages, onClose, showThai = false }: PDFExporterProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [includeImages, setIncludeImages] = useState(true);
  const [includeQualityInfo, setIncludeQualityInfo] = useState(true);
  const [useAIGeneration, setUseAIGeneration] = useState(true); // New option for AI-generated PDF

  const exportToAIPDF = async () => {
    console.log('🚀 Starting AI PDF export...');
    console.log('📄 Article content length:', article.content.length);
    console.log('🖼️ Uploaded images count:', uploadedImages.size);
    console.log('⚙️ Include images:', includeImages);
    console.log('📊 Include quality info:', includeQualityInfo);
    
    try {
      // Get current content based on language selection
      const currentContent = showThai && article.thaiContent ? article.thaiContent : article.content;
      const currentLayout = showThai && article.thaiLayout ? article.thaiLayout : article.layout;
      
      // Prepare content for AI PDF generation
      let processedContent = currentContent;
      
      if (includeImages) {
        // Replace image placeholders with descriptions for AI
        processedContent = processedContent.replace(/!\{\{([^}]+)\}\}\(placeholder\)/g, (match, imageId) => {
          const uploadedImage = uploadedImages.get(imageId);
          const imageSlot = currentLayout.imageSlots.find(slot => slot.id === imageId);
          
          if (uploadedImage) {
            return `[IMAGE: ${imageSlot?.description || uploadedImage.file.name}]`;
          }
          
          return `[IMAGE PLACEHOLDER: ${imageSlot?.description || 'Image position'} - Suggested type: ${imageSlot?.suggestedType || 'image'}]`;
        });
      } else {
        // Remove image placeholders
        processedContent = processedContent.replace(/!\{\{([^}]+)\}\}\(placeholder\)/g, '');
      }

      const requestBody = {
        content: processedContent,
        include_quality_info: includeQualityInfo,
        quality_score: article.qualityScore,
        iterations: article.iterations
      };

      console.log('📦 Request body prepared:', {
        contentLength: processedContent.length,
        include_quality_info: includeQualityInfo,
        quality_score: article.qualityScore,
        iterations: article.iterations
      });

      console.log('🌐 Making API request to /api/generate-pdf...');
      const response = await fetch('/api/generate-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      console.log('📡 API response status:', response.status);
      console.log('📡 API response ok:', response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ API error response:', errorText);
        throw new Error(`PDF generation failed: ${response.status} ${response.statusText} - ${errorText}`);
      }

      console.log('✅ Parsing API response...');
      const result = await response.json();
      console.log('📋 API result keys:', Object.keys(result));
      console.log('📏 pdf_base64 length:', result.pdf_base64?.length || 0);
      
      // Decode AI-enhanced HTML from base64
      console.log('🔓 Decoding base64 HTML...');
      const enhancedHTML = atob(result.pdf_base64);
      console.log('📄 Enhanced HTML length:', enhancedHTML.length);
      
      // Create temporary container with AI-enhanced HTML
      const tempContainer = document.createElement('div');
      tempContainer.innerHTML = enhancedHTML;
      tempContainer.style.position = 'absolute';
      tempContainer.style.left = '-9999px';
      tempContainer.style.top = '0';
      tempContainer.style.width = '800px';
      
      document.body.appendChild(tempContainer);
      
      // Convert to PDF using html2canvas + jsPDF
      const canvas = await html2canvas(tempContainer, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: 'white'
      });

      // Create PDF
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      const imgWidth = 210; // A4 width in mm
      const pageHeight = 295; // A4 height in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;
      let position = 0;

      // Add first page
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      // Add additional pages if needed
      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }

      // Clean up
      document.body.removeChild(tempContainer);

      // Download PDF
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
      pdf.save(`jenosize-article-ai-${timestamp}.pdf`);

      toast.success('AI-enhanced PDF exported successfully!');
      onClose();

    } catch (error) {
      console.error('❌ AI PDF export error:', error);
      console.error('❌ Error type:', typeof error);
      console.error('❌ Error message:', error instanceof Error ? error.message : String(error));
      console.error('❌ Error stack:', error instanceof Error ? error.stack : 'No stack trace');
      toast.error('Failed to generate AI PDF. Falling back to standard export...');
      // Fallback to standard PDF generation
      return exportToStandardPDF();
    }
  };

  const exportToStandardPDF = async () => {
    try {
      // Create a temporary container for PDF content
      const container = document.createElement('div');
      container.style.width = '800px';
      container.style.padding = '40px';
      container.style.fontFamily = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
      container.style.lineHeight = '1.6';
      container.style.color = '#2d3748';
      container.style.backgroundColor = 'white';
      container.style.position = 'absolute';
      container.style.left = '-9999px';
      container.style.top = '0';
      
      document.body.appendChild(container);

      // Add quality info if requested
      if (includeQualityInfo) {
        const qualityDiv = document.createElement('div');
        qualityDiv.style.backgroundColor = '#edf2f7';
        qualityDiv.style.padding = '15px';
        qualityDiv.style.borderRadius = '8px';
        qualityDiv.style.marginBottom = '30px';
        qualityDiv.style.borderLeft = '4px solid #0ea5e9';
        qualityDiv.innerHTML = `
          <strong style="font-size: 14px; color: #1e293b;">Article Quality Score: ${formatQualityScore(article.qualityScore)}</strong><br>
          <small style="color: #64748b;">Generated in ${article.iterations} iteration${article.iterations !== 1 ? 's' : ''} using GPT-4o</small>
        `;
        container.appendChild(qualityDiv);
      }

      // Process Markdown content
      let processedContent = article.content;
      
      if (includeImages) {
        // Replace image placeholders with actual images or styled placeholders
        processedContent = processedContent.replace(/!\{\{([^}]+)\}\}\(placeholder\)/g, (match, imageId) => {
          const uploadedImage = uploadedImages.get(imageId);
          const imageSlot = currentLayout.imageSlots.find(slot => slot.id === imageId);
          
          if (uploadedImage) {
            return `<div style="text-align: center; margin: 20px 0;">
              <img src="${uploadedImage.preview}" alt="${uploadedImage.file.name}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);" />
              <p style="margin-top: 8px; font-size: 0.9em; color: #64748b; font-style: italic;">${imageSlot?.description || uploadedImage.file.name}</p>
            </div>`;
          }
          
          return `<div style="background: #f7fafc; border: 2px dashed #cbd5e0; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
            <div style="font-size: 2em; margin-bottom: 10px;">🖼️</div>
            <strong style="display: block; margin-bottom: 5px;">${imageSlot?.position || 'Image Placeholder'}</strong>
            <em style="display: block; margin-bottom: 5px; color: #64748b;">${imageSlot?.description || 'Upload an image for this position'}</em>
            <small style="color: #64748b;">Suggested type: ${imageSlot?.suggestedType || 'image'}</small>
          </div>`;
        });
      } else {
        // Remove image placeholders
        processedContent = processedContent.replace(/!\{\{([^}]+)\}\}\(placeholder\)/g, '');
      }

      // Convert Markdown to HTML
      const htmlContent = await marked(processedContent, {
        gfm: true,
        breaks: true,
      });

      // Create content div
      const contentDiv = document.createElement('div');
      contentDiv.innerHTML = htmlContent;
      
      // Apply styles to elements
      const applyStyles = (element: HTMLElement) => {
        const tagName = element.tagName.toLowerCase();
        
        switch (tagName) {
          case 'h1':
            Object.assign(element.style, {
              fontSize: '2.5em',
              color: '#1a202c',
              marginBottom: '0.8em',
              fontWeight: '700',
              borderBottom: '2px solid #e2e8f0',
              paddingBottom: '0.5em'
            });
            break;
          case 'h2':
            Object.assign(element.style, {
              fontSize: '1.8em',
              color: '#2d3748',
              marginTop: '2em',
              marginBottom: '0.8em',
              fontWeight: '600'
            });
            break;
          case 'h3':
            Object.assign(element.style, {
              fontSize: '1.4em',
              color: '#4a5568',
              marginTop: '1.5em',
              marginBottom: '0.6em',
              fontWeight: '600'
            });
            break;
          case 'p':
            Object.assign(element.style, {
              marginBottom: '1.2em',
              textAlign: 'justify'
            });
            break;
          case 'strong':
            Object.assign(element.style, {
              fontWeight: '600',
              color: '#1a202c'
            });
            break;
          case 'em':
            Object.assign(element.style, {
              fontStyle: 'italic',
              color: '#4a5568'
            });
            break;
          case 'ul':
          case 'ol':
            Object.assign(element.style, {
              marginBottom: '1.2em',
              paddingLeft: '1.5em'
            });
            break;
          case 'li':
            Object.assign(element.style, {
              marginBottom: '0.5em'
            });
            break;
          case 'table':
            Object.assign(element.style, {
              width: '100%',
              borderCollapse: 'collapse',
              margin: '1.5em 0',
              border: '1px solid #e2e8f0'
            });
            break;
          case 'th':
            Object.assign(element.style, {
              padding: '12px',
              textAlign: 'left',
              borderBottom: '1px solid #e2e8f0',
              backgroundColor: '#f8fafc',
              fontWeight: '600',
              color: '#2d3748'
            });
            break;
          case 'td':
            Object.assign(element.style, {
              padding: '12px',
              textAlign: 'left',
              borderBottom: '1px solid #e2e8f0'
            });
            break;
          case 'blockquote':
            Object.assign(element.style, {
              borderLeft: '4px solid #0ea5e9',
              padding: '1em 1.5em',
              margin: '1.5em 0',
              backgroundColor: '#f0f9ff',
              fontStyle: 'italic',
              color: '#0c4a6e'
            });
            break;
        }
        
        // Apply styles to children
        Array.from(element.children).forEach(child => {
          if (child instanceof HTMLElement) {
            applyStyles(child);
          }
        });
      };

      applyStyles(contentDiv);
      container.appendChild(contentDiv);

      // Convert to canvas
      const canvas = await html2canvas(container, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: 'white',
        width: 800,
        height: container.scrollHeight
      });

      // Create PDF
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      const imgWidth = 210; // A4 width in mm
      const pageHeight = 295; // A4 height in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;
      let position = 0;

      // Add first page
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      // Add additional pages if needed
      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }

      // Clean up
      document.body.removeChild(container);

      // Download PDF
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
      pdf.save(`jenosize-article-${timestamp}.pdf`);
      
      toast.success('PDF exported successfully!');
      onClose();
      
    } catch (error) {
      console.error('PDF export error:', error);
      toast.error('Failed to export PDF. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const exportToPDF = async () => {
    setIsExporting(true);
    
    try {
      if (useAIGeneration) {
        await exportToAIPDF();
      } else {
        await exportToStandardPDF();
      }
    } catch (error) {
      console.error('PDF export error:', error);
      toast.error('Failed to export PDF. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 p-8">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="icon-wrapper">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-navy-800">Export to PDF</h3>
              <p className="text-sm text-gray-600 mt-1">Create a professional PDF document</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-xl transition-colors"
            disabled={isExporting}
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <div className="space-y-6 mb-8">
          <div className="flex items-center gap-4 p-4 bg-gradient-to-r from-sky-50 to-navy-50 border border-sky-200 rounded-xl">
            <input
              type="checkbox"
              id="useAIGeneration"
              checked={useAIGeneration}
              onChange={(e) => setUseAIGeneration(e.target.checked)}
              disabled={isExporting}
              className="w-5 h-5 text-sky-600 rounded-lg focus:ring-sky-500"
            />
            <label htmlFor="useAIGeneration" className="text-sm font-medium text-gray-700 flex-1">
              <span className="font-semibold text-sky-700">✨ AI-Enhanced PDF Generation</span>
              <span className="block text-xs text-gray-600 mt-1">Better layout, formatting, and professional quality</span>
            </label>
          </div>

          <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl">
            <input
              type="checkbox"
              id="includeImages"
              checked={includeImages}
              onChange={(e) => setIncludeImages(e.target.checked)}
              disabled={isExporting}
              className="w-5 h-5 text-sky-600 rounded-lg focus:ring-sky-500"
            />
            <label htmlFor="includeImages" className="text-sm font-medium text-gray-700 flex-1">
              Include image placeholders and uploaded images
            </label>
          </div>

          <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl">
            <input
              type="checkbox"
              id="includeQuality"
              checked={includeQualityInfo}
              onChange={(e) => setIncludeQualityInfo(e.target.checked)}
              disabled={isExporting}
              className="w-5 h-5 text-sky-600 rounded-lg focus:ring-sky-500"
            />
            <label htmlFor="includeQuality" className="text-sm font-medium text-gray-700 flex-1">
              Include quality score and generation info
            </label>
          </div>

          <div className="bg-gradient-to-r from-sky-50 to-navy-50 p-6 rounded-2xl border border-sky-200">
            <h4 className="text-lg font-semibold text-dark-navy-800 mb-4">Export Summary</h4>
            <div className="grid grid-cols-2 gap-6 text-sm">
              <div>
                <span className="font-medium text-navy-600">Quality Score:</span>
                <div className="text-xl font-bold text-sky-600">{formatQualityScore(article.qualityScore)}</div>
              </div>
              <div>
                <span className="font-medium text-navy-600">Images:</span>
                <div className="text-xl font-bold text-dark-navy-700">{uploadedImages.size} of {article.layout.imageSlots.length}</div>
              </div>
              <div className="col-span-2">
                <span className="font-medium text-navy-600">Sections:</span>
                <div className="text-xl font-bold text-dark-navy-700">{article.layout.sections.length} main sections</div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            disabled={isExporting}
            className="btn-secondary flex-1"
          >
            Cancel
          </button>
          <button
            onClick={exportToPDF}
            disabled={isExporting}
            className="btn-primary flex-1 flex items-center justify-center gap-2"
          >
            {isExporting ? (
              <>
                <div className="loading-spinner w-4 h-4" />
                Exporting...
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                Export PDF
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}