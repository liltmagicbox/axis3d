---
kind: decision
id: 0015
title: Networking v1 is server-authoritative over TCP with length-prefixed frames, reader threads, and per-step queue draining
status: accepted
date: 2026-09-18
decided_by: ai
confidence: medium
reversible: yes — transport is one module; the message set stays
brief_ko: 서버가 World를 소유하고 스냅샷을 보낸다. TCP 길이 접두 프레임, 소켓당 수신 스레드→큐, 게임 루프가 스텝마다 큐를 비운다. UDP·델타·예측은 v2.
---
# 0015 — Server-authoritative TCP v1

## Question
How do states cross the network in v1 without pulling the whole engine into async code?

## Decision
`docs/spec/network.md`: one server steps the world; clients send `INPUT` rows and receive `SNAPSHOT` bytes every
3 ticks. TCP with `u32 length | u8 kind | payload`. One reader thread per socket pushes into a `queue.Queue`; the loop
thread drains queues once per step. No prediction, no interpolation between snapshots.

## Options
1. UDP first — the user's earlier notes favoured it; but v1 has no delta and no loss handling, so TCP is simpler.
2. `asyncio` — clean, but it colours every caller; the loop is synchronous by design (`app/loop.py`).
3. WebSockets — useful for a browser client later; not now.
4. Threads + queues + TCP (chosen) — exactly the shape the user's prototype reached after "7, 5, 12 hours"
   (`axis3d/test_socket.py`), with the framing bug fixed by length prefixes.

## Why
It works with the standard library, it is readable, and every later step (UDP, delta) changes one module.

## Assumptions (check me)
- LAN only; 20 Hz × ~1 MB is fine there. The user did not ask for internet play.
- A single loop thread touching `World` is enough; reader threads only touch sockets and queues.
- 8 clients maximum for v1 (`spec/targets.md`).

## Consequences
- `E-003` (marker merging) and `E-004` (dict changed size during iteration) from the prototype are recorded and tested.
- Client rendering lags the server by up to 3 ticks plus latency; acceptable for v1, noted in the tour.
