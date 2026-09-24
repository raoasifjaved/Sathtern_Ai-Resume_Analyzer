import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    groq_model: str
    groq_timeout: float
    max_upload_mb: int
    max_resume_chars: int
    database_path: str

settings = Settings(
    groq_api_key=os.getenv("GROQ_API_KEY", "").strip(),
    groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip(),
    groq_timeout=float(os.getenv("GROQ_TIMEOUT", "60")),
    max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "5")),
    max_resume_chars=int(os.getenv("MAX_RESUME_CHARS", "12000")),
    database_path=os.getenv("DATABASE_PATH", str(BASE_DIR / "resume_lens.db")),
)
