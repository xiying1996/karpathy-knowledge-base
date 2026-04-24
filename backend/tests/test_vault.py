import pytest
from pathlib import Path
from app.config import settings


def test_vault_path_default():
    assert settings.VAULT_PATH is not None
    assert isinstance(settings.VAULT_PATH, Path)
