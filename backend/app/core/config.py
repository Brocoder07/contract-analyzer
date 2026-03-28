from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import List
from enum import Enum

class SuggestionModelType(str, Enum):
    """Available suggestion generation models"""
    RULE_BASED = "rule_based"
    T5 = "t5"
    GPT = "gpt"
    HYBRID = "hybrid"

class SummarizationModelType(str, Enum):
    """Available summarization models"""
    RULE_BASED = "rule_based"
    BART = "bart"
    PEGASUS = "pegasus"
    T5 = "t5"
    BART_SAMSUM = "bart_samsum"
    HYBRID = "hybrid"

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "Contract Risk Analyzer"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    # Risk analysis Model paths and configuration
    ML_MODEL_PATH: str = "./app/data/models/bert_contracts"
    RULE_CONFIG_PATH: str = "./app/services/ai/rules.json"
    TRANSLATION_MODEL_PATH: str = "./app/data/models/en_hi_translate/en-hi-final"

    # Custom trained multi-task model (MiniLM + CUAD 15 categories)
    CUSTOM_MODEL_PATH: str = "./app/data/models/custom_analysis_model"

    # Risk Analysis Model Selection:
    #   local_contracts_bert | contracts_bert | legal_bert | deberta_large |
    #   legal_bert_small | roberta_large | custom
    ML_MODEL_CHOICE: str = "custom"
    
    # Model performance settings
    ML_CONFIDENCE_THRESHOLD: float = 0.6
    ML_BATCH_SIZE: int = 16
    TRANSLATION_MAX_INPUT_LENGTH: int = 256
    TRANSLATION_MAX_OUTPUT_LENGTH: int = 256
    
    # Suggestion Model settings
    SUGGESTION_MODEL_TYPE: SuggestionModelType = SuggestionModelType.T5
    
    # Individual model toggles (for hybrid mode)
    ENABLE_RULE_SUGGESTIONS: bool = True
    ENABLE_T5_SUGGESTIONS: bool = True
    ENABLE_GPT_SUGGESTIONS: bool = True
    
    # Model names/paths
    SUGGESTION_T5_MODEL: str = "google/flan-t5-base"
    SUGGESTION_GPT_MODEL: str = "distilgpt2"
    
    # Alternative models (can switch via env vars)
    # SUGGESTION_T5_MODEL: str = "google/flan-t5-large"  # Better quality, slower
    # SUGGESTION_GPT_MODEL: str = "gpt2"  # Larger GPT-2 model
    
    # Generation parameters
    SUGGESTION_MIN_CONFIDENCE: float = 0.6
    SUGGESTION_MAX_LENGTH: int = 150
    SUGGESTION_MAX_RESULTS: int = 5  # Top N suggestions to return
    
    # Deduplication settings
    ENABLE_SUGGESTION_DEDUPLICATION: bool = True
    DEDUPLICATION_SIMILARITY_THRESHOLD: float = 0.85

    # Summarization Model settings
    SUMMARIZATION_MODEL_TYPE: SummarizationModelType = SummarizationModelType.BART
    
    # Individual model toggles (for hybrid mode)
    ENABLE_RULE_SUMMARIZATION: bool = True
    ENABLE_BART_SUMMARIZATION: bool = True
    ENABLE_PEGASUS_SUMMARIZATION: bool = False
    ENABLE_T5_SUMMARIZATION: bool = False
    ENABLE_BART_SAMSUM_SUMMARIZATION: bool = False
    
    # Model names/paths
    SUMMARIZATION_BART_MODEL: str = "facebook/bart-large-cnn"
    SUMMARIZATION_PEGASUS_MODEL: str = "google/pegasus-cnn_dailymail"
    SUMMARIZATION_T5_MODEL: str = "t5-base"
    SUMMARIZATION_BART_SAMSUM_MODEL: str = "philschmid/bart-large-cnn-samsum"
    
    # Summarization parameters
    SUMMARY_MIN_LENGTH: int = 50
    SUMMARY_MAX_LENGTH: int = 300
    SUMMARY_EXTRACTIVE_SENTENCES: int = 5  # For rule-based extractive summary
    SUMMARY_INCLUDE_KEY_POINTS: bool = True
    SUMMARY_INCLUDE_PARTIES: bool = True
    SUMMARY_INCLUDE_DATES: bool = True
    
    # Hybrid summarization settings
    ENABLE_SUMMARY_FUSION: bool = True  # Combine multiple summaries
    SUMMARY_FUSION_METHOD: str = "weighted_average"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # MongoDB (auth)
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "contract_analyzer"
    MONGODB_USERS_COLLECTION: str = "users"
    
    # File upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".docx", ".txt"]
    
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore"  # This allows extra fields in .env without errors
    )

settings = Settings()