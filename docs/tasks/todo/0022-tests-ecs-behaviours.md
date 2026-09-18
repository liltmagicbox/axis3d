---
kind: task
id: 0022
title: tests: ECS behaviours as examples
pack: test
role: tester
model: small
status: todo
blocked_by: [0004]
brief_ko: spec/ecs.md 의 모든 동작을 초보자가 예제로 읽을 수 있는 테스트로 보강. 코드는 고치지 않는다.
---
# 0022 — tests: ECS behaviours as examples

## Goal
Every sentence in `docs/spec/ecs.md` that states a behaviour has a test named after it, readable as an example.

## Read
- `docs/spec/ecs.md`
- `tests/ecs/test_table.py`, `tests/ecs/test_world.py`, `tests/ecs/test_query.py` (what 0003/0004 already cover)

## Write
- `tests/ecs/test_table.py`, `tests/ecs/test_world.py`, `tests/ecs/test_query.py` (extend)

## Do
1. List the behaviours: broadcast rules, zero-fill, growth ×2 and never shrink, `has`, views after `remove`,
   `despawn` of an id present in two tables removes it from both, `step` with an empty `SYSTEMS`, `join` with an
   empty table, `inputs` capacity 8.
2. Add one test per behaviour not yet covered; expectation comment first line; N ≤ 5; no helpers over 5 lines.
3. Run and report the behaviour → test → PASS/FAIL table. Do not change `src/`.

## Done when
- The table in the report covers every behaviour sentence of the spec; failures are reported, not fixed.
- `uv run pytest -q tests/ecs` runs in < 1 s.

## Out of scope
- Snapshot, systems, performance.
