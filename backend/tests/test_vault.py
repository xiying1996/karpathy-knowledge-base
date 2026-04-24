import tempfile
from pathlib import Path

import pytest

from app.services.vault_reader import VaultReader


@pytest.fixture
def temp_vault(tmp_path):
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    return vault_dir


@pytest.fixture
def vault_reader(temp_vault):
    return VaultReader(vault_path=temp_vault)


def test_list_vault_files(vault_reader, temp_vault):
    (temp_vault / "note1.md").write_text("---\ntitle: Note 1\n---\n# Note 1\nContent")
    (temp_vault / "note2.md").write_text("---\ntitle: Note 2\n---\n# Note 2\nContent")
    sub_dir = temp_vault / "subdir"
    sub_dir.mkdir()
    (sub_dir / "note3.md").write_text("---\ntitle: Note 3\n---\n# Note 3\nContent")

    files = vault_reader.list_vault_files()

    assert len(files) == 3
    paths = [f["id"] for f in files]
    assert "note1.md" in paths
    assert "subdir/note3.md" in paths


def test_parse_frontmatter_with_title_tags_date(vault_reader):
    content = """---
title: My Note
tags:
  - tag1
  - tag2
date: 2026-04-24
---

# My Note
Content here
"""
    frontmatter, body = vault_reader.parse_frontmatter(content)

    assert frontmatter["title"] == "My Note"
    assert frontmatter["tags"] == ["tag1", "tag2"]
    assert frontmatter["date"] == "2026-04-24"
    assert "# My Note" in body


def test_parse_frontmatter_without_frontmatter(vault_reader):
    content = "# Just a heading\n\nSome content without frontmatter"
    frontmatter, body = vault_reader.parse_frontmatter(content)

    assert frontmatter == {}
    assert body == content


def test_parse_content_removes_obsidian_syntax(vault_reader):
    body = """# Heading

Some **bold** and *italic* text with [[obsidian links]].

## Sub heading

More content
"""
    parsed = vault_reader.parse_content(body)

    assert "# Heading" not in parsed
    assert "**bold**" not in parsed
    assert "[[obsidian links]]" not in parsed or "obsidian links" in parsed
    assert "Heading" in parsed


def test_get_note_returns_all_fields(vault_reader, temp_vault):
    note_path = temp_vault / "test_note.md"
    note_path.write_text("""---
title: Test Note
tags:
  - test
  - sample
date: 2026-04-24
aliases:
  - Alias1
---

# Test Note

This is the content of my note with some text.

Here is a link to [[Another Note]].
""")

    note = vault_reader.get_note(note_path)

    assert note["id"] == str(note_path)
    assert note["title"] == "Test Note"
    assert note["tags"] == ["test", "sample"]
    assert "excerpt" in note
    assert len(note["excerpt"]) <= 200
    assert "content" in note
    assert "links" in note
    assert "Another Note" in note["links"]


def test_get_note_extracts_title_from_content(vault_reader, temp_vault):
    note_path = temp_vault / "no_title.md"
    note_path.write_text("---\ntags: [test]\n---\n\n# Only Heading Here\n\nSome content")

    note = vault_reader.get_note(note_path)

    assert note["title"] == "Only Heading Here"


def test_get_note_uses_filename_when_no_title(vault_reader, temp_vault):
    note_path = temp_vault / "some_random_name.md"
    note_path.write_text("No frontmatter, no heading")

    note = vault_reader.get_note(note_path)

    assert note["title"] == "some_random_name"


def test_list_notes_returns_all_notes(vault_reader, temp_vault):
    (temp_vault / "a.md").write_text("---\ntitle: A\n---\n# A\n")
    (temp_vault / "b.md").write_text("---\ntitle: B\n---\n# B\n")

    notes = vault_reader.list_notes()

    assert len(notes) == 2
    titles = [n["title"] for n in notes]
    assert "A" in titles
    assert "B" in titles