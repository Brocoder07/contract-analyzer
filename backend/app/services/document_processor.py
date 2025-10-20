import io
from typing import Optional
import PyPDF2
import pdfplumber
import docx

class DocumentProcessor:
    """
    Handles document text extraction from various formats
    """
    
    @staticmethod
    def extract_text(content: bytes, filename: str) -> str:
        file_extension = "." + filename.split(".")[-1].lower() if "." in filename else ""
        
        try:
            if file_extension == ".pdf":
                return DocumentProcessor._extract_from_pdf(content)
            elif file_extension == ".docx":
                return DocumentProcessor._extract_from_docx(content)
            elif file_extension == ".txt":
                return DocumentProcessor._extract_from_txt(content)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            raise Exception(f"Failed to extract text from {filename}: {str(e)}")
    
    @staticmethod
    def _extract_from_pdf(content: bytes) -> str:
        text = ""
        
        # Try PyPDF2 first
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    
            if text.strip():
                return text.strip()
                
        except Exception:
            pass
        
        # Fallback to pdfplumber
        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text.strip():
                return text.strip()
                
        except Exception:
            pass
        
        raise Exception("Could not extract text from PDF using any method")
    
    @staticmethod
    def _extract_from_docx(content: bytes) -> str:
        try:
            doc = docx.Document(io.BytesIO(content))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
            
            if not text.strip():
                raise ValueError("No text content found in DOCX file")
                
            return text.strip()
            
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")
    
    @staticmethod
    def _extract_from_txt(content: bytes) -> str:
        try:
            text = content.decode('utf-8').strip()
            
            if not text:
                raise ValueError("Empty text file")
                
            return text
            
        except UnicodeDecodeError:
            # Try different encoding
            try:
                text = content.decode('latin-1').strip()
                return text
            except Exception as e:
                raise Exception(f"TXT extraction failed with all encodings: {e}")
        except Exception as e:
            raise Exception(f"TXT extraction failed: {e}")