---
kind: template
brief_ko: 작업 카드 템플릿. 작은 모델이 카드만 보고 끝낼 수 있게 경로·시그니처·테스트 이름을 문자 그대로 적는다.
---
# Template: task card

`uv run python tools/new.py task "<title>" --pack <pack> --role <role>` copies the block below to
`docs/tasks/todo/NNNN-<slug>.md`. Keep it ≤ 60 lines. Copy signatures from the spec, never paraphrase.
**Done when** lists test names with the expected behaviour in words.

````
---
kind: task
id: {{id}}
title: {{title}}
pack: {{pack}}
role: {{role}}
model: small
status: todo
blocked_by: []
brief_ko: <한 줄: 무엇을 만드는 카드인가>
---
# {{id}} — {{title}}

## Goal
<one to three lines; the user-visible outcome>

## Read
- `docs/spec/<file>.md` — section "<name>"

## Write
- `src/axis3d/<path>.py`
- `tests/<path>/test_<module>.py`

## Do
1. <step with the exact signature>
2. <step>

## Done when
- `tests/<path>/test_<module>.py::test_<function>_<behaviour>` — <expected behaviour>
- `uv run ruff check . && uv run pytest -q` pass; no public names beyond `docs/spec/api_budget.md`

## Out of scope
- <what a later card does>

## Notes
- <facts the implementer would otherwise have to look up>
````
