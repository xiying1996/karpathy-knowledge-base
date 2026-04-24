import logging
from typing import Any

import httpx

from app.config import settings
from app.services.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG engine: retrieve context from vector store, generate answer via LLM."""

    def __init__(self, model: str | None = None):
        self.model = model
        self._vector_store = get_vector_store()

    def _get_llm_config(self) -> tuple[str, str, str]:
        """根据 provider 返回 (api_key, base_url, model)"""
        match settings.LLM_PROVIDER:
            case "deepseek":
                return settings.DEEPSEEK_API_KEY, settings.DEEPSEEK_BASE_URL, settings.DEEPSEEK_MODEL
            case _:  # minimax as default
                return settings.MINIMAX_API_KEY, settings.MINIMAX_BASE_URL, settings.MINIMAX_MODEL

    def retrieve(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Retrieve top-k relevant chunks from vector store."""
        try:
            return self._vector_store.query(query_texts=[query], n_results=limit)
        except Exception as e:
            logger.error(f"[RAG] Vector store query failed: {e}")
            return []

    def generate(self, question: str, contexts: list[dict[str, Any]]) -> tuple[str, list[str]]:
        """
        Generate answer using OpenAI-compatible API with retrieved context.
        Returns (answer, source_titles).
        """
        if not contexts:
            return "抱歉，我在你的知识库中没有找到相关的内容。", []

        context_texts = []
        source_titles = []
        for ctx in contexts:
            title = ctx.get("title", "未知笔记")
            snippet = ctx.get("snippet", "")
            context_texts.append(f"- [[{title}]]\n  {snippet}")
            if title not in source_titles:
                source_titles.append(title)

        context_block = "\n\n".join(context_texts)

        prompt = f"""你是一个个人知识库助手。请基于以下笔记片段回答问题。
如果笔记中没有相关信息，请明确说明。

## 笔记片段
{context_block}

## 问题
{question}

请用简洁、有条理的方式回答，并在回答末尾注明来源笔记。"""

        api_key, base_url, model = self._get_llm_config()

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "你是一个个人知识库助手。"},
                            {"role": "user", "content": prompt}
                        ],
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                answer = result["choices"][0]["message"]["content"].strip()
                return answer, source_titles
        except httpx.ConnectError:
            logger.error(f"[RAG] Cannot connect to {settings.LLM_PROVIDER}")
            return f"抱歉，AI 服务（{settings.LLM_PROVIDER}）当前不可用，请检查配置。", source_titles
        except httpx.TimeoutException:
            logger.error(f"[RAG] {settings.LLM_PROVIDER} request timed out")
            return "抱歉，AI 生成超时，请稍后重试。", source_titles
        except Exception as e:
            logger.error(f"[RAG] {settings.LLM_PROVIDER} generate failed: {e}")
            return "抱歉，AI 生成时发生错误。", source_titles

    def ask(self, question: str, context_limit: int = 5) -> tuple[str, list[str]]:
        """
        Full RAG pipeline: retrieve + generate.
        Returns (answer, source_titles).
        """
        contexts = self.retrieve(question, limit=context_limit)
        return self.generate(question, contexts)


_rag_engine: RAGEngine | None = None


def get_rag_engine() -> RAGEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
