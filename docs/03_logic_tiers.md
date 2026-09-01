# 03. 게임 오브젝트 로직 — 3계층

## 요지

**개수 × 로직 복잡도**로 계층을 나눈다. 전부 벡터화할 필요도, 전부 객체일 필요도 없다.

## 예산 (실측)

| 방식 | 프레임당 |
|---|---|
| 파이썬 객체 `update()` × 1천 | 0.05 ms |
| 파이썬 객체 `update()` × 1만 | 0.5 ms |
| 파이썬 객체 `update()` × 10만 | 5.3 ms — 여기부터 불가 |
| 시차 실행: 뇌 1만 중 1/10씩만 생각 | 0.06 ms |
| branchless FSM 10만 (행동만) | 0.8 ms |
| 10만 일괄검사 → 당첨 ~100개 파이썬 처리 | 0.03 ms |

## 계층

1. **군중** (총알, 파티클: 1만~10만+)
   로직 자체를 데이터로. 벡터화 FSM(→ 04). 명중/수명종료 같은 사건은 일괄 조건검사 후
   `np.nonzero`로 당첨자 인덱스만 뽑아 파이썬 처리.
2. **스마트** (soldier류: 수백~수천)
   몸과 뇌를 분리. 몸(pos, vel, hp, state)은 공유 배열 슬롯, 뇌는 인덱스를 쥔 파이썬 객체 —
   상태머신/AI를 그냥 파이썬답게 짠다. 수천까진 매 프레임 호출해도 1ms 미만.
   1만 넘으면 시차 실행(프레임마다 1/10씩 결정, 나머지는 이전 결정대로 몸만 배치 이동).
3. **소수** (플레이어, 카메라, 게임모드)
   그냥 파이썬 객체. 아키텍처가 필요 없는 곳에 아키텍처를 적용하지 않는 것도 설계다.

## sense → decide → act

```python
# sense: 전 유닛의 감각을 일괄 계산해 배열로 깔아둔다 (프레임당 1회, numpy/KD-tree)
nearest_dist = compute_all_distances(pos)      # (N,)

# decide: 뇌는 파이썬 — 감각 배열을 읽고, 결정을 배열에 쓴다
class Brain:
    def update(self, dt):
        if nearest_dist[self.idx] < ATTACK_RANGE:
            state[self.idx] = ATTACKING
            target[self.idx] = nearest_idx[self.idx]

# act: 결정(state, target, desired_vel)을 읽어 이동/발사를 다시 배치로 실행
```

- 뇌는 무거운 계산(최근접, 가시선)을 직접 하지 않는다 — 미리 깔린 감각 배열만 읽는다.
- 뇌의 출력도 개별 실행이 아니라 **배열에 쓴 명령**이다. 실행은 배치가 한다.

## 데이터 배치 (핫/콜드)

- 핫 (매 프레임 읽고 씀): uarr 슬롯 — pos, vel, hp, state, timer.
- 콜드 (가끔 접근): 파이썬 dict/객체 — 이름, 스탯 원본, 로드된 설정.

현재 코드와의 대응: `bullet_unit.py`의 uarr + free-idx + "Unit은 배열의 뷰어" 구조가 이 뼈대와 일치한다
(슬롯 0을 쓰레기통으로 쓰는 uid→idx 방식 포함). `soldier_unit.py`/`UnitDict`의 per-object dict는
콜드 전용으로 좁히고, 핫 데이터는 uarr 슬롯으로 옮긴다. 뇌 객체가 dict와 배열 인덱스를 둘 다 쥔다.

## 규칙

- 파이썬 루프는 전체 N이 아니라 사건이 일어난 소수 위에서만 (`np.nonzero`).
- 매 프레임 모두가 생각할 필요 없다 — 시차 실행은 사실상 공짜다.
- 이 구조가 ECS(Entity Component System)가 공식화한 패턴이다.
  프레임워크 없이 numpy SoA + 인덱스 쥔 파이썬 객체로 이득의 90%를 얻는다.
