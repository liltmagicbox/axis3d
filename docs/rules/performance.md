---
kind: rule
brief_ko: 성능 규칙. 엔티티 루프 금지, float32, 사전 할당, 프레임 루프에 glGet 금지, 측정 후 최적화.
---
# Rule: performance

Budgets are in `docs/spec/targets.md`. This file is how we stay under them.

## Must
- F1 Systems touch whole columns: `pos += vel * dt`. A Python `for` over entities is a bug unless N ≤ 16 and a comment says why.
- F2 State is `float32` / `int32`. Cast at the boundary (input, file, network), never inside a system.
- F3 Preallocate: tables double capacity; per-step scratch arrays live in the table (`_scratch_*`) or are reused.
- F4 Write in place when the shape is fixed: `np.add(a, b, out=a)`, `np.multiply(a, s, out=a)`.
- F5 GPU uploads go through persistent-mapped stream rings; one write per buffer per frame. No `glBufferSubData` in the loop.
- F6 Measure before optimising: a speed claim cites a `docs/records/benchmarks.md` row before and after.
- F7 Draw calls: one `draw_indirect` per pipeline per pass. State changes per frame ≤ number of pipelines.

## Never
- F8 No per-entity Python objects in a step. No `dict` keyed by entity inside a system.
- F9 No `np.append` / `np.concatenate` / list comprehensions producing arrays inside a step.
- F10 No `glGet*`, `glFinish`, or readback in the frame loop outside profiler code paths.
- F11 No optimisation without a failing budget. Clarity wins ties.

## Check
- [ ] no entity loops  - [ ] float32/int32  - [ ] no per-step allocation  - [ ] no glGet in the frame
- [ ] speed claims cite benchmark rows
