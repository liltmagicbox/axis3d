---
kind: decision
id: 0020
title: Documents are English with a one-line Korean brief_ko, typed by kind, and held to line budgets by a tool
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: yes — budgets are one dict in tools/check_docs.py
brief_ko: 문서 본문은 영어(토큰 절약), 머리말 brief_ko 한 줄이 한국어 요약. 종류별 줄 수 예산을 tools/check_docs.py가 강제한다.
---
# 0020 — English documents, Korean briefs, enforced budgets

## Question
The user asked for English documents to save tokens, Korean briefings so the role of each document stays clear,
and core documents that are short by current standards. How is "short" kept true over time?

## Decision
Frontmatter `kind` + `brief_ko` on every document. Budgets per kind (entry 60, role 70, rule 60, spec 140,
variant 90, decision 50, pack 40, task 60; ledgers unlimited) enforced by `tools/check_docs.py`, run in CI and
by `tests/test_tools.py`. Over budget → split or move detail to a decision or record.

## Options
1. Guidelines only — documents grow until nobody loads them.
2. Token counts — precise but tool-dependent; lines are visible in any editor.
3. Line budgets per kind with a checker (chosen).

## Why
A budget that fails a test is the only kind that survives twenty contributors and two years.

## Assumptions (check me)
- One Korean line per document is enough for the user to know what each document does; longer Korean summaries
  live in `docs/README.md` and in discussion digests when the human is quoted.
- 8 k tokens is the right ceiling for an implementation prompt for a small model (`docs/README.md`); adjust after
  the first real runs.

## Consequences
- `docs/README.md` carries the only Korean paragraph; everything else is `brief_ko`.
- Adding a document kind means adding a budget entry and a template.
