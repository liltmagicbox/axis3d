---
kind: decision
id: 0006
title: Depth uses [0, 1] clip range with reversed-Z and a 32-bit float depth buffer
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: yes — projection function and four GL state lines
brief_ko: 깊이는 glClipControl(ZERO_TO_ONE)와 역Z(가까움=1, 멂=0), GREATER 비교, D32F. Vulkan과 같은 범위라 이식이 쉽다.
---
# 0006 — Reversed-Z in [0, 1]

## Question
The user wants a 0–1 depth range. How is depth precision and portability handled?

## Decision
`glClipControl(GL_LOWER_LEFT, GL_ZERO_TO_ONE)`; the projection maps near → 1.0 and far → 0.0 (reversed);
depth test `GREATER`; clear depth `0.0`; depth attachment `d32f`. `perspective(fov_y, aspect, near, far=None)`
supports an infinite far plane (`far=None`).

## Options
1. Classic `[-1, 1]` with `LESS`: familiar, but wastes float precision near the far plane and differs from Vulkan.
2. `[0, 1]` without reversal: better than 1, still loses precision; no reason to stop half way.
3. `[0, 1]` reversed with float depth (chosen): near-uniform precision across the range; Vulkan-native range.

## Why
Reversed-Z with a float buffer removes z-fighting at scale for free, and the `[0, 1]` range is what the future
Vulkan backend expects (`docs/variants/vulkan.md`), so no projection code changes at port time.

## Assumptions (check me)
- All target GPUs support `GL_ARB_clip_control` (core since 4.5): true for the platforms in `spec/targets.md`.
- GLES 3.1 has no clip control; the variant emulates it in the projection matrix with lower precision, which is
  acceptable for a mini engine (`docs/variants/gles31.md`).
- Nobody reads `gl_FragCoord.z` expecting 1.0 to mean "far" (`spec/shaders.md` says so).

## Consequences
- Every depth comparison and clear in the backend follows this; `PipelineState.depth_test=True` means `GREATER`.
- Debug tools that assume `LESS` (some frame captures) show inverted depth; document in the tour.
