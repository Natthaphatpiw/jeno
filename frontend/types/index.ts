export interface ArticleRequest {
  topicCategory?: string;
  industry?: string;
  targetAudience?: string;
  sourceUrl?: string;  // Keep for backward compatibility
  sourceUrls?: string[];  // New field for multiple URLs (max 5)
  pdfBase64?: string;
  seoKeywords?: string;
  customPrompt?: string;  // Custom user instructions
}

export interface ImageSlot {
  id: string;
  description: string;
  position: string;
  suggestedType: string;
  placementRationale?: string;
  contentGuidance?: string;
  dimensions?: string;
  aspectRatio?: string;
  alternatives?: string;
}

export interface ArticleLayout {
  sections: string[];
  imageSlots: ImageSlot[];
}

export interface SourceUsageDetail {
  sourceTitle: string;
  sourceUrl: string;
  contentUsed: string;
  usageLocation: string;
  usagePurpose: string;
  transformation: string;
}

export interface ArticleAnalysis {
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  summary: string;
}

export interface ArticleResponse {
  content: string;
  layout: ArticleLayout;
  qualityScore: number;
  iterations: number;
  sourceUsageDetails?: SourceUsageDetail[];
  analysis?: ArticleAnalysis;
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