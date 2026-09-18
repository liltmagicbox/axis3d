---
kind: spec
brief_ko: 엔진 개요. 다섯 원칙, 프레임의 데이터 흐름, 스냅샷 하나로 저장·네트워크·리플레이·GPU 미러를 얻는 구조, 하위 spec 목록.
---
# Overview

axis3d is a data-oriented 3D simulation engine in Python. numpy holds the state, OpenGL 4.6 draws it,
and the code is written to be read.

## Five principles
1. **State is data.** All mutable simulation state is numpy arrays inside one `World` (tables, tick, rng, inputs).
   Nothing else changes between steps. (ADR 0003)
2. **Systems are functions.** `system(world, dt)`. A step is an ordered list of calls in `ecs/schedule.py`. (ADR 0004)
3. **One layout, two homes.** GPU-visible structs are declared once (`layout.Struct`); the numpy dtype and the GLSL
   struct are generated from it, so the bytes are identical on both sides. (ADR 0011)
4. **Thin device.** `gpu.Device` is a ≤ 20-method interface shaped like Vulkan; `gpu/gl46` implements it with DSA.
   No GL call exists outside that folder. (ADR 0009, 0010)
5. **Fenced difficulty.** Every module is walk-through or `HARD ZONE`. The main path is walk-through end to end. (ADR 0018)

## The payoff of principle 1
`snapshot(world) -> bytes` is the tables' raw bytes plus a small header. That one function is:
save/load (write the bytes to a file), network sync (send the bytes), replay (restore, then replay the `inputs`
table), and GPU mirroring (the same column bytes are what compute shaders read).

## A frame
```
inputs table ─▶ World.step()  =  integrate ▸ collide ▸ resolve ▸ bounds ▸ expire ▸ apply removals ▸ tick += 1
                     │
                     ├─▶ io.snapshot(world) ─▶ net.server.broadcast / file
                     │
render.gather(world, meshes, alpha) ─▶ Frame UBO + Instances SSBO + DrawCommands SSBO (mapped ring slices)
                     │
Device: begin_frame ▸ begin_pass ▸ bind_pipeline ▸ bind_buffer×4 ▸ bind_geometry ▸ draw_indirect ▸ end_pass ▸ end_frame
```
Fixed step `DT = 1/60`; rendering interpolates between `prev_pos` and `pos` with `alpha` (ADR 0013).

## Subsystems
| area | spec | zone |
|---|---|---|
| axes, units, depth, matrices, ids, time | `docs/spec/conventions.md` | walk |
| tables, world, systems, schedule, join | `docs/spec/ecs.md` | walk |
| struct layouts numpy ↔ GLSL | `docs/spec/layout.md` | HARD |
| device interface | `docs/spec/gpu_interface.md` | interface walk; backend HARD |
| meshes, gather, renderer, camera | `docs/spec/render.md` | walk |
| shader files, bindings, vertex layout | `docs/spec/shaders.md` | walk |
| integrate, collide, resolve | `docs/spec/physics.md` | grid HARD; rest walk |
| snapshot bytes | `docs/spec/snapshot.md` | walk |
| framing, messages, authority | `docs/spec/network.md` | walk |
| glTF export | `docs/spec/gltf.md` | walk |
| window, loop, input | `docs/spec/app.md` | walk |
| targets and non-goals | `docs/spec/targets.md` | — |
| public API registry | `docs/spec/api_budget.md` | — |
| package tree with status | `docs/spec/module_map.md` | — |
