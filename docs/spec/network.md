---
kind: spec
brief_ko: 네트워크 v1. 서버 권위, TCP 길이 접두 프레임, 메시지 5종, 스레드 수신→큐, 스텝당 큐 배출, UDP·델타는 v2.
---
# Network

`src/axis3d/net/` (walk-through). One server owns the `World`; clients send inputs and receive snapshots. (ADR 0015)

## Framing — `net/framing.py`
```python
encode(kind: int, payload: bytes) -> bytes             # u32 length (of kind+payload) | u8 kind | payload
read_frames(buffer: bytearray) -> list[tuple[int, bytes]]   # consumes complete frames, leaves the partial tail
```
Length-prefixed frames end the classic TCP problem the earlier prototype hit (E-003): markers can merge in one `recv`.

## Messages
| kind | name | direction | payload |
|---|---|---|---|
| 1 | HELLO | client → server | utf-8 name |
| 2 | WELCOME | server → client | u32 client_id, f32 dt, u32 schema_hash |
| 3 | INPUT | client → server | u64 tick, then one `inputs` row as raw bytes |
| 4 | SNAPSHOT | server → client | `snapshot(world)` bytes |
| 5 | PING / PONG | both | f64 send time (echoed) |

## Server — `net/server.py`
```python
Server(world: World, port: int = 41000, snapshot_every: int = 3)
s.start() -> None          # accept thread; one reader thread per client feeding a queue.Queue
s.pump() -> None           # called once per step: drain queues, write INPUT rows into world.inputs
s.broadcast() -> None      # every `snapshot_every` ticks: send SNAPSHOT to all clients
s.stop() -> None
```
Threads touch only sockets and queues. The game loop thread is the only one touching `World`.

## Client — `net/client.py`
```python
Client(host: str, port: int = 41000, name: str = "player")
c.connect() -> int         # returns client_id; raises on schema mismatch
c.send_input(tick, row: np.ndarray) -> None
c.latest_snapshot() -> bytes | None   # newest complete SNAPSHOT since last call, or None
c.close() -> None
```
The client renders `restore(local_world, latest_snapshot())`. No prediction, no interpolation between snapshots in v1.

## Rules
- Localhost first; the earlier prototype measured loopback as fastest (B-005). Never block the loop thread on a socket.
- Sizes: one snapshot per 3 ticks at 60 Hz = 20 Hz × ~0.9 MB for 10k bodies. LAN only until delta snapshots exist.
- Tests use `socket.socketpair()` for framing and a real localhost server for one round trip (`tests/net/`).

## Planned v2
UDP with latest-tick-wins for SNAPSHOT, delta snapshots, client-side interpolation between the last two snapshots.
