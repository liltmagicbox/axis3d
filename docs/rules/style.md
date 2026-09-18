---
kind: rule
brief_ko: 코드 스타일. 4칸 들여쓰기, ruff, 100자, 짧은 함수, 평범한 이름, 마법 금지, 왜-주석만.
---
# Rule: code style

`ruff format` and `ruff check` (config in `pyproject.toml`) decide layout. Below is what ruff cannot see.

## Must
- S1 4-space indent, ≤ 100 chars, `snake_case` functions and variables, `PascalCase` classes, `UPPER_CASE` constants.
- S2 A function does one thing and fits on a screen: ≤ 40 lines, ≤ 5 parameters (a small dataclass beyond that).
- S3 A module is one topic: ≤ 300 lines, a one-paragraph docstring on top saying what it holds and who calls it.
- S4 Public functions have type hints and a docstring whose first line is a plain sentence; one example line when the
   call is not obvious. Array parameters state shape and dtype: `pos: (N, 3) float32`.
- S5 Names say what, not how: `pairs_within_radius`, not `process`. Units in names unless meters/seconds: `angle_rad`.
- S6 Comments explain *why*, or cite a rule or decision (`# ADR 0006: reversed-Z`). Code explains *what*.
- S7 Imports in three groups (stdlib, third-party, `axis3d`), absolute only, at the top of the module.
- S8 Errors are package-defined exceptions (`SnapshotSchemaError`) whose message names the offending value.

## Never
- S9 No `__getattr__`/`__setattr__` tricks, metaclasses, signature-changing decorators, `exec`, or `eval`.
- S10 No inheritance deeper than one level; no mixins. Prefer functions and dataclasses.
- S11 No `global`, no module-level side effects (windows, GL calls, threads at import time).
- S12 No commented-out code, no `TODO` without a task id, no Korean in code (Korean lives in `brief_ko` and briefs).
- S13 No abbreviations beyond the fixed set: `pos vel acc rot dt id ids idx n rng`.

## Check
- [ ] ruff clean  - [ ] function ≤ 40 lines, module ≤ 300  - [ ] docstring first line is a plain sentence
- [ ] shapes/dtypes in docstrings  - [ ] no S9–S11 patterns  - [ ] only why-comments
