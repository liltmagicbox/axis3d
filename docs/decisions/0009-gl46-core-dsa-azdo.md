---
kind: decision
id: 0009
title: The v1 backend is OpenGL 4.6 core using DSA only and AZDO patterns; older GL and macOS are not targets
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: moderate — the interface hides GL, but the backend is a HARD ZONE written around DSA
brief_ko: GL 4.6 코어, DSA 함수만 사용, AZDO(영구 매핑 링, MDI, SSBO 인스턴싱, 단일 VAO). 4.1 호환과 macOS는 포기.
---
# 0009 — OpenGL 4.6 core, DSA, AZDO

## Question
The user asked for desktop GL 4.6, DSA and AZDO. What exactly does the backend commit to, and what does it give up?

## Decision
- Context 4.6 core, forward-compatible, sRGB-capable, debug when `AXIS3D_DEBUG=1`.
- Direct State Access for every resource edit (`glCreate*`, `glNamed*`, `glTexture*`, `glVertexArray*`); binding
  happens only to draw (`glBindBufferRange`, `glBindTextureUnit`, `glUseProgram`, one VAO).
- AZDO: persistent-mapped triple-ring stream buffers with fences, `glMultiDrawElementsIndirect`, per-instance data
  in SSBOs read via `gl_BaseInstance + gl_InstanceID` (a 4.6 builtin), no `glGet*`/`glFinish` in the frame.
- Optional extensions are feature-checked, never required (`docs/variants/gl46.md`).

## Options
1. GL 4.1 (the user's earlier shaders): runs on macOS, but no compute, no SSBO, no DSA, no clip control.
2. GL 4.5: everything except `gl_BaseInstance` in GLSL and SPIR-V ingestion; 4.6 is the same hardware.
3. GL 4.6 (chosen).

## Why
Compute shaders, SSBOs, and clip control are load-bearing for ADR 0006, 0011, 0016. `gl_BaseInstance` makes the
instancing story one line in the shader.

## Assumptions (check me)
- The user's development GPUs support 4.6 (any NVIDIA since 2014, AMD/Intel with recent drivers).
- macOS is out of scope; the user did not mention it.
- PyOpenGL's binding overhead per call is acceptable because AZDO keeps calls per frame in the tens.

## Consequences
- The backend is a HARD ZONE (`gpu/gl46/device.py`), used only through `create_device` and the `Device` methods.
- GLES 3.1 port emulates DSA and MDI inside its own folder (`docs/variants/gles31.md`).
