'use client';

import { useState } from 'react';
import { X, Download, FileText } from 'lucide-react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import toast from 'react-hot-toast';
import { ArticleResponse, UploadedImage } from '../types';
import { formatQualityScore } from '../utils/helpers';

interface PDFExporterProps {
  article: ArticleResponse;
  uploadedImages: Map<string, UploadedImage>;
  onClose: () => void;
}

export default function PDFExporter({ article, uploadedImages, onClose }: PDFExporterProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [includeImages, setIncludeImages] = useState(true);
  const [includeQualityInfo, setIncludeQualityInfo] = useState(true);

  const exportToPDF = async () => {
    setIsExporting(true);
    
    try {
      // Create a temporary container for PDF content
      const container = document.createElement('div');
      container.style.width = '800px';
      container.style.padding = '40px';
      container.style.fontFamily = 'Arial, sans-serif';
      container.style.lineHeight = '1.6';
      container.style.color = '#333';
      container.style.backgroundColor = 'white';
      container.style.position = 'absolute';
      container.style.left = '-9999px';
      container.style.top = '0';
      
      document.body.appendChild(container);

      // Add quality info if requested
      if (includeQualityInfo) {
        const qualityDiv = document.createElement('div');
        qualityDiv.style.backgroundColor = '#f8f9fa';
        qualityDiv.style.padding = '15px';
        qualityDiv.style.borderRadius = '8px';
        qualityDiv.style.marginBottom = '30px';
        qualityDiv.style.border = '1px solid #e9ecef';
        qualityDiv.innerHTML = `
          <strong>Article Quality Score: ${formatQualityScore(article.qualityScore)}</strong><br>
          <small>Generated in ${article.iterations} iteration${article.iterations !== 1 ? 's' : ''}</small>
        `;
        container.appendChild(qualityDiv);
      }

      // Add article content
      const contentDiv = document.createElement('div');
      contentDiv.innerHTML = article.content;
      
      // Style the content
      const headings = contentDiv.querySelectorAll('h1, h2, h3, h4, h5, h6');
      headings.forEach((heading, index) => {
        const element = heading as HTMLElement;
        if (heading.tagName === 'H1') {
          element.style.fontSize = '2.5em';
          element.style.color = '#1a202c';
          element.style.marginBottom = '0.5em';
          element.style.borderBottom = '2px solid #e2e8f0';
          element.style.paddingBottom = '0.5em';
        } else if (heading.tagName === 'H2') {
          element.style.fontSize = '1.8em';
          element.style.color = '#2d3748';
          element.style.marginTop = '2em';
          element.style.marginBottom = '0.5em';
        } else if (heading.tagName === 'H3') {
          element.style.fontSize = '1.3em';
          element.style.color = '#4a5568';
          element.style.marginTop = '1.5em';
          element.style.marginBottom = '0.5em';
        }
      });

      const paragraphs = contentDiv.querySelectorAll('p');
      paragraphs.forEach(p => {
        const element = p as HTMLElement;
        element.style.marginBottom = '1em';
        element.style.textAlign = 'justify';
      });

      const lists = contentDiv.querySelectorAll('ul, ol');
      lists.forEach(list => {
        const element = list as HTMLElement;
        element.style.marginBottom = '1em';
        element.style.paddingLeft = '1.5em';
      });

      container.appendChild(contentDiv);

      // Add image placeholders if requested
      if (includeImages && article.layout.imageSlots.length > 0) {
        for (const slot of article.layout.imageSlots) {
          const imageDiv = document.createElement('div');
          imageDiv.style.margin = '30px 0';
          imageDiv.style.padding = '20px';
          imageDiv.style.border = '2px dashed #cbd5e0';
          imageDiv.style.backgroundColor = '#f7fafc';
          imageDiv.style.textAlign = 'center';
          imageDiv.style.borderRadius = '8px';

          const uploadedImage = uploadedImages.get(slot.id);
          
          if (uploadedImage) {
            const img = document.createElement('img');
            img.src = uploadedImage.preview;
            img.style.maxWidth = '100%';
            img.style.maxHeight = '400px';
            img.style.borderRadius = '4px';
            img.style.marginBottom = '10px';
            imageDiv.appendChild(img);
            
            const caption = document.createElement('div');
            caption.style.fontSize = '0.9em';
            caption.style.color = '#666';
            caption.innerHTML = `<strong>${slot.position}</strong><br><em>${slot.description}</em>`;
            imageDiv.appendChild(caption);
          } else {
            imageDiv.innerHTML = `
              <div style="color: #666; font-size: 1.1em; margin-bottom: 10px;">📷</div>
              <div style="font-weight: bold; margin-bottom: 5px;">${slot.position}</div>
              <div style="font-style: italic; color: #666; margin-bottom: 5px;">${slot.description}</div>
              <div style="font-size: 0.8em; color: #999;">Suggested type: ${slot.suggestedType}</div>
            `;
          }
          
          container.appendChild(imageDiv);
        }
      }

      // Convert to canvas
      const canvas = await html2canvas(container, {
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
          <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl">
            <input
              type="checkbox"
              id="includeImages"
              checked={includeImages}
              onChange={(e) => setIncludeImages(e.target.checked)}
              disabled={isExporting}
              className="w-5 h-5 text-teal-600 rounded-lg focus:ring-teal-500"
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
              className="w-5 h-5 text-teal-600 rounded-lg focus:ring-teal-500"
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