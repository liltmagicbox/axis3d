---
kind: decision
id: 0023
title: Tests are pytest mirrors of src, deterministic and mock-free; GPU tests are marked and skipped without AXIS3D_GPU=1
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: yes — conftest and a rule
brief_ko: 테스트는 src 구조를 그대로 미러하는 pytest, 시드 고정, 목 금지. GPU 테스트는 gpu 마커를 달고 AXIS3D_GPU=1 없이는 건너뛴다.
---
# 0023 — Testing strategy

## Question
CI has no GPU; the engine is mostly GPU-adjacent. How do tests stay meaningful and green?

## Decision
`docs/rules/testing.md`. CPU suite (`uv run pytest -q`) runs everywhere and must stay under 30 s. GPU tests carry
`@pytest.mark.gpu` and run locally with `AXIS3D_GPU=1` on a hidden window. Backend contract tests live in
`tests/gpu/` and run against any backend. No mocks: real `World`, real `socketpair`, real hidden window.

## Options
1. Mock GL — tests then verify the mock; the user's earlier bugs were all in real GL behaviour.
2. Software GL (Mesa llvmpipe) in CI — possible for 4.5/4.6 with recent Mesa; deferred until a task adds it.
3. Marked GPU tests + strong CPU coverage (chosen).

## Why
Everything that matters for correctness (physics, snapshots, layouts, framing) is CPU-testable by construction
(ADR 0003, 0011). GPU tests check the plumbing, which only a real driver can check.

## Assumptions (check me)
- Contributors have a GL 4.6 machine to run `gpu` tests before pushing backend changes; CI cannot catch those.
- Round-trip tests (`restore(snapshot(w))`) and mirror tests (CPU vs GPU physics) give more value than coverage numbers.

## Consequences
- `tests/conftest.py` implements the skip; `pyproject.toml` declares the marker.
- The document system is tested too (`tests/test_tools.py`), so a broken pack fails CI.
