import logging
import sys
from pathlib import Path

from app.config import settings
from app.services.vault_reader import VaultReader

logger = logging.getLogger(__name__)

try:
    from chromadb import HttpClient
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


_chroma_client = None


def get_chroma_client():
    global _chroma_client
    if not CHROMA_AVAILABLE:
        return None
    if _chroma_client is None:
        host = settings.CHROMA_HOST.split(":")[0] if ":" in settings.CHROMA_HOST else settings.CHROMA_HOST
        port = settings.CHROMA_PORT
        _chroma_client = HttpClient(host=host, port=port)
    return _chroma_client


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    if not text:
        return []
    lines = text.split("\n")
    chunks = []
    current = []
    current_len = 0
    for line in lines:
        line_len = len(line)
        if current_len + line_len > chunk_size and current:
            chunks.append("\n".join(current))
            current = current[-2:] if len(current) > 2 else current
            current_len = sum(len(line) for line in current)
        current.append(line)
        current_len += line_len
    if current:
        chunks.append("\n".join(current))
    return chunks


class Indexer:
    def __init__(self, vault_path: str | None = None):
        self.vault_path = vault_path or settings.VAULT_PATH
        self.vault_reader = VaultReader(self.vault_path)
        self._collection = None

    @property
    def collection(self):
        if not CHROMA_AVAILABLE:
            return None
        client = get_chroma_client()
        if client is None:
            return None
        if self._collection is None:
            try:
                self._collection = client.get_or_create_collection("notes")
            except Exception:
                self._collection = client.create_collection("notes")
        return self._collection

    def upsert_note(self, note_id: str, title: str, content: str, path: str):
        if self.collection is None:
            logger.warning(f"[Indexer] ChromaDB not available, skipping upsert for {note_id}")
            return
        chunks = _chunk_text(content)
        for i, chunk in enumerate(chunks):
            doc_id = f"{note_id}_{i}"
            self.collection.upsert(
                ids=[doc_id],
                documents=[chunk],
                metadatas=[{"note_id": note_id, "title": title, "path": path, "chunk_index": i}],
            )
        logger.info(f"[Indexer] Upserting chunks: {len(chunks)} for {note_id}")

    def delete_note(self, note_id: str):
        if self.collection is None:
            logger.warning(f"[Indexer] ChromaDB not available, skipping delete for {note_id}")
            return
        try:
            result = self.collection.get(where={"note_id": note_id})
            if result and result.get("ids"):
                self.collection.delete(ids=result["ids"])
            logger.info(f"[Indexer] Deleting vectors for {note_id}")
        except Exception as e:
            logger.error(f"[Indexer] Error deleting {note_id}: {e}")

    def on_file_change(self, event_type: str, file_path: str):
        path = Path(file_path)
        note_id = path.stem
        if event_type in ("CREATE", "MODIFY"):
            try:
                note = self.vault_reader.read_note(path)
                self.upsert_note(note["id"], note["title"], note["content"], note["path"])
            except Exception as e:
                logger.error(f"[Indexer] Error indexing {file_path}: {e}")
        elif event_type == "DELETE":
            self.delete_note(note_id)

    def upsert_all_notes(self) -> int:
        notes = self.vault_reader.list_notes()
        for note in notes:
            try:
                self.upsert_note(note["id"], note["title"], note["content"], note["path"])
            except Exception as e:
                logger.error(f"[Indexer] Error upserting {note['id']}: {e}")
        logger.info(f"[Indexer] Full sync completed: {len(notes)} notes indexed")
        return len(notes)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    rebuild_file = None
    if len(sys.argv) > 1 and sys.argv[1] == "--rebuild":
        if len(sys.argv) > 2:
            rebuild_file = sys.argv[2]
    indexer = Indexer()
    if rebuild_file:
        path = Path(rebuild_file).resolve()
        note_id = path.stem
        try:
            note = indexer.vault_reader.read_note(path)
            indexer.upsert_note(note["id"], note["title"], note["content"], note["path"])
            print(f"Rebuilt: {note_id}")
        except Exception as e:
            print(f"Error rebuilding {rebuild_file}: {e}")
            sys.exit(1)
    else:
        count = indexer.upsert_all_notes()
        print(f"Full sync completed: {count} notes indexed")


if __name__ == "__main__":
    main()