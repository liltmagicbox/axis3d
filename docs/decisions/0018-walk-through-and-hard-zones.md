---
kind: decision
id: 0018
title: Every module is either walk-through (beginner-readable) or a fenced HARD ZONE used through ≤ 3 names
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: yes — labels and a rule
brief_ko: 모든 모듈은 초보자가 읽을 수 있는 walk-through이거나, 첫 줄에 이유를 적고 이름 3개 이하로만 쓰이는 HARD ZONE이다. 주 경로는 전부 walk-through.
---
# 0018 — Walk-through code and HARD ZONEs

## Question
The user wants code that impresses a curious reader and that a beginner can follow, while allowing deliberately
hard, isolated parts. How is that made checkable?

## Decision
`docs/rules/education.md`: each module declares its zone in its docstring. HARD ZONE modules start with
`HARD ZONE: <why>. Use through: <names>.` and expose at most three names. The main path
`app.loop → World.step → systems → render.gather → Device` is walk-through end to end. Initial HARD ZONEs:
`layout/struct.py`, `sim/collide/grid.py`, `gpu/gl46/device.py`.

## Options
1. "Write clean code" as advice — unverifiable.
2. Everything simple, no hard parts — impossible for std430, grid hashing, and GL plumbing.
3. Declared zones with a size cap and a name cap (chosen) — a reviewer and the teacher role can check it.

## Why
Curiosity is rewarded when the map says "this part is hard, here is why, and you can use it without reading it".

## Assumptions (check me)
- Three HARD ZONEs are enough for v1; if the count grows past six, the design is drifting (`teacher` reports it).
- The reader model (Python basics + numpy indexing) is the right bar; not "any programmer", not "graphics engineers".

## Consequences
- The user's earlier `__getattr__`-based `Unit` and `UnitDict` patterns are excluded from walk-through code
  (`rules/style.md` S9).
- `docs/tour/` exists so a human has a guided path; the teacher role maintains it.
