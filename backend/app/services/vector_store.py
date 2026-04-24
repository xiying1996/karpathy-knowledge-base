import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings


class VectorStore:
    def __init__(self):
        self._client = None
        self._collection = None

    @property
    def client(self):
        if self._client is None:
            self._client = chromadb.Client(
                ChromaSettings(
                    chroma_api_impl="rest",
                    chroma_server_host=settings.CHROMA_HOST,
                    chroma_server_http_port=settings.CHROMA_PORT,
                )
            )
        return self._client

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_collection("notes")
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