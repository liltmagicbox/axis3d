---
kind: decision
id: 0010
title: A thin Device interface of ≤ 20 methods, shaped like Vulkan, hides every GL call
status: accepted
date: 2026-09-18
decided_by: ai
confidence: medium
reversible: moderate — callers are few (render, meshes, examples) but backends implement all of it
brief_ko: GL 호출은 Device 인터페이스(19+2 메서드) 뒤에만 존재. 파이프라인 객체·패스·명시적 배리어 등 Vulkan 모양이라 나중에 VK/RT 백엔드가 쉽다.
---
# 0010 — Thin, Vulkan-shaped device interface

## Question
The user wants GL now, Vulkan later for ray tracing, and an abstract "graphics card interface" with minimal state.
How thick is the abstraction and what shape does it take?

## Decision
`gpu.Device` (a `Protocol`) with opaque handles, a frozen `PipelineState`, 19 frame/resource methods plus
`destroy`/`close` (`docs/spec/gpu_interface.md`). Shape borrowed from Vulkan: pipelines bundle shader + fixed state,
passes are explicit, stream buffers are fenced rings, barriers are explicit calls, binding slots are numbered.

## Options
1. Raw GL calls throughout the renderer — fastest to write, impossible to port, GL global state leaks everywhere.
2. A full RHI (command buffers, descriptor sets, render graphs) — right for a big engine, wrong for a readable one.
3. `moderngl` — a good thin layer, but its object model is GL's, not Vulkan's (ADR 0002).
4. Own ≤ 20-method interface (chosen).

## Why
Small enough to read in one sitting; explicit enough that a Vulkan backend is a table of one-to-one mappings
(`docs/variants/vulkan.md`), and a GLES 3.1 backend is the same table with a few emulations.

## Assumptions (check me)
- 19 methods cover v1 rendering and compute. Ray tracing methods are added later behind `device.features` by ADR.
- One window, one queue, one thread is enough; multi-queue is not on the roadmap.
- Fixed binding slots (0–7) do not become a bottleneck; 8 SSBO slots is the GL minimum guaranteed everywhere.

## Consequences
- Contract tests (`tests/gpu/test_device_contract.py`) define backend correctness: same bytes in, same pixels out.
- `render/` and `examples/` never import anything from `gpu/gl46/`.
