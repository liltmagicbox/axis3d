---
kind: record
brief_ko: 엣지케이스 장부. 깨지는 입력, 관찰, 기대(spec 근거), 재현 테스트, 상태. 옛 저장소의 메모에서 옮긴 사례로 시작.
---
# Edge cases ledger (append-only)

Ids `E-NNN`. Status `open | fixed | by-design | planned` (planned = the card that will add the test is named).
Rows E-001…E-012 were harvested from the earlier repositories' inline notes so the lessons are not lost.

| id | module | input / situation | observed | expected (spec) | test | status |
|---|---|---|---|---|---|---|
| E-001 | numpy | `np.prod(np.arange(...))` on int64 | silent overflow to negative (`highspeed/nptest.py`) | never rely on integer reductions for big ranges (`rules/numpy.md` N7) | — | by-design |
| E-002 | numpy | `np.random.random(3, 2)` | `TypeError`; `rand(3, 2)` works | use `world.rng` only (`rules/testing.md` T3) | — | by-design |
| E-003 | net/framing | two frames arrive in one `recv` | START/END markers merged: `b"...ENDSTART..."` (`test_socket.py`) | length-prefixed frames split exactly (`spec/network.md`) | `tests/net/test_framing.py::test_read_frames_splits_coalesced_frames` | planned 0015 |
| E-004 | net/server | client disconnects during broadcast | `RuntimeError: dictionary changed size during iteration` | iterate over `tuple(clients)` (`spec/network.md`) | `tests/net/test_server.py::test_broadcast_survives_disconnect` | planned 0015 |
| E-005 | gpu | uniform optimised out by the compiler | `glGetUniformLocation` returns -1 | no loose uniforms exist (ADR 0007) | — | by-design |
| E-006 | gpu | any GL object created before a context exists | obscure failure in `glCreateShader` | `create_device` asserts a current context (`variants/gl46.md`) | `tests/gpu/test_device_contract.py::test_create_device_without_context_raises` | planned 0008 |
| E-007 | net/client | server restarts while a client's buffer holds old bytes | `int()` parse error on stale header | HELLO/WELCOME handshake resets state (`spec/network.md`) | `tests/net/test_client.py::test_reconnect_discards_stale_bytes` | planned 0015 |
| E-008 | ecs/table | `remove(ids)` with an id not in the table or already removed | — | ignored silently (`spec/ecs.md`) | `tests/ecs/test_table.py::test_remove_unknown_ids_is_ignored` | planned 0003 |
| E-009 | ecs/table | `col()` view kept across an `insert` that grows capacity | stale view (old buffer) | fetch views at the top of a system (`spec/ecs.md`) | `tests/ecs/test_table.py::test_col_view_refetched_after_growth` | planned 0003 |
| E-010 | layout | `vec3` field in an SSBO struct | 16-byte stride mismatch with numpy | `Struct` rejects `vec3` (`spec/layout.md`) | `tests/layout/test_struct.py::test_vec3_is_rejected` | planned 0005 |
| E-011 | linalg | column-major vs row-major matrices | days lost in `new3dkatsu/code/matrix.py` | one layout everywhere (ADR 0007) | `tests/linalg/test_transform.py::test_trs_matches_hand_computed_matrix` | planned 0002 |
| E-012 | sim | `np.sum` over float32 pairs in hash order | run-to-run differences | sorted pairs, `np.add.at` (`rules/numpy.md` N6) | `tests/sim/test_determinism.py::test_fifty_steps_are_byte_identical` | planned 0014 |
