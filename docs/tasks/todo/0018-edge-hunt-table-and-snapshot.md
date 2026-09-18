---
kind: task
id: 0018
title: edge hunt: Table and snapshot
pack: edge
role: edge_hunter
model: medium
status: todo
blocked_by: [0006]
brief_ko: Table 과 snapshot 의 특이 입력(N=0/1, 중복·죽은·정렬 안 된 id, float64 입력, 성장 중 뷰, 잘린 바이트, 스키마 불일치) 사냥.
---
# 0018 — edge hunt: Table and snapshot

## Goal
Find what breaks `ecs/table.py` and `io/snapshot.py`; leave each finding as a strict-xfail test and a ledger row.

## Read
- `docs/spec/ecs.md` — "Table", "Lifecycle rules"
- `docs/spec/snapshot.md`
- `src/axis3d/ecs/table.py`, `src/axis3d/io/snapshot.py`

## Write
- `tests/ecs/test_table_edges.py`, `tests/io/test_snapshot_edges.py`
- `docs/records/edge_cases.md` (append rows)

## Do
1. Table: `insert` with `float64` values, with `ids` as a Python list, with `(k,)` values for a `(3,)` column,
   with `ids` containing duplicates *within one call*; `remove` of the same id twice in one call; `row_of` with a
   negative id; growth exactly at capacity; 1 000 000 rows once (memory).
2. Snapshot: truncated bytes at every boundary (header, ids, mid-column); wrong magic; version 2; a world whose
   table order differs but columns match; rng restored twice; `restore` into a world with more rows than the bytes.
3. Reproduce each; rank by damage; write strict-xfail tests for real bugs and normal tests for by-design behaviour.

## Done when
- ≥ 8 new rows in `docs/records/edge_cases.md`, each with a test name and a status.
- Every real bug has an `xfail(strict=True)` test; every by-design case has a passing test.
- Report ranks findings and proposes cards for the top three.

## Out of scope
- Fixing anything. World, systems, network.

## Notes
- A duplicate id within one `insert` call is not covered by the spec's "twice" rule: check what happens and say what
  the spec should say (report → architect).
