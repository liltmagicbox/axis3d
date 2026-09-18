---
kind: spec
brief_ko: 물리. 반음해 오일러 적분, 균일 격자 광역 단계(HARD ZONE), 구-구 협역 단계, 위치 보정+충격량 해결, 결정적 쌍 순서, CPU 기준→GPU 미러.
---
# Physics

CPU numpy is the reference implementation; a GPU compute mirror must match it within tolerance. (ADR 0016)
Tables: `bodies` with `pos vel acc prev_pos (N,3) rot (N,4) scale (N,3) mass radius (N,) flags (N,) uint8`.

## Stages per step (in `ecs/schedule.SYSTEMS` order)
| stage | module | zone | in → out |
|---|---|---|---|
| integrate | `sim/integrate.py` | walk | `prev_pos = pos; vel += (acc + gravity) * dt; pos += vel * dt` |
| collide | `sim/collide/grid.py` → `narrow.py` | grid HARD, narrow walk | `pos, radius → pairs (m,2) int32, normal (m,3), depth (m,)` |
| resolve | `sim/collide/resolve.py` | walk | pairs → corrected `pos`, updated `vel` |
| bounds | `sim/bounds.py` | walk | keep bodies inside the world box; reflect velocity |
| expire | `sim/lifetime.py` | walk | `ttl (N,)` column reaches 0 → `world.despawn` |

## Broad phase — `sim/collide/grid.py` (HARD ZONE, use through `candidate_pairs`)
```python
candidate_pairs(pos: (N,3) float32, radius: (N,) float32, cell_size: float) -> (m, 2) int32   # i < j, sorted
```
Uniform grid hashing: `cell = floor(pos / cell_size)` as `int32 (N,3)`; sort bodies by cell key; for each of the
27 neighbour offsets, join sorted keys (`np.searchsorted`) to emit pairs; drop `i >= j` and duplicates
(`np.unique` on packed `i * N + j`). `cell_size` = 2 × max radius by default. Output is sorted lexicographically
so every later stage is deterministic regardless of memory layout.

## Narrow phase — `sim/collide/narrow.py`
```python
sphere_pairs(pos, radius, pairs) -> tuple[(m,2) int32, (m,3) float32, (m,) float32]   # touching pairs, normal, depth
```
`d = pos[j] - pos[i]`, `dist = |d|`, keep `dist < r_i + r_j`; `normal = d / dist` (or `(0,0,1)` when `dist == 0`),
`depth = r_i + r_j - dist`.

## Resolve — `sim/collide/resolve.py`
```python
resolve_pairs(pos, vel, mass, pairs, normal, depth, restitution: float = 0.2) -> None   # in place; called by the `resolve` system
```
Positional correction: move each body along `normal` by `depth * w / (w_i + w_j)` with `w = 1 / mass`
(`mass == 0` means static, `w = 0`). Impulse: `j = -(1 + e) * (v_rel · n) / (w_i + w_j)` for approaching pairs only.
Accumulate with `np.add.at` because one body may appear in many pairs. One iteration in v1.

## Determinism contract
Same snapshot + same inputs → identical bytes after `step()` on any machine with the same numpy version.
Pairs are sorted before use; scatter uses `np.add.at` (ordered); no hash-order dependence anywhere.

## GPU mirror (planned; `render/shaders/integrate.comp` first)
Same stages as compute shaders over SSBO slots 4–7 (`docs/spec/shaders.md`). Test: run both for 60 steps on the
same seed; `assert_allclose(pos_gpu, pos_cpu, atol=1e-4)`.

## Tolerances and limits
N ≤ 10 000 bodies in v1 at ≤ 4 ms per `collide + resolve` (`docs/spec/targets.md`). Radii within 10× of each other
(the uniform grid degrades beyond that; a hierarchy is a v2 decision).
