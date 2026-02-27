"""
Contract analysis endpoints
Handles file upload, text analysis, suggestion generation, and summarization
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional

from app.services.document_processor import DocumentProcessor
from app.services.ai.risk_analyzer import HybridRiskAnalyzer
from app.core.config import settings
from app.models.schemas import AnalysisResponse, RiskItem

router = APIRouter()

# Initialize analyzer with settings for suggestion and summarization
analyzer = HybridRiskAnalyzer(
    rule_config_path=settings.RULE_CONFIG_PATH,
    ml_model_path=settings.ML_MODEL_PATH,
    settings=settings,
    model_choice=settings.ML_MODEL_CHOICE
)

doc_processor = DocumentProcessor()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_contract(
    file: UploadFile = File(...),
    generate_suggestions: bool = Query(
        True, 
        description="Generate mitigation suggestions for detected risks"
    ),
    generate_summary: bool = Query(
        True,
        description="Generate contract summary"
    )
):
    """
    Analyze uploaded contract document for risks
    
    - **file**: Contract file (PDF, DOCX, or TXT)
    - **generate_suggestions**: Whether to generate mitigation suggestions (default: True)
    - **generate_summary**: Whether to generate contract summary (default: True)
    
    Returns analysis results with detected risks, suggestions, and summary
    """
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
        
        # Analyze with optional suggestion and summary generation
        result = analyzer.analyze_contract(
            text, 
            generate_suggestions=generate_suggestions,
            generate_summary=generate_summary
        )
        
        # Add suggestion statistics if suggestions were generated
        if generate_suggestions and result.get("risks"):
            result["suggestion_stats"] = analyzer.get_suggestion_stats(result["risks"])
        
        # Attach extracted text so the frontend can use it for position-based editing
        result["extracted_text"] = text

        return AnalysisResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze-text", response_model=AnalysisResponse)
async def analyze_text(
    text: str,
    generate_suggestions: bool = Query(
        True,
        description="Generate mitigation suggestions for detected risks"
    ),
    generate_summary: bool = Query(
        True,
        description="Generate contract summary"
    )
):
    """
    Analyze plain text contract for risks
    
    - **text**: Contract text content
    - **generate_suggestions**: Whether to generate mitigation suggestions (default: True)
    - **generate_summary**: Whether to generate contract summary (default: True)
    
    Returns analysis results with detected risks, suggestions, and summary
    """
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Analyze with optional suggestion and summary generation
        result = analyzer.analyze_contract(
            text.strip(), 
            generate_suggestions=generate_suggestions,
            generate_summary=generate_summary
        )
        
        # Add suggestion statistics if suggestions were generated
        if generate_suggestions and result.get("risks"):
            result["suggestion_stats"] = analyzer.get_suggestion_stats(result["risks"])
        
        return AnalysisResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/regenerate-suggestions/{risk_id}")
async def regenerate_suggestions(
    risk_id: str,
    risk_data: RiskItem,
    text_context: Optional[str] = None
):
    """
    Regenerate suggestions for a specific risk
    
    - **risk_id**: Unique identifier for the risk
    - **risk_data**: The RiskItem object
    - **text_context**: Optional surrounding text for better context
    
    Returns new suggestions for the risk
    """
    try:
        suggestions = analyzer.regenerate_suggestions_for_risk(
            risk_data,
            text_context or ""
        )
        
        return {
            "risk_id": risk_id,
            "suggestions": suggestions,
            "count": len(suggestions),
            "model_type": settings.SUGGESTION_MODEL_TYPE
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate suggestions: {str(e)}"
        )


@router.post("/regenerate-summary")
async def regenerate_summary(text: str):
    """
    Regenerate contract summary
    
    - **text**: Contract text content
    
    Returns new summary
    """
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        result = analyzer.regenerate_summary(text.strip())
        
        if not result:
            raise HTTPException(status_code=500, detail="Summary generation failed")
        
        return {
            "summary": result.get("summary"),
            "metadata": result.get("metadata"),
            "model_type": settings.SUMMARIZATION_MODEL_TYPE
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate summary: {str(e)}"
        )


@router.get("/suggestion-config")
async def get_suggestion_config():
    """
    Get current suggestion model configuration
    """
    return {
        "model_type": settings.SUGGESTION_MODEL_TYPE,
        "enabled_models": {
            "rule_based": settings.ENABLE_RULE_SUGGESTIONS,
            "t5": settings.ENABLE_T5_SUGGESTIONS,
            "gpt": settings.ENABLE_GPT_SUGGESTIONS
        },
        "parameters": {
            "min_confidence": settings.SUGGESTION_MIN_CONFIDENCE,
            "max_length": settings.SUGGESTION_MAX_LENGTH,
            "max_results": settings.SUGGESTION_MAX_RESULTS,
            "deduplication_enabled": settings.ENABLE_SUGGESTION_DEDUPLICATION,
            "similarity_threshold": settings.DEDUPLICATION_SIMILARITY_THRESHOLD
        },
        "models": {
            "t5_model": settings.SUGGESTION_T5_MODEL,
            "gpt_model": settings.SUGGESTION_GPT_MODEL
        }
    }


@router.get("/summarization-config")
async def get_summarization_config():
    """
    Get current summarization model configuration
    """
    return {
        "model_type": settings.SUMMARIZATION_MODEL_TYPE,
        "enabled_models": {
            "rule_based": settings.ENABLE_RULE_SUMMARIZATION,
            "bart": settings.ENABLE_BART_SUMMARIZATION,
            "pegasus": settings.ENABLE_PEGASUS_SUMMARIZATION,
            "t5": settings.ENABLE_T5_SUMMARIZATION,
            "bart_samsum": settings.ENABLE_BART_SAMSUM_SUMMARIZATION
        },
        "parameters": {
            "min_length": settings.SUMMARY_MIN_LENGTH,
            "max_length": settings.SUMMARY_MAX_LENGTH,
            "extractive_sentences": settings.SUMMARY_EXTRACTIVE_SENTENCES,
            "include_key_points": settings.SUMMARY_INCLUDE_KEY_POINTS,
            "include_parties": settings.SUMMARY_INCLUDE_PARTIES,
            "include_dates": settings.SUMMARY_INCLUDE_DATES,
            "enable_fusion": settings.ENABLE_SUMMARY_FUSION,
            "fusion_method": settings.SUMMARY_FUSION_METHOD
        },
        "models": {
            "bart": settings.SUMMARIZATION_BART_MODEL,
            "pegasus": settings.SUMMARIZATION_PEGASUS_MODEL,
            "t5": settings.SUMMARIZATION_T5_MODEL,
            "bart_samsum": settings.SUMMARIZATION_BART_SAMSUM_MODEL
        }
    }