---
kind: task
id: 0017
title: bench: harness and first numbers
pack: perf
role: profiler
model: medium
status: todo
blocked_by: [0014, 0011]
brief_ko: bench/ 하네스와 첫 측정: Table insert/remove, step(1만 바디), collide, gather(10만 인스턴스), (N,3) vs (N,4) 레이아웃 비교.
---
# 0017 — bench: harness and first numbers

## Goal
Replace the guesses in `docs/spec/targets.md` with measured rows in `docs/records/benchmarks.md`, and settle
A-015 and A-017 with data.

## Read
- `docs/spec/targets.md`
- `docs/records/assumptions.md` — rows A-009, A-015, A-017
- `docs/records/benchmarks.md`

## Write
- `bench/run.py`, `bench/bench_table.py`, `bench/bench_step.py`, `bench/bench_collide.py`, `bench/bench_gather.py`
- `docs/records/benchmarks.md` (append rows)

## Do
1. `bench/run.py`: runs every `bench_*.py`, prints a table, records machine info (`platform`, numpy version).
2. `bench_table.py`: insert 100 000 rows in one call vs 1 000 calls of 100; remove 10 000 random ids.
3. `bench_step.py`: `world.step()` with 10 000 bodies, no collision; then with `(N, 4)` padded columns to test A-015.
4. `bench_collide.py`: `collide + resolve` at N = 1 000 and 10 000, uniform random in the box.
5. `bench_gather.py`: 100 000 instances into preallocated structured arrays (CPU only; mapped-memory variant is a
   gpu-guarded run) to test A-017.

## Done when
- Rows B-008 … B-013 appended with medians, targets, and status; each cites its script.
- A-015 and A-017 get a status (`confirmed` or `rejected → proposed ADR`) in `docs/records/assumptions.md`.
- Report lists any `OVER BUDGET` path with a proposed card (no code changes by the profiler).

## Out of scope
- Optimising anything. GPU timing beyond the guarded gather variant.

## Notes
- 3 warm-ups, median of 10, `time.perf_counter`. Seed 0. Same inputs for both layouts in `bench_step.py`.
