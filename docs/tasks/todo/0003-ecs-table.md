---
kind: task
id: 0003
title: ecs/table.py: SoA Table with ids and row_of
pack: implement
role: implementer
model: small
status: todo
blocked_by: [0002]
brief_ko: 열마다 (capacity,*shape) 배열, dense ids, id→row 배열, insert/remove(swap)/row_of/has 를 갖는 Table 구현.
---
# 0003 — ecs/table.py

## Goal
`Table` exactly as `docs/spec/ecs.md` describes: columns are views into preallocated arrays, rows are dense,
ids map to rows through an `int32` array.

## Read
- `docs/spec/ecs.md` — section "Table"
- `docs/records/edge_cases.md` — rows E-008, E-009

## Write
- `src/axis3d/ecs/__init__.py`, `src/axis3d/ecs/table.py`
- `tests/ecs/test_table.py`

## Do
1. `Table(name, columns, capacity=1024)`; `columns` maps name → `(shape, dtype)`; every column becomes
   `np.zeros((capacity, *shape), dtype)`; plain attribute per column is set once (`self.pos`), plus `col(name)`.
2. `ids`, `n`, `insert(ids, **values)` (grow ×2 when `n + k > capacity`; duplicate id → `ValueError` naming the id;
   missing values → zeros; values broadcast with `np.broadcast_to`).
3. `remove(ids)`: swap-remove using vectorised moves where possible; unknown ids ignored; `_row_of_id` updated.
4. `row_of(ids) -> int32` (`-1` for absent, including ids beyond the map's length), `has(ids) -> bool`.

## Done when
- `tests/ecs/test_table.py::test_insert_sets_values_and_zeros_missing` — 3 ids, `pos` given, `mass` is zeros
- `tests/ecs/test_table.py::test_insert_broadcasts_scalar_to_all_rows` — `mass=2.0` fills all rows
- `tests/ecs/test_table.py::test_remove_swaps_last_row_into_hole` — remove the middle of 3; ids and pos stay paired
- `tests/ecs/test_table.py::test_remove_unknown_ids_is_ignored` — E-008
- `tests/ecs/test_table.py::test_col_view_refetched_after_growth` — E-009: after growth a fresh `col()` sees all rows
- `tests/ecs/test_table.py::test_row_of_returns_minus_one_for_absent` — absent and out-of-range ids → −1
- `tests/ecs/test_table.py::test_insert_duplicate_id_raises` — `ValueError` names the id
- `tests/ecs/test_table.py::test_empty_table_operations_are_safe` — `n == 0`: `col()` is `(0, 3)`, `remove([])` ok

## Out of scope
- World, spawn ids, deferred removal (0004).

## Notes
- Keep `_row_of_id` growth in one small function `_ensure_map_size(max_id)`.
- Swap-remove for k ids at once: process ids whose rows are ≥ `n - k` carefully; a simple loop over ≤ k ids is
  acceptable only with a `why` comment (F1) — prefer the vectorised "move tail rows into holes" formulation.
