from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import List

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
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Model paths
    ML_MODEL_PATH: str = "./app/data/models/production"
    RULE_CONFIG_PATH: str = "./app/services/ai/rules.json"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # File upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".docx", ".txt"]
    
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore"  # This allows extra fields in .env without errors
    )

settings = Settings()