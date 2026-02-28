import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from src.core.traceback import traceBack, TrackType

class Settings:
    def __init__(self):
        env_path: Path = Path(__file__).resolve().parents[2] / ".env" / "var.env"

        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            traceBack(".env loaded")
        else:
            traceBack(".env not loaded, using os variables if exists. Check for variables if errors are raised")

        self.DATABASE_URL: str = "sqlite:///./bank.db"
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-key")
        self.ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 45
        self.EMAIL: str = os.getenv("EMAIL")
        self.EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
        self.IS_DEPLOYED: bool = os.getenv("DEPLOY") is not None
        self.ORIGINS: list[str] = self._get_origins()
        traceBack(f"Loaded origins {self.ORIGINS}")
        self.APP: FastAPI = None
        self.TEMPLATES: Jinja2Templates = Jinja2Templates(directory="src/templates")
    
    def _get_origins(self) -> list[str]:
        origins = []
        
        if os.getenv("DEBUG") is not None:
            origins.append("http://localhost:5173")
            origins.append("http://127.0.0.1:5173")
        
        frontend = os.getenv("FRONTEND_LINK")
        if frontend:
            origins.append(frontend)
        
        return origins

settings = Settings()