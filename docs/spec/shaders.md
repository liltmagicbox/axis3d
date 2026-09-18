---
kind: spec
brief_ko: 셰이더 규약. GLSL 460, 파일 구조와 #include 전처리, 고정 바인딩 표(유일본), 정점 레이아웃, 인스턴스 접근, v1 파이프라인.
---
# Shaders

GLSL `#version 460 core`. Files live in `src/axis3d/render/shaders/`: one `.vert` / `.frag` / `.comp` per pipeline,
shared code in `.glsl` includes. Structs are never hand-written in GLSL; they come from `gen/structs.glsl`.

## Preprocess — `render/shaders/preprocess.py` (walk-through)
`preprocess(path: Path, defines: dict[str, str] | None = None) -> str` inlines `#include "file.glsl"` (relative to the
shaders folder, once per file), prepends the version line and `#define`s for the active variant, and inserts `#line`
directives so driver errors name the right file. Variants change only this header step (`docs/variants/*.md`).

## Binding table (the one copy; everything else cites it)
| slot | kind | block name | contents |
|---|---|---|---|
| 0 | UBO | Frame | view, proj, view_proj (mat4), time (vec4: t, dt, alpha, 0), camera_pos (vec4) |
| 1 | SSBO | Instances | `Instance[]`, sorted by mesh id |
| 2 | SSBO | Meshes | `MeshInfo[]` |
| 3 | SSBO | DrawCommands | `DrawCommand[]`, one per mesh with ≥ 1 instance |
| 4 | SSBO | SimPos | `vec4[]` position (w unused) — compute only |
| 5 | SSBO | SimVel | `vec4[]` velocity — compute only |
| 6 | SSBO | SimAux | `vec4[]` (radius, mass, flags, 0) — compute only |
| 7 | SSBO | Scratch | compute scratch: cell ids, pair lists |
| 0–7 | sampler2D | tex0 … tex7 | material textures (unused in v1) |
Every block: `layout(std430, row_major, binding = N) buffer|uniform Name { ... };`

## Vertex layout (fixed, engine-wide)
| location | name | type |
|---|---|---|
| 0 | in_pos | vec3 |
| 1 | in_normal | vec3 |
| 2 | in_uv | vec2 |
| 3 | in_color | vec4 |
Interleaved, 48 bytes per vertex, `uint32` indices. (`vec3` is fine for vertex attributes; the std430 ban is for blocks.)

## Per-instance access
```glsl
Instance inst = instances[gl_BaseInstance + gl_InstanceID];   // gl_BaseInstance is a GLSL 4.6 builtin
gl_Position = frame.view_proj * inst.model * vec4(in_pos, 1.0);
```
`DrawCommand.base_instance` is the first instance of that mesh; `render/gather.py` sorts instances by mesh id.

## Pipelines v1
| name | vert | frag | state |
|---|---|---|---|
| unlit | `mesh.vert` | `unlit.frag` | default |
| lambert | `mesh.vert` | `lambert.frag` | default |
| lines | `line.vert` | `unlit.frag` | topology lines, depth_write False |
Compute v1: `integrate.comp` (mirrors `sim/integrate.py`). Planned: `grid.comp`, `cull.comp`.

## Conventions inside shaders
- Names: `in_*` attributes, `v_*` varyings, `out_color` output, samplers `tex0…`. No `u_*`: there are no loose uniforms.
- Depth is reversed-Z; never treat `1.0` as far.
- Row-major matrices: write `M * v` exactly as numpy `M @ v`. No transposes anywhere.
