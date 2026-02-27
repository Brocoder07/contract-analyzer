import io
import re
from typing import List
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
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
        Converts raw text into a well-formatted DOCX file stream.

        Formatting rules applied automatically:
        - All-caps lines (e.g. "AGREEMENT TERMS AND CONDITIONS") → Heading 1
        - Numbered section lines (e.g. "1. TERM AND RENEWAL: …")  → Heading 2
        - Blank lines                                              → thin spacer paragraph
        - Everything else                                          → Normal body paragraph
        """
        doc = Document()

        # Remove default empty paragraph Word always adds
        for p in doc.paragraphs:
            p._element.getparent().remove(p._element)

        doc.add_heading('Modified Contract', 0)

        # Patterns for auto-detecting heading lines
        all_caps_re = re.compile(r'^[A-Z][A-Z\s\-&/]{4,}$')
        numbered_re = re.compile(r'^\d+\.\s+[A-Z]')

        for line in text.split('\n'):
            stripped = line.strip()

            if stripped == '':
                # Blank line → small spacer so sections breathe
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)

            elif all_caps_re.match(stripped):
                # Document-level title / major section heading
                heading = doc.add_heading(stripped, level=1)
                heading.paragraph_format.space_before = Pt(12)
                heading.paragraph_format.space_after = Pt(4)

            elif numbered_re.match(stripped):
                # Numbered clause heading (e.g. "3. INTELLECTUAL PROPERTY: …")
                heading = doc.add_heading(stripped, level=2)
                heading.paragraph_format.space_before = Pt(10)
                heading.paragraph_format.space_after = Pt(2)

            else:
                # Regular body text
                p = doc.add_paragraph(stripped)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(4)

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