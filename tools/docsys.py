"""What the document system's tools share: where the repo is, and how a doc is parsed.

`pack.py` and `check_docs.py` both need to read frontmatter and to find the file paths a
"## Load" or "## Read" section lists in backticks. Keeping that in one place means the checker
validates exactly what the packer will try to load.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PATH_IN_BACKTICKS = re.compile(r"`([^`\s]+\.(?:md|py|glsl|toml|yml|yaml|txt))`")


def frontmatter(text: str) -> dict[str, str] | None:
    """Parse the `---` block at the top of a doc into a dict; None if it is missing."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    return fields


def section(text: str, heading: str) -> str:
    """Return the body of the '## <heading>' section, or '' if the doc has none."""
    out: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().lower().startswith(heading.lower())
            continue
        if inside:
            out.append(line)
    return "\n".join(out)


def listed_paths(text: str, heading: str) -> list[str]:
    """Paths written in backticks inside one section, in order, without duplicates."""
    found: list[str] = []
    for match in PATH_IN_BACKTICKS.finditer(section(text, heading)):
        path = match.group(1)
        if path not in found:
            found.append(path)
    return found
