from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    CHROMA_HOST: str = Field(default="localhost:8000")
    CHROMA_PORT: int = Field(default=8000)
    DATA_DIR: str = Field(default="./vault")
    VAULT_PATH: str = Field(default="./vault")
    LOG_LEVEL: str = Field(default="INFO")
    API_KEY: str | None = Field(default=None)
    BACKEND_CORS_ORIGINS: str = Field(default="http://localhost:3000,http://127.0.0.1:3000")
    FILE_WATCHER_ENABLED: bool = Field(default=True)
    FILE_WATCHER_MODE: str = Field(default="watch")
    FILE_WATCHER_POLL_INTERVAL: int = Field(default=2)
    FILE_WATCHER_DEBOUNCE: int = Field(default=2)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
