---
kind: decision
id: 0002
title: Toolchain is Python ≥ 3.11 with uv, numpy, PyOpenGL, glfw; pytest and ruff for checks; nothing else at runtime
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: yes — adding a dependency is one ADR plus a pyproject line
brief_ko: 런타임 의존성은 numpy, PyOpenGL, glfw 셋뿐. uv로 관리하고 pytest·ruff로 검사한다. moderngl·pyglm·numba는 쓰지 않는다.
---
# 0002 — Toolchain

## Question
Which libraries and tools does the engine depend on, and which tempting ones does it refuse?

## Decision
Runtime: `numpy >= 2.0`, `PyOpenGL >= 3.1.7`, `glfw >= 2.7`. Dev: `pytest`, `ruff`. Build: `hatchling`.
Manager: `uv` (`uv sync`, `uv run`, committed `uv.lock`). Python `>= 3.11`.

## Options
- `moderngl` — pleasant, but it is a second abstraction over GL that hides DSA and would fight our own `Device`.
- `pyglm` — fast vector math, but a second vector type violates `rules/simplicity.md` P9; numpy is the math library.
- `numba` — real speedups for the grid broad phase; adds a compiler, warm-up time, and a HARD ZONE of its own. Deferred:
  only after a benchmark row shows numpy cannot meet `spec/targets.md`.
- `pygltflib` / `trimesh` — glTF is small enough to write by hand (ADR 0017).

## Why
Three runtime dependencies keep the engine readable and installable in one command; every extra library is a thing
a beginner must learn before they can read the code.

## Assumptions (check me)
- The user's machines have `uv` or can install it; PyOpenGL's `OpenGL.GL` exposes the 4.6 entry points needed (it does).
- Python 3.11 as the floor (instead of 3.12) costs nothing for this code and widens where it runs.
- Windows is a first-class target; all three dependencies ship wheels for it.

## Consequences
- `pyproject.toml` restricts ruff and pytest to the new code; legacy root files are ignored.
- CI (`.github/workflows/ci.yml`) runs `uv sync`, ruff, `tools/check_docs.py`, and the CPU test suite.
