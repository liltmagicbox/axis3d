# 04. 벡터화 상태머신 (branchless FSM)

실행 가능한 데모: [../test_vecfsm.py](../test_vecfsm.py) — 10만 개, IDLE/CHASE/FLEE/DEAD, 전이 3스타일.

## 정의

상태머신 = **boolean 조합 논리 + 기억(레지스터)**. 벡터화 버전은 그 구조를 배열로 옮긴 것이다:

- `state` 배열 (int8) = 10만 개의 레지스터
- boolean 전이식 = next-state 조합 논리
- 프레임 틱 = 클럭 엣지

단순 boolean 조합과의 구분선은 **state가 규칙의 우변에도 등장하는가**다: `next = f(state, input)`.
같은 입력이라도 현재 상태에 따라 결과가 달라야 상태머신이고, 그래야만 히스테리시스·타임아웃·sticky(죽으면 계속 죽음)가 표현된다.

## 부품 1 — 행동: 계수 룩업 테이블 (branchless의 심장)

상태별 스칼라는 전부 (상태수,) 테이블로 둔다. 테이블을 (N,) state로 인덱싱하면 각자의 계수가 담긴 (N,) 배열이 나온다 — **if가 표 조회로 바뀐다**.

```python
#            [IDLE, CHASE, FLEE, DEAD]
SPEED     = np.array([0.,  3.,  6., 0.], np.float32)
MOVE_SIGN = np.array([0., -1., +1., 0.], np.float32)   # 질적 차이(방향)도 부호 테이블로
REGEN     = np.array([2.,  0.,  1., 0.], np.float32)

vel[:] = away_dir * (MOVE_SIGN[state] * SPEED[state])[:, None]
hp[:] += REGEN[state] * dt
```

IDLE/DEAD는 계수 0이라 "안 움직이는 분기"조차 필요 없다.
속도, 회전율, 리젠, 중력 배수, 애니메이션 행, 색 — 상태별로 다른 모든 값이 테이블의 열이 된다.

## 부품 2 — 전이: 조건 일괄평가 + 우선순위 덮어쓰기

조건(near, low_hp, timeout, died)을 전원에 대해 불리언 배열로 한 번에 평가한 뒤 적용한다.
세 스타일 모두 성능 동률(풀 틱 4.2~4.7ms) — 규칙이 적으면 masked, 많으면 table.

```python
# 1) masked write — 나중 쓰기가 이긴다 (우선순위 = 줄 순서)
state[(state == IDLE) & near]    = CHASE
state[(state == CHASE) & low_hp] = FLEE
state[died]                      = DEAD          # 마지막 = 최강

# 2) np.select — 첫 매치가 이긴다 (우선순위 = 리스트 순서)
state[:] = np.select([died, to_flee, to_chase], [DEAD, FLEE, CHASE], default=state)

# 3) 전이 테이블 — FSM 전체가 (상태수, 이벤트수) 배열 하나. 교과서의 δ(q,σ) 그대로
state[:] = TRANS[state, event]                   # 상태가 늘어도 코드가 안 는다
```

## 부품 3 — on-enter 와 타이머

```python
prev = state.copy()
transitions()
changed = np.nonzero(state != prev)[0]   # 이번 프레임에 전이한 소수
timer[changed] = 0.0                     # 상태 진입 시각 리셋
for i in changed: spawn_effect(i)        # 사운드/이펙트 — 파이썬은 여기서만

timer[:] += dt                           # 전이 조건에 timer > 3.0 → "3초 후 복귀"가 벡터화된다
```

## 왜 상태가 필요한가 (실측)

추격 경계(dist 60)에서 거리가 노이즈로 흔들리는 몹 하나, 600프레임:

- stateless 매핑 `state = (dist < 60)`: **313번 상태 플립** (매 프레임 덜덜 떨림)
- FSM (진입 <60 / 이탈 >80): **1번**

진입 조건과 이탈 조건이 다른 것(히스테리시스)은 상태를 기억할 때만 가능하다.

## 성능

- 풀 로직 틱(감각 + 전이 + on-enter + 행동 + 타이머) 10만 개 = **~4.2ms**. 행동만이면 0.8ms.
- 비용 모델: **풀스윕 횟수 × ~0.15ms** (N=10만). 스윕 수를 세라.
- 규칙이 늘어 예산이 빡빡해지면 numba로 스윕들을 한 루프로 융합한다 (→ 02의 융합 항목).

## 함정

- fancy indexing 읽기-계산-쓰기 `pos[mask] += ...`는 gather/scatter 복사 → 4.5ms.
  branchless(계수 곱)는 0.8ms. 단, 마스크 **쓰기** `state[mask] = x`는 싸다.
- 함수 안에서 전역 배열에 `pos += ...` → UnboundLocalError. `pos[:] += ...`로.
- state는 int8 (대역폭 절약).

## 경계

이 패턴은 "얕고 넓은" FSM까지다. 어떤 상태의 행동이 균일한 산술이 아니라 진짜 알고리즘(경로탐색, 대화)이면,
그 상태의 개체만 `np.nonzero(state == PATHFINDING)`으로 뽑아 뇌 계층(→ 03)으로 졸업시킨다.
계층적 상태(HSM), 상태 스택이 필요한 개체도 마찬가지. 군중 로직의 대부분은 얕고 넓은 쪽으로 충분하다는 것이 이 패턴의 베팅이다.
