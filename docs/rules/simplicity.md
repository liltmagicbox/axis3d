---
kind: rule
brief_ko: 단순성. 공개 API 예산, 추상화 허용 조건(사용처 2개), 한 개념 한 자리, 매니저·플러그인 금지.
---
# Rule: simplicity

The engine stays small on purpose. Growth needs a decision, not a pull request.

## Must
- P1 Public names are budgeted per package in `docs/spec/api_budget.md`. Adding one = ADR + budget edit.
- P2 One concept lives in one place: conventions in `conventions.py`, layouts in `layout/`, GL calls in `gpu/gl46/`.
- P3 An abstraction needs two real callers before it exists. Until then, repeat three lines.
- P4 Data is numpy arrays; behaviour is functions `f(world, dt)`. Objects only hold arrays and handles.
- P5 Prefer a constant to a config, a function to a class, a tuple to a dataclass, a dataclass to a hierarchy.
- P6 Sizes: `Device` ≤ 20 methods, a table ≤ 12 columns, a function ≤ 5 parameters, a package ≤ 8 modules.

## Never
- P7 No plugin systems, registries, event buses, dependency injection, or `*Manager` classes.
- P8 No parameters that switch behaviour (`fast=True`). Write two functions or make a decision.
- P9 No wrappers around numpy (`Vec3` classes). Arrays are the API.
- P10 No feature flags for unshipped code. Unfinished work lives on a branch, not behind an `if`.
- P11 No `utils`/`helpers`/`common` modules. A helper belongs to the topic that uses it.

## Check
- [ ] public names per package ≤ cap  - [ ] no new hierarchy  - [ ] no P7–P11 patterns
- [ ] every new abstraction has ≥ 2 callers in this change
