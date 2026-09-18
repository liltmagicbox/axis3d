---
kind: template
brief_ko: 하위 모델 보고 형식. 상태, 바뀐 파일, 실행한 검사, 추가한 가정, 후속 제안. 사실과 file:line만.
---
# Template: report (every role replies in this shape)

```
STATUS: DONE | PARTIAL | BLOCKED        (then one line why, if not DONE)
TASK: docs/tasks/todo/NNNN-<slug>.md
FILES:
- src/axis3d/ecs/table.py (new, 142 lines)
- tests/ecs/test_table.py (new, 9 tests)
CHECKS:
- uv run ruff check . && uv run ruff format --check . → clean
- uv run pytest -q → 12 passed
- uv run python tools/check_docs.py → 0 errors
ASSUMPTIONS ADDED: A-031, A-032           (ids from docs/records/assumptions.md, or "none")
PUBLIC NAMES ADDED: none                  (or the names and the ADR id that allows them)
FOLLOW-UPS:
- <proposed card title> — <one line why>
RULE FEEDBACK:
- <rule id> — <why it hurt here>        (or "none")
```

## Role-specific sections (append when the role file says so)
- **reviewer**: table `rule | PASS/FAIL/N/A/UNSURE | file:line — quote`, then `ACCEPT` or `REJECT: <ids>`.
- **tester**: table `behaviour | test name | PASS/FAIL`.
- **profiler**: table `path | N | median ms | target ms | status`.
- **edge_hunter**: ranked list `E-id | input | observed | expected (spec line) | test`.
- **teacher**: table `file:line | reader's question | fix | rule id`, then the tour path.
- **porter**: table `method | direct/emulated/unsupported | variant fact`.
