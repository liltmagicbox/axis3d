---
kind: variant
brief_ko: OpenGL ES 3.1 미니 엔진용 사실. DSA 없음(백엔드 안에서 bind-to-edit), MDI 없음, clip control 없음, 영구 매핑 확장, GLSL ES 310 방언, 격차 표.
---
# Variant: OpenGL ES 3.1 (mini engine target)

Folder `src/axis3d/gpu/gles31/`. Same `Device` interface, same shaders through `preprocess.py`, same tests.
Use `docs/packs/port_gles31.md`; it swaps this file for `gl46.md` and nothing else. Context via EGL or ANGLE (task 0021).

## Context
EGL/ANGLE with `EGL_CONTEXT_CLIENT_VERSION 3`, minor 1; check `GL_VERSION` starts with `OpenGL ES 3.1`.
Shader header written by `preprocess.py`: `#version 310 es` + `precision highp float; precision highp int;`
and `#define GLES31 1`. sRGB: `GL_EXT_sRGB_write_control` if present, else convert in the fragment shader (`#ifdef GLES31`).

## Interface → GLES 3.1
| interface | GLES 3.1 | mode |
|---|---|---|
| `create_buffer static` | `glGenBuffers` + `glBindBuffer` + `glBufferData(STATIC_DRAW)` inside the backend | emulated (bind-to-edit) |
| `create_buffer stream` | `GL_EXT_buffer_storage` + `glMapBufferRange(PERSISTENT)`; else 3 buffers with `glBufferSubData` per frame | emulated |
| `read` | `glMapBufferRange(GL_MAP_READ_BIT)` after `glFenceSync` | direct |
| `create_texture` | `glTexStorage2D` (bound) | emulated |
| `create_pipeline` | same; GLSL ES 3.10 dialect | direct |
| `create_compute` | compute is core in ES 3.1 | direct |
| `create_target` | `glFramebufferTexture2D` (bound) | emulated |
| `bind_buffer` | `glBindBufferRange` UBO/SSBO; SSBO max bindings ≥ 4 in vertex? **No**: ES 3.1 guarantees SSBOs only in compute and fragment (`MAX_VERTEX_SHADER_STORAGE_BLOCKS` may be 0) | see Gaps |
| `bind_geometry` | one VAO, `glVertexAttribPointer` with stride 48 | emulated |
| `draw_indirect` | `glDrawElementsIndirect` in a Python loop of `count` (no multi-draw); `GL_EXT_multi_draw_indirect` when present | emulated |
| `dispatch`, `barrier` | direct | direct |
| depth `[0,1]` | no `glClipControl`: `perspective()` gets `clip_zero_to_one=False`; reversed-Z kept, precision lower | emulated |
| `gl_BaseInstance` | absent in ES: `preprocess.py` defines `BASE_INSTANCE` from a per-draw uniform-buffer offset written by the loop above | emulated |

## Gaps (porter appends rows)
| method / feature | status | why |
|---|---|---|
| Instances SSBO in the vertex stage | conditional | needs `MAX_VERTEX_SHADER_STORAGE_BLOCKS ≥ 2`; else read instances from a `samplerBuffer` fallback (task) |
| `create_target` with `rgba16f` | conditional | needs `GL_EXT_color_buffer_float` |
| bindless textures, mesh shaders | unsupported | not in ES |
| `d32f` depth | direct | `GL_DEPTH_COMPONENT32F` is core in ES 3.0 |

## Shader dialect differences handled in `preprocess.py`
No `gl_BaseInstance`, no `gl_DrawID`; explicit `precision`; `layout(std430, row_major)` is valid in ES 3.10;
no `#include` natively (we inline anyway); integer texture formats need `highp` samplers.

## Known traps
- ES contexts may lack a default framebuffer sRGB conversion; check `GL_FRAMEBUFFER_ATTACHMENT_COLOR_ENCODING`.
- ANGLE on Windows translates to D3D11: persistent mapping is emulated by the driver and can be slow; measure (profiler).
- `glMapBufferRange` without `GL_MAP_UNSYNCHRONIZED_BIT` stalls; the ring must still be fenced by hand.
