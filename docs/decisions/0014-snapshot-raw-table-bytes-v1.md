---
kind: decision
id: 0014
title: Snapshot v1 is a small header plus the raw bytes of every table; schema is hashed, not stored
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: yes — the format is versioned in the header
brief_ko: 스냅샷 v1 = 헤더(매직·버전·tick·스키마 해시·rng·next_id) + 테이블별 ids와 열 원시 바이트. 압축·델타는 v2.
---
# 0014 — Snapshot format v1

## Question
What is the byte format of `snapshot(world)`, and how much does v1 promise?

## Decision
`docs/spec/snapshot.md`: magic `AX3D`, `u32 version`, `u64 tick`, `u32 schema_hash`, rng state, `next_id`, then per
table its name, `n`, `ids`, and each column's raw bytes in declared order. Schema (names, shapes, dtypes) is not stored;
`restore` refuses a mismatching `schema_hash`. No compression, no delta.

## Options
1. `pickle` — one line, but unsafe to receive over a network and not readable by other tools.
2. `np.savez` — fine for files, awkward for sockets and for a 20 Hz stream.
3. Self-describing format with schema inside — more code now; needed only when formats must evolve independently.
4. Raw bytes + schema hash (chosen) — zero parsing on the hot path, trivially readable in a hex dump.

## Why
The whole point of ADR 0003 is that state is already bytes. The format should be the thinnest possible envelope.

## Assumptions (check me)
- Both ends run the same code version (LAN play, save files from the same build). Schema evolution is deferred:
  a version bump plus a migration function per version when it is needed.
- ~1 MB per snapshot for 10 k bodies is fine for LAN at 20 Hz (20 MB/s); WAN needs delta snapshots (v2).
- Storing `PCG64` state as integers (not pickle) keeps the format language-neutral.

## Consequences
- Save files are `.ax3d`; a replay is a snapshot plus the `inputs` table per tick.
- Network `SNAPSHOT` messages carry these bytes verbatim (ADR 0015).
