---
kind: template
brief_ko: 벤치마크 장부 행 형식. id, 날짜, 경로, N, 중앙값 ms, 목표 ms, 상태, 머신, 비고.
---
# Template: benchmark row

Append one row to `docs/records/benchmarks.md`. Ids `B-NNN`. Median of 10 runs after 3 warm-ups; cite the script.

```
| B-014 | 2026-10-02 | sim.collide (grid + narrow) | 10000 | 3.1 | 4.0 | ok | i7-12700 / RTX 3060 / py3.12 / np2.1 | bench/bench_collide.py, cell_size = 2·max_r |
```
Status `ok | OVER BUDGET | n/a`. Rows from earlier repositories carry `hist` in the status column.
