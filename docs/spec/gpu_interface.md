---
kind: spec
brief_ko: 추상 GPU 장치 인터페이스. 불투명 핸들, 고정 상태 데이터클래스, 19개 메서드, 프레임/패스 프로토콜. GL 호출은 백엔드 폴더 안에서만.
---
# GPU device interface

`src/axis3d/gpu/device.py` defines `Device` as a `typing.Protocol` plus frozen dataclasses. It is shaped so that
GL 4.6 today and Vulkan later both fit without the interface changing. (ADR 0010)

## Handles (opaque; only the backend reads their fields)
`Buffer(nbytes, kind)`, `Texture(width, height, fmt)`, `Pipeline`, `ComputePipeline`, `RenderTarget`.
`kind ∈ {"static", "stream", "readback"}` · `fmt ∈ {"rgba8_srgb", "rgba8", "rgba16f", "r32f", "d32f"}`.

## Fixed state
```python
@dataclass(frozen=True)
class PipelineState:
    topology: str = "triangles"   # "triangles" | "lines" | "points"
    depth_test: bool = True       # reversed-Z GREATER when True (conventions.md)
    depth_write: bool = True
    cull: str = "back"            # "back" | "none"
    blend: str = "none"           # "none" | "alpha" | "add"
```

## Methods (19)
```python
create_buffer(nbytes: int, kind: str, data: np.ndarray | None = None) -> Buffer
write(buffer: Buffer, data: np.ndarray, offset: int = 0) -> None       # static only; outside the frame loop
map(buffer: Buffer) -> np.ndarray                                     # stream only: uint8 view of THIS frame's slice
read(buffer: Buffer) -> bytes                                         # readback only; waits for the fence
create_texture(width: int, height: int, fmt: str, data=None, mips: bool = False) -> Texture
create_pipeline(vert_src: str, frag_src: str, state: PipelineState) -> Pipeline
create_compute(comp_src: str) -> ComputePipeline
create_target(width: int, height: int, color_fmts: tuple[str, ...], depth_fmt: str | None) -> RenderTarget
begin_frame() -> None                    # waits on this ring slot's fence, rotates stream slices
end_frame() -> None                      # inserts the fence, swaps buffers
begin_pass(target: RenderTarget | None, clear_color=None, clear_depth=None) -> None   # None = the window
end_pass() -> None
bind_pipeline(pipeline: Pipeline) -> None
bind_buffer(slot: int, buffer: Buffer, offset: int = 0, size: int | None = None) -> None   # slot: shaders.md table
bind_texture(slot: int, texture: Texture) -> None
bind_geometry(vertex_buffer: Buffer, index_buffer: Buffer) -> None      # engine-wide vertex layout (shaders.md)
draw(vertex_count: int, instance_count: int = 1) -> None
draw_indirect(indirect_buffer: Buffer, count: int, stride: int) -> None  # multi-draw, uint32 indices
dispatch(pipeline: ComputePipeline, x: int, y: int = 1, z: int = 1) -> None
barrier(kind: str = "all") -> None                                       # "buffer" | "image" | "all"
```
`gpu.Unsupported(method, why)` is raised by a backend that cannot implement a method (listed in its variant's Gaps).

## Protocol rules
- One `Device` per window: `gpu.create_device(backend="gl46", window=window)`.
- Resources are created outside `begin_frame` / `end_frame`. Frames only bind, write mapped slices, draw, dispatch.
- Stream buffers are rings of 3 slices; `map()` returns the current slice; the caller writes it fully each frame.
- Every pass starts from the bound pipeline's `PipelineState`. Nothing depends on leftover state.
- Vertex layout is fixed engine-wide; the backend owns the single vertex array object.
- Shader sources arrive already preprocessed (`render/shaders/preprocess.py`).
- Handles are freed by `device.destroy(handle)`; the device frees everything in `device.close()`. (Two extra names,
  counted in the budget, not in the 19 frame methods.)

## Backends
| backend | folder | status | facts |
|---|---|---|---|
| OpenGL 4.6 core, DSA | `src/axis3d/gpu/gl46/` | v1 | `docs/variants/gl46.md` |
| OpenGL ES 3.1 | `src/axis3d/gpu/gles31/` | variant | `docs/variants/gles31.md` |
| Vulkan 1.3 | `src/axis3d/gpu/vulkan/` | variant | `docs/variants/vulkan.md` |
Contract tests in `tests/gpu/test_device_contract.py` (`@pytest.mark.gpu`) run unchanged against every backend.
