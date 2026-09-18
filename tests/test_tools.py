"""The document system checks itself: budgets hold and every pack builds."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=ROOT, capture_output=True, text=True, check=False
    )


def test_check_docs_passes():
    # every doc has frontmatter, fits its budget, and points at files that exist
    result = run_tool("tools/check_docs.py")
    assert result.returncode == 0, result.stdout + result.stderr


def test_every_pack_builds():
    # each pack lists only files that exist, so pack.py can print a prompt for it
    packs = sorted((ROOT / "docs" / "packs").glob("*.md"))
    assert packs, "no packs found"
    for pack in packs:
        result = run_tool("tools/pack.py", str(pack))
        assert result.returncode == 0, f"{pack.name}: {result.stderr}"
        assert "===== FILE:" in result.stdout


def test_pack_with_task_appends_task():
    # a task card is appended last, after the files its Read section adds
    task = next((ROOT / "docs" / "tasks" / "todo").glob("0002-*.md"))
    result = run_tool("tools/pack.py", "docs/packs/implement.md", "--task", str(task))
    assert result.returncode == 0, result.stderr
    assert result.stdout.rstrip().count("===== TASK:") == 1
    assert result.stdout.index("===== FILE:") < result.stdout.index("===== TASK:")
