---
kind: rule
brief_ko: 교육성. 초보자가 주 경로를 처음부터 끝까지 읽을 수 있어야 하고, 어려운 부분은 HARD ZONE으로 격리한다.
---
# Rule: education

Reader model: knows Python basics, functions, and numpy indexing. Does not know GL, ECS, or std430.

## Must
- E1 Every module is either **walk-through** (readable by the reader model, top to bottom) or a **HARD ZONE**.
- E2 A HARD ZONE docstring starts `HARD ZONE: <why it is hard>.` then `Use through: <≤ 3 names>.` Those names are its
   whole public surface.
- E3 Walk-through code uses only functions, dataclasses, numpy indexing and broadcasting, `for` over small lists, `dict`.
- E4 The main path `app.loop → World.step → systems → render.gather → Device` is walk-through end to end.
- E5 Names teach: `rows_of_alive`, `pairs_within_radius`, `size_bytes`.
- E6 One REPL-runnable example per public docstring: `>>> t.insert(ids, pos=[[0, 0, 0], [1, 0, 0]])`.
- E7 When you must be clever, put the clever part in its own ≤ 15-line function with a `why` comment above it.

## Never
- E8 No hidden control flow: callbacks registered at import, decorators that run code, `__init_subclass__`.
- E9 No premature generality in walk-through code ("supports any dtype"). One dtype, one shape, stated.
- E10 No HARD ZONE over 200 lines. Split by stage instead.

## Check
- [ ] zone declared per module  - [ ] HARD ZONE surface ≤ 3 names  - [ ] main path walk-through
- [ ] examples in public docstrings  - [ ] no E8 patterns
