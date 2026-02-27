from pydantic import BaseModel, Field
from typing import List, Optional

class ModificationRequest(BaseModel):
    """
    Request model for applying suggestions to a document.
    """
    original_text: str = Field(..., description="The full original text of the contract")
    # We use a list of indices and replacements. 
    # We don't send the full 'RiskItem' to save bandwidth, just what's needed.
    modifications: List['TextModification']

class TextModification(BaseModel):
    """
    A specific change to be applied.
    """
    start_pos: int = Field(..., description="Start index of the text to replace")
    end_pos: int = Field(..., description="End index of the text to replace")
    replacement_text: str = Field(..., description="The new text to insert")
    comment: Optional[str] = Field(None, description="Optional comment for the change log")

class EditResponse(BaseModel):
    """
    Result of the edit operation.
    """
    modified_text: str
    changes_applied: int
    download_url: Optional[str] = None