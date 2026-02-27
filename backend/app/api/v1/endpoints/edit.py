from fastapi import APIRouter, HTTPException, Response
from app.models.edit_schemas import ModificationRequest, EditResponse
from app.services.document_editor import DocumentEditor

router = APIRouter()
editor_service = DocumentEditor()

@router.post("/apply", response_model=EditResponse)
async def apply_edits(request: ModificationRequest):
    """
    Receives original text and suggestions, returns the new text.
    """
    try:
        new_text = editor_service.apply_modifications(
            request.original_text, 
            request.modifications
        )
        
        return EditResponse(
            modified_text=new_text,
            changes_applied=len(request.modifications)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download/docx")
async def download_contract(request: ModificationRequest):
    """
    Applies edits and directly returns a DOCX file.
    """
    try:
        # 1. Apply changes
        new_text = editor_service.apply_modifications(
            request.original_text, 
            request.modifications
        )
        
        # 2. Generate file
        docx_stream = editor_service.generate_docx(new_text)
        
        # 3. Return as downloadable file
        headers = {
            'Content-Disposition': 'attachment; filename="modified_contract.docx"'
        }
        return Response(
            content=docx_stream.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers=headers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))