---
kind: decision
id: 0025
title: Code style is PEP 8 through ruff (4 spaces, 100 columns), short functions, English-only code, no magic
status: accepted
date: 2026-09-18
decided_by: ai
confidence: medium
reversible: yes — one rule file and the ruff section
brief_ko: 코드 스타일은 ruff 기준 PEP 8(4칸, 100자), 함수 40줄·모듈 300줄 이하, 코드 안 한글 금지, __getattr__ 같은 마법 금지.
---
# 0025 — Code style baseline

## Question
The earlier repositories mix tabs and spaces, Korean and English comments, and clever attribute magic.
What is the baseline for the new engine?

## Decision
`docs/rules/style.md`: ruff format/check with `E F I B UP N SIM`, 4-space indent, 100 columns, `snake_case`,
functions ≤ 40 lines, modules ≤ 300 lines, plain-sentence docstrings with shapes, why-comments only, English-only
code, no `__getattr__`/metaclass/decorator magic in walk-through code.

## Options
1. Keep the author's habits (tabs, inline Korean journals) — the journals are valuable but belong in `docs/records/`.
2. Strict typing with `mypy --strict` — good later; today it would slow small models with noise. Deferred by ADR.
3. PEP 8 via ruff + a short human rule file (chosen).

## Why
Small models produce consistent code when the formatter decides layout and the rule file is one screen.

## Assumptions (check me)
- The user accepts 4 spaces over tabs (their `axis3d` files use tabs, `new3dkatsu` mostly spaces). If not, one
  ruff setting and S1 change.
- Excluding Korean from code (not from documents) is what "docs in English to save tokens" implies; the user's
  inline Korean notes are preserved as records (`docs/records/discussions/`, `edge_cases.md`).
- The ruff rule set is deliberately modest; pydocstyle and mypy can be added by ADR after the first sprint.

## Consequences
- Legacy root files are excluded from ruff (`pyproject.toml`) so CI is green from day one.
- `stylist` may fix S1–S8 mechanically; S9–S13 violations go back to the implementer.
