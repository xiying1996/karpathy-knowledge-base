from unittest.mock import MagicMock, patch

import pytest

from app.models import SearchResponse
from app.routers.search import search_notes


@pytest.fixture
def mock_vector_store():
    with patch("app.routers.search.get_vector_store") as mock:
        store = MagicMock()
        mock.return_value = store
        yield store


@pytest.mark.asyncio
async def test_search_returns_results(mock_vector_store):
    mock_vector_store.query.return_value = [
        {
            "note_id": "概念-第二大脑",
            "title": "第二大脑",
            "snippet": "...第二大脑是一种...",
            "score": 0.92,
        }
    ]
    from app.models import SearchRequest
    response = await search_notes(SearchRequest(query="第二大脑"))
    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1
    assert response.results[0].title == "第二大脑"


@pytest.mark.asyncio
async def test_search_returns_empty_for_nonsense(mock_vector_store):
    mock_vector_store.query.return_value = []
    from app.models import SearchRequest
    response = await search_notes(SearchRequest(query="xyznonexistent123xyz"))
    assert isinstance(response, SearchResponse)
    assert len(response.results) == 0


@pytest.mark.asyncio
async def test_search_result_contains_snippet(mock_vector_store):
    mock_vector_store.query.return_value = [
        {
            "note_id": "概念-第二大脑",
            "title": "第二大脑",
            "snippet": "...第二大脑是一种利用...",
            "score": 0.92,
        }
    ]
    from app.models import SearchRequest
    response = await search_notes(SearchRequest(query="第二大脑"))
    assert hasattr(response.results[0], "snippet")
    assert "第二大脑" in response.results[0].snippet


@pytest.mark.asyncio
async def test_search_respects_limit(mock_vector_store):
    mock_vector_store.query.return_value = []
    from app.models import SearchRequest
    await search_notes(SearchRequest(query="test", limit=5))
    mock_vector_store.query.assert_called_once_with(query_texts=["test"], n_results=5)