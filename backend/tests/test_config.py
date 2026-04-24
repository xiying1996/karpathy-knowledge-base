import pytest
from app.config import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.OLLAMA_BASE_URL == "http://localhost:11434"
    assert settings.CHROMA_HOST == "localhost:8000"
    assert settings.LOG_LEVEL == "INFO"
