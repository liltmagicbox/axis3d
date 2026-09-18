"""Concatenate the documents a pack lists into one prompt for a sub-model.

Usage:
    uv run python tools/pack.py docs/packs/implement.md --task docs/tasks/todo/0003-ecs-table.md
    uv run python tools/pack.py docs/packs/review.md --stats

A pack is a markdown file with a "## Load" section listing files in order.
A task card may add files under its "## Read" section. The prompt goes to stdout;
"--stats" prints a size table to stderr so you can see what the model will pay for.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from docsys import ROOT, listed_paths


def build(pack_path: Path, task_path: Path | None) -> tuple[str, list[tuple[str, int]]]:
    """Return (prompt_text, [(path, line_count), ...]) for a pack and an optional task card."""
    paths = listed_paths(pack_path.read_text(encoding="utf-8"), "Load")
    task_text = task_path.read_text(encoding="utf-8") if task_path else ""
    for path in listed_paths(task_text, "Read"):
        if path not in paths:
            paths.append(path)

    pieces: list[str] = []
    stats: list[tuple[str, int]] = []
    for rel in paths:
        file = ROOT / rel
        if not file.is_file():
            sys.exit(f"pack.py: missing file listed in pack or task: {rel}")
        text = file.read_text(encoding="utf-8")
        pieces.append(f"===== FILE: {rel} =====\n{text}\n\n")
        stats.append((rel, text.count("\n") + 1))
    if task_path:
        rel = task_path.resolve().relative_to(ROOT).as_posix()
        pieces.append(f"===== TASK: {rel} =====\n{task_text}\n")
        stats.append((rel, task_text.count("\n") + 1))
    return "".join(pieces), stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pack", type=Path, help="pack file, e.g. docs/packs/implement.md")
    parser.add_argument("--task", type=Path, help="task card to append")
    parser.add_argument("--stats", action="store_true", help="print sizes to stderr")
    args = parser.parse_args()

    prompt, stats = build(args.pack, args.task)
    if args.stats:
        for rel, lines in stats:
            print(f"{lines:5d}  {rel}", file=sys.stderr)
        total = sum(lines for _, lines in stats)
        print(f"{total:5d}  lines total, ~{len(prompt) // 4} tokens", file=sys.stderr)
    sys.stdout.write(prompt)


if __name__ == "__main__":
    main()
