from unittest.mock import MagicMock, patch

from app.services.indexer import Indexer, _chunk_text


def test_chunk_text_simple():
    text = "line1\nline2\nline3"
    chunks = _chunk_text(text, chunk_size=10, overlap=2)
    assert len(chunks) >= 1


def test_chunk_text_empty():
    chunks = _chunk_text("", chunk_size=10, overlap=2)
    assert chunks == []


def test_chunk_text_long_line():
    long_line = "a" * 200 + "\n" + "b" * 200
    chunks = _chunk_text(long_line, chunk_size=100, overlap=10)
    assert len(chunks) >= 2


@patch("app.services.indexer.CHROMA_AVAILABLE", False)
def test_indexer_without_chroma():
    with patch("app.services.indexer.get_chroma_client", return_value=None):
        indexer = Indexer(vault_path="/tmp/nonexistent")
        assert indexer.collection is None


@patch("app.services.indexer.CHROMA_AVAILABLE", False)
def test_indexer_upsert_note_no_chroma(tmp_path, caplog):
    with caplog.at_level("WARNING"):
        indexer = Indexer(vault_path=str(tmp_path))

        test_md = tmp_path / "testnote.md"
        test_md.write_text("---\ntitle: Test\n---\n# Test Note\nContent here.")

        note = indexer.vault_reader.read_note(test_md)
        indexer.upsert_note(note["id"], note["title"], note["content"], note["path"])

        assert any("ChromaDB" in record.message or "not available" in record.message for record in caplog.records)


def test_indexer_on_file_change_delete(tmp_path):
    with patch("app.services.indexer.CHROMA_AVAILABLE", False):
        indexer = Indexer(vault_path=str(tmp_path))
        indexer.on_file_change("DELETE", str(tmp_path / "deleted.md"))


@patch("app.services.indexer.CHROMA_AVAILABLE", True)
@patch("app.services.indexer.get_chroma_client")
def test_indexer_upsert_with_mock_collection(mock_get_client, tmp_path):
    mock_collection = MagicMock()
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_get_client.return_value = mock_client

    indexer = Indexer(vault_path=str(tmp_path))
    _ = indexer.collection

    test_md = tmp_path / "testnote.md"
    test_md.write_text("---\ntitle: Test\n---\n# Test Note\nContent here.")
    note = indexer.vault_reader.read_note(test_md)

    indexer.upsert_note(note["id"], note["title"], note["content"], note["path"])

    assert mock_collection.upsert.called


@patch("app.services.indexer.CHROMA_AVAILABLE", True)
@patch("app.services.indexer.get_chroma_client")
def test_indexer_delete_with_mock_collection(mock_get_client, tmp_path):
    mock_collection = MagicMock()
    mock_collection.get.return_value = {"ids": ["note1_0", "note1_1"]}
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_get_client.return_value = mock_client

    indexer = Indexer(vault_path=str(tmp_path))
    _ = indexer.collection

    indexer.delete_note("note1")

    assert mock_collection.delete.called