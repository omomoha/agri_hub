from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+psycopg2://agrilink_user:agrilink_password@db:5432/agrilink"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 120
    
    # Payment
    psp_mock_secret: str = "mock-psp-secret"
    
    # File storage
    file_storage_dir: str = "/app/storage"
    
    # CORS
    allowed_origins: list = ["http://localhost:3000", "http://frontend:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
