from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class RiskType(str, Enum):
    AUTO_RENEWAL = "auto_renewal"
    LIABILITY = "liability"
    TERMINATION = "termination"
    IP_OWNERSHIP = "ip_ownership"
    INDEMNIFICATION = "indemnification"
    CONFIDENTIALITY = "confidentiality"

class RiskItem(BaseModel):
    risk_type: RiskType
    text: str = Field(..., description="The actual text where risk was found")
    description: str = Field(..., description="Description of the risk")
    suggestion: str = Field(..., description="Suggested fix or improvement")
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    start_pos: Optional[int] = Field(None, description="Start position in text")
    end_pos: Optional[int] = Field(None, description="End position in text")
    detector: str = Field(..., description="Which detector found this (rule_based, ml_model)")

class AnalysisResponse(BaseModel):
    risks: List[RiskItem]
    overall_risk_score: float = Field(..., ge=0, le=1, description="Overall risk score 0-1")
    risk_level: RiskLevel
    total_risks_found: int = Field(..., ge=0)
    processing_time: float = Field(..., description="Processing time in seconds")
    document_metadata: Dict[str, Any] = Field(default_factory=dict)

class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool
    timestamp: datetime

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)