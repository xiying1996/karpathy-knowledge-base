import logging
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        collection_name: str = "notes",
    ):
        self.host = host or settings.CHROMA_HOST
        self.port = port or settings.CHROMA_PORT
        self.collection_name = collection_name
        self._client = None
        self._collection = None

    @property
    def client(self):
        if self._client is None:
            self._client = chromadb.Client(
                ChromaSettings(
                    chroma_server_host=self.host,
                    chroma_server_http_port=self.port,
                )
            )
        return self._client

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name
            )
            logger.info(f"[VectorStore] Created collection: {self.collection_name}")
        return self._collection

    def upsert_notes(self, notes: list[dict[str, Any]], embeddings: list[list[float]]) -> None:
        if not notes:
            return
        ids = [note["id"] for note in notes]
        documents = [note["content"] for note in notes]
        metadatas = [
            {"title": note.get("title", ""), "path": note.get("path", "")}
            for note in notes
        ]
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        logger.info(f"[VectorStore] Upserted {len(ids)} vectors into {self.collection_name}")

    def delete_notes(self, note_ids: list[str]) -> None:
        if not note_ids:
            return
        self.collection.delete(ids=note_ids)
        logger.info(f"[VectorStore] Deleted vectors for {note_ids}")

    def similarity_search(
        self, query_embedding: list[float], limit: int = 5
    ) -> list[dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
        )
        return results