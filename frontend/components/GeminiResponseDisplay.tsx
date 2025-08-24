'use client';

import { useState } from 'react';
import { Download, Copy, CheckCircle, FileText } from 'lucide-react';
// No longer need markdown parsing libraries

interface GeminiResponseDisplayProps {
  responseData: any; // Raw JSON response from Gemini
  onRegenerateRequest: () => void;
}

export default function GeminiResponseDisplay({ responseData, onRegenerateRequest }: GeminiResponseDisplayProps) {
  const [activeTab, setActiveTab] = useState<'article' | 'raw' | 'json'>('article');
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopyJson = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(responseData, null, 2));
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy JSON:', err);
    }
  };

  const downloadJson = () => {
    const blob = new Blob([JSON.stringify(responseData, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `gemini-response-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const extractTextFromHtml = (html: string): string => {
    // Create a temporary DOM element to parse HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    
    // Extract text content, preserving some structure
    const textContent = tempDiv.innerText || tempDiv.textContent || '';
    return textContent;
  };

  const downloadText = () => {
    const htmlContent = responseData?.content || 'No content available';
    const textContent = extractTextFromHtml(htmlContent);
    
    const blob = new Blob([textContent], {
      type: 'text/plain'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `gemini-article-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full max-w-6xl mx-auto bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Gemini 2.5 Pro Response</h2>
            <p className="text-sm text-gray-600 mt-1">Raw AI response with full JSON structure</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyJson}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              {copySuccess ? <CheckCircle size={16} /> : <Copy size={16} />}
              {copySuccess ? 'Copied!' : 'Copy JSON'}
            </button>
            <button
              onClick={downloadJson}
              className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              <Download size={16} />
              Download JSON
            </button>
            <button
              onClick={downloadText}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              <FileText size={16} />
              Download Text
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('article')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'article'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-700 hover:text-gray-900'
            }`}
          >
            Article
          </button>
          <button
            onClick={() => setActiveTab('raw')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'raw'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-700 hover:text-gray-900'
            }`}
          >
            Raw Content
          </button>
          <button
            onClick={() => setActiveTab('json')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'json'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-700 hover:text-gray-900'
            }`}
          >
            Full JSON
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-0">
        {activeTab === 'article' && (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            {/* Article Display Area */}
            <div 
              className="p-8 prose prose-lg max-w-none"
              dangerouslySetInnerHTML={{ 
                __html: responseData?.content || '<p>No content available</p>' 
              }}
              style={{
                // Additional CSS to ensure proper styling
                lineHeight: '1.6',
                fontSize: '16px'
              }}
            />
          </div>
        )}

        {activeTab === 'raw' && (
          <div className="bg-gray-50 rounded-lg p-4 m-6">
            <pre className="whitespace-pre-wrap text-sm text-gray-800 overflow-auto max-h-96">
              {responseData?.content || 'No content available'}
            </pre>
          </div>
        )}

        {activeTab === 'json' && (
          <div className="bg-gray-900 rounded-lg p-4 m-6 overflow-auto max-h-96">
            <pre className="text-green-400 text-sm font-mono">
              {JSON.stringify(responseData, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* Metadata */}
      {responseData && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Response Metadata</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Sections:</span>
              <span className="ml-2 font-medium">
                {responseData?.layout?.sections?.length || 0}
              </span>
            </div>
            <div>
              <span className="text-gray-600">Image Slots:</span>
              <span className="ml-2 font-medium">
                {responseData?.layout?.image_slots?.length || 0}
              </span>
            </div>
            <div>
              <span className="text-gray-600">Content Length:</span>
              <span className="ml-2 font-medium">
                {responseData?.content?.length || 0} chars
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="px-6 py-4 border-t border-gray-200 flex justify-between">
        <button
          onClick={onRegenerateRequest}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Regenerate Article
        </button>
        <div className="text-sm text-gray-500">
          Generated with Gemini 2.5 Pro
        </div>
      </div>
    </div>
  );
}