---
kind: decision
id: 0004
title: ECS is dense SoA tables keyed by a global id with an id→row array; no archetypes, no sparse sets
status: accepted
date: 2026-09-18
decided_by: ai
confidence: medium
reversible: moderate — Table's interface is small, but every system uses (N, k) column shapes
brief_ko: 테이블은 열마다 (N,k) numpy 배열, 행은 촘촘히(swap-remove), id→row 배열로 조회. 아키타입·스파스셋은 v1에서 배제.
---
# 0004 — Dense tables with an id→row map

## Question
How are entities and components stored so that numpy vectorisation, composition, and snapshots all work?

## Decision
`Table` = one preallocated array per column with shape `(capacity, *shape)`, a dense `ids` column, and an
`int32` `_row_of_id` array (`-1` = absent). `insert` appends, `remove` swap-removes, `row_of(ids)` gathers.
Composition = the same id appears in several tables; `join(a, b)` is one gather plus a mask.
Removal during a step is deferred to the end of the step (`world.despawn`).

## Options
1. One 2D array `(k, N)` per kind with attribute slices (the user's `Axis` class): simplest, but heterogeneous column
   shapes (`rot (4,)`, `mesh int32`) do not fit one dtype, and "kind" is not composition.
2. Sparse sets with generation-tagged ids: robust to reuse, but two indirections and more code for a beginner.
3. Archetypes: fastest iteration, but moving rows between archetypes on add/remove is a HARD ZONE at the core.
4. Dense per-table columns + global id map (chosen): each piece is a few lines; joins are gathers.

## Why
Every system is `table.col(...)` reads and writes; a beginner sees plain arrays. Joins are rare and cheap.

## Assumptions (check me)
- Systems are vectorised, so `(N, 3)` vs `(3, N)` layout does not matter. The user measured `(3, N)` 2× faster in a
  *per-row Python loop* (B-002); that loop shape is banned by `rules/performance.md` F1. Re-measure in task 0017.
- Ids are never reused within a run, so no generation bits are needed; `_row_of_id` grows to `max id + 1` ints,
  which is fine below ~10 M spawns per run.
- Swap-remove changing row order is acceptable because nothing may keep row indices (`spec/conventions.md`).

## Consequences
- Column views are invalidated by `insert` growth and `remove`; systems fetch them at the top and never cache.
- A `parent` hierarchy, if ever needed, is a column of ids, not a tree of objects.
