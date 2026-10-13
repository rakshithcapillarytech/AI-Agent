from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

ROOT = Path(__file__).resolve().parent.parent

# Load .env into os.environ so ChatAnthropic and LangSmith pick up their keys too.
load_dotenv(ROOT / ".env")


class Settings(BaseSettings):
    llm_provider: str = "google"  # google (dev, free key) | anthropic | bedrock
    main_model: str | None = None  # None → provider default in app/llm.py
    helper_model: str | None = None
    database_url: str = "postgresql://hydra:hydra@localhost:5432/hydra"
    api_base_url: str = "http://localhost:8000"
    knowledge_base_dir: Path = ROOT / "knowledge_base"


@lru_cache
def get_settings() -> Settings:
    return Settings()
