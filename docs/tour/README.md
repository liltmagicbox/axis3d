---
kind: tour
brief_ko: 사람을 위한 읽기 경로 색인. 첫 tour는 task 0019에서 teacher가 쓴다. 지금은 계획된 경로만 적혀 있다.
---
# Tours: how to read axis3d

Tours are for humans. Each is 10–20 steps of "open this file, look at this, notice this" written by the `teacher`
role (`docs/templates/tour.md`). They are created when the code they walk through exists.

## Planned tours
| tour | walks through | written by |
|---|---|---|
| `core.md` | `conventions.py` → `ecs/table.py` → `ecs/world.py` → `sim/integrate.py` → `io/snapshot.py` | task 0019 |
| `frame.md` | `app/loop.py` → `render/gather.py` → `render/renderer.py` → `gpu/device.py` | after task 0012 |
| `physics.md` | `sim/collide/grid.py` (HARD ZONE) → `narrow.py` → `resolve.py` | after task 0014 |
| `network.md` | `net/framing.py` → `server.py` → `client.py` | after task 0015 |
| `layouts.md` | `layout/struct.py` (HARD ZONE) → `shaders/gen/structs.glsl` → `mesh.vert` | after task 0009 |

## Until then: the 15-minute paper tour
1. `AGENTS.md` — what the project is and what every agent must respect.
2. `docs/spec/overview.md` — five principles and the frame diagram. Notice how one function, `snapshot`, is four features.
3. `docs/spec/conventions.md` — Z-up, `(N, 3)`, row-major, reversed-Z. Every later file assumes these.
4. `docs/spec/ecs.md` — a table is columns plus ids; a system is a function. That is the whole engine model.
5. `docs/decisions/0004-*.md` and `0005-*.md` — why, with the assumptions that a human should challenge.
6. `docs/records/assumptions.md` — the list of things the AI decided without being told.
