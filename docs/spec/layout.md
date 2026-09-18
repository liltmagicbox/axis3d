---
kind: spec
brief_ko: Struct 단일 원천. 파이썬 선언 하나에서 numpy dtype과 GLSL struct를 생성. std430 정렬표, 암묵적 패딩은 오류.
---
# Layout: one struct, two homes

`src/axis3d/layout/struct.py` is a HARD ZONE (std430 rules). Use it through three names: `Struct`, `.dtype`, `.glsl()`.
(ADR 0011)

## Declaring
```python
from axis3d.layout import Struct, f32, i32, u32, vec2, vec4, mat4

Instance = Struct("Instance", model=mat4, color=vec4, mesh=u32, pad=(u32, 3))
Instance.size      # 96
Instance.align     # 16
Instance.dtype     # np.dtype([("model", "<f4", (4, 4)), ("color", "<f4", (4,)), ("mesh", "<u4"), ("pad", "<u4", (3,))])
Instance.glsl()    # "struct Instance {\n  mat4 model;\n  vec4 color;\n  uint mesh;\n  uint pad[3];\n};"
Instance.zeros(n)  # np.zeros(n, dtype=Instance.dtype)
```
Field types: `f32 i32 u32 vec2 vec4 mat4` and fixed arrays `(type, count)`.
**No `vec3`, no `mat3`, no nested structs, no bool.** Fields keep declaration order.

## Alignment (std430)
| type | size | align |
|---|---|---|
| f32 / i32 / u32 | 4 | 4 |
| vec2 | 8 | 8 |
| vec4 | 16 | 16 |
| mat4 (row_major) | 64 | 16 |
| `(T, k)` array | k · size(T) | align(T) |
Field offset = round up to the field's align. Struct align = max field align. Struct size = round up to struct align.

## The rule that keeps it honest
If a field would need implicit padding before it, `Struct` raises
`LayoutError("Instance: pad needed before 'color' at offset 68; add pad=(u32, 3)")`.
Trailing padding to the struct's alignment is added on both sides automatically. Because no padding is implicit,
dtype offsets and GLSL offsets agree without anyone trusting the rules by heart.

## Structs in use (fields in order)
| struct | fields | home |
|---|---|---|
| Frame | view mat4, proj mat4, view_proj mat4, time vec4 (t, dt, alpha, 0), camera_pos vec4 | UBO 0 |
| Instance | model mat4, color vec4, mesh u32, pad (u32, 3) | SSBO 1 |
| MeshInfo | first_index u32, index_count u32, base_vertex u32, pad u32 | SSBO 2 |
| DrawCommand | count u32, instance_count u32, first_index u32, base_vertex u32, base_instance u32, pad (u32, 3) | SSBO 3 |
`layout/structs.py` declares these four. `render/shaders/preprocess.py` writes all declared structs to
`src/axis3d/render/shaders/gen/structs.glsl` at startup (ignored by git).

## Contract tests (`tests/layout/test_struct.py`)
- `size`, `align`, and every field offset match a hand-computed table for the four structs above.
- `Struct("Bad", a=f32, b=vec4)` raises `LayoutError` naming `b` and the pad to add.
- `Instance.zeros(3).nbytes == 3 * Instance.size`; `glsl()` output compiles inside a `.comp` under the gpu marker.
