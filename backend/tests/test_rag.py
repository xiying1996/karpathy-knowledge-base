from unittest.mock import MagicMock, patch

import pytest

from app.models import AskRequest
from app.routers.rag import ask


@pytest.fixture
def mock_rag_engine():
    with patch("app.routers.rag.get_rag_engine") as mock:
        engine = MagicMock()
        mock.return_value = engine
        yield engine


@pytest.mark.asyncio
async def test_ask_returns_answer_and_sources(mock_rag_engine):
    mock_rag_engine.ask.return_value = ("这是答案。", ["笔记A", "笔记B"])

    request = AskRequest(question="什么是第二大脑")
    response = await ask(request)

    assert response.answer == "这是答案。"
    assert response.sources == ["笔记A", "笔记B"]
    mock_rag_engine.ask.assert_called_once_with("什么是第二大脑", context_limit=5)


@pytest.mark.asyncio
async def test_ask_empty_sources(mock_rag_engine):
    mock_rag_engine.ask.return_value = ("没有找到相关内容。", [])

    request = AskRequest(question="完全不相关的问题")
    response = await ask(request)

    assert response.sources == []


@pytest.mark.asyncio
async def test_ask_respects_context_limit(mock_rag_engine):
    mock_rag_engine.ask.return_value = ("答案", [])

    request = AskRequest(question="测试", context_limit=3)
    await ask(request)

    mock_rag_engine.ask.assert_called_once_with("测试", context_limit=3)
