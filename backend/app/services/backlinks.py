"""
BacklinksService — 倒排索引服务

负责维护笔记的反向链接索引（note_id → [note_ids that link to it]）。
数据存储在 vault/.kkb/backlinks.json。
"""

import json
import logging
import re
from pathlib import Path
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

# 正则：匹配 [[笔记名]] 和 [[笔记名|显示文本]]
_WIKI_LINK_PATTERN = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")

# 当前索引版本，每次不兼容变更时递增
_INDEX_VERSION = 1

# 上下文片段最大字符数
_CONTEXT_SNIPPET_MAX = 200


class BacklinksService:
    def __init__(self, vault_path: str | None = None, index_path: Path | None = None):
        self.vault_path = vault_path or settings.VAULT_PATH
        self.index_path = index_path or Path(self.vault_path) / ".kkb" / "backlinks.json"

        # 确保 .kkb 目录存在
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

        # 内存中的索引：{ "被引用的 note_id": [引用者的 note_id, ...] }
        self._index: dict[str, list[str]] = {}
        self._version = _INDEX_VERSION
        self._last_updated: str | None = None

        self._load_or_rebuild()

    # ─── 内部工具 ──────────────────────────────────────────────────────────────

    def _load_or_rebuild(self):
        """尝试从磁盘加载索引，失败则全量重建。"""
        try:
            if self.index_path.exists():
                data = json.loads(self.index_path.read_text(encoding="utf-8"))
                if data.get("version") == _INDEX_VERSION:
                    self._version = data["version"]
                    self._last_updated = data.get("last_updated")
                    self._index = data.get("backlinks", {})
                    logger.info(f"[Backlinks] Loaded index from {self.index_path}")
                    return
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"[Backlinks] Failed to load index: {e}")

        # 加载失败或不兼容，全量重建
        logger.info("[Backlinks] Rebuilding full index...")
        self.rebuild_full_index()

    def _persist(self):
        """将内存索引写入磁盘。"""
        from datetime import datetime, timezone

        data = {
            "version": self._version,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "backlinks": self._index,
        }
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self._last_updated = data["last_updated"]

    def get_index_state(self) -> dict[str, Any]:
        """返回当前索引的完整状态（用于测试和调试）。"""
        return {
            "version": self._version,
            "last_updated": self._last_updated,
            "backlinks": self._index,
        }

    @staticmethod
    def _extract_forward_links(content: str) -> list[str]:
        """从笔记内容中提取所有 wiki link 的 note_id。"""
        matches = _WIKI_LINK_PATTERN.findall(content)
        # 去重，保持顺序
        seen = set()
        result = []
        for m in matches:
            note_id = m.strip()
            if note_id and note_id not in seen:
                seen.add(note_id)
                result.append(note_id)
        return result

    def _context_around_link(self, source_note_id: str, target_note_id: str) -> str:
        """在源笔记内容中查找引用目标笔记的那一行作为上下文片段。"""
        target_link = f"[[{target_note_id}]]"
        # 也匹配别名形式 [[note_id|alias]]
        alias_pattern = f"[[{re.escape(target_note_id)}|"
        try:
            for md_file in Path(self.vault_path).rglob("*.md"):
                if md_file.stem == source_note_id:
                    content = md_file.read_text(encoding="utf-8")
                    for line in content.splitlines():
                        if target_link in line or alias_pattern in line:
                            snippet = line.strip()
                            if len(snippet) > _CONTEXT_SNIPPET_MAX:
                                snippet = snippet[:_CONTEXT_SNIPPET_MAX] + "..."
                            return snippet
                    # 找到了文件但没找到那一行，返回文件开头
                    return content.splitlines()[0][:_CONTEXT_SNIPPET_MAX] if content else ""
        except OSError:
            pass
        return ""

    # ─── FileWatcher 集成接口 ───────────────────────────────────────────────

    def on_file_change(self, event_type: str, file_path: str):
        """
        供 FileWatcher 调用的增量更新接口。
        CREATED/MODIFIED：读取文件内容，提取 forward_links，调用 update_note
        DELETED：调用 delete_note
        """
        from app.services.vault_reader import VaultReader

        p = Path(file_path)
        note_id = p.stem

        if event_type in ("CREATE", "MODIFY"):
            try:
                vr = VaultReader(self.vault_path)
                note = vr.read_note(p)
                links = self._extract_forward_links(note["content"])
                self.update_note(note_id, links)
            except Exception:
                # 文件可能还在写入，跳过
                pass
        elif event_type == "DELETE":
            self.delete_note(note_id)

    # ─── 公共接口 ─────────────────────────────────────────────────────────────

    def rebuild_full_index(self) -> int:
        """
        全量重建倒排索引：扫描 vault 中所有 .md 文件。
        返回索引的链接总数。
        """
        from datetime import datetime, timezone

        self._index = {}

        for md_file in Path(self.vault_path).rglob("*.md"):
            if md_file.is_file() and not md_file.name.startswith("."):
                try:
                    note_id = md_file.stem
                    content = md_file.read_text(encoding="utf-8")
                    forward_links = self._extract_forward_links(content)

                    for target_id in forward_links:
                        # 链接到不存在的笔记不写入索引
                        if not self._note_exists(target_id):
                            continue
                        if target_id not in self._index:
                            self._index[target_id] = []
                        if note_id not in self._index[target_id]:
                            self._index[target_id].append(note_id)
                except OSError:
                    continue

        total_links = sum(len(v) for v in self._index.values())
        self._last_updated = datetime.now(timezone.utc).isoformat()
        self._persist()

        logger.info(f"[Backlinks] Full index rebuilt: {len(self._index)} notes have backlinks, {total_links} total link refs")
        return total_links

    def update_note(self, note_id: str, forward_links: list[str]):
        """
        增量更新：笔记 note_id 的 forward_links 变化了。
        1. 从所有旧的被引用者的 backlinks 中移除 note_id
        2. 添加到新的被引用者的 backlinks 中
        """
        # 找出旧的 forward_links（note_id 出现在谁的 backlinks 里）
        old_targets: set[str] = set()
        for target_id, sources in self._index.items():
            if note_id in sources:
                old_targets.add(target_id)

        # 从旧的 backlinks 中移除 note_id
        for target_id in old_targets:
            if target_id in self._index:
                self._index[target_id] = [s for s in self._index[target_id] if s != note_id]
                if not self._index[target_id]:
                    del self._index[target_id]

        # 添加到新的 backlinks 中
        for target_id in forward_links:
            if target_id == note_id:
                continue  # 不能自链接
            # 链接到不存在的笔记不写入索引
            if not self._note_exists(target_id):
                continue
            if target_id not in self._index:
                self._index[target_id] = []
            if note_id not in self._index[target_id]:
                self._index[target_id].append(note_id)

        self._persist()

    def delete_note(self, note_id: str):
        """删除笔记：从所有被引用者的 backlinks 中移除 note_id。"""
        # 先从 note_id 自己的出链关联中清理
        # 找出 note_id 被谁引用（作为 target），从那些 target 的 backlinks 中移除
        if note_id in self._index:
            del self._index[note_id]

        # 从所有其他笔记的 backlinks 中移除 note_id（作为 source）
        for target_id, sources in list(self._index.items()):
            if note_id in sources:
                self._index[target_id] = [s for s in sources if s != note_id]
                if not self._index[target_id]:
                    del self._index[target_id]

        self._persist()

    def get_backlinks(self, note_id: str) -> list[str]:
        """返回引用了 note_id 的所有笔记 ID。"""
        return list(self._index.get(note_id, []))

    def get_backlinks_with_context(self, note_id: str) -> list[dict[str, Any]]:
        """
        返回引用了 note_id 的所有笔记及其引用片段。
        返回格式：[{id, title, snippet}, ...]
        """
        results = []
        for source_id in self._index.get(note_id, []):
            snippet = self._context_around_link(source_id, note_id)
            title = self._get_note_title(source_id)
            results.append({
                "id": source_id,
                "title": title,
                "snippet": snippet,
            })
        return results

    # ─── 内部辅助 ─────────────────────────────────────────────────────────────

    def _note_exists(self, note_id: str) -> bool:
        """检查 vault 中是否存在指定 note_id 的笔记。"""
        for md_file in Path(self.vault_path).rglob("*.md"):
            if md_file.is_file() and md_file.stem == note_id:
                return True
        return False

    def _get_note_title(self, note_id: str) -> str:
        """根据 note_id 查找笔记标题。"""
        import frontmatter

        for md_file in Path(self.vault_path).rglob("*.md"):
            if md_file.is_file() and md_file.stem == note_id:
                try:
                    post = frontmatter.loads(md_file.read_text(encoding="utf-8"))
                    title = post.metadata.get("title")
                    if title:
                        return title
                    # 尝试从 # 标题行提取
                    match = re.search(r"^#\s+(.+)$", post.content, re.MULTILINE)
                    if match:
                        return match.group(1).strip()
                    return note_id
                except Exception:
                    return note_id
        return note_id


# ─── FastAPI 依赖注入 ─────────────────────────────────────────────────────────


def get_backlinks() -> BacklinksService:
    """FastAPI 依赖：返回 BacklinksService 单例（整个应用共享）"""
    global _backlinks_singleton
    if _backlinks_singleton is None:
        _backlinks_singleton = BacklinksService()
    return _backlinks_singleton


_backlinks_singleton: BacklinksService | None = None
