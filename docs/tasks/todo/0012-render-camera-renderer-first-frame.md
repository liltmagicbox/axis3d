---
kind: task
id: 0012
title: render: Camera, Renderer, first frame
pack: implement_gpu
role: implementer
model: medium
status: todo
blocked_by: [0009, 0010, 0011]
brief_ko: 카메라(뷰·투영), 파이프라인 3종의 셰이더, 렌더러(한 패스, indirect draw 한 번), 첫 예제 스크립트로 화면에 구 그리기.
---
# 0012 — render: Camera, Renderer, first frame

## Goal
Bouncing spheres on screen: `examples/bouncing_spheres.py` runs the startup sequence from `docs/spec/app.md`
and shows lit spheres falling in a box.

## Read
- `docs/spec/render.md` — "Renderer", "Camera"
- `docs/spec/shaders.md` — "Per-instance access", "Pipelines v1", "Conventions inside shaders"
- `docs/spec/app.md` — "Startup sequence"

## Write
- `src/axis3d/render/camera.py`, `src/axis3d/render/renderer.py`
- `src/axis3d/render/shaders/mesh.vert`, `unlit.frag`, `lambert.frag`, `line.vert`
- `src/axis3d/__init__.py` (re-exports), `src/axis3d/app/__init__.py` (`run`), `examples/bouncing_spheres.py`
- `tests/render/test_camera.py` (CPU), `tests/render/test_renderer.py` (gpu)

## Do
1. `Camera(pos, target, up=(0,0,1), fov_y, near, far=None)`: `view_matrix()` via `look_at`, `proj_matrix(aspect)`.
2. Shaders: `mesh.vert` reads `Frame` (UBO 0) and `Instances` (SSBO 1) with `gl_BaseInstance + gl_InstanceID`;
   `lambert.frag` uses a fixed light direction `normalize(vec3(0.3, 0.2, 1.0))` in world space (Z-up).
3. `Renderer(device, meshes)`: builds `PIPELINES`, the three stream buffers (`Frame`, 100 000 `Instance`, 256 `DrawCommand`),
   `draw(world, camera, alpha, width, height)` per the spec sequence.
4. `axis3d.run(world_setup: Callable[[World], None])`: the startup sequence; the example spawns 200 spheres.

## Done when
- `tests/render/test_camera.py::test_view_matrix_moves_target_to_negative_z` — target lands on view −Z
- `tests/render/test_camera.py::test_proj_matrix_is_reversed_z` — reuses the projection test idea for aspect 2
- `tests/render/test_renderer.py::test_first_frame_draws_a_sphere_pixel` — offscreen target, centre pixel ≠ clear colour (gpu)
- `examples/bouncing_spheres.py` runs at ≥ 60 FPS with 200 spheres on the reference machine (profiler notes it)
- `uv run ruff check . && uv run pytest -q` pass headless

## Out of scope
- Collision (spheres pass through each other until 0014), textures, culling.

## Notes
- `renderables.color` feeds `Instance.color`; the lambert shader multiplies by `max(dot(n, l), 0.15)`.
- The example is the first thing a human runs; keep it ≤ 40 lines and comment each startup step with the spec section.
