# 지침 17. 측정 습관과 Numba 확장 경로

> 선행: [지침 11](11-kernels.md) · 관련 결정: D-012 · 원칙: 제8조

## 측정 문화 — 이미 있던 전통의 정식화

test_np*.py, highspeed/는 이 프로젝트의 가장 좋은 유산이다. 감이 아니라 수치로 (3,N) 레이아웃과 nonzero 인덱싱을 골랐다. 규칙으로 만든다:

1. **성능 결정은 실험 파일과 함께 온다.** 파일은 `experiments/bench_*.py`, 맨 위에 질문 한 줄과 날짜, 맨 아래에 결론 주석.
2. **수치는 세 곳에 남는다**: 실험 파일 주석(원본) → [00 문서의 숫자 표](../00-history-and-lessons.md)(요약) → decisions.md(그로 인한 결정).
3. **환경이 바뀌면 재측정.** 2023 수치는 당시 데스크톱 기준이다. 새 머신 첫 세션에서 `bench_baseline.py` 한 번 돌려 표를 갱신한다.

## 측정 도구

```python
# experiments/timing.py — 공용 하네스
from time import perf_counter
from contextlib import contextmanager

@contextmanager
def timed(label, n=1):
    t = perf_counter()
    yield
    print(f"{label}: {(perf_counter()-t)/n*1000:.3f} ms")

def bench(fn, *args, repeat=5, warmup=2, **kw):
    """워밍업 후 최소값 채택 — 노이즈에 강하다."""
    for _ in range(warmup): fn(*args, **kw)
    return min(perf_counter_run(fn, *args, **kw) for _ in range(repeat))
```

- `perf_counter` 고정 (time.time 금지 — mvc3d 시절부터의 교훈).
- **최소값**을 대표값으로 (평균은 GC·OS 노이즈에 오염된다).
- 첫 호출은 버린다 — numpy 내부 캐시, 그리고 훗날 Numba JIT 컴파일 시간이 섞이기 때문.
- 프레임 전체는 tick 안에 구간 타이머: input/update/draw별 ms를 STATUS 갱신 때 기록할 수 있게.

## 프레임 예산 회계

60fps = 16.6ms. 배분 초안 (M2에서 실측으로 갱신):

| 구간 | 예산 |
|---|---|
| 커널 파이프라인 (적분 등) | 4ms |
| 충돌 (브로드+반응) | 6ms |
| 2층 (이벤트/Behavior) | 2ms |
| 경계 (스냅샷 추출+pack+송신) | 3ms |
| 여유 | 1.6ms |

예산 초과가 2세션 연속 관측되면 → 아래 승격 절차.

## Numba 승격 절차 (하나씩, 측정과 함께)

전제: [지침 11](11-kernels.md)의 3계명을 지킨 커널만 승격 가능하다. 후보 우선순위: ① 충돌 셀 루프 ② `np.*.at` 류 산란 합산 ③ 깊은 조건 분기 커널. 단순 적분은 승격 이득이 거의 없다 — numpy가 이미 메모리 대역폭 한계다.

1. **베이스라인 기록**: 현재 numpy 커널의 bench 수치.
2. **루프로 재작성**: 같은 시그니처, 같은 테스트. Numba 세계에서는 명시 루프가 정답이다 (임시 배열 0).
3. **장식**: `@njit(cache=True)` (컴파일 캐시 — 매 실행 JIT 대기 방지). 병렬은 `parallel=True` + `prange`를 **측정이 요구할 때만**.
4. **검증**: 기존 테스트 통과 + numpy 버전과 결과 allclose 비교 테스트 추가.
5. **측정·기록**: before/after를 실험 파일과 00 표에. 이득이 2배 미만이면 되돌린다 (복잡도 값을 못 한다).
6. **폴백 유지**: no-op njit 셔틀(지침 11) 덕에 Numba 미설치 환경에서도 동작해야 한다. CI/스모크는 양쪽 모드로.

**Numba 함정 목록** (승격 시 점검):
- dict/문자열/파이썬 객체 인자 — 컴파일 불가 또는 object mode 추락. 시그니처가 배열+스칼라면 안전.
- f32 배열에 파이썬 float 연산 시 f64 승격으로 조용한 캐스팅 — dtype 명시.
- 예외·print는 디버깅 후 제거.
- 첫 호출 컴파일 수 초 — 벤치 워밍업 규칙이 여기서도 지켜준다.

## GPU 컴퓨트는 그 다음이다

Numba 승격 후에도 예산을 넘고, [지침 12](12-cpu-vs-gpu.md) 체크리스트를 전부 통과하는 계산만 GPU 검토 대상. 순서를 건너뛰지 않는다: numpy → (측정) → Numba → (측정) → 그래도 안 되면 설계 재고(N 줄이기, 주기 낮추기) → 마지막이 GPU.

## 단계별 작업

1. [ ] `experiments/timing.py` 하네스 작성 + 기존 벤치들을 하네스로 통일.
2. [ ] `experiments/bench_baseline.py`: 새 환경 기준표 생성 (00 표의 항목들 재측정) → 00 문서 갱신.
3. [ ] tick 구간 타이머를 Simulator에 내장 (`sim.timings` dict, 데모 종료 시 출력).
4. [ ] (예산 초과가 실제로 관측되면) 승격 절차 1회 수행 — 예상 1호: 충돌 셀 루프.

## 완료 기준

- 아무 세션에서나 "지금 프레임 어디에 쓰고 있지?"에 `sim.timings` 출력으로 30초 안에 답할 수 있다.
- 00 숫자 표가 현재 환경 기준으로 갱신되어 있다.
