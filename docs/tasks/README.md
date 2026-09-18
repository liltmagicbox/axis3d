---
kind: map
brief_ko: 작업 보드. 첫 스프린트의 카드 목록, 순서, 의존성, 역할, 모델 크기, 상태. 계획자와 기록자가 갱신한다.
---
# Task board

Cards live in `todo/` and move to `done/` (scribe). `blocked_by` names cards that must be done first.
Status `todo | in-progress | done | blocked | needs-human`. Sprint 1 goal: **bouncing spheres on screen, snapshotted,
synced over LAN, exported to glTF**, with the document system proven on real cards.

| id | title | role | model | pack | blocked_by | status |
|---|---|---|---|---|---|---|
| 0001 | Bootstrap project skeleton and doc tools | implementer | — | implement | — | done |
| 0002 | conventions.py and linalg (quaternion, transform, projection) | implementer | medium | implement | 0001 | in-progress |
| 0003 | ecs/table.py: SoA Table with ids and row_of | implementer | small | implement | 0002 | todo |
| 0004 | ecs: World, schedule, join | implementer | small | implement | 0003 | todo |
| 0005 | layout/struct.py: Struct → dtype + GLSL (HARD ZONE) | implementer | medium | implement | 0002 | todo |
| 0006 | io/snapshot.py: snapshot, restore, schema_hash | implementer | medium | implement | 0004 | todo |
| 0007 | sim: integrate, bounds, expire | implementer | small | implement | 0004 | todo |
| 0008 | gpu: Device interface and gl46 buffers/textures | implementer | medium | implement_gpu | 0001 | in-progress |
| 0009 | gpu: gl46 pipelines, passes, frame ring, preprocess | implementer | medium | implement_gpu | 0008 | todo |
| 0010 | app: Window, Input, bindings, loop | implementer | medium | implement_gpu | 0004 | todo |
| 0011 | render: Meshes, primitives, gather | implementer | medium | implement | 0005, 0007 | todo |
| 0012 | render: Camera, Renderer, first frame | implementer | medium | implement_gpu | 0009, 0010, 0011 | todo |
| 0013 | sim/collide/grid.py: candidate_pairs (HARD ZONE) | implementer | medium | implement | 0007 | todo |
| 0014 | sim/collide: sphere_pairs, resolve_pairs, determinism test | implementer | small | implement | 0013 | todo |
| 0015 | net: framing, Server, Client | implementer | medium | implement | 0006 | todo |
| 0016 | io/gltf.py: export_glb | implementer | medium | implement | 0011 | todo |
| 0017 | bench: harness and first numbers | profiler | medium | perf | 0014, 0011 | todo |
| 0018 | edge hunt: Table and snapshot | edge_hunter | medium | edge | 0006 | todo |
| 0019 | tour: core path | teacher | medium | teach | 0007 | todo |
| 0020 | Move legacy root experiments to legacy/ | scribe | small | record | — | done |
| 0021 | gpu/gles31 backend (mini engine) | porter | medium | port_gles31 | 0012 | blocked |
| 0022 | tests: ECS behaviours as examples | tester | small | test | 0004 | todo |

## Running a card
```
uv run python tools/pack.py docs/packs/<pack>.md --task docs/tasks/todo/<id>-*.md --stats > /tmp/prompt.md
```
Give `/tmp/prompt.md` to a model in the card's role (or use the `.claude/agents/<role>` wrapper with the card path).
Then: reviewer on the diff → stylist → scribe moves the card. Profiler/edge_hunter when the board says so.
