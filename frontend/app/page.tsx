'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { articleAPI } from '../services/api';
import { ArticleRequest, ArticleResponse, GenerationStatus } from '../types';
import InputForm from '../components/InputForm';
import ArticleDisplay from '../components/ArticleDisplay';

export default function HomePage() {
  const [article, setArticle] = useState<ArticleResponse | null>(null);
  const [generationStatus, setGenerationStatus] = useState<GenerationStatus>({
    isGenerating: false,
    currentStep: '',
    progress: 0,
  });
  const [currentView, setCurrentView] = useState<'input' | 'result'>('input');
  const [abortController, setAbortController] = useState<AbortController | null>(null);

  const handleGenerateArticle = async (request: ArticleRequest) => {
    // Create abort controller for cancellation
    const controller = new AbortController();
    setAbortController(controller);
    
    setGenerationStatus({
      isGenerating: true,
      currentStep: 'Initializing generation...',
      progress: 10,
    });

    // Auto-scroll to progress section
    setTimeout(() => {
      const progressSection = document.querySelector('[data-progress-section]');
      if (progressSection) {
        progressSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);

    try {
      // Simulate progress updates
      const progressSteps = [
        { step: 'Processing input parameters...', progress: 20 },
        { step: 'Scraping web content...', progress: 30 },
        { step: 'Extracting PDF content...', progress: 40 },
        { step: 'Generating article with AI...', progress: 60 },
        { step: 'Evaluating article quality...', progress: 80 },
        { step: 'Finalizing content...', progress: 90 },
      ];

      for (const { step, progress } of progressSteps) {
        if (controller.signal.aborted) {
          throw new Error('Generation cancelled by user');
        }
        setGenerationStatus(prev => ({ ...prev, currentStep: step, progress }));
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      setGenerationStatus(prev => ({ 
        ...prev, 
        currentStep: 'Generating article...', 
        progress: 95 
      }));

      const response = await articleAPI.generateArticle(request, controller.signal);
      
      if (controller.signal.aborted) {
        return;
      }
      
      // Debug: Log API response
      console.log('API Response:', response);
      console.log('Has thaiContent:', !!response.thaiContent);
      console.log('Thai content length:', response.thaiContent?.length || 0);
      
      setArticle(response);
      setCurrentView('result');
      setGenerationStatus({
        isGenerating: false,
        currentStep: 'Complete',
        progress: 100,
      });

      toast.success(
        `Article generated successfully! Quality score: ${(response.qualityScore * 100).toFixed(1)}%`
      );

    } catch (error) {
      if (error instanceof Error && error.message === 'Generation cancelled by user') {
        toast('Article generation cancelled', { icon: 'ℹ️' });
        setGenerationStatus({
          isGenerating: false,
          currentStep: '',
          progress: 0,
        });
        return;
      }
      
      console.error('Error generating article:', error);
      const message = error instanceof Error ? error.message : 'Failed to generate article';
      toast.error(message);
      
      setGenerationStatus({
        isGenerating: false,
        currentStep: 'Error',
        progress: 0,
      });
    } finally {
      setAbortController(null);
    }
  };

  const handleCancelGeneration = () => {
    if (abortController) {
      abortController.abort();
    }
  };

  const handleBackToInput = () => {
    setCurrentView('input');
    setArticle(null);
    setGenerationStatus({
      isGenerating: false,
      currentStep: '',
      progress: 0,
    });
  };

  const handleRegenerateRequest = () => {
    setCurrentView('input');
    setArticle(null);
    setGenerationStatus({
      isGenerating: false,
      currentStep: '',
      progress: 0,
    });
  };

  return (
    <div className="section-spacing">
      {/* Conditional Header - Only show on input page */}
      {currentView === 'input' && (
        <section className="text-center mb-16">
          <div className="max-w-5xl mx-auto">
            <h1 className="text-5xl lg:text-6xl font-bold gradient-text mb-8">
              AI-Powered Article Generator
            </h1>
            <p className="text-xl lg:text-2xl text-gray-600 leading-relaxed mb-12">
              Generate high-quality business articles about trends and future ideas with the power of GPT-4o. 
              Designed for professional standards and innovative content creation.
            </p>
            
            {/* Feature highlights */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
              <div className="card-sky text-center">
                <div className="icon-wrapper mx-auto mb-4">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-dark-navy-800 mb-2">Professional Quality</h3>
                <p className="text-sm text-navy-600">Enterprise-grade content with quality assurance</p>
              </div>
              
              <div className="card-sky text-center">
                <div className="icon-wrapper mx-auto mb-4">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-dark-navy-800 mb-2">AI-Powered</h3>
                <p className="text-sm text-navy-600">Advanced GPT-4o technology for intelligent content</p>
              </div>
              
              <div className="card-sky text-center">
                <div className="icon-wrapper mx-auto mb-4">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-dark-navy-800 mb-2">Brand Aligned</h3>
                <p className="text-sm text-navy-600">Consistent tone and style for your business</p>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Result Page Header */}
      {currentView === 'result' && (
        <section className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl lg:text-4xl font-bold text-dark-navy-800 mb-2">
                Generated Article
              </h1>
              <p className="text-lg text-gray-600">
                Your AI-powered content is ready for review and enhancement
              </p>
            </div>
            <button
              onClick={handleBackToInput}
              className="btn-secondary flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Generator
            </button>
          </div>
        </section>
      )}

      {/* Generation Progress */}
      {generationStatus.isGenerating && (
        <section className="mb-12" data-progress-section>
          <div className="card-navy max-w-4xl mx-auto">
            <div className="flex flex-col lg:flex-row items-center gap-8">
              <div className="loading-spinner border-sky-300 w-12 h-12" />
              <div className="flex-1 text-center lg:text-left">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between mb-4">
                  <span className="text-xl font-semibold text-white mb-2 lg:mb-0">
                    {generationStatus.currentStep}
                  </span>
                  <span className="text-lg text-sky-300 font-medium">
                    {generationStatus.progress}%
                  </span>
                </div>
                <div className="w-full bg-dark-navy-800 rounded-full h-4 mb-4">
                  <div 
                    className="bg-gradient-to-r from-sky-400 to-navy-400 h-4 rounded-full transition-all duration-500 shadow-lg"
                    style={{ width: `${generationStatus.progress}%` }}
                  />
                </div>
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  <div className="text-sm text-sky-200">
                    Creating professional content with AI-powered quality assurance
                  </div>
                  <button
                    onClick={handleCancelGeneration}
                    className="btn-secondary bg-red-500 hover:bg-red-600 border-red-500 hover:border-red-600 text-white flex items-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Input View */}
      {currentView === 'input' && (
        <section className="max-w-4xl mx-auto">
          <InputForm 
            onSubmit={handleGenerateArticle}
            isGenerating={generationStatus.isGenerating}
          />
        </section>
      )}

      {/* Result View */}
      {currentView === 'result' && article && (
        <section>
          <ArticleDisplay 
            article={article}
            onRegenerateRequest={handleRegenerateRequest}
          />
        </section>
      )}

      {/* Footer - Only show on input page */}
      {currentView === 'input' && (
        <footer className="mt-24">
          <div className="card-navy">
          <div className="max-w-4xl mx-auto text-center">
            <div className="mb-12">
              <h2 className="text-3xl font-bold text-white mb-6">
                Powered by Advanced AI Technology
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="group">
                  <div className="icon-wrapper mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">Lightning Fast</h3>
                  <p className="text-sky-200">
                    Generate comprehensive articles in minutes with GPT-4o's advanced language processing
                  </p>
                </div>
                
                <div className="group">
                  <div className="icon-wrapper mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">Quality First</h3>
                  <p className="text-sky-200">
                    Intelligent quality scoring with iterative improvements for professional content
                  </p>
                </div>
                
                <div className="group">
                  <div className="icon-wrapper mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">Enterprise Ready</h3>
                  <p className="text-sky-200">
                    Professional standards with consistent branding and customizable outputs
                  </p>
                </div>
              </div>
            </div>
            
            <div className="border-t border-sky-500/30 pt-8">
              <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
                <div className="text-center lg:text-left">
                  <p className="text-sky-300 font-bold text-lg mb-1">Powered by GPT-4o</p>
                  <p className="text-sky-200 text-sm">Built with ❤️ for Jenosize</p>
                </div>
                <div className="flex flex-wrap gap-3">
                  <span className="bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full text-white text-sm">Advanced AI</span>
                  <span className="bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full text-white text-sm">Quality Assured</span>
                  <span className="bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full text-white text-sm">Professional</span>
                </div>
              </div>
            </div>
          </div>
          </div>
        </footer>
      )}
    </div>
  );
}