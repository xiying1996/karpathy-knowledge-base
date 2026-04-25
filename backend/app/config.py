from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="qwen2.5:7b")

    # LLM Provider (minimax | deepseek)
    LLM_PROVIDER: str = Field(default="minimax")

    # MiniMax (OpenAI 兼容)
    MINIMAX_API_KEY: str = Field(default="")
    MINIMAX_BASE_URL: str = Field(default="https://api.minimax.chat/v1")
    MINIMAX_MODEL: str = Field(default="MiniMax-Text-01")

    # DeepSeek (OpenAI 兼容)
    DEEPSEEK_API_KEY: str = Field(default="")
    DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = Field(default="deepseek-chat")

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

    # Daily Note 配置
    DAILY_NOTE_ENABLED: bool = Field(default=True)
    DAILY_NOTE_AUTO_CREATE: bool = Field(default=False)
    DAILY_NOTE_AUTO_CREATE_TIME: str = Field(default="00:01")
    DAILY_NOTE_PATH_FORMAT: str = Field(default="daily/{date}.md")
    DAILY_NOTE_TEMPLATE_PATH: str = Field(default="templates/daily.md")
    DAILY_NOTE_AI_SUGGESTION: bool = Field(default=False)


settings = Settings()
