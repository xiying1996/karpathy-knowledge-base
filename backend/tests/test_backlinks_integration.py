"""
测试 BacklinksService 与 FileWatcher 的集成：
1. FileWatcher 检测到文件变化时，BacklinksService 同步更新索引
2. 启动时同时重建 Backlinks 索引
"""

import time
from pathlib import Path

import pytest

from app.services.backlinks import BacklinksService
from app.services.file_watcher import FileWatcher


def test_file_watcher_triggers_backlinks_update(vault_root, kkb_dir):
    """
    场景：FileWatcher 检测到 Note-A 创建（引用 Note-B），然后修改 Note-A（不再引用 B）。
    验证：B 的 backlinks 从有 A 变为无 A。
    """
    vault = vault_root
    demo = vault / "demo"
    demo.mkdir(exist_ok=True)

    # 创建 Note-B（被引用者）
    (demo / "Note-B.md").write_text(
        "---\ntitle: Note B\n---\n# Note B\n\nIndependent note.\n",
        encoding="utf-8",
    )

    # 初始化 BacklinksService（全量构建）
    backlinks = BacklinksService(
        vault_path=str(vault), index_path=kkb_dir / "backlinks.json"
    )
    backlinks.rebuild_full_index()
    assert backlinks.get_backlinks("Note-B") == []

    # FileWatcher on_change 触发 BacklinksService 增量更新
    def on_backlinks_change(event_type: str, file_path: str):
        p = Path(file_path)
        note_id = p.stem
        if event_type in ("CREATE", "MODIFY"):
            try:
                content = p.read_text(encoding="utf-8")
                links = BacklinksService._extract_forward_links(content)
                backlinks.update_note(note_id, links)
            except Exception:
                pass
        elif event_type == "DELETE":
            backlinks.delete_note(note_id)

    watcher = FileWatcher(
        vault_path=str(vault),
        mode="poll",
        poll_interval=1,
        debounce=0.5,
        on_change=on_backlinks_change,
    )
    watcher.start()
    time.sleep(1.5)

    # 创建 Note-A，引用 Note-B
    (demo / "Note-A.md").write_text(
        "---\ntitle: Note A\n---\n# Note A\n\nLinks to [[Note-B]].\n",
        encoding="utf-8",
    )
    time.sleep(2.5)  # poll interval + debounce

    assert "Note-A" in backlinks.get_backlinks("Note-B")

    # 修改 Note-A，删除对 B 的引用
    (demo / "Note-A.md").write_text(
        "---\ntitle: Note A\n---\n# Note A\n\nNo links.\n",
        encoding="utf-8",
    )
    time.sleep(2.5)

    # B 的 backlinks 不再包含 A
    assert "Note-A" not in backlinks.get_backlinks("Note-B")
    watcher.stop()


def test_startup_rebuilds_backlinks_index(vault_root, kkb_dir):
    """
    验证：应用启动时 BacklinksService 全量重建索引。
    """
    vault = vault_root
    demo = vault / "demo"
    demo.mkdir(exist_ok=True)

    # 创建 3 篇相互链接的笔记
    (demo / "Note-X.md").write_text(
        "---\ntitle: Note X\n---\n# Note X\n\nLinks to [[Note-Y]] and [[Note-Z]].\n",
        encoding="utf-8",
    )
    (demo / "Note-Y.md").write_text(
        "---\ntitle: Note Y\n---\n# Note Y\n\nLinks to [[Note-Z]].\n",
        encoding="utf-8",
    )
    (demo / "Note-Z.md").write_text(
        "---\ntitle: Note Z\n---\n# Note Z\n\nIndependent.\n",
        encoding="utf-8",
    )

    # 模拟启动时全量重建
    backlinks = BacklinksService(
        vault_path=str(vault), index_path=kkb_dir / "backlinks.json"
    )
    count = backlinks.rebuild_full_index()

    assert count == 3  # X→Y, X→Z, Y→Z
    assert set(backlinks.get_backlinks("Note-Y")) == {"Note-X"}
    assert set(backlinks.get_backlinks("Note-Z")) == {"Note-X", "Note-Y"}
    assert backlinks.get_backlinks("Note-X") == []
