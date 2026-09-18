---
kind: task
id: 0009
title: gpu: gl46 pipelines, passes, frame ring, preprocess
pack: implement_gpu
role: implementer
model: medium
status: todo
blocked_by: [0008]
brief_ko: 셰이더 전처리(#include, 버전 헤더, gen/structs.glsl), gl46의 파이프라인·렌더타깃·패스·프레임 펜스·바인딩·draw/dispatch/barrier.
---
# 0009 — gpu: gl46 pipelines, passes, frame ring, preprocess

## Goal
The rest of the `Device` methods on gl46 and the shader preprocessor, so a clear-screen frame and a compute
dispatch work end to end.

## Read
- `docs/spec/gpu_interface.md` — "Methods", "Protocol rules"
- `docs/spec/shaders.md` — "Preprocess", "Binding table", "Vertex layout"
- `docs/variants/gl46.md`

## Write
- `src/axis3d/gpu/gl46/device.py` (extend), `src/axis3d/gpu/gl46/debug.py`
- `src/axis3d/render/__init__.py`, `src/axis3d/render/shaders/preprocess.py`, `src/axis3d/render/shaders/common.glsl`
- `tests/render/test_preprocess.py` (CPU), `tests/gpu/test_device_contract.py` (extend, gpu)

## Do
1. `preprocess(path, defines=None) -> str`: version line from the variant (`#version 460 core`), `#define`s,
   `#include` inlining once with `#line` directives; `write_generated_structs(dir)` writes `gen/structs.glsl` from
   `layout.all_glsl()`.
2. gl46: `create_pipeline` (compile, link, log errors with file names), `create_compute`, `create_target`
   (`glCreateFramebuffers` + textures), `begin_frame`/`end_frame` with `glFenceSync` ring, `begin_pass`/`end_pass`,
   `bind_pipeline` applying `PipelineState` (depth GREATER, cull, blend, topology), `bind_buffer` (`glBindBufferRange`,
   UBO for slot 0 else SSBO), `bind_texture`, `bind_geometry` (one VAO with the fixed layout), `draw`, `draw_indirect`,
   `dispatch`, `barrier`.
3. `debug.py`: `install(raise_on_error: bool)` with once-per-id printing.

## Done when
- `tests/render/test_preprocess.py::test_include_is_inlined_once_with_line_directives` — CPU, tmp files
- `tests/render/test_preprocess.py::test_version_header_comes_first` — CPU
- `tests/gpu/test_device_contract.py::test_clear_pass_reads_back_clear_color` — offscreen target, readback pixel (gpu)
- `tests/gpu/test_device_contract.py::test_compute_doubles_buffer` — `x2.comp` over an SSBO, read back (gpu)
- `tests/gpu/test_device_contract.py::test_generated_structs_compile` — `gen/structs.glsl` included in a `.comp` (gpu)
- `uv run ruff check . && uv run pytest -q` pass headless

## Out of scope
- Meshes, gather, camera, the mesh shaders (0011, 0012).

## Notes
- `draw_indirect` binds `GL_DRAW_INDIRECT_BUFFER` (a bind-to-draw, allowed) and calls `glMultiDrawElementsIndirect`.
- Pixel readback for tests: `glGetTextureImage` is fine inside a test (F10 applies to the frame loop, not tests).
