from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.document_processor import DocumentProcessor
from app.services.ai.risk_analyzer import HybridRiskAnalyzer
from app.core.config import settings
from app.models.schemas import AnalysisResponse

router = APIRouter()
analyzer = HybridRiskAnalyzer(settings.RULE_CONFIG_PATH, settings.ML_MODEL_PATH, settings.ML_MODEL_CHOICE)
doc_processor = DocumentProcessor()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_contract(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file type
        file_extension = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
        if file_extension not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported. Allowed: {settings.ALLOWED_FILE_TYPES}"
            )
        
        # Read file
        content = await file.read()
        
        # Check file size
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Extract text
        text = doc_processor.extract_text(content, file.filename)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text content found")
        
        # Analyze
        result = analyzer.analyze_contract(text)
        return AnalysisResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze-text", response_model=AnalysisResponse)
async def analyze_text(text: str):
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        result = analyzer.analyze_contract(text.strip())
        return AnalysisResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")