---
kind: variant
brief_ko: Vulkan 1.3 백엔드 사실(레이트레이싱 경로용). 인터페이스 개념 대응표, Y 뒤집기, [0,1] 깊이 기본, 명시적 동기화, RT 확장 방법.
---
# Variant: Vulkan 1.3 (future backend; ray tracing path)

Folder `src/axis3d/gpu/vulkan/`. The `Device` interface was shaped so this port is a mapping, not a redesign. (ADR 0010)
Python binding: `vulkan` (pyvulkan) or `pyvk`; decided by ADR when the port starts. Use `docs/packs/port_vulkan.md`.

## Concept mapping
| interface | Vulkan |
|---|---|
| `Device` | `VkInstance` + `VkPhysicalDevice` + `VkDevice` + one graphics/compute queue + swapchain |
| `Buffer static` | `VkBuffer` device-local, filled through a staging buffer once |
| `Buffer stream` | host-visible, host-coherent `VkBuffer` mapped persistently; ring of 3 with frame fences |
| `Buffer readback` | host-visible, host-cached; `read` waits the frame fence |
| `Texture` | `VkImage` + `VkImageView` + `VkSampler`; layouts transitioned inside the backend |
| `Pipeline` | `VkPipeline` with fixed state baked from `PipelineState`; dynamic viewport/scissor |
| `ComputePipeline` | `VkPipeline` compute |
| `RenderTarget` | dynamic rendering (`VK_KHR_dynamic_rendering`, core in 1.3); no render-pass objects |
| `begin_frame` / `end_frame` | acquire image, wait fence, begin command buffer / submit, present |
| `begin_pass` / `end_pass` | `vkCmdBeginRendering` / `vkCmdEndRendering` |
| `bind_buffer(slot, …)` | one descriptor set per frame with bindings 0–7 exactly as `docs/spec/shaders.md`; UBO at 0, SSBOs 1–7 |
| `bind_texture` | combined image samplers in a second set, bindings 0–7 |
| `bind_geometry` | `vkCmdBindVertexBuffers`, `vkCmdBindIndexBuffer` (uint32) |
| `draw_indirect` | `vkCmdDrawIndexedIndirect(buffer, offset, count, stride)`; `DrawCommand` matches `VkDrawIndexedIndirectCommand` |
| `dispatch` / `barrier` | `vkCmdDispatch` / `vkCmdPipelineBarrier` with buffer memory barriers |

## What matches for free
- Depth `[0, 1]` is Vulkan's native clip range: reversed-Z works unchanged (ADR 0006).
- `layout(std430, row_major)` and the binding numbers compile to SPIR-V through `glslangValidator` unchanged.
- No global state in the interface means no hidden GL-isms to unwind.

## What differs
- Clip-space Y points down: use a negative viewport height (`VK_KHR_maintenance1`, core) so shaders stay identical.
- `gl_BaseInstance` exists in SPIR-V as `BaseInstance` builtin (`GL_ARB_shader_draw_parameters` semantics): fine.
- Explicit sync: every stream write needs the frame fence; every compute → draw needs a barrier (the interface
  already forces `barrier()` calls between them).
- Shaders must be compiled to SPIR-V offline or at startup; `preprocess.py` gains a `to_spirv()` step.

## Ray tracing (the reason this variant exists)
`VK_KHR_acceleration_structure` + `VK_KHR_ray_tracing_pipeline` (or `VK_KHR_ray_query` inside compute, simpler).
Extension methods, behind `device.features`, proposed by ADR when needed:
`create_blas(vertex_buffer, index_buffer, ranges)`, `create_tlas(instances_buffer)`, `trace(pipeline, w, h)`.
The `Instance` struct already carries `model` and `mesh`, which is what a TLAS instance needs.

## Gaps (porter appends rows)
| method / feature | status | why |
|---|---|---|
| — | — | none recorded yet |
