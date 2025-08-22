export interface ArticleRequest {
  topicCategory?: string;
  industry?: string;
  targetAudience?: string;
  sourceUrl?: string;
  pdfBase64?: string;
  seoKeywords?: string;
}

export interface ImageSlot {
  id: string;
  description: string;
  position: string;
  suggestedType: string;
}

export interface ArticleLayout {
  sections: string[];
  imageSlots: ImageSlot[];
}

export interface ArticleResponse {
  content: string;
  layout: ArticleLayout;
  qualityScore: number;
  iterations: number;
}

export interface GenerationStatus {
  isGenerating: boolean;
  currentStep: string;
  progress: number;
}

export interface UploadedImage {
  id: string;
  file: File;
  preview: string;
  slotId: string;
}