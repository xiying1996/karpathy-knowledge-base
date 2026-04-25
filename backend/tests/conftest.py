import pytest

from app.services.backlinks import BacklinksService


@pytest.fixture
def vault_root(tmp_path):
    """测试用 vault 根目录（tmp_path/vault/）"""
    vault = tmp_path / "vault"
    vault.mkdir()
    return vault


@pytest.fixture
def kkb_dir(vault_root):
    """.kkb 目录（每个测试独立）"""
    kkb = vault_root / ".kkb"
    kkb.mkdir(exist_ok=True)
    return kkb


@pytest.fixture
def empty_vault(vault_root):
    """空 vault（含 demo 子目录）"""
    demo = vault_root / "demo"
    demo.mkdir()
    return vault_root


@pytest.fixture
def backlinks_service(empty_vault, kkb_dir):
    return BacklinksService(vault_path=str(empty_vault), index_path=kkb_dir / "backlinks.json")


@pytest.fixture
def vault_with_notes(vault_root):
    """创建测试用 vault，包含多个相互链接的笔记（每个测试独立）"""
    demo = vault_root / "demo"
    demo.mkdir()

    # 笔记 A：引用 B 和 C
    (demo / "Note-A.md").write_text(
        "---\ntitle: Note A\n---\n# Note A\n\nThis is [[Note-B]] and [[Note-C]].\n",
        encoding="utf-8",
    )
    # 笔记 B：引用 C
    (demo / "Note-B.md").write_text(
        "---\ntitle: Note B\n---\n# Note B\n\nReference [[Note-C]].\n",
        encoding="utf-8",
    )
    # 笔记 C：无人引用（孤立节点）
    (demo / "Note-C.md").write_text(
        "---\ntitle: Note C\n---\n# Note C\n\nIndependent note.\n",
        encoding="utf-8",
    )
    # 笔记 D：使用别名语法，引用 A 和 C
    (demo / "Note-D.md").write_text(
        "---\ntitle: Note D\n---\n# Note D\n\nSee [[Note-A|alias for Note A]] and [[Note-C]].\n",
        encoding="utf-8",
    )
    return vault_root
