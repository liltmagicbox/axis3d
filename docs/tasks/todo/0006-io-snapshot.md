---
kind: task
id: 0006
title: io/snapshot.py: snapshot, restore, schema_hash
pack: implement
role: implementer
model: medium
status: todo
blocked_by: [0004]
brief_ko: World를 바이트로, 바이트를 World로. 헤더·rng 상태·next_id·테이블 원시 바이트, 스키마 해시 검사, 왕복 테스트.
---
# 0006 — io/snapshot.py

## Goal
`snapshot(world) -> bytes` and `restore(world, data)` such that `restore(w2, snapshot(w1))` makes `w2` step
byte-identically to `w1`.

## Read
- `docs/spec/snapshot.md`
- `docs/spec/ecs.md` — section "Table" (storage layout)

## Write
- `src/axis3d/io/__init__.py`, `src/axis3d/io/snapshot.py`
- `tests/io/test_snapshot.py`

## Do
1. `schema_hash(world)`: `zlib.crc32` over a canonical string of `name:col:shape:dtype` entries in table/column order.
2. `snapshot(world)`: header per spec (`struct.pack("<4sIQII", ...)` then rng state, then `next_id`), then tables.
   rng: `world.rng.bit_generator.state["state"]["state"]`, `["inc"]`, `has_uint32`, `uinteger` as integers.
3. `restore(world, data)`: validate magic/version/schema (raise `SnapshotSchemaError`), then set `tick`, rng state,
   `next_id`, and each table: ensure capacity, copy `ids` and columns, rebuild `_row_of_id`.
4. Build the byte list with a `list` and `b"".join` (B-006); never `bytes +=`.

## Done when
- `tests/io/test_snapshot.py::test_round_trip_restores_tables_tick_and_next_id` — 3 bodies, tick 7
- `tests/io/test_snapshot.py::test_round_trip_restores_rng_state` — next random after restore equals the original's
- `tests/io/test_snapshot.py::test_schema_mismatch_raises` — a world with a different column set refuses the bytes
- `tests/io/test_snapshot.py::test_empty_world_round_trips` — zero rows in every table
- `tests/io/test_snapshot.py::test_snapshot_size_is_header_plus_raw_bytes` — exact byte count for 2 rows
- `uv run ruff check . && uv run pytest -q` pass; only budgeted names are public

## Out of scope
- Delta snapshots, compression, file helpers beyond `Path.write_bytes` in tests.

## Notes
- `Table` needs a small internal hook to load rows: add `_load(ids, columns_bytes)` (private, so not budgeted) in
  `table.py` rather than poking arrays from `snapshot.py`.
