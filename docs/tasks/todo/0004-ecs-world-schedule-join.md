---
kind: task
id: 0004
title: ecs: World, schedule, join
pack: implement
role: implementer
model: small
status: todo
blocked_by: [0003]
brief_ko: World(테이블·tick·rng·inputs·spawn/despawn/step), SYSTEMS 스케줄, join 구현.
---
# 0004 — ecs: World, schedule, join

## Goal
A `World` that owns tables, ids, the tick, the rng, and the `inputs` table, and steps through `SYSTEMS`.

## Read
- `docs/spec/ecs.md` — sections "World", "Systems and schedule", "Join", "Lifecycle rules"
- `docs/spec/conventions.md` — sections "Time", "Identity", "Randomness"

## Write
- `src/axis3d/ecs/world.py`, `src/axis3d/ecs/schedule.py`, `src/axis3d/ecs/query.py`
- `tests/ecs/test_world.py`, `tests/ecs/test_query.py`

## Do
1. `World(seed=0, dt=DT)`: `tables`, `tick`, `dt`, `rng`, `next_id`, `_pending_removal` (list of int32 arrays),
   `inputs = add_table("inputs", {"move": ((3,), f32), "look": ((2,), f32), "buttons": ((), u32)}, capacity=8)`.
2. `add_table(name, columns, capacity=1024)`; `spawn(count) -> ids`; `despawn(ids)` queues; `step()` runs
   `schedule.SYSTEMS`, then removes queued ids from every table, then `tick += 1`.
3. `schedule.py`: `System` alias and `SYSTEMS: list[System] = []` (systems register themselves later, 0007).
4. `query.py`: `join(a, b)` as in the spec (four lines).

## Done when
- `tests/ecs/test_world.py::test_spawn_ids_are_monotonic_and_unique` — two spawns never overlap
- `tests/ecs/test_world.py::test_step_runs_systems_in_order_and_increments_tick` — two recording systems
- `tests/ecs/test_world.py::test_despawn_is_applied_after_the_step` — inside a system the row is still there
- `tests/ecs/test_world.py::test_inputs_table_exists_with_spec_columns` — shapes `(N,3)`, `(N,2)`, `(N,)`
- `tests/ecs/test_query.py::test_join_returns_matching_rows_only` — 3 ids in a, 2 of them in b
- `uv run ruff check . && uv run pytest -q` pass; only budgeted names are public

## Out of scope
- Any real system (0007). Snapshot of rng (0006).

## Notes
- `SYSTEMS` is a plain module-level list; tests may append and restore it. No registry, no decorator (E8).
