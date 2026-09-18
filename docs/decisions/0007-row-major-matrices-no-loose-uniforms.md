---
kind: decision
id: 0007
title: Matrices are numpy (4,4) row-major with M @ v; GLSL blocks declare row_major; no loose matrix uniforms
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: yes — a layout qualifier and a docstring, if ever
brief_ko: 행렬은 numpy (4,4) C-order로 두고 GLSL 블록에 row_major를 선언해 바이트를 그대로 쓴다. 전치도 없고 loose uniform도 없다.
---
# 0007 — Row-major matrices, one memory layout

## Question
numpy is row-major; GL's default is column-major. The user's earlier code spent many comments fighting this
(`matrix.py`, `test_renderer.py`). How do we make matrix bytes mean one thing everywhere?

## Decision
- Store `(4, 4) float32` in C order, math convention `M @ v` with column vectors. `model = T @ R @ S`.
- Every UBO/SSBO block is declared `layout(std430, row_major, ...)`, so GLSL reads the same bytes correctly and
  `M * v` in GLSL equals `M @ v` in numpy. No transposes anywhere.
- Matrices never go through `glUniformMatrix4fv`; per-frame matrices live in the `Frame` UBO, per-instance ones in
  the `Instances` SSBO. This is also what AZDO wants (ADR 0009).

## Options
1. Transpose on upload (`transpose=GL_TRUE`) — works for uniforms only, not for buffers; two mechanisms.
2. Store column-major (`order="F"`) in numpy — correct bytes, but every numpy user is surprised by `.T` semantics.
3. `row_major` qualifier on blocks + no loose uniforms (chosen) — one rule, zero transposes.

## Why
One rule a beginner can verify: "the bytes of `M` are the same in Python and in the shader".

## Assumptions (check me)
- Every backend we target honours `row_major` in std430 blocks (GL 4.6, GLES 3.10, SPIR-V: yes).
- Vertex-attribute matrices (which cannot take `row_major`) are never used; instances come from SSBO instead.

## Consequences
- `layout.Struct` declares `mat4` as `('<f4', (4, 4))`; `spec/layout.md` alignment table treats it as 4 × vec4.
- `spec/shaders.md` forbids `u_*` uniforms; samplers are the only non-block bindings.
