import io
from typing import List
from docx import Document
from app.models.edit_schemas import TextModification

class DocumentEditor:
    """
    Service class responsible for applying edits to contract text and 
    generating downloadable files.
    """

    def apply_modifications(self, original_text: str, modifications: List[TextModification]) -> str:
        """
        Applies a list of modifications to the text.
        
        CRITICAL LOGIC: 
        We must sort modifications in REVERSE order (descending start_pos).
        If we replace text at the beginning first, all subsequent indices 
        become invalid. Replacing from the end preserves earlier indices.
        """
        # Sort modifications by start_pos descending
        sorted_mods = sorted(modifications, key=lambda x: x.start_pos, reverse=True)
        
        modified_text = original_text
        
        for mod in sorted_mods:
            # specific validation to prevent crashes
            if mod.start_pos < 0 or mod.end_pos > len(modified_text):
                continue
                
            # String slicing to replace the segment
            before = modified_text[:mod.start_pos]
            after = modified_text[mod.end_pos:]
            modified_text = before + mod.replacement_text + after
            
        return modified_text

    def generate_docx(self, text: str) -> io.BytesIO:
        """
        Converts raw text into a formatted DOCX file stream.
        """
        doc = Document()
        doc.add_heading('Modified Contract', 0)
        
        # Split by newlines to preserve paragraphs
        for paragraph in text.split('\n'):
            if paragraph.strip():
                doc.add_paragraph(paragraph)
                
        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

    def generate_diff_summary(self, modifications: List[TextModification]) -> dict:
        """
        Optional: Returns a summary of what changed for audit logs.
        """
        return {
            "total_changes": len(modifications),
            "sections_touched": [f"{m.start_pos}-{m.end_pos}" for m in modifications]
        }