---
kind: task
id: 0008
title: gpu: Device interface and gl46 buffers/textures
pack: implement_gpu
role: implementer
model: medium
status: todo
blocked_by: [0005]
brief_ko: Device 프로토콜·PipelineState·핸들·Unsupported 정의와, gl46 백엔드의 버퍼(static/stream 링/readback)·텍스처·create_device.
---
# 0008 — gpu: Device interface and gl46 buffers

## Goal
`gpu/device.py` complete as an interface; `gpu/gl46/device.py` implementing device creation, buffers (all three
kinds, with the persistent-mapped ring), textures, `destroy`, `close`. Draw and pipeline methods raise
`NotImplementedError` until 0009.

## Read
- `docs/spec/gpu_interface.md`
- `docs/variants/gl46.md` — sections "Context", "Interface → GL", "Known traps"

## Write
- `src/axis3d/gpu/__init__.py`, `src/axis3d/gpu/device.py`, `src/axis3d/gpu/gl46/__init__.py`, `src/axis3d/gpu/gl46/device.py`
- `tests/gpu/test_device_contract.py` (`@pytest.mark.gpu`), `tests/gpu/test_device_interface.py` (CPU)

## Do
1. `device.py`: frozen dataclasses for handles and `PipelineState`; `class Device(Protocol)` with the 19 methods +
   `destroy`, `close`; `class Unsupported(RuntimeError)`; `BACKENDS = ("gl46",)`; `create_device(backend, window)`.
2. `gl46/device.py` (first docstring line `HARD ZONE: GL 4.6 DSA plumbing. Use through: create_device, Device methods.`):
   context asserts (E-006), `glClipControl`, sRGB, depth state; buffers via `glCreateBuffers` + `glNamedBufferStorage`;
   stream = 3 × size, mapped once, `map()` returns the uint8 slice for `frame_index % 3`; readback with fence wait.
3. Textures via `glCreateTextures`/`glTextureStorage2D`/`glTextureSubImage2D`; formats table from the spec.
4. A hidden-window fixture in `tests/gpu/conftest.py` (glfw `VISIBLE=False`) shared by all gpu tests.

## Done when
- `tests/gpu/test_device_interface.py::test_pipeline_state_defaults` — CPU: defaults per spec, frozen
- `tests/gpu/test_device_interface.py::test_create_device_unknown_backend_raises` — CPU
- `tests/gpu/test_device_contract.py::test_create_device_without_context_raises` — E-006 (gpu)
- `tests/gpu/test_device_contract.py::test_static_buffer_round_trip_via_readback` — write 1 KB, copy, read back (gpu)
- `tests/gpu/test_device_contract.py::test_stream_map_rotates_three_slices` — three frames give three offsets (gpu)
- `tests/gpu/test_device_contract.py::test_texture_creation_formats` — every `fmt` in the spec creates (gpu)
- `uv run ruff check . && uv run pytest -q` pass headless; `AXIS3D_GPU=1 uv run pytest -q tests/gpu` passes locally

## Out of scope
- Pipelines, passes, draws, dispatch, targets (0009).

## Notes
- PyOpenGL: `glMapNamedBufferRange` → `ctypes` pointer → `np.ctypeslib.as_array(ctypes.cast(ptr, POINTER(c_uint8)), (nbytes,))`.
- Keep GL enum-to-format tables as module constants; no `glGet*` after init except `GL_VERSION` once.
