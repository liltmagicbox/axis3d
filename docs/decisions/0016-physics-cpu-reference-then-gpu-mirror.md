---
kind: decision
id: 0016
title: Physics is a numpy reference implementation first (spheres, uniform grid); the GPU compute mirror must match it
status: accepted
date: 2026-09-18
decided_by: ai
confidence: medium
reversible: moderate — stages are separate modules; a different broad phase is one HARD ZONE swap
brief_ko: 물리는 numpy CPU 구현이 기준(구 충돌, 균일 격자, 위치 보정+충격량). GPU 컴퓨트 미러는 CPU와 허용오차 안에서 일치해야 한다.
---
# 0016 — CPU reference physics, GPU mirror later

## Question
The user wants compute shaders and collision physics. Which comes first, and how do we keep them honest?

## Decision
Stages `integrate → collide (grid + narrow) → resolve → bounds → expire` in numpy (`docs/spec/physics.md`).
Spheres only in v1. The grid broad phase is the one HARD ZONE. GPU compute versions come stage by stage
(`integrate.comp` first) and are tested against the CPU result with `atol=1e-4` over 60 steps.

## Options
1. GPU-first — faster ceilings, but no oracle to test against, and beginners cannot read a compute-only physics.
2. CPU-only forever — misses the user's compute-shader goal and the 100 k particle target.
3. CPU reference + GPU mirror (chosen).

## Why
A reference implementation that anyone can read and run headless is worth more than early speed; the mirror test
is the cheapest possible correctness check for GPU code.

## Assumptions (check me)
- 10 k spheres in ≤ 4 ms CPU is achievable with a sorted-key grid in numpy (the user measured an O(N²) loop at
  ~30 ms for N ≈ 1000, B-002; the grid is O(N log N) and vectorised). To be confirmed by task 0017.
- Radii within 10× of each other; a uniform grid degrades beyond that. Hierarchical grids are a v2 ADR.
- One resolve iteration is enough for visual plausibility; stacking stability is not a v1 goal.

## Consequences
- Pairs are sorted before use so results are deterministic (`rules/numpy.md` N6).
- Compute shaders read `vec4[]` mirrors of the columns (ADR 0012) on slots 4–7.
