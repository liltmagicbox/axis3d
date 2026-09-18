---
kind: decision
id: 0001
title: The engine lives in the axis3d repository as src/axis3d; earlier experiments stay untouched
status: accepted
date: 2026-09-18
decided_by: ai
confidence: medium
reversible: yes — renaming the package is a search-and-replace plus this ADR's successor
brief_ko: 새 엔진은 axis3d 저장소의 src/axis3d 패키지로 만든다. 루트의 옛 실험 파일과 new3dkatsu는 건드리지 않는다.
---
# 0001 — Host repository and package layout

## Question
Two repositories were in scope (`axis3d`, `new3dkatsu`). Where does the new engine and its document system live?

## Decision
- Repository `axis3d`, package `src/axis3d/`, tests in `tests/`, benchmarks in `bench/`, documents in `docs/`.
- The Python files at the repository root (`axis.py`, `*_unit.py`, `test_*.py`, `vector.py`, …) are earlier
  experiments. They are excluded from ruff and pytest (`pyproject.toml`) and are neither edited nor imported.
- `new3dkatsu` receives nothing. Its ideas (own matrix code, procedural rings/floors, Unit/Transform/Visual) are
  referenced in `docs/records/` where useful.

## Options
1. A brand-new repository — cleanest, but loses the history the user already has, and was not asked for.
2. `new3dkatsu` — older OOP design, 340 MB of binaries and videos committed; wrong direction for a data-oriented engine.
3. `axis3d` (chosen) — its `Axis`/`UnitArray` experiments are the direct ancestor of the table design (ADR 0004).

## Why
The name already means "table of columns" to the user, the branch was created there, and the repository is small.

## Assumptions (check me)
- The user wants continuity with the `axis3d` name rather than a new project name.
- Leaving legacy scripts at the root is acceptable for now; task 0020 proposes moving them to `legacy/` and waits for a human.
- `src/` layout (not flat) is worth the small indirection because it stops tests importing an un-installed package.

## Consequences
- `uv sync` installs the package editable; `import axis3d` works from anywhere in the repo.
- Everything under `docs/` refers to code by `src/axis3d/...` paths; the module map is the index (`docs/spec/module_map.md`).
