import axios from 'axios';
import { ArticleRequest, ArticleResponse } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for article generation
  headers: {
    'Content-Type': 'application/json',
  },
});

export const articleAPI = {
  generateArticle: async (request: ArticleRequest, signal?: AbortSignal): Promise<ArticleResponse> => {
    try {
      const response = await apiClient.post('/api/generate-article', {
        topic_category: request.topicCategory,
        industry: request.industry,
        target_audience: request.targetAudience,
        source_url: request.sourceUrl,
        pdf_base64: request.pdfBase64,
        seo_keywords: request.seoKeywords,
      }, {
        signal
      });
      
      return {
        content: response.data.content,
        layout: {
          sections: response.data.layout.sections,
          imageSlots: response.data.layout.image_slots.map((slot: any) => ({
            id: slot.id,
            description: slot.description,
            position: slot.position,
            suggestedType: slot.suggested_type,
          })),
        },
        qualityScore: response.data.quality_score,
        iterations: response.data.iterations,
      };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.code === 'ERR_CANCELED') {
          throw new Error('Generation cancelled by user');
        }
        const message = error.response?.data?.detail || error.message;
        throw new Error(`API Error: ${message}`);
      }
      throw error;
    }
  },

  healthCheck: async (): Promise<{ status: string }> => {
    const response = await apiClient.get('/api/health');
    return response.data;
  },
};

export default apiClient;