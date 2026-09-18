---
kind: decision
id: 0011
title: GPU-visible structs are declared once in Python and generate both the numpy dtype and the GLSL struct
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: yes — replace the generator; declarations stay
brief_ko: Struct 선언 하나로 numpy dtype과 GLSL struct를 만든다. std430 규칙은 HARD ZONE 한 파일에만 있고, 암묵적 패딩은 오류로 막는다.
---
# 0011 — One struct, two homes

## Question
CPU and GPU must agree on the bytes of `Instance`, `Frame`, `DrawCommand`. Where do those layouts live?

## Decision
`layout.Struct` (`docs/spec/layout.md`): fields typed `f32 i32 u32 vec2 vec4 mat4` or fixed arrays; computes std430
offsets; exposes `.dtype`, `.glsl()`, `.size`, `.align`, `.zeros(n)`. Implicit padding raises `LayoutError` with the
exact pad to add. All structs are declared in `layout/structs.py`; `preprocess.py` writes them into
`shaders/gen/structs.glsl` at startup.

## Options
1. Hand-write both sides and keep them in sync by discipline — the bug class this ADR exists to delete.
2. Parse GLSL to derive dtypes — a parser is a bigger HARD ZONE than a generator.
3. Generate GLSL from Python (chosen) — Python is where the arrays are made; GLSL is the derived artefact.

## Why
"The bytes are the same on both sides" is provable by one test per struct and readable by anyone who can read a
table of offsets. It is also the mechanism that makes SSBO use elegant rather than fragile.

## Assumptions (check me)
- Four structs are enough for v1; more will come (particles, lights) and the same generator serves them.
- Forbidding `vec3`/`mat3` in blocks costs nothing (vertex attributes may still use `vec3`).
- Explicit padding fields (`pad=(u32, 3)`) are an acceptable thing for a beginner to see once the error message
  tells them what to write.

## Consequences
- `rules/gpu_layout.md` G1–G4 are enforced by construction, not by review.
- Compute shaders read the sim columns as `vec4[]` buffers (ADR 0012), not as structs.
