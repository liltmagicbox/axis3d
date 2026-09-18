---
kind: rule
brief_ko: 테스트 규칙. pytest, src 미러 구조, 결정적, 작은 리터럴, 허용오차, GPU 표시, 목 금지.
---
# Rule: testing

## Must
- T1 `pytest`; files mirror `src/`: `src/axis3d/ecs/table.py` → `tests/ecs/test_table.py`.
- T2 One behaviour per test, named `test_<function>_<behaviour>`; first line a comment with the expectation in words.
- T3 Deterministic: `rng = np.random.default_rng(0)`; no wall-clock, no network, no files outside `tmp_path`.
- T4 Floats: `np.testing.assert_allclose(actual, expected, rtol=1e-5, atol=1e-6)`. Ints and ids: exact.
- T5 Small literals: N ≤ 5 in unit tests. Scale runs live in `bench/`, not in `tests/`.
- T6 GPU tests carry `@pytest.mark.gpu` and are skipped unless `AXIS3D_GPU=1`. Backend contract tests live in `tests/gpu/`.
- T7 Every public function has at least one test; every row in `docs/records/edge_cases.md` names its test.
- T8 Prefer round trips: `restore(snapshot(w))` equals `w`; `decode(encode(x)) == x`.
- T9 `uv run pytest -q` passes on a machine with no GPU and no display.

## Never
- T10 Never mock numpy, GL, or sockets. Use a real `World`, a hidden window, or `socket.socketpair()`.
- T11 Never assert on private names or log text. Never depend on test order.
- T12 Never skip or `xfail` an existing test to pass CI (`agent_conduct.md` C7).

## Check
- [ ] file mirrors src  - [ ] names + expectation comment  - [ ] seeded  - [ ] tolerance per T4
- [ ] gpu marked  - [ ] no mocks  - [ ] CPU suite passes headless
