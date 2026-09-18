---
kind: decision
id: 0003
title: All mutable simulation state is numpy arrays inside one World object
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: hard — this shapes every module; changing it is a rewrite
brief_ko: 변하는 상태는 모두 World 안의 numpy 배열이다. 그래서 스냅샷·네트워크·리플레이·GPU 미러가 같은 바이트 복사 한 번이 된다.
---
# 0003 — State is data

## Question
Where does simulation state live, and what may hold state between steps?

## Decision
Only `World` holds mutable simulation state: its tables (numpy columns), `tick`, `rng` state, `next_id`, and the
pending removal list. Systems are stateless functions. Renderer, device, window, and network objects hold handles
and buffers but no simulation truth.

## Options
1. Objects with attributes per entity (the `new3dkatsu` design): easy to write, impossible to snapshot or vectorise.
2. Hybrid: arrays for hot data, objects for "logic" (the `axis3d` `Unit`/`UnitArray` experiment): two truths, sync bugs.
3. Arrays only (chosen): every feature that needs "the state" gets it from one place.

## Why
`snapshot()` becomes a byte copy. Network sync, save/load, replay, deterministic tests, and GPU mirroring are then
the same operation, which is the single most educational idea in the engine (`docs/spec/overview.md`).

## Assumptions (check me)
- Gameplay logic that "wants an object" can be expressed as columns plus a system; when it cannot, a `scripts`
  table of small integer opcodes is still data. Untested belief.
- Python-level per-entity behaviour (the user's `Behavior`/`Timer` idea) is either vectorised (`ttl` column) or
  deferred to Godot after export (ADR 0022).

## Consequences
- `inputs` are a table too (ADR 0026); wall-clock never enters `step()` (ADR 0013).
- No system may keep module-level caches; scratch arrays live in tables as `_scratch_*` columns or are reused.
