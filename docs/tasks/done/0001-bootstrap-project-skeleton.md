---
kind: task
id: 0001
title: Bootstrap project skeleton and doc tools
pack: implement
role: implementer
model: large
status: done
blocked_by: []
brief_ko: uv 프로젝트, 패키지 뼈대, 스모크 테스트, 문서 도구(pack/check_docs/new), CI, 에이전트 래퍼를 만든 첫 카드. 완료.
---
# 0001 — Bootstrap project skeleton and doc tools

## Goal
A repository where `uv sync`, `uv run pytest -q`, `uv run ruff check .`, and `uv run python tools/check_docs.py`
all pass, and where a pack plus a card can be turned into one prompt.

## Read
- `docs/README.md`

## Write
- `pyproject.toml`, `src/axis3d/__init__.py`, `tests/conftest.py`, `tests/test_smoke.py`, `tests/test_tools.py`
- `tools/pack.py`, `tools/check_docs.py`, `tools/new.py`, `.github/workflows/ci.yml`, `.claude/agents/*.md`

## Done when
- `tests/test_smoke.py::test_package_has_version` — the package imports without GL
- `tests/test_tools.py::test_check_docs_passes` — every document has frontmatter and fits its budget
- `tests/test_tools.py::test_every_pack_builds` — every pack lists only existing files

## Outcome
Done 2026-09-18 by the architect while creating the document system. Ruff, pytest, and check_docs pass;
`uv.lock` committed. Legacy root files excluded from lint and tests (ADR 0001). No engine code yet beyond `__init__`.
