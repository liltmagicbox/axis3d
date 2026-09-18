"""Check that the document system stays small and consistent.

Usage:
    uv run python tools/check_docs.py          # exit 1 on any error

Checks: every doc has frontmatter with `kind` and `brief_ko`; each kind respects its
line budget (docs/README.md lists them); packs and tasks point at files that exist;
decision ids are unique; task cards name a real pack and role.
"""

from __future__ import annotations

import sys
from pathlib import Path

from docsys import DOCS, ROOT, frontmatter, listed_paths

# Max lines per document kind, frontmatter included. None = no limit (append-only ledgers).
BUDGET: dict[str, int | None] = {
    "entry": 60,
    "map": 160,
    "role": 70,
    "rule": 60,
    "spec": 140,
    "variant": 90,
    "decision": 50,
    "pack": 40,
    "task": 60,
    "template": 60,
    "discussion": 80,
    "tour": 120,
    "record": None,
}
# Which section of a doc names files that tools/pack.py will load, per kind.
LOADED_FROM = {"pack": "Load", "task": "Read"}


def check_doc(path: Path, errors: list[str]) -> dict[str, str]:
    """Run the per-document checks; append problems to `errors`; return the frontmatter."""
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8")
    meta = frontmatter(text)
    if meta is None:
        errors.append(f"{rel}: missing frontmatter (--- kind: ... brief_ko: ... ---)")
        return {}
    for key in ("kind", "brief_ko"):
        if not meta.get(key):
            errors.append(f"{rel}: frontmatter lacks `{key}`")
    kind = meta.get("kind", "")
    if kind not in BUDGET:
        errors.append(f"{rel}: unknown kind `{kind}`")
        return meta

    limit = BUDGET[kind]
    lines = text.count("\n") + 1
    if limit is not None and lines > limit:
        errors.append(f"{rel}: {lines} lines > budget {limit} for kind `{kind}`")

    if kind in LOADED_FROM:
        for ref in listed_paths(text, LOADED_FROM[kind]):
            if kind == "task" and not ref.startswith("docs"):
                continue  # a card may read code that an earlier, unfinished card creates
            if not (ROOT / ref).is_file():
                errors.append(f"{rel}: `## {LOADED_FROM[kind]}` names a missing file `{ref}`")
    return meta


def check_task(path: Path, meta: dict[str, str], errors: list[str]) -> None:
    """A task card must name a pack and a role that exist."""
    rel = path.relative_to(ROOT).as_posix()
    if not (DOCS / "packs" / f"{meta.get('pack', '')}.md").is_file():
        errors.append(f"{rel}: pack `{meta.get('pack')}` not found in docs/packs/")
    if not (DOCS / "roles" / f"{meta.get('role', '')}.md").is_file():
        errors.append(f"{rel}: role `{meta.get('role')}` not found in docs/roles/")


def main() -> int:
    errors: list[str] = []
    decision_ids: dict[str, str] = {}
    paths = sorted(DOCS.rglob("*.md")) + [ROOT / "AGENTS.md"]
    for path in paths:
        meta = check_doc(path, errors)
        kind = meta.get("kind")
        if kind == "task":
            check_task(path, meta, errors)
        if kind == "decision":
            doc_id = meta.get("id", "")
            if not path.name.startswith(doc_id + "-"):
                errors.append(f"{path.name}: filename does not start with id `{doc_id}-`")
            if doc_id in decision_ids:
                errors.append(
                    f"{path.name}: duplicate decision id {doc_id} ({decision_ids[doc_id]})"
                )
            decision_ids[doc_id] = path.name

    for error in errors:
        print(f"ERROR {error}")
    print(f"check_docs: {len(paths)} documents, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
