---
kind: task
id: 0015
title: net: framing, Server, Client
pack: implement
role: implementer
model: medium
status: todo
blocked_by: [0006]
brief_ko: 길이 접두 프레임 인코더/디코더, 수신 스레드→큐 서버, 클라이언트, localhost 왕복 테스트. 옛 소켓 프로토타입의 버그 3개를 테스트로 고정.
---
# 0015 — net: framing, Server, Client

## Goal
A server that steps a world and pushes snapshots, and a client that receives them, over localhost, with the
three prototype bugs (E-003, E-004, E-007) turned into passing tests.

## Read
- `docs/spec/network.md`
- `docs/records/edge_cases.md` — rows E-003, E-004, E-007

## Write
- `src/axis3d/net/__init__.py`, `framing.py`, `server.py`, `client.py`
- `tests/net/test_framing.py`, `tests/net/test_server.py`, `tests/net/test_client.py`

## Do
1. `framing.py`: `Kind` (`IntEnum` 1–6), `encode(kind, payload) -> bytes`, `read_frames(buffer) -> list[(kind, bytes)]`
   consuming complete frames from a `bytearray` in place.
2. `server.py`: `Server(world, port=DEFAULT_PORT, snapshot_every=3)`: `start()` (accept thread + one reader thread per
   client, each feeding a `queue.Queue`), `pump()`, `broadcast()`, `stop()`. Iterate `tuple(self.clients)` (E-004).
3. `client.py`: `Client(host, port, name)`: `connect()` (HELLO → WELCOME, schema check), `send_input(tick, row)`,
   `latest_snapshot()`, `close()`. Discard the buffer on reconnect (E-007).

## Done when
- `tests/net/test_framing.py::test_read_frames_splits_coalesced_frames` — E-003: two frames in one chunk
- `tests/net/test_framing.py::test_read_frames_keeps_partial_tail` — half a frame stays in the buffer
- `tests/net/test_server.py::test_client_receives_snapshot_after_three_ticks` — localhost, ≤ 1 s wall time
- `tests/net/test_server.py::test_broadcast_survives_disconnect` — E-004
- `tests/net/test_client.py::test_reconnect_discards_stale_bytes` — E-007
- `tests/net/test_client.py::test_schema_mismatch_raises_on_connect` — different world schema
- `uv run ruff check . && uv run pytest -q` pass (these are CPU tests; use port 0 = ephemeral)

## Out of scope
- UDP, delta snapshots, prediction, compression.

## Notes
- Tests must not sleep in loops; use `queue.get(timeout=1.0)` and `socket.settimeout(1.0)`.
- `bytes` assembly with lists and `b"".join` (B-006).
