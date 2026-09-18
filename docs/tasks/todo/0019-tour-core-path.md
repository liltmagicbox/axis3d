---
kind: task
id: 0019
title: tour: core path
pack: teach
role: teacher
model: medium
status: todo
blocked_by: [0007]
brief_ko: conventions → table → world → integrate → snapshot 을 걷는 첫 읽기 경로 작성과 교육성 검토.
---
# 0019 — tour: core path

## Goal
`docs/tour/core.md`: a human can read the core in about 20 minutes, and every stop where they would get lost is
either fixed by a proposed docstring or fenced as a HARD ZONE.

## Read
- `docs/rules/education.md`
- `docs/tour/README.md`
- `src/axis3d/conventions.py`, `src/axis3d/ecs/table.py`, `src/axis3d/ecs/world.py`, `src/axis3d/sim/integrate.py`, `src/axis3d/io/snapshot.py`

## Write
- `docs/tour/core.md`

## Do
1. Read as a first-time reader; log every stop as `file:line — question — fix — rule id`.
2. Check zone labels: `table.py`, `world.py`, `integrate.py`, `snapshot.py` must be walk-through; confirm no
   secretly hard function (> 15 lines of index arithmetic without a `why` comment).
3. Write the tour: 12–18 steps; end with "Try it" running `examples/bouncing_spheres.py` or a snapshot round trip in a REPL.
4. Propose (do not apply) docstring and naming changes as a stylist card.

## Done when
- `docs/tour/core.md` exists, passes `tools/check_docs.py`, and every step names a real file and function.
- Report has the findings table and one "this is nice because" line.

## Out of scope
- Editing code. Tours for render/physics/network (later cards).
