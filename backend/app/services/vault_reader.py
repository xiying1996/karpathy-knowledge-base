import re
from pathlib import Path
from typing import Any

import frontmatter


class VaultReader:
    _NOTE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]+$")
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)

    def _extract_wiki_links(self, content: str) -> list[str]:
        pattern = r"\[\[([^\]]+)\]\]"
        return re.findall(pattern, content)

    def _extract_title(self, content: str) -> str:
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""

    def _note_id_from_path(self, path: Path) -> str:
        return path.stem

    def read_note(self, note_path: Path) -> dict[str, Any]:
        post = frontmatter.loads(note_path.read_text(encoding="utf-8"))
        content = post.content
        metadata = post.metadata

        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        tags = [t if isinstance(t, str) else t.get("status", "") for t in tags]

        return {
            "id": self._note_id_from_path(note_path),
            "title": metadata.get("title") or self._extract_title(content),
            "content": content.strip(),
            "path": str(note_path.relative_to(self.vault_path)),
            "tags": tags,
            "links": self._extract_wiki_links(content),
            "created": str(metadata.get("date", "")) or None,
            "modified": None,
        }

    def list_notes(self, search: str | None = None) -> list[dict[str, Any]]:
        notes = []
        for md_file in self.vault_path.rglob("*.md"):
            if md_file.is_file() and not md_file.name.startswith("."):
                try:
                    note = self.read_note(md_file)
                    if search:
                        search_lower = search.lower()
                        if (
                            search_lower not in note["title"].lower()
                            and search_lower not in note["content"].lower()
                        ):
                            continue
                    notes.append(note)
                except Exception:
                    continue
        return sorted(notes, key=lambda n: n.get("created") or "", reverse=True)

    def get_note_by_id(self, note_id: str) -> dict[str, Any] | None:
        if not self._NOTE_ID_PATTERN.match(note_id):
            return None
        for md_file in self.vault_path.rglob("*.md"):
            if md_file.is_file() and md_file.stem == note_id:
                resolved = md_file.resolve()
                if not resolved.is_relative_to(self.vault_path.resolve()):
                    continue
                return self.read_note(md_file)
        return None