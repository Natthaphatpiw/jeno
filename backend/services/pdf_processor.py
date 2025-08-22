import base64
import io
from typing import Optional
from openai import OpenAI
from PyPDF2 import PdfReader
from config.settings import settings

class PDFProcessorService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def process_pdf_base64(self, pdf_base64: str) -> Optional[str]:
        """Process PDF from base64 string and extract text"""
        try:
            # Decode base64 to bytes
            pdf_bytes = base64.b64decode(pdf_base64)
            
            # Try PyPDF2 first for text extraction
            text_content = self._extract_text_with_pypdf2(pdf_bytes)
            
            # If PyPDF2 extraction is insufficient, use GPT-4o for OCR
            if not text_content or len(text_content.strip()) < 100:
                text_content = self._extract_text_with_gpt4o(pdf_base64)
            
            return self._clean_extracted_text(text_content)
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def _extract_text_with_pypdf2(self, pdf_bytes: bytes) -> str:
        """Extract text using PyPDF2"""
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PdfReader(pdf_file)
            
            text_content = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
            
            return text_content
            
        except Exception as e:
            print(f"PyPDF2 extraction failed: {str(e)}")
            return ""
    
    def _extract_text_with_gpt4o(self, pdf_base64: str) -> str:
        """Extract text using GPT-4o OCR capabilities"""
        try:
            # Create a data URL for the PDF
            pdf_data_url = f"data:application/pdf;base64,{pdf_base64}"
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please extract and return all the text content from this PDF document. Return only the extracted text without any additional commentary or formatting."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": pdf_data_url
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4000,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"GPT-4o OCR extraction failed: {str(e)}")
            return ""
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and format extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace and normalize
        import re
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove common PDF artifacts
        artifacts = [
            r'^\d+\s*$',  # Page numbers
            r'^Page \d+ of \d+$',  # Page headers
            r'^\s*\.\s*$',  # Dots
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 3:  # Keep meaningful content
                # Check if line matches any artifact pattern
                is_artifact = any(re.match(pattern, line) for pattern in artifacts)
                if not is_artifact:
                    cleaned_lines.append(line)
        
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Limit content length
        if len(cleaned_text) > 5000:
            cleaned_text = cleaned_text[:5000] + '...'
        
        return cleaned_text.strip()