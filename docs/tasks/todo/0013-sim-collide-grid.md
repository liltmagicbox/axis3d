---
kind: task
id: 0013
title: sim/collide/grid.py: candidate_pairs (HARD ZONE)
pack: implement
role: implementer
model: medium
status: todo
blocked_by: [0007]
brief_ko: 균일 격자 해싱으로 충돌 후보 쌍을 벡터화 생성. 정렬된 (m,2) int32, i<j, 중복 없음. HARD ZONE.
---
# 0013 — sim/collide/grid.py

## Goal
`candidate_pairs(pos, radius, cell_size) -> (m, 2) int32` with no Python loop over bodies, deterministic order.

## Read
- `docs/spec/physics.md` — "Broad phase"
- `docs/rules/numpy.md`

## Write
- `src/axis3d/sim/collide/__init__.py`, `src/axis3d/sim/collide/grid.py`
- `tests/sim/collide/test_grid.py`

## Do
1. Docstring first line: `HARD ZONE: sorted-key uniform grid. Use through: candidate_pairs.`
2. `cell = np.floor(pos / cell_size).astype(np.int32)`; key = pack 3 × 21-bit offsets into `int64`; `order = np.argsort(key, kind="stable")`.
3. For each of the 27 neighbour offsets (a `(27, 3)` constant): compute neighbour keys, `np.searchsorted` left/right
   into the sorted keys to get candidate ranges, expand ranges with `np.repeat` + `np.arange` tricks (one function,
   ≤ 15 lines, with a `why` comment), emit `(i, j)` pairs.
4. Keep `i < j`, pack `i * N + j`, `np.unique`, unpack, return `(m, 2)` sorted.

## Done when
- `tests/sim/collide/test_grid.py::test_two_touching_spheres_form_one_pair` — literal positions
- `tests/sim/collide/test_grid.py::test_far_spheres_form_no_pairs` — distance ≫ cell
- `tests/sim/collide/test_grid.py::test_pairs_are_sorted_unique_with_i_less_than_j` — 5 random bodies, seed 0
- `tests/sim/collide/test_grid.py::test_matches_brute_force_on_small_set` — N=5: every brute-force pair within
  `2 × cell_size` is present (superset property)
- `tests/sim/collide/test_grid.py::test_empty_and_single_body` — `(0, 2)` shape
- `uv run ruff check . && uv run pytest -q` pass; only `candidate_pairs` is public

## Out of scope
- Narrow phase, resolve (0014); GPU version.

## Notes
- Brute force reference for tests: `np.triu_indices(N, 1)` and a distance mask; keep it in the test file (≤ 5 lines).
- Negative coordinates: add a large offset before packing keys so the 21-bit fields stay non-negative.
