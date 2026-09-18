---
kind: task
id: 0007
title: sim: integrate, bounds, expire
pack: implement
role: implementer
model: small
status: todo
blocked_by: [0004]
brief_ko: 첫 시스템 세 개(반음해 오일러 적분과 prev_pos, 월드 박스 반사, ttl 만료→despawn)와 스케줄 등록.
---
# 0007 — sim: integrate, bounds, expire

## Goal
Three walk-through systems that make bodies move, stay in a box, and die on time, wired into `SYSTEMS`.

## Read
- `docs/spec/physics.md` — table "Stages per step", section "Determinism contract"
- `docs/spec/ecs.md` — "Systems and schedule"

## Write
- `src/axis3d/sim/__init__.py`, `src/axis3d/sim/integrate.py`, `src/axis3d/sim/bounds.py`, `src/axis3d/sim/lifetime.py`
- `tests/sim/test_integrate.py`, `tests/sim/test_bounds.py`, `tests/sim/test_lifetime.py`

## Do
1. `integrate(world, dt)`: on `bodies`: `prev_pos[:] = pos; vel += (acc + GRAVITY) * dt; pos += vel * dt`, in place (F4).
2. `bounds(world, dt)`: `BOX = ((-50, -50, 0), (50, 50, 100))`; clamp `pos` into the box (minus `radius`) and flip
   the velocity component that crossed, damped by 0.8.
3. `expire(world, dt)`: `ttl -= dt` on the `lifetime` table; `world.despawn(ids[ttl <= 0])`.
4. `sim/__init__.py` imports the three and sets `schedule.SYSTEMS[:] = [integrate, bounds, expire]` (collide and
   resolve are inserted by 0014); export `integrate, bounds, expire`.

## Done when
- `tests/sim/test_integrate.py::test_integrate_applies_gravity_and_velocity` — one body, one step, literal expected `pos`
- `tests/sim/test_integrate.py::test_integrate_keeps_prev_pos` — `prev_pos` equals the position before the step
- `tests/sim/test_bounds.py::test_bounds_reflects_and_damps_velocity` — a body below the floor is pushed up, `vel.z` flips
- `tests/sim/test_lifetime.py::test_expire_despawns_when_ttl_reaches_zero` — after `world.step()` the id is gone
- `tests/sim/test_lifetime.py::test_expire_with_no_rows_is_safe` — empty table
- `uv run ruff check . && uv run pytest -q` pass; only budgeted names are public

## Out of scope
- Collision (0013, 0014), rotation integration.

## Notes
- Column definitions for `bodies` and `lifetime` come from `conventions.COLUMNS`; tests build worlds with
  `world.add_table("bodies", {k: COLUMNS[k] for k in ("pos","vel","acc","prev_pos","rot","scale","mass","radius","flags")})`.
