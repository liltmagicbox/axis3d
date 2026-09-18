---
kind: task
id: 0016
title: io/gltf.py: export_glb
pack: implement
role: implementer
model: medium
status: todo
blocked_by: [0011]
brief_ko: renderables⋈bodies 를 노드로, 메시 레지스트리를 메시로, Z-up→Y-up 변환을 적용해 .glb 로 쓴다. 의존성 없음.
---
# 0016 — io/gltf.py: export_glb

## Goal
`export_glb(world, meshes, path, names=None)` writes a valid `.glb` that Blender or Godot opens with the spheres
where the simulation had them.

## Read
- `docs/spec/gltf.md`
- `docs/spec/conventions.md` — "Space", "Rotation"

## Write
- `src/axis3d/io/gltf.py`
- `tests/io/test_gltf.py`

## Do
1. Build JSON: `asset`, `scene`, `scenes`, `nodes` (TRS from `bodies` rows joined to `renderables`), `meshes`,
   `materials` (one per distinct `color`), `accessors`, `bufferViews`, `buffers`.
2. Binary chunk: positions/normals/uvs/colours interleaved from the registry (one bufferView with `byteStride 48`),
   indices as `uint32` (own bufferView). Compute accessor `min`/`max` for positions (required by the spec).
3. Apply `WORLD_TO_VIEW` to vertex positions and normals, to node translations, and to rotations
   (`quat_multiply(basis_quat, rot)`), all vectorised.
4. Write header (`glTF`, version 2, total length) and the two chunks with 4-byte padding.

## Done when
- `tests/io/test_gltf.py::test_glb_header_and_chunk_lengths_are_valid` — parse the file back with `struct`
- `tests/io/test_gltf.py::test_two_cubes_export_two_nodes_with_rotated_translations` — Z-up `(0,0,5)` → glTF `(0,5,0)`
- `tests/io/test_gltf.py::test_accessor_counts_match_registry` — vertex and index counts
- `tests/io/test_gltf.py::test_json_chunk_is_valid_gltf_2` — `asset.version == "2.0"`, required keys present
- `uv run ruff check . && uv run pytest -q` pass; only `export_glb` is added to the budget (already listed)

## Out of scope
- Import, textures, hierarchy, animation, cameras, lights.

## Notes
- `names` maps id → node name; default `f"entity_{id}"`.
- Validate once by hand with Blender's importer; note the result in the report (not a CI dependency).
