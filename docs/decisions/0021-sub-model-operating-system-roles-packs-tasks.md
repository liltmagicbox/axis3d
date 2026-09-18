---
kind: decision
id: 0021
title: Sub-models work through roles, atomic rules, specs, swappable variants, packs, and task cards; small models implement and test
status: accepted
date: 2026-09-18
decided_by: ai
confidence: medium
reversible: yes — folders and a tool
brief_ko: 하위 모델 운영 체계: roles(누가)·rules(반드시/절대)·spec(무엇)·variants(백엔드)·decisions(왜)·packs(조합)·tasks(카드)·records(장부). 구현·테스트는 소형 모델이 맡는다.
---
# 0021 — The sub-model operating system

## Question
The user wants many small documents, each model in a different role, composable so that swapping a few files
changes agent behaviour, and small models doing implementation and tests. What is the structure?

## Decision
`docs/README.md` is the map. Eleven roles; ten rules with reviewer checklists; specs as current contracts; variants
for backend facts; decisions with `decided_by`/`confidence`/`Assumptions (check me)`; packs as ordered load lists;
task cards with exact signatures and test names; append-only records. `tools/pack.py` builds one prompt from a pack
and a card; `.claude/agents/*.md` are thin wrappers pointing at `docs/roles/*.md`.

Model sizes by role: implementer/tester/reviewer/stylist/scribe → small; profiler/edge_hunter/planner/teacher/porter →
medium; architect → large.

## Options
1. One big `CLAUDE.md` — cheap to start, impossible to swap parts of, loads everything every time.
2. Skills only (`SKILL.md` per topic) — good progressive disclosure, but no notion of roles, verdicts, or ledgers.
3. Layered folders + packs + cards (chosen) — each file has one owner, one budget, one reason to change.

## Why
It answers the user's two scenarios directly: change one rule file → behaviour changes; port to GLES 3.1 → swap
one variant in one pack.

## Assumptions (check me)
- Small models can follow a 60-line role and a 60-line card if signatures and test names are literal; this is the
  central bet and is unverified until the first cards run.
- Roles are enough separation; we do not need per-role tool sandboxes beyond the wrapper `tools:` lists.
- The user prefers Claude Code agents but wants the system to work with any model; hence the plain-markdown packs.

## Consequences
- The document system is itself under test (`tests/test_tools.py`).
- The first sprint (`docs/tasks/README.md`) doubles as the evaluation of this decision; the scribe records how it went.
