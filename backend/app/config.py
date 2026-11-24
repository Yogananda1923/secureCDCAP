import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "SecureCompilerAI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DESCRIPTION: str = "A Semantic Compiler for Intelligent Vulnerability Detection and Verified Code Optimization"
    
    # Database
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'secure_compiler.db')}"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # Limits & Execution Security
    MAX_FILE_SIZE_BYTES: int = 2 * 1024 * 1024  # 2MB
    EXECUTION_TIMEOUT_SECONDS: int = 5
    ALLOWED_EXTENSIONS: List[str] = [".py", ".c", ".h", ".java", ".txt"]
    
    class Config:
        case_sensitive = True

settings = Settings()

