---
kind: template
brief_ko: 엣지케이스 장부 행 형식. id, 모듈, 입력, 관찰, 기대(spec 근거), 재현 테스트 이름, 상태.
---
# Template: edge case row

Append one row to the table in `docs/records/edge_cases.md`. Ids `E-NNN`, increasing. Status `open | fixed | by-design`.

```
| E-013 | ecs/table | remove() with an id removed earlier | KeyError from _row_of_id | ignored (spec/ecs.md "unknown ids are ignored") | tests/ecs/test_table_edges.py::test_remove_twice_is_ignored | open |
```
The reproducer (≤ 10 lines) lives in the test, not in the table. A row without a test name is a rumour.
