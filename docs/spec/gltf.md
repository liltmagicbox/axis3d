---
kind: spec
brief_ko: glTF 2.0 .glb 내보내기. 자체 최소 작성기, 노드=renderables 행, Z-up→Y-up 변환 한 곳, 기본 PBR 재질, Godot 임포트 경로.
---
# glTF export

`src/axis3d/io/gltf.py` (walk-through). Writes a `.glb` any viewer, Blender, or Godot opens. (ADR 0017, 0022)

## API
```python
export_glb(world: World, meshes: Meshes, path: Path, names: dict[int, str] | None = None) -> None
```

## Mapping
| axis3d | glTF |
|---|---|
| one row of `renderables` joined with `bodies` | one `node` with `translation`, `rotation`, `scale`, `mesh` |
| `mesh` id | one `mesh` with one `primitive` (TRIANGLES) |
| vertex `pos normal uv color` | accessors `POSITION`, `NORMAL`, `TEXCOORD_0`, `COLOR_0` (float) |
| indices `uint32` | accessor `componentType 5125` |
| `color` column | `material.pbrMetallicRoughness.baseColorFactor`, `metallicFactor 0`, `roughnessFactor 1` |
Node names: `names.get(id, f"entity_{id}")`. One scene, flat hierarchy (a `parent` column becomes `children` in v2).

## Axes
glTF is +Y up, right-handed. Every translation, rotation, and vertex position is transformed by the constant
`WORLD_TO_VIEW` from `conventions.py` (world Z-up → Y-up), the same rotation the camera uses. It is applied here
and in `render/camera.py`, nowhere else. Quaternions are already `(x, y, z, w)`, glTF's order.

## Binary layout
`.glb` = 12-byte header, JSON chunk (padded to 4 with spaces), BIN chunk (padded with zeros). One buffer, one
bufferView per accessor kind (positions, normals, uvs, colors, indices) with `byteStride` where interleaved.
Writer uses `json` and `struct` only; no dependencies.

## Tests (`tests/io/test_gltf.py`)
- Header magic and chunk lengths are valid; JSON parses and lists `asset.version == "2.0"`.
- A world with two cubes exports two nodes whose translations equal the rotated positions.
- Round-trip sanity: accessor `count` values match vertex and index counts.

## Godot path (ADR 0022)
Godot 4 imports `.glb` directly with Y-up. Meshes and transforms port as-is; systems (behaviour) are rewritten
in GDScript by hand. Nothing in the engine depends on Godot.

## Not in v1
Import, textures, skinning, animation, cameras, lights.
