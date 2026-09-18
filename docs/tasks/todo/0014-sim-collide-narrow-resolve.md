---
kind: task
id: 0014
title: sim/collide: sphere_pairs, resolve_pairs, determinism test
pack: implement
role: implementer
model: small
status: todo
blocked_by: [0013]
brief_ko: 구-구 협역 검사, 위치 보정+충격량 해결, collide/resolve 시스템 등록, 50스텝 바이트 동일성 테스트.
---
# 0014 — sim/collide: sphere_pairs, resolve_pairs, determinism

## Goal
Spheres bounce off each other, and the determinism contract is proven by a test.

## Read
- `docs/spec/physics.md` — "Narrow phase", "Resolve", "Determinism contract"
- `docs/spec/snapshot.md` — for the determinism test

## Write
- `src/axis3d/sim/collide/narrow.py`, `src/axis3d/sim/collide/resolve.py`, `src/axis3d/sim/__init__.py` (extend)
- `tests/sim/collide/test_narrow.py`, `tests/sim/collide/test_resolve.py`, `tests/sim/test_determinism.py`

## Do
1. `sphere_pairs(pos, radius, pairs) -> (pairs, normal, depth)` per spec; `dist == 0` → normal `(0, 0, 1)`.
2. `resolve_pairs(pos, vel, mass, pairs, normal, depth, restitution=0.2) -> None`: `w = np.where(mass > 0, 1/mass, 0)`;
   positional correction and impulse via `np.add.at` (N3, N6).
3. Systems `collide(world, dt)` (stores pairs/normal/depth in `world.tables["bodies"]._scratch`) and `resolve(world, dt)`;
   `sim/__init__.py` sets `SYSTEMS[:] = [integrate, collide, resolve, bounds, expire]`.

## Done when
- `tests/sim/collide/test_narrow.py::test_overlapping_spheres_report_depth_and_normal` — literal case
- `tests/sim/collide/test_narrow.py::test_touching_but_not_overlapping_is_excluded` — `dist == r_i + r_j`
- `tests/sim/collide/test_resolve.py::test_head_on_equal_masses_swap_velocities_partly` — restitution 0.2 arithmetic
- `tests/sim/collide/test_resolve.py::test_static_body_does_not_move` — `mass == 0`
- `tests/sim/test_determinism.py::test_fifty_steps_are_byte_identical` — E-012: two worlds from one snapshot
- `uv run ruff check . && uv run pytest -q` pass; only budgeted names are public

## Out of scope
- Friction, rotation response, multiple iterations, AABBs.

## Notes
- Scratch storage: `Table` may carry a `_scratch: dict[str, np.ndarray]` (private) so no allocation per step (F3).
