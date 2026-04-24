import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


class VaultReader:
    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    OBSIDIAN_LINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")
    WIKI_LINK_PATTERN = re.compile(r"!\[([^\]]*)\]\[([^\]]*)\]")
    MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^\)]+\)")
    HEADER_PATTERN = re.compile(r"^#{1,6}\s+", re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```")
    INLINE_CODE_PATTERN = re.compile(r"`([^`]+)`")
    BOLD_ITALIC_PATTERN = re.compile(r"\*\*\*([^\*]+)\*\*\*")
    ITALIC_PATTERN = re.compile(r"\*(?!\*)([^\*]+)\*")
    BOLD_PATTERN = re.compile(r"\*\*([^\*]+)\*\*")

    def __init__(self, vault_path: str | Path | None = None):
        self.vault_path = Path(vault_path) if vault_path else Path("./vault")

    def list_vault_files(self) -> list[dict[str, Any]]:
        files = []
        for md_path in self.vault_path.rglob("*.md"):
            rel_path = md_path.relative_to(self.vault_path)
            stat = md_path.stat()
            files.append({
                "id": str(rel_path),
                "path": str(md_path),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        return files

    def parse_frontmatter(self, content: str) -> tuple[dict[str, Any], str]:
        match = self.FRONTMATTER_PATTERN.match(content)
        if not match:
            return {}, content
        try:
            frontmatter = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            return {}, content
        body = content[match.end():]
        return self._normalize_frontmatter(frontmatter), body

    def _normalize_frontmatter(self, fm: dict[str, Any]) -> dict[str, Any]:
        normalized = {}
        for key, value in fm.items():
            lower_key = key.lower()
            if lower_key == "tags" and isinstance(value, list):
                normalized["tags"] = [str(t) for t in value]
            elif lower_key in ("date", "created", "modified"):
                normalized[lower_key] = str(value) if value else None
            else:
                normalized[lower_key] = value
        return normalized

    def parse_content(self, body: str) -> str:
        text = self.CODE_BLOCK_PATTERN.sub("", body)
        text = self.INLINE_CODE_PATTERN.sub(r"\1", text)
        text = self.BOLD_ITALIC_PATTERN.sub(r"\1", text)
        text = self.ITALIC_PATTERN.sub(r"\1", text)
        text = self.BOLD_PATTERN.sub(r"\1", text)
        text = self.OBSIDIAN_LINK_PATTERN.sub(r"\1", text)
        text = self.MARKDOWN_LINK_PATTERN.sub(r"\1", text)
        text = self.HEADER_PATTERN.sub("", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def read_file(self, file_path: str | Path) -> dict[str, Any]:
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        frontmatter, body = self.parse_frontmatter(content)
        stat = path.stat()
        return {
            "path": str(path),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "frontmatter": frontmatter,
            "body": body,
        }

    def get_note(self, file_path: str | Path) -> dict[str, Any]:
        info = self.read_file(file_path)
        fm = info["frontmatter"]
        body = info["body"]
        title = fm.get("title")
        if not title:
            title_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
            title = title_match.group(1) if title_match else Path(file_path).stem
        tags = fm.get("tags", [])
        excerpt = self.parse_content(body)[:200]
        return {
            "id": str(file_path),
            "title": title,
            "tags": tags,
            "modified": fm.get("date") or fm.get("modified") or info["modified"],
            "created": fm.get("created") or info["created"],
            "excerpt": excerpt,
            "content": self.parse_content(body),
            "links": self._extract_links(body),
        }

    def _extract_links(self, body: str) -> list[str]:
        return self.OBSIDIAN_LINK_PATTERN.findall(body)

    def list_notes(self) -> list[dict[str, Any]]:
        notes = []
        for file_info in self.list_vault_files():
            try:
                note = self.get_note(file_info["path"])
                notes.append(note)
            except Exception:
                continue
        return notes