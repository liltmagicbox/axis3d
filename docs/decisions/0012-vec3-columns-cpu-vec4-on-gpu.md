---
kind: decision
id: 0012
title: CPU tables keep natural (N, 3) columns; GPU mirrors use vec4 stride, padded during the write into the mapped slice
status: accepted
date: 2026-09-18
decided_by: ai
confidence: medium
reversible: yes — a slice expression in the upload path
brief_ko: CPU 열은 (N,3) 그대로 두고, GPU에 올릴 때 매핑된 버퍼의 [:, :3]에 쓰면서 vec4 stride로 패딩한다. 별도 복사 패스 없음.
---
# 0012 — (N, 3) on the CPU, vec4 on the GPU

## Question
std430 gives `vec3` a 16-byte stride, so an `(N, 3)` float32 array cannot be uploaded as-is. Store `(N, 4)` on the
CPU, or pad on the way up?

## Decision
Tables store `(N, 3)`. Stream buffers for sim columns are `(N, 4)` float32 views of the mapped slice; the upload is
`slice_view[:n, :3] = pos` (one strided copy, no extra pass). Compute shaders declare `vec4[]` and ignore `.w`.
Structured buffers (`Instance` …) are written field by field into the mapped structured view.

## Options
1. `(N, 4)` everywhere — zero-copy uploads, but every numpy formula carries a `[:, :3]` and 33 % more CPU memory.
2. Pad with `np.pad`/`np.concatenate` per frame — allocates every frame (`rules/performance.md` F9).
3. Padded write into the mapped destination (chosen) — the copy we must do anyway does the padding.

## Why
Beginners read `pos[:, 2]` as "z". Persistent mapping means the upload is a memcpy into GPU-visible memory either
way; letting numpy's strided assignment do the padding costs nothing extra.

## Assumptions (check me)
- Strided writes into write-combined mapped memory are not pathologically slow on target drivers. Must be measured
  (task 0017, `bench_gather.py`); if slow, switch to option 1 for the sim columns only.
- The `w` lane being garbage is never read by a shader; `SimAux` packs radius/mass/flags explicitly instead.

## Consequences
- `render/gather.py` and the compute mirror upload paths are the only places that know about the vec4 stride.
- `spec/shaders.md` slots 4–7 are documented as `vec4[]`.
