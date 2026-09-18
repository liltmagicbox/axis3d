---
kind: task
id: 0020
title: Move legacy root experiments to legacy/
pack: record
role: scribe
model: small
status: done
blocked_by: []
brief_ko: 저장소 루트의 옛 실험 파일들을 legacy/ 로 옮기는 카드. 사람 승인 전에는 실행하지 않는다.
---
# 0020 — Move legacy root experiments to legacy/

## Goal
The repository root shows only the new engine; the earlier experiments stay available for reference.

## Read
- `docs/decisions/0001-host-repo-and-package-layout.md`
- `docs/records/assumptions.md` — row A-002

## Write
- `legacy/` (git `mv` of `axis.py`, `*_unit.py`, `unitfactory*.py`, `vao.py`, `shader.py`, `interface.py`,
  `inputmanager.py`, `viewmodel.py`, `cylinder.py`, `vector.py`, `test_*.py`, `ham.txt`, `highspeed/`, `scr/`)
- `legacy/README.md` — one paragraph: what these were and which ideas survived (link ADR 0004, records B-001…B-007)

## Do
1. Wait for a human to change `status` to `todo`.
2. `git mv` with history preserved; update `.gitignore` paths; confirm `pyproject.toml` excludes still hold.
3. Add the README; run `uv run pytest -q` and `tools/check_docs.py`.

## Done when
- Root listing contains only: `AGENTS.md CLAUDE.md README.md LICENSE pyproject.toml uv.lock src tests tools bench docs examples legacy .github .claude`.
- CI green.

## Out of scope
- Rewriting or deleting anything in the moved files.

## Outcome
Done 2026-09-18 after the user confirmed A-002. `git mv` of 25 files and 2 folders into `legacy/`, `legacy/README.md`
maps each prototype to the engine idea it became. `AGENTS.md`, `README.md`, ADR 0001 now point at `legacy/`.
ruff, pytest, check_docs green.
