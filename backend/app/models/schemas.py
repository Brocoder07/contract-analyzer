from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid

class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class RiskType(str, Enum):
    # Original categories
    AUTO_RENEWAL = "auto_renewal"
    LIABILITY = "liability"
    TERMINATION = "termination"
    IP_OWNERSHIP = "ip_ownership"
    INDEMNIFICATION = "indemnification"
    CONFIDENTIALITY = "confidentiality"
    # CUAD unfair-clause categories (custom model)
    TERMINATION_FOR_CONVENIENCE = "termination_for_convenience"
    UNCAPPED_LIABILITY = "uncapped_liability"
    CAP_ON_LIABILITY = "cap_on_liability"
    LIQUIDATED_DAMAGES = "liquidated_damages"
    NON_COMPETE = "non_compete"
    EXCLUSIVITY = "exclusivity"
    COVENANT_NOT_TO_SUE = "covenant_not_to_sue"
    MINIMUM_COMMITMENT = "minimum_commitment"
    IP_OWNERSHIP_ASSIGNMENT = "ip_ownership_assignment"
    NO_SOLICIT_OF_EMPLOYEES = "no_solicit_of_employees"
    NON_DISPARAGEMENT = "non_disparagement"
    ANTI_ASSIGNMENT = "anti_assignment"
    CHANGE_OF_CONTROL = "change_of_control"
    ROFR_ROFO_ROFN = "rofr_rofo_rofn"
    POST_TERMINATION_SERVICES = "post_termination_services"

class Suggestion(BaseModel):
    suggestion_text: str
    rationale: str
    confidence: float
    source: str
    priority: int 

class RiskItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    risk_type: RiskType
    text: str = Field(..., description="The actual text where risk was found")
    description: str = Field(..., description="Description of the risk")
    suggestion: str = Field(..., description="Suggested fix or improvement")
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    start_pos: Optional[int] = Field(None, description="Start position in text")
    end_pos: Optional[int] = Field(None, description="End position in text")
    detector: str = Field(..., description="Which detector found this (rule_based, ml_model)")
    suggestions: Optional[List[Suggestion]] = Field(default_factory=list)
    best_suggestion: Optional[Suggestion] = None

class Summary(BaseModel):
    summary_text: str
    key_points: List[str] = []
    parties_involved: List[str] = []
    important_dates: List[str] = []
    contract_type: Optional[str] = None
    confidence: float
    source: str  # "rule_based", "bart", "pegasus", "t5", "bart_samsum", "hybrid"
    word_count: int
    compression_ratio: float  # original_length / summary_length
    
class SummaryMetadata(BaseModel):
    """Metadata about the summarization process"""
    total_summaries_generated: int
    models_used: List[str]
    processing_time: float
    original_word_count: int
    summary_word_count: int
    compression_ratio: float

class AnalysisResponse(BaseModel):
    risks: List[RiskItem]
    overall_risk_score: float = Field(..., ge=0, le=1, description="Overall risk score 0-1")
    risk_level: RiskLevel
    total_risks_found: int = Field(..., ge=0)
    processing_time: float = Field(..., description="Processing time in seconds")
    summary: Optional[Summary] = None  
    summary_metadata: Optional[SummaryMetadata] = None 
    document_metadata: Dict[str, Any] = Field(default_factory=dict)
    extracted_text: Optional[str] = Field(None, description="Raw extracted text for client-side editing")

class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool
    timestamp: datetime

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)