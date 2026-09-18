"""Create a decision, task card, or discussion digest from its template with the next id.

Usage:
    uv run python tools/new.py decision "Z-up world space"
    uv run python tools/new.py task "Table: SoA columns" --pack implement --role implementer
    uv run python tools/new.py discussion "camera rig options"

Prints the path of the new file. Templates live in docs/templates/ and use {{placeholders}}.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path

from docsys import DOCS, ROOT

TARGET_DIR = {
    "decision": DOCS / "decisions",
    "task": DOCS / "tasks" / "todo",
    "discussion": DOCS / "records" / "discussions",
}


def slugify(title: str) -> str:
    """'Table: SoA columns' -> 'table-soa-columns'."""
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def copyable_block(template_text: str) -> str:
    """The part of a template between its two ```` lines; the whole text if it has none."""
    lines = template_text.splitlines()
    fences = [i for i, line in enumerate(lines) if line.strip() == "````"]
    if len(fences) < 2:
        return template_text
    return "\n".join(lines[fences[0] + 1 : fences[1]]) + "\n"


def next_id(folder: Path, done_folder: Path | None = None) -> str:
    """Highest NNNN- prefix in the folder(s) plus one, as a 4-digit string."""
    folders = [folder] + ([done_folder] if done_folder else [])
    numbers = [
        int(p.name[:4]) for f in folders if f.exists() for p in f.glob("[0-9][0-9][0-9][0-9]-*.md")
    ]
    return f"{max(numbers, default=0) + 1:04d}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("kind", choices=sorted(TARGET_DIR))
    parser.add_argument("title")
    parser.add_argument("--pack", default="implement")
    parser.add_argument("--role", default="implementer")
    args = parser.parse_args()

    folder = TARGET_DIR[args.kind]
    folder.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    if args.kind == "discussion":
        doc_id = today
    elif args.kind == "task":
        doc_id = next_id(folder, DOCS / "tasks" / "done")
    else:
        doc_id = next_id(folder)

    template = DOCS / "templates" / f"{'adr' if args.kind == 'decision' else args.kind}.md"
    text = copyable_block(template.read_text(encoding="utf-8"))
    fill = {
        "id": doc_id,
        "title": args.title,
        "slug": slugify(args.title),
        "date": today,
        "pack": args.pack,
        "role": args.role,
    }
    for key, value in fill.items():
        text = text.replace("{{" + key + "}}", value)

    out = folder / f"{doc_id}-{slugify(args.title)}.md"
    if out.exists():
        raise SystemExit(f"new.py: {out} already exists")
    out.write_text(text, encoding="utf-8")
    print(out.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
