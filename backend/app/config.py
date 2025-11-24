from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Groq API
    GROQ_API_KEY: str
    
    # LLM Settings
    LLM_MODEL: str = "llama-3.1-70b-versatile"
    LLM_BASE_URL: str = "https://api.groq.com/openai/v1"
    LLM_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 800
    
    # Database
    DATABASE_URL: str = "sqlite:///./interview_partner.db"
    
    # Interview Settings
    MAX_QUESTIONS: int = 6
    ENABLE_SEMANTIC_PERSONA: bool = True
    
    # Voice Settings (optional)
    ENABLE_VOICE: bool = False  # ✅ ADDED THIS
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # ✅ ADDED THIS - Ignores extra fields in .env

@lru_cache()
def get_settings() -> Settings:
    return Settings()
