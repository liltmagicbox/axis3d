---
kind: decision
id: 0024
title: Rendering is one multi-draw-indirect per pipeline from a single mesh registry and an instance SSBO
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: moderate — gather and renderer are small; shaders assume gl_BaseInstance
brief_ko: 모든 메시는 하나의 VBO/IBO에 붙이고, 인스턴스는 SSBO에 메시 순으로 정렬해 파이프라인당 indirect draw 한 번으로 그린다.
---
# 0024 — MDI rendering from one registry

## Question
The user's earlier renderer set uniforms and drew per object. What is the v1 rendering strategy that is both fast
and readable?

## Decision
`Meshes` appends every mesh into one vertex buffer and one index buffer and keeps a `MeshInfo` SSBO.
`gather()` writes `Instance` rows sorted by mesh id and one `DrawCommand` per used mesh into mapped stream slices;
the renderer issues one `draw_indirect` per pipeline (`docs/spec/render.md`). Shaders fetch their instance with
`gl_BaseInstance + gl_InstanceID`.

## Options
1. One draw per object with uniforms — the old way; thousands of calls through PyOpenGL is the bottleneck.
2. Instanced draw per mesh — better; still a Python loop over meshes and per-mesh binds.
3. MDI with sorted instances (chosen) — the Python side does one `argsort` and one `bincount`.

## Why
The whole frame submission is ~10 GL calls regardless of instance count, which is what makes Python viable for
100 k instances (`spec/targets.md`).

## Assumptions (check me)
- Sorting instances every frame (`np.argsort`, stable) at 100 k is within the 2 ms gather budget. Measure (task 0017).
- One material family per pass is enough for v1; per-material sorting comes with textures (v2).
- Bindless textures remain optional; a texture array fallback keeps the single-draw property when textures arrive.

## Consequences
- `DrawCommand` must match `DrawElementsIndirectCommand` byte for byte (`spec/layout.md`); a test checks it.
- Culling later becomes a compute pass that rewrites `DrawCommands` without touching Python.
