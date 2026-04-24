import chromadb
from chromadb import HttpClient

from app.config import settings


class VectorStore:
    def __init__(self):
        self._client = None
        self._collection = None

    @property
    def client(self):
        if self._client is None:
            host = settings.CHROMA_HOST.split(":")[0] if ":" in settings.CHROMA_HOST else settings.CHROMA_HOST
            port = settings.CHROMA_PORT
            self._client = HttpClient(host=host, port=port)
        return self._client

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection("notes")
        return self._collection

    def query(
        self, query_texts: list[str], n_results: int = 10
    ) -> list[dict]:
        results = self.collection.query(
            query_texts=query_texts,
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        processed = []
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]
            score = 1.0 - distance
            content = doc
            match_pos = doc.lower().find(query_texts[0].lower())
            if match_pos >= 0:
                start = max(0, match_pos - 50)
                end = min(len(content), match_pos + len(query_texts[0]) + 50)
                snippet = content[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."
            else:
                snippet = content[:100] + "..." if len(content) > 100 else content

            processed.append({
                "note_id": metadata.get("note_id", ""),
                "title": metadata.get("title", ""),
                "snippet": snippet,
                "score": score,
            })
        return processed


_vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store