---
kind: spec
brief_ko: 규약. 월드 Z-up 오른손, 단위, 쿼터니언 xyzw, 행렬 행우선(row_major), 역Z 0-1 깊이, 고정 스텝, id, dtype, 색.
---
# Conventions

Everything here is a constant in `src/axis3d/conventions.py` and is never restated elsewhere in code.

## Space (ADR 0005)
- World: right-handed, **+X right (east), +Y forward (north), +Z up**. Same as Blender and most math texts.
- View (GL camera): +X right, +Y up, −Z forward. The change of basis is one constant `WORLD_TO_VIEW`, a rotation of
  −90° about X: `(x, y, z) → (x, z, −y)`, equal to `look_at(origin, +Y, up=+Z)`. Only two places produce that basis:
  `render/camera.py: view_matrix()` (through `look_at` with `up=UP`) and `io/gltf.py` (applies the constant). Nothing
  else knows that GL is Y-up.
- Front faces are counter-clockwise; back faces are culled by default.

## Units
Meters, seconds, kilograms, radians. Degrees appear only in UI text. Default gravity `(0, 0, -9.81)`.

## Rotation (ADR 0008)
Unit quaternion stored `(x, y, z, w)`, glTF order; identity `(0, 0, 0, 1)`. Helpers in `linalg/quaternion.py`.
Euler angles are input-only: `quat_from_euler(roll, pitch, yaw)` in radians, applied as yaw·pitch·roll (Z, then Y, then X).

## Arrays
- `float32` for state, `int32` for ids/rows/indices, `uint8` for flags, `int64` for `tick` and byte counts.
- A column of N vectors is `(N, 3)`; `pos[:, 2]` is z. Never `(3, N)` (ADR 0004, benchmark B-002).
- Reserved column names and shapes:
  `pos vel acc prev_pos scale (N,3)` · `rot (N,4)` · `mass radius (N,)` · `color (N,4)` · `mesh (N,) int32` · `flags (N,) uint8`.

## Matrices (ADR 0007)
- numpy `(4, 4) float32`, C order (row-major), math convention `M @ v` with column vectors `v = (x, y, z, 1)`.
- GLSL blocks declare `layout(row_major)`; the bytes are then identical. Matrices never travel through loose uniforms.
- `model = T @ R @ S`; `view_proj = proj @ view`. Compose with `@`, never `*`.

## Depth (ADR 0006)
`glClipControl(GL_LOWER_LEFT, GL_ZERO_TO_ONE)` and reversed-Z: near → 1.0, far → 0.0, depth test `GREATER`,
clear depth `0.0`, depth format `d32f`. `linalg/projection.py: perspective(fov_y, aspect, near, far=None)`;
`far=None` is an infinite far plane. `orthographic(left, right, bottom, top, near, far)` is reversed too.

## Time (ADR 0013)
`DT = 1 / 60` fixed. `world.tick` (`int64`) counts steps since the last restore. Wall-clock never enters a system.
Render interpolation `alpha ∈ [0, 1)` between `prev_pos` and `pos`.

## Identity
An entity is an `int32` id ≥ 0 from `world.spawn(n)`: monotonic, never reused within a run. A row index is a
position inside one table; it changes on `remove`, so never store it across a step.

## Randomness
`world.rng = np.random.default_rng(seed)`; its state is part of the snapshot. Systems draw from `world.rng` only.

## Color
Linear RGB floats in the engine and in shaders. The window framebuffer is sRGB; conversion happens there only.
