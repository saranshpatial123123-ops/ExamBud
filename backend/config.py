import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Resolve paths relative to this config file
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "data", "uploads")
    CHROMA_DB_DIR: str = os.path.join(BASE_DIR, "data", "chroma")
    
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    
    # For OpenAI usage
    OPENAI_API_KEY: str = ""

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
