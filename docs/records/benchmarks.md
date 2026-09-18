---
kind: record
brief_ko: 벤치마크 장부. 옛 저장소에서 측정한 숫자(hist)로 시작하고, profiler가 새 행을 추가한다. 목표치와 비교.
---
# Benchmarks ledger (append-only)

Ids `B-NNN`. Status `ok | OVER BUDGET | n/a | hist`. `hist` rows come from the earlier repositories' notes and
screenshots; they are measurements of old code, kept because they shaped decisions (ADR 0004, 0016, 0024).

| id | date | path | N | median ms | target ms | status | machine | notes |
|---|---|---|---|---|---|---|---|---|
| B-001 | 2023 | `UnitArray.extend` vs 100 000 × `append` | 100 000 | 100 vs 1000 | — | hist | user's desktop | batch insert is 10× faster (`soldier_unit.py`) |
| B-002 | 2023 | O(N²) pairwise distance, per-row Python loop | 900–1300 | ~30 (`(3,N)`) vs ~60 (`(N,3)`) | 4.0 (grid) | hist | user's desktop | layout mattered for the loop pattern; the loop pattern is banned (F1); see A-015 |
| B-003 | 2022 | 200 000 × TRS matrix build | 200 000 | ≈ 5000 (own) | — | hist | user's desktop | ~40 000 matrices/s in pure Python; vectorised `trs()` replaces it (`new3dkatsu/code/matrix.py`) |
| B-004 | 2023 | 1 000 000 × `list.append` vs `Queue.put` | 1 000 000 | list ≪ Queue | — | hist | user's desktop | queues only at thread boundaries (`spec/network.md`) |
| B-005 | 2023 | loopback `localhost` vs host IP | — | localhost fastest | — | hist | user's desktop | default host for tests |
| B-006 | 2023 | `bytes +=` vs `b"".join(list)` for 1500 chunks | 1 500 | join ≪ += | — | hist | user's desktop | framing builds lists then joins |
| B-007 | 2022 | instanced draw of snow particles | 180 000 | interactive | 2.0 (gather) | hist | user's desktop | `new3dkatsu/etc/instanced_snow_180000.png`; the 100 k v1 target is conservative |
