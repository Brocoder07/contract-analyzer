# Copilot Instructions for Contract Risk Analyzer

## Architecture Overview

This is a **FastAPI-based AI contract risk detection system** with a hybrid analysis approach:

- **Backend**: FastAPI app in `/backend/app/` with layered architecture (core, models, services, api)
- **AI Pipeline**: Hybrid risk detection combining rule-based patterns and ML models
- **Document Processing**: Multi-format support (PDF, DOCX, TXT) with fallback extraction methods

## Key Components & Patterns

### Service Layer Architecture
- `HybridRiskAnalyzer` (`app/services/ai/risk_analyzer.py`) - Main orchestrator combining multiple detection methods
- `RuleEngine` - spaCy-powered pattern matching with sentence-level analysis
- `MLModel` - Transformer-based classifier (currently mock implementation with DistilBERT placeholder)
- `DocumentProcessor` - Multi-library document extraction with PyPDF2/pdfplumber fallbacks

### Data Models (Pydantic)
- `RiskItem` - Core risk detection result with position tracking, confidence scores, and detector attribution
- Enums: `RiskType` (auto_renewal, liability, etc.) and `RiskLevel` (high/medium/low/none)
- Response schemas include metadata: processing time, document stats, confidence metrics

### Configuration Pattern
- Settings via Pydantic `BaseSettings` with `.env` support (`app/core/config.py`)
- Model paths, file limits, and Redis config centralized
- Environment-aware defaults (development vs production)

## Development Workflows

### Testing
```bash
cd backend && python test_system.py  # End-to-end system test with sample contract
```

### Running the Server
```bash
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints
- `POST /api/v1/analyze` - File upload analysis
- `POST /api/v1/analyze-text` - Direct text analysis
- Both return `AnalysisResponse` with risk items and metadata

## AI/ML Implementation Details

### Hybrid Analysis Flow
1. **Document Processing**: Multi-library extraction with graceful fallbacks
2. **Parallel Analysis**: Rule engine + ML model run simultaneously
3. **Risk Merging**: Position-based deduplication with confidence-weighted selection
4. **Scoring**: Weighted risk calculation considering confidence and severity

### spaCy Integration
- Both rule engine and ML model use `en_core_web_sm` for sentence segmentation
- Sentence-level analysis prevents partial clause matches
- Position tracking (`start_char`, `end_char`) enables precise risk location

### Error Handling Strategy
- Graceful degradation: If ML model fails, rule engine continues
- Document processing: Multiple extraction libraries with fallback chain
- API layer: Structured error responses with specific HTTP status codes

## Project-Specific Conventions

- **Lazy Loading**: AI models loaded on first analysis request, not app startup
- **Enum Values**: Always use `.value` when serializing enums to avoid object references
- **File Validation**: Size limits (10MB) and extension checking before processing
- **Position Tracking**: All risk items include character positions for UI highlighting
- **Detector Attribution**: Each risk tagged with detection method for debugging/analytics

## Dependencies & Integration Points

- **AI Stack**: transformers, torch, spaCy, scikit-learn
- **Document Processing**: pdfplumber (primary), PyPDF2 (fallback), python-docx
- **API Framework**: FastAPI with automatic OpenAPI docs at `/docs`
- **Future Integration**: Redis for caching, SQLAlchemy for persistence (configured but not yet implemented)