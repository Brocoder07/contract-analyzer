import io
import re
from typing import Optional
import PyPDF2
import pdfplumber
import docx

class DocumentProcessor:
    """
    Handles document text extraction from various formats
    """

    @staticmethod
    def _normalise(text: str) -> str:
        """
        Cleans raw extracted text regardless of source (PDF, DOCX, TXT).

        PDF extractors often emit one word per line (or one token per line with
        stray spaces).  Strategy:
          1. Normalise line endings.
          2. Guard lines that look like headings (ALL-CAPS or numbered clause)
             with blank lines so they keep their own paragraph identity.
          3. Collapse single newlines between non-blank lines into a space
             (i.e. join soft-wrapped / word-per-line chunks).
          4. Collapse 3+ blank lines → one blank line.
          5. Strip internal runs of spaces/tabs within each line.
        """
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        all_caps_re = re.compile(r'^[A-Z][A-Z\s\-&/]{4,}$')
        numbered_re = re.compile(r'^\d+(\.\d+)*[\.\)]\s+[A-Z]')

        lines = text.split('\n')
        guarded = []
        for line in lines:
            s = line.strip()
            if s and (all_caps_re.match(s) or numbered_re.match(s)):
                if guarded and guarded[-1].strip():
                    guarded.append('')
                guarded.append(line)
                guarded.append('')
            else:
                guarded.append(line)
        text = '\n'.join(guarded)

        # Join soft-wrapped / word-per-line runs
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

        # Collapse 3+ newlines → two
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Tidy each line
        lines = [re.sub(r'[ \t]+', ' ', ln).strip() for ln in text.split('\n')]
        return '\n'.join(lines).strip()

    @staticmethod
    def extract_text(content: bytes, filename: str) -> str:
        file_extension = "." + filename.split(".")[-1].lower() if "." in filename else ""
        
        try:
            if file_extension == ".pdf":
                raw = DocumentProcessor._extract_from_pdf(content)
            elif file_extension == ".docx":
                raw = DocumentProcessor._extract_from_docx(content)
            elif file_extension == ".txt":
                raw = DocumentProcessor._extract_from_txt(content)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")

            return DocumentProcessor._normalise(raw)
                
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