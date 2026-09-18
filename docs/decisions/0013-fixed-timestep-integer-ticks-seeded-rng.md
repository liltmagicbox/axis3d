---
kind: decision
id: 0013
title: Fixed 60 Hz timestep with an accumulator, integer ticks, and a seeded generator inside World
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: yes — DT constant and the loop
brief_ko: 시뮬레이션은 1/60 고정 스텝, tick은 정수, 난수는 World의 시드 생성기에서만. 렌더는 alpha로 보간. 결정성과 네트워크의 기초.
---
# 0013 — Fixed timestep, ticks, seeded randomness

## Question
Variable `dt` per frame (the earlier prototypes) or a fixed step? Where does randomness come from?

## Decision
`DT = 1/60`; `app/loop.py` accumulates wall-clock and calls `world.step()` zero or more times per frame (max 15,
clamp 0.25 s); rendering interpolates `prev_pos → pos` with `alpha`. `world.tick` is `int64`. Randomness comes only
from `world.rng` (`np.random.default_rng(seed)`), whose state is inside the snapshot.

## Options
1. Variable `dt` — simplest loop, but physics results depend on frame rate and nothing is reproducible.
2. Fixed step without interpolation — reproducible but visibly stutters at non-multiple refresh rates.
3. Fixed step + interpolation + seeded rng (chosen).

## Why
Determinism is what makes snapshots, network sync, replays, and tests agree byte for byte (`spec/physics.md`
determinism contract). Integer ticks are the clock the network protocol speaks.

## Assumptions (check me)
- 60 Hz is a fine default for a simulation engine; making it configurable per World is one constructor argument
  and is already allowed (`World(dt=...)`), but changing it mid-run is not.
- Interpolating only positions (not rotations) is acceptable for v1; rotation interpolation is a slerp away.
- numpy float32 arithmetic is deterministic across machines with the same numpy build. Known risk: BLAS-backed
  reductions may differ; systems avoid them (`rules/numpy.md` N6).

## Consequences
- `prev_pos` is a reserved column written by `integrate` (`spec/physics.md`).
- Tests can run 1000 steps headless in milliseconds and compare bytes.
