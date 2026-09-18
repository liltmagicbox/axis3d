---
kind: task
id: 0011
title: render: Meshes, primitives, gather
pack: implement
role: implementer
model: medium
status: todo
blocked_by: [0005, 0007]
brief_ko: 단일 VBO/IBO 메시 레지스트리, 큐브·구·격자 생성기, 테이블→Frame/Instance/DrawCommand 를 배열 연산으로 채우는 gather.
---
# 0011 — render: Meshes, primitives, gather

## Goal
Everything the renderer needs that does not touch GL: mesh data, primitives, and the vectorised gather.
`Meshes` takes a `Device` but is tested here with a tiny fake that only records `create_buffer`/`write` calls.

## Read
- `docs/spec/render.md` — "Meshes", "Gather"
- `docs/spec/layout.md` — "Structs in use"

## Write
- `src/axis3d/render/meshes.py`, `src/axis3d/render/primitives.py`, `src/axis3d/render/gather.py`
- `tests/render/test_primitives.py`, `tests/render/test_meshes.py`, `tests/render/test_gather.py`

## Do
1. `primitives.py`: `cube()`, `sphere(rings=8, slices=16)`, `grid(size=10.0, step=1.0)` → `(vertices (V,12) float32, indices (I,) uint32)`,
   CCW winding, unit size, normals outward, colours white.
2. `meshes.py`: `Meshes(device)`: `add(vertices, indices) -> int` appends to CPU lists; `upload()` concatenates
   and creates/writes `vertex_buf`, `index_buf`, `info_buf` (static); `info` is a `MeshInfo` structured array.
3. `gather.py`: `gather(world, meshes, alpha, frame_out, instances_out, commands_out) -> int` per the six spec steps;
   `renderables` table columns: `mesh (N,) int32`, `color (N,4)`.

## Done when
- `tests/render/test_primitives.py::test_cube_has_36_indices_and_ccw_faces` — literal counts, one face normal check
- `tests/render/test_meshes.py::test_add_two_meshes_gives_offsets` — `first_index`, `base_vertex` of the second
- `tests/render/test_gather.py::test_gather_sorts_instances_by_mesh_and_counts_commands` — 3 instances, 2 meshes
- `tests/render/test_gather.py::test_gather_interpolates_positions_with_alpha` — alpha 0.5 midpoint in `model[:, :3, 3]`
- `tests/render/test_gather.py::test_gather_with_no_renderables_returns_zero` — empty
- `uv run ruff check . && uv run pytest -q` pass; only budgeted names are public

## Out of scope
- Shaders, pipelines, camera, actual drawing (0012).

## Notes
- The fake device for tests lives in `tests/render/conftest.py` and implements only `create_buffer` and `write`;
  that is not a mock of numpy or GL (T10), it is a test double for our own interface.
- Model matrices: `trs(p, rot, scale)` from 0002; write into `instances_out["model"]` in sorted order.
