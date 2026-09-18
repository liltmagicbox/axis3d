---
kind: spec
brief_ko: 스냅샷 바이트 포맷 v1. 헤더(매직·버전·tick·스키마 해시·rng), 테이블별 ids와 열의 원시 바이트. 스키마 불일치는 예외.
---
# Snapshot

`src/axis3d/io/snapshot.py` (walk-through). The whole world becomes bytes and back. (ADR 0014)

## API
```python
snapshot(world: World) -> bytes
restore(world: World, data: bytes) -> None       # in place: resizes tables, sets tick and rng state
schema_hash(world: World) -> int                  # uint32 over table names, column names, shapes, dtypes, in order
class SnapshotSchemaError(ValueError): ...        # message: "schema 0x1234abcd != world 0x9876fedc"
```

## Format v1 (little-endian, no alignment padding)
```
header:  b"AX3D" | u32 version = 1 | u64 tick | u32 schema_hash | u32 n_tables | u32 rng_len | rng_len bytes
                   (rng bytes = pickle-free: np.random.PCG64 state as 4 × u64 + u8 has_uint32 + u32 uinteger)
table ×n: u16 name_len | name utf-8 | u32 n | ids (n × int32) | for each column in declared order: raw bytes
          (n × prod(shape) × itemsize, C order)
```
Column names, shapes, and dtypes are *not* stored; they are the world's schema and are checked by `schema_hash`.
`next_id` of the world is stored as the last u32 before the tables so `spawn` continues without id reuse.

## Rules
- `restore` first validates magic, version, and schema hash; on failure it raises before touching the world.
- Tables are restored to exactly `n` rows; capacity grows if needed and is never shrunk.
- After `restore`, `world.step()` produces byte-identical results to the original run (`docs/spec/physics.md`
  determinism contract). Test: snapshot at tick 100, step both 50 times, compare bytes.
- Size: 10 000 bodies ≈ 10 000 × (4 + 3·4·4 + 4·4 + 3·4 + 4 + 4 + 1) ≈ 0.9 MB. Fine for LAN and files; delta for WAN.

## File use
`Path.write_bytes(snapshot(w))`, `restore(w, Path.read_bytes())`. Extension `.ax3d`. No compression in v1
(a `zlib` flag bit in `version` is reserved for v2).

## Planned v2 (not now)
Delta snapshots: per table a changed-row bitmask plus only those rows; keyed to the tick of the base snapshot.
