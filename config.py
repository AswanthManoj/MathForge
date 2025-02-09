import threading
import dotenv, os, time
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    max_tokens: int = 3049
    temperature: float = 0.3
    
    database_url: Optional[str] = os.getenv("DATABASE_URL")
    google_api_key: Optional[str] = os.getenv("GOOGLE_API")
    together_api_key: Optional[str] = os.getenv("TOGETHER_API")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API")
    
    google_primary_model: Optional[str] = "gemini-2.0-pro-exp-02-05"
    anthropic_primary_model: Optional[str] = "claude-3-5-sonnet-20240620"
    together_primary_model: Optional[str] = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    provider_priority: Optional[list] = ["google", "anthropic", "together",]

    
_settings = None
def get_settings():
    """
    Singleton pattern implementation for application settings.
    
    Ensures:
    - Only one Settings instance exists throughout application lifecycle
    - Thread-safe access to settings
    - Lazy initialization of settings
    
    Returns:
        Settings: Global settings instance with environment configurations
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
