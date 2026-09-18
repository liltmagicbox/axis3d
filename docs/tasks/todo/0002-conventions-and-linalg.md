---
kind: task
id: 0002
title: conventions.py and linalg (quaternion, transform, projection)
pack: implement
role: implementer
model: medium
status: todo
blocked_by: [0001]
brief_ko: 규약 상수 파일과 선형대수 3모듈(쿼터니언, TRS·look_at, 역Z 투영)을 numpy 벡터화로 구현.
---
# 0002 — conventions.py and linalg

## Goal
The constants every module cites, and vectorised quaternion / matrix / projection helpers with tests that pin
the conventions (Z-up, `(x, y, z, w)`, row-major, reversed-Z in `[0, 1]`).

## Read
- `docs/spec/conventions.md`
- `docs/spec/api_budget.md` — rows `axis3d.conventions`, `axis3d.linalg`

## Write
- `src/axis3d/conventions.py`, `src/axis3d/linalg/__init__.py`, `quaternion.py`, `transform.py`, `projection.py`
- `tests/linalg/test_quaternion.py`, `tests/linalg/test_transform.py`, `tests/linalg/test_projection.py`

## Do
1. `conventions.py`: `DT = 1/60`, `GRAVITY`, `UP`, `FORWARD`, `RIGHT` as `(3,) float32`, `QUAT_IDENTITY`,
   `WORLD_TO_VIEW` `(4,4) float32` = rotation of −90° about X, `COLUMNS` dict of reserved column shapes/dtypes.
2. `quaternion.py`, all over `(N, 4) float32`: `quat_identity(n)`, `quat_multiply(a, b)`, `quat_from_axis_angle(axis, angle_rad)`,
   `quat_from_euler(roll, pitch, yaw)`, `quat_normalize(q)`, `quat_rotate(q, v)`, `quat_to_matrix(q) -> (N, 3, 3)`.
3. `transform.py`: `trs(pos, rot, scale) -> (N, 4, 4)`, `translate(v)`, `scale(v)`, `rotate(q)`, each `(4, 4)`,
   `look_at(eye, target, up) -> (4, 4)` producing GL view space (+X right, +Y up, −Z forward).
4. `projection.py`: `perspective(fov_y, aspect, near, far=None)`, `orthographic(l, r, b, t, near, far)`, reversed-Z.

## Done when
- `tests/linalg/test_quaternion.py::test_quat_rotate_z_axis_quarter_turn` — rotating `(1,0,0)` by 90° about Z gives `(0,1,0)`
- `tests/linalg/test_quaternion.py::test_quat_to_matrix_matches_quat_rotate` — matrix and direct rotation agree
- `tests/linalg/test_transform.py::test_trs_matches_hand_computed_matrix` — T·R·S for one literal case, row-major
- `tests/linalg/test_transform.py::test_look_at_zup_maps_up_to_view_y` — with `up=(0,0,1)` world +Z becomes view +Y
- `tests/linalg/test_projection.py::test_perspective_near_maps_to_one_far_to_zero` — clip z/w is 1 at near, 0 at far
- `tests/linalg/test_projection.py::test_perspective_infinite_far_stays_in_unit_range` — z/w ∈ (0, 1] for far points
- `uv run ruff check . && uv run pytest -q` pass; only budgeted names are public

## Out of scope
- Camera class (0012), interpolation, slerp.

## Notes
- Reversed-Z finite: rows `[f/aspect,0,0,0], [0,f,0,0], [0,0,near/(far-near), far*near/(far-near)], [0,0,-1,0]` with `f = 1/tan(fov_y/2)`.
  Infinite: third row `[0,0,0,near]`. Orthographic third row `[0,0,1/(far-near), far/(far-near)]`. Views use `z<0` forward.
- `WORLD_TO_VIEW` equals `look_at((0,0,0), (0,1,0), (0,0,1))`; a test may assert that equality.
