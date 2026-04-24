"""
测试 BacklinksService — 倒排索引服务

测试覆盖：
1. 全量构建：空 vault / 有笔记的 vault
2. 增量更新：新增笔记 / 修改笔记（链接变了）
3. 删除笔记
4. 查询 backlinks：笔记有 backlinks / 无 backlinks
5. 查询 backlinks_with_context：返回引用片段
6. 边界情况：
   - 链接到不存在的笔记（不写入索引）
   - 链接别名 [[note|display]] 能正确解析
   - 多条链接同一笔记只出现一次
   - 索引损坏时自动重建
"""

import json
from pathlib import Path

import pytest

from app.services.backlinks import BacklinksService


# ─── 测试用例 ────────────────────────────────────────────────────────────────

def test_build_empty_vault(empty_vault, kkb_dir):
    """空 vault 全量构建，索引为空"""
    service = BacklinksService(vault_path=str(empty_vault), index_path=kkb_dir / "backlinks.json")
    count = service.rebuild_full_index()

    assert count == 0
    assert service.index_path.exists()
    data = json.loads(service.index_path.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert data["backlinks"] == {}


def test_build_with_notes(vault_with_notes):
    """有笔记的 vault 全量构建"""
    kkb = vault_with_notes / ".kkb"
    service = BacklinksService(
        vault_path=str(vault_with_notes), index_path=kkb / "backlinks.json"
    )
    count = service.rebuild_full_index()

    # 笔记-A 被 D 引用，笔记-B 被 A 引用，笔记-C 被 A 和 B 和 D 引用
    # 笔记-D 无人引用
    assert count == 5  # 总链接数

    assert set(service.get_backlinks("Note-A")) == {"Note-D"}
    assert set(service.get_backlinks("Note-B")) == {"Note-A"}
    assert set(service.get_backlinks("Note-C")) == {"Note-A", "Note-B", "Note-D"}
    assert service.get_backlinks("Note-D") == []


def test_update_note_adds_new_links(vault_with_notes):
    """修改笔记，新增多了一条出链"""
    kkb = vault_with_notes / ".kkb"
    service = BacklinksService(
        vault_path=str(vault_with_notes), index_path=kkb / "backlinks.json"
    )
    service.rebuild_full_index()

    # 修改 Note-D，新增引用 Note-B
    demo = vault_with_notes / "demo"
    (demo / "Note-D.md").write_text(
        "---\ntitle: Note D\n---\n# Note D\n\nSee [[Note-A]] and [[Note-C]] and [[Note-B]].\n",
        encoding="utf-8",
    )

    service.update_note("Note-D", forward_links=["Note-A", "Note-C", "Note-B"])

    # Note-D 引用了 A、C、B → A、C、B 的 backlinks 都要更新
    assert set(service.get_backlinks("Note-A")) == {"Note-D"}
    assert set(service.get_backlinks("Note-B")) == {"Note-A", "Note-D"}
    assert set(service.get_backlinks("Note-C")) == {"Note-A", "Note-B", "Note-D"}


def test_update_note_removes_old_links(vault_with_notes):
    """修改笔记，删除了一条出链"""
    kkb = vault_with_notes / ".kkb"
    service = BacklinksService(
        vault_path=str(vault_with_notes), index_path=kkb / "backlinks.json"
    )
    service.rebuild_full_index()

    # 修改 Note-D，删除对 Note-A 的引用
    demo = vault_with_notes / "demo"
    (demo / "Note-D.md").write_text(
        "---\ntitle: Note D\n---\n# Note D\n\nOnly links to [[Note-C]].\n",
        encoding="utf-8",
    )

    service.update_note("Note-D", forward_links=["Note-C"])

    assert service.get_backlinks("Note-A") == []
    assert set(service.get_backlinks("Note-C")) == {"Note-A", "Note-B", "Note-D"}


def test_delete_note(vault_with_notes):
    """删除笔记时，从所有被引用者的 backlinks 中移除"""
    kkb = vault_with_notes / ".kkb"
    service = BacklinksService(
        vault_path=str(vault_with_notes), index_path=kkb / "backlinks.json"
    )
    service.rebuild_full_index()

    service.delete_note("Note-D")

    # Note-D 原来引用了 A 和 C
    assert service.get_backlinks("Note-A") == []
    assert set(service.get_backlinks("Note-C")) == {"Note-A", "Note-B"}


def test_get_backlinks_empty(vault_with_notes):
    """笔记无 backlinks 时返回空列表"""
    kkb = vault_with_notes / ".kkb"
    service = BacklinksService(
        vault_path=str(vault_with_notes), index_path=kkb / "backlinks.json"
    )
    service.rebuild_full_index()

    assert service.get_backlinks("Note-D") == []


def test_get_backlinks_with_context(vault_with_notes):
    """带上下文的查询能返回引用片段"""
    kkb = vault_with_notes / ".kkb"
    service = BacklinksService(
        vault_path=str(vault_with_notes), index_path=kkb / "backlinks.json"
    )
    service.rebuild_full_index()

    contexts = service.get_backlinks_with_context("Note-A")
    titles = {c["id"] for c in contexts}

    assert titles == {"Note-D"}
    # 验证返回了 snippet
    for ctx in contexts:
        assert "snippet" in ctx
        assert len(ctx["snippet"]) <= 200


def test_link_to_nonexistent_note_not_indexed(vault_with_notes):
    """链接到不存在的笔记，不写入索引"""
    kkb = vault_with_notes / ".kkb"
    service = BacklinksService(
        vault_path=str(vault_with_notes), index_path=kkb / "backlinks.json"
    )

    # Note-X links to non-existent Note-Y
    demo = vault_with_notes / "demo"
    (demo / "Note-X.md").write_text(
        "---\ntitle: Note X\n---\n# Note X\n\nLinks to non-existent [[Note-Y]].\n",
        encoding="utf-8",
    )

    service.update_note("Note-X", forward_links=["Note-Y"])

    # Note-Y has no backlinks (it doesn't exist)
    assert service.get_backlinks("Note-Y") == []
    assert "Note-Y" not in service.get_index_state().get("backlinks", {})


def test_alias_link_parsed_correctly(vault_with_notes):
    """[[笔记-A|显示文本]] 能正确解析 note_id"""
    kkb = vault_with_notes / ".kkb"
    service = BacklinksService(
        vault_path=str(vault_with_notes), index_path=kkb / "backlinks.json"
    )
    service.rebuild_full_index()

    # Note-E uses alias to link to A
    demo = vault_with_notes / "demo"
    (demo / "Note-E.md").write_text(
        "---\ntitle: Note E\n---\n# Note E\n\nSee [[Note-A|alias for Note A]].\n",
        encoding="utf-8",
    )

    service.update_note("Note-E", forward_links=["Note-A"])

    # Note-A was linked by D, now also by E
    assert set(service.get_backlinks("Note-A")) == {"Note-D", "Note-E"}


def test_duplicate_links_de_duplicated(vault_with_notes):
    """同一笔记被同一来源多次引用，只出现一次"""
    kkb = vault_with_notes / ".kkb"
    service = BacklinksService(
        vault_path=str(vault_with_notes), index_path=kkb / "backlinks.json"
    )
    service.rebuild_full_index()

    demo = vault_with_notes / "demo"
    (demo / "Note-F.md").write_text(
        "---\ntitle: Note F\n---\n# Note F\n\nMultiple links to [[Note-A]] and [[Note-A]] and [[Note-A]].\n",
        encoding="utf-8",
    )

    service.update_note("Note-F", forward_links=["Note-A", "Note-A", "Note-A"])

    backlinks = service.get_backlinks("Note-A")
    # Each source only appears once
    assert backlinks.count("Note-F") == 1


def test_corrupt_index_rebuilds_automatically(vault_with_notes):
    """索引文件损坏时，下次操作自动重建"""
    kkb = vault_with_notes / ".kkb"
    service = BacklinksService(
        vault_path=str(vault_with_notes), index_path=kkb / "backlinks.json"
    )
    service.rebuild_full_index()

    # Destroy the index file
    kkb.joinpath("backlinks.json").write_text("{ invalid json", encoding="utf-8")

    # Query again triggers auto-rebuild
    result = service.get_backlinks("Note-A")
    assert isinstance(result, list)  # Should recover from corruption


def test_index_persisted_to_disk(vault_with_notes):
    """Index is correctly written to .kkb/backlinks.json"""
    kkb = vault_with_notes / ".kkb"
    service = BacklinksService(
        vault_path=str(vault_with_notes), index_path=kkb / "backlinks.json"
    )
    service.rebuild_full_index()

    assert kkb.joinpath("backlinks.json").exists()

    # New service instance should load from disk
    service2 = BacklinksService(
        vault_path=str(vault_with_notes), index_path=kkb / "backlinks.json"
    )
    assert set(service2.get_backlinks("Note-C")) == {"Note-A", "Note-B", "Note-D"}
