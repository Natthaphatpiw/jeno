export interface UrlContentInstruction {
  url: string;
  contentFocus?: string;  // What specific content to extract from this URL
  usageInstruction?: string;  // How to use the content from this URL
  sectionTarget?: string;  // Which section of the article should use this URL's content
  extractionType?: string;  // e.g., "statistics", "case_study", "methodology", "quotes"
}

export interface ArticleRequest {
  topicCategory?: string;
  industry?: string;
  targetAudience?: string;
  sourceUrl?: string;  // Keep for backward compatibility
  sourceUrls?: string[];  // New field for multiple URLs (max 5)
  urlInstructions?: UrlContentInstruction[];  // Detailed instructions for URL content
  pdfBase64?: string;
  seoKeywords?: string;
  customPrompt?: string;  // Custom user instructions
  includeThaiTranslation?: boolean;  // Whether to generate Thai translation
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
  instructionCompliance?: string;  // How user's URL content instructions were followed
  extractionTypeUsed?: string;  // Type of content extracted
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
  thaiContent?: string;  // Thai translated content
  thaiLayout?: ArticleLayout;  // Thai translated layout
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