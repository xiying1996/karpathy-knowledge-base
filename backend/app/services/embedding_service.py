import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.EMBEDDING_MODEL

    def generate_embedding(self, text: str) -> list[float]:
        logger.info(f"[EmbeddingService] Generating embedding for: {text[:50]}..., model: {self.model}")
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                )
                response.raise_for_status()
                result = response.json()
                vector = result.get("embedding", [])
                logger.info(f"[EmbeddingService] Embedding generated, dim={len(vector)}")
                return vector
        except Exception as e:
            logger.error(f"[EmbeddingService] Ollama request failed: {e}")
            raise

    def encode_note(self, note: dict[str, Any]) -> list[float]:
        combined_text = f"{note.get('title', '')}\n{note.get('content', '')}"
        return self.generate_embedding(combined_text)