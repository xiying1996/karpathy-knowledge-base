import logging
from typing import Any

from app.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.vault_reader import VaultReader
from app.services.vector_store import VectorStore

logger = logging.getLogger(__name__)


class NoteIndexer:
    def __init__(
        self,
        vault_path: str | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ):
        self.vault_path = vault_path or settings.VAULT_PATH
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()
        self.vault_reader = VaultReader(self.vault_path)
        self._indexed_ids: set[str] = set()

    def full_index(self) -> dict[str, Any]:
        logger.info("[Indexer] Starting full index")
        notes = self.vault_reader.list_notes()
        if not notes:
            logger.info("[Indexer] No notes found to index")
            return {"indexed": 0, "errors": 0}

        indexed = 0
        errors = 0
        for note in notes:
            try:
                embedding = self.embedding_service.encode_note(note)
                self.vector_store.upsert_notes([note], [embedding])
                indexed += 1
                self._indexed_ids.add(note["id"])
            except Exception as e:
                logger.error(f"[Indexer] Failed to index note {note['id']}: {e}")
                errors += 1

        logger.info(f"[Indexer] Full index completed: {indexed} indexed, {errors} errors")
        return {"indexed": indexed, "errors": errors}

    def incremental_index(self) -> dict[str, Any]:
        logger.info("[Indexer] Starting incremental index")
        all_notes = self.vault_reader.list_notes()
        notes_to_index = [n for n in all_notes if n["id"] not in self._indexed_ids]

        if not notes_to_index:
            logger.info("[Indexer] No new notes to index")
            return {"indexed": 0, "errors": 0}

        indexed = 0
        errors = 0
        for note in notes_to_index:
            try:
                embedding = self.embedding_service.encode_note(note)
                self.vector_store.upsert_notes([note], [embedding])
                indexed += 1
                self._indexed_ids.add(note["id"])
            except Exception as e:
                logger.error(f"[Indexer] Failed to index note {note['id']}: {e}")
                errors += 1

        logger.info(f"[Indexer] Incremental index completed: {indexed} indexed, {errors} errors")
        return {"indexed": indexed, "errors": errors}

    def delete_notes(self, note_ids: list[str]) -> None:
        self.vector_store.delete_notes(note_ids)
        self._indexed_ids.difference_update(note_ids)
        logger.info(f"[Indexer] Deleted {len(note_ids)} notes from index")


def create_scheduled_indexer(
    vault_path: str | None = None,
    interval_seconds: int = 300,
) -> tuple[NoteIndexer, Any]:
    import threading

    indexer = NoteIndexer(vault_path=vault_path)
    stop_event = threading.Event()

    def _run():
        while not stop_event.is_set():
            try:
                indexer.incremental_index()
            except Exception as e:
                logger.error(f"[Indexer] Scheduled index error: {e}")
            stop_event.wait(interval_seconds)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    def stop():
        stop_event.set()

    return indexer, stop