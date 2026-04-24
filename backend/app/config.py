from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    CHROMA_HOST: str = "localhost:8000"
    CHROMA_PORT: int = 8000
    DATA_DIR: Path = Path(__file__).parent.parent.parent / "vault"
    VAULT_PATH: Path = Path(__file__).parent.parent.parent / "vault"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
