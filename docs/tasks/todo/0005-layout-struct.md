---
kind: task
id: 0005
title: layout/struct.py: Struct → dtype + GLSL (HARD ZONE)
pack: implement
role: implementer
model: medium
status: todo
blocked_by: [0002]
brief_ko: std430 규칙으로 오프셋을 계산해 numpy dtype과 GLSL struct 문자열을 만드는 Struct와 네 개의 엔진 구조체 선언.
---
# 0005 — layout/struct.py

## Goal
`Struct` as in `docs/spec/layout.md`, plus `layout/structs.py` declaring `Frame`, `Instance`, `MeshInfo`, `DrawCommand`.

## Read
- `docs/spec/layout.md`
- `docs/rules/gpu_layout.md`

## Write
- `src/axis3d/layout/__init__.py`, `src/axis3d/layout/struct.py`, `src/axis3d/layout/structs.py`
- `tests/layout/test_struct.py`, `tests/layout/test_structs.py`

## Do
1. Field types as small frozen dataclasses `FieldType(glsl: str, np_format: str, shape: tuple, size: int, align: int)`;
   constants `f32 i32 u32 vec2 vec4 mat4`. Arrays are `(FieldType, count)`.
2. `Struct(name, **fields)`: compute offsets by std430; raise `LayoutError` if any field needs implicit padding
   (message names the field, the offset, and the pad to add); add trailing padding to the struct alignment.
3. Expose `size`, `align`, `dtype` (built with explicit `offsets` and `itemsize`), `glsl()`, `zeros(n)`, `fields`.
4. `structs.py`: the four declarations; `STRUCTS` list; `all_glsl()` returning them joined in dependency order.
5. Module docstring first line: `HARD ZONE: std430 offset rules. Use through: Struct, .dtype, .glsl().`

## Done when
- `tests/layout/test_struct.py::test_instance_offsets_size_align` — offsets 0/64/80/84, size 96, align 16
- `tests/layout/test_struct.py::test_implicit_padding_raises_layout_error` — `Struct("Bad", a=f32, b=vec4)` names `b`
- `tests/layout/test_struct.py::test_vec3_is_rejected` — E-010: no `vec3` field type exists / `Struct` refuses it
- `tests/layout/test_struct.py::test_glsl_text_for_instance` — exact expected string
- `tests/layout/test_structs.py::test_draw_command_matches_gl_indirect_layout` — 5 × u32 at offsets 0..16, size 32
- `tests/layout/test_structs.py::test_frame_size` — 3 × 64 + 2 × 16 = 224
- `uv run ruff check . && uv run pytest -q` pass; only budgeted names are public

## Out of scope
- Writing `gen/structs.glsl` to disk (0009 `preprocess.py`).

## Notes
- numpy: `np.dtype({"names": [...], "formats": [...], "offsets": [...], "itemsize": size})`; `mat4` format `("<f4", (4, 4))`.
- Trailing padding: only `itemsize` grows; no named pad field is added (GLSL rounds the same way).
