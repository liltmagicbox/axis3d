# 지침 11. 커널 작성 규칙 — Numba 없이 빠르게, Numba가 꽂히는 형태로

> 선행: [지침 10](10-core-array.md) · 관련 결정: D-005, D-006, D-012

## 커널이란

매 프레임 N개 개체 전체를 훑는 함수. 적분, 감쇠, 수명, 충돌, 경계 반사 같은 것들.
axis.py의 원형을 계승한다:

```python
def integrate(pos, vel, acc, dt):
    """pos/vel/acc: (3,N) f32 뷰. 전부 in-place."""
    vel += acc * dt
    pos += vel * dt
```

**커널의 3계명**

1. **배열과 스칼라만 받는다.** dict, Unit, ArchetypeArray, self — 금지. 이 계명 하나로 커널은 테스트 가능하고, 벤치 가능하고, 훗날 `@njit`을 붙일 수 있는 상태가 된다.
2. **in-place로 쓴다.** 반환값으로 새 배열을 만들지 않는다. 필요한 출력 버퍼는 인자로 받는다 (`out=` 스타일).
3. **개체 루프를 돌지 않는다.** `for i in range(N)`이 커널 안에 보이면 설계를 다시 본다. (예외: Numba로 넘어간 뒤의 커널 — 그때는 루프가 정답이 된다. 아래 참조.)

## Numba 없이 빠르게 — 규칙들

- **연산 융합보다 임시 배열 절약.** `vel += acc*dt`는 임시 하나로 끝나지만, 긴 수식은 임시가 줄줄이 생긴다. 핫한 커널은 `np.multiply(acc, dt, out=tmp); vel += tmp`처럼 프레임 밖에서 할당한 스크래치 버퍼를 재사용한다. 스크래치는 커널이 인자로 받는다 (전역 금지).
- **마스크 연산은 인덱스로.** 살아있는 것만 갱신할 때 `pos[:, mask] += ...`가 아니라, 프레임당 1회 뽑은 `idxs = active_idxs()`로 `pos[:, idxs]`. 단, **전체 갱신이 부분 갱신보다 싼 경우가 많다** — 죽은 열을 그냥 같이 계산하는 게 fancy 인덱싱 복사보다 쌀 수 있다. 갈림길이면 재라 ([지침 17](17-profiling-and-numba.md)).
- **조건 분기는 np.where / 곱셈 마스크로.** `vel *= (pos[2] > 0)` 같은 식. 분기를 데이터로 바꾼다.
- **reduce는 numpy에 맡긴다.** min/max/argmin/sum은 손으로 짜지 않는다.
- **dtype을 지킨다.** f32 배열에 파이썬 float를 섞는 것은 무해하지만, i64에 f32 나눗셈 결과를 넣는 등의 암묵 캐스팅은 조용한 복사·오버플로의 근원. 커널 docstring에 기대 dtype/shape을 적는다.
- **작은 N에 벡터화 강박 금지.** 프레임당 8개 도는 카메라 로직을 벡터화하지 않는다. N-스케일만 커널이다. 나머지는 2층에서 편하게 쓴다.

## 업데이트 파이프라인

시스템 실행 순서는 명시적 리스트다. axis.py의 타입힌트 자동 등록은 재치있지만 마법이다 — 명시가 이긴다:

```python
# world/pipeline.py
PIPELINE = [
    # (아키타입, 커널, 필요한 속성 이름들, 스칼라 kwargs)
    ('bullet', kernels.integrate, ('pos', 'vel', 'acc'), {}),
    ('bullet', kernels.lifetime,  ('age', 'alive'), {'max_age': 3.5}),
    ('soldier', kernels.integrate, ('pos', 'vel', 'acc'), {}),
]

def update(world, dt):
    for arch_name, kernel, attrs, kw in PIPELINE:
        arch = world.archetypes[arch_name]
        kernel(*arch.arrays(*attrs), dt=dt, **kw)
```

- 순서가 곧 문서다. 파이프라인 정의를 보면 한 프레임에 무슨 일이 일어나는지 다 보인다.
- 커널은 아키타입을 모른다. 같은 integrate가 총알에도 눈송이에도 꽂힌다.
- 타입힌트 스키마 선언(`pos:3`)을 슈가로 부활시키고 싶다면 등록 함수를 따로 — 커널 본체는 순수하게 유지.

## Numba 확장 경로 (지금 안 쓰고, 나중에 공짜로 얻기)

3계명을 지킨 커널은 나중에 이렇게 승격한다:

```python
# core/kernels.py
try:
    from numba import njit
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    def njit(*a, **k):                # no-op 데코레이터
        return a[0] if a and callable(a[0]) else (lambda f: f)

@njit(cache=True)                      # numba 없으면 그냥 파이썬 함수
def collide_pairs(pos, radius, out_i, out_j):
    ...  # 여기서는 for 루프가 정답이 된다
```

- **승격 대상은 프로파일이 정한다.** 벡터화로 안 풀리는 것들 — O(N²)/이웃 탐색, 개체별 분기가 깊은 로직 — 이 1순위. 단순 적분은 numpy로 이미 충분해서 승격 이득이 거의 없다.
- 승격 시 벡터화 코드를 루프 코드로 다시 쓰는 것은 정상이다 (Numba에서는 루프가 빠르다). 함수 시그니처가 안 변하는 것이 이 설계의 보상이다 — 파이프라인·테스트·벤치 전부 그대로.
- `USE_NUMBA` 환경 플래그로 강제 on/off 가능하게 (버그 격리용).
- Numba가 못 먹는 것들을 커널에 안 넣는 습관이 곧 3계명이다: dict 접근, 문자열, 파이썬 객체, 가변 kwargs.

## 단계별 작업

1. [ ] `core/kernels.py`: integrate, gravity, damp, lifetime(나이 증가+수명 초과 마스크 반환), bounds(경계 반사) — 각각 3계명 준수 + docstring에 shape/dtype.
2. [ ] `world/pipeline.py`: PIPELINE 리스트 + update(). `__main__` 데모: 총알 아키타입 10만에 integrate+lifetime.
3. [ ] no-op njit 셔틀(위 코드) 넣어두기 — import 실패 안전.
4. [ ] `experiments/bench_kernels.py`: 10만/100만에서 커널별 ms 기록. 전체 갱신 vs active만 갱신 비교 실험 1개 포함.
5. [ ] 커널 단위 테스트: 수치 자체보다 **in-place 동작**(원본이 변했다)과 **부수효과 없음**(다른 속성 불변)을 검증.

## 완료 기준

- 10만 개체 integrate+lifetime+bounds 합계가 프레임 예산의 1/4(≈4ms) 이하 (새 환경 실측으로 기준 조정 가능 — 수치를 기록하는 것이 핵심).
- 커널 아무거나 하나 골라 `@njit`을 붙였다 떼도 테스트가 전부 통과한다 (승격 리허설).

## 함정

- 커널 안에서 `arch.get(...)` 호출 — 3계명 위반이자 매 호출 오버헤드. 배열은 파이프라인이 꽂아준다.
- `pos = pos + vel*dt` — 이름 재바인딩일 뿐 원본 불변. in-place(`+=`, `[:] =`)만 원본을 바꾼다.
- dt 스파이크: 프레임이 밀린 뒤 큰 dt가 들어오면 물리가 터진다. update 진입부에서 dt 클램프 (mvc3d 시절 sleep 실측이 보여준 현실).
