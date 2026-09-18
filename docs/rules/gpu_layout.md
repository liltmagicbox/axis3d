---
kind: rule
brief_ko: GPU 버퍼 레이아웃과 상태 규칙. std430, vec3 금지, row_major mat4, 고정 바인딩, 영구 매핑 링, 상태 누수 금지.
---
# Rule: GPU buffer layout and state

## Must
- G1 Every buffer-visible struct is a `layout.Struct`; its `.dtype` and `.glsl()` are the only sources of truth.
- G2 `std430` only: `layout(std430, row_major, binding = N)`. Slots come from the table in `docs/spec/shaders.md`.
- G3 Vectors in buffer blocks are `vec2`, `vec4`, or scalars. `vec3` is forbidden there (16-byte stride trap). Pad explicitly.
- G4 Matrices in buffers are `mat4` only, row-major on both sides (numpy C order ↔ `row_major`). No `mat3`.
- G5 Per-frame constants → UBO 0 (`Frame`). Per-instance and per-draw data → SSBOs. No loose uniforms except samplers.
- G6 Stream buffers are persistent-mapped rings of 3 frames guarded by fences; the CPU writes only the current slice.
- G7 A pass sets its full fixed state from `PipelineState` (depth, cull, blend, topology). Nothing relies on leftovers.
- G8 Depth is reversed-Z in `[0, 1]`: `GREATER`, clear `0.0` (`docs/spec/conventions.md`).

## Never
- G9 No GL call outside `src/axis3d/gpu/gl46/`. No `glGet*` in the frame loop. No `glBind*` to edit a resource (DSA only).
- G10 No `std140`. No `layout(location)` on blocks. No implicit padding (`Struct` raises `LayoutError`).
- G11 No shader text assembled by string concatenation in Python; `.glsl` files + `#include` through `preprocess.py`.

## Check
- [ ] Struct used  - [ ] no vec3/mat3 in blocks  - [ ] slots from the table  - [ ] no GL outside gl46
- [ ] state from PipelineState  - [ ] persistent ring for stream data
