# 지침 13. 이벤트와 고급 객체 — 2층의 설계

> 선행: [지침 10](10-core-array.md), [11](11-kernels.md) · 관련 결정: D-002, D-014 · 원칙: 제4·5조

## 두 층의 세계

| | 1층: 수치 코어 | 2층: 객체 세계 |
|---|---|---|
| 내용물 | ArchetypeArray, 커널, 파이프라인 | Unit, Behavior, Timer, Controller, GameMode, 이벤트 |
| 규모 | N (수만~수십만) | 프레임당 수십 건 |
| 스타일 | 벡터화, dtype 규율 | 편한 파이썬 OOP — 느려도 된다 |
| 서로 접촉 | — | **인덱스와 마스크로만** 1층을 만진다 |

이 분리가 mvc3d의 "pos 전쟁"과 axis3d의 unitfactory가 도달한 합의다. 개성 있는 로직을 배열에 욱여넣으려 하면 코어가 오염되고, N-스케일 로직을 객체로 하면 프레임이 죽는다.

## Unit — 배열 위의 얼굴

axis3d unitfactory.py의 Unit을 계승하되 함정을 제거한다:

```python
# world/unit.py
class Unit:
    """(archetype, idxs)를 들고 배열을 OOP처럼 읽고 쓰는 뷰. 데이터를 소유하지 않는다."""
    __slots__ = ('_arch', '_idxs', 'behavior')
    def __init__(self, arch, idxs, behavior=None): ...
    def __getattr__(self, key):  return self._arch.get(key, self._idxs)
    def __setattr__(self, key, value): self._arch.set(key, value, self._idxs)  # _슬롯 제외
    def __len__(self): return len(self._idxs)
    def release(self):           # ★ 명시적으로만. __del__ 금지 (D-014)
        self._arch.release(self._idxs)
```

- 1개면 개체처럼(`u.hp -= 1`), 1000개면 무리처럼(`squad.vel = ...`) 다뤄진다 — 같은 코드로.
- **`__del__`에서 release 금지.** GC 타이밍에 개체 생사를 맡기면 "변수 덮어썼더니 병사가 증발" 류의 유령 버그가 된다 (unitfactory.py의 실제 함정). 죽음은 항상 명시적 사건이다.
- Unit은 캐시하지 말고 가볍게 만들었다 버린다. 오래 들고 있을 것은 idxs(int64 배열)뿐.

## UnitFactory — 아키타입 명부

```python
uf.register('soldier', schema={'pos':3,'vel':3,'hp':1}, defaults='data/soldier.txt', behavior=SoldierBehavior)
squad = uf.order('soldier', n=100, pos=spawn_grid(100))   # -> Unit
```

- 기본값은 평문 데이터 파일(`hp:5` 형식, ham.txt 계승)에서 — 밸런싱은 코드 수정이 아니다.
- order는 내부적으로 배치 acquire — 낱개 10배 손해를 구조적으로 차단.

## Behavior와 Timer — 시간이 걸리는 로직

- Behavior는 Unit(무리)당 하나 붙는 2층 객체. `update(unit, dt)`에서 편하게 파이썬을 쓴다. 단 그 안에서 N-루프가 생기기 시작하면 그 로직은 커널로 내려보낼 후보다.
- Timer는 "3.5초 뒤 자멸" 같은 예약 실행 (unitfactory.py 원형). 구현은 heapq 기반 (발화 시각, 순번, 콜백) — 원본의 dict 순회는 삽입 순서에 기대는 버그가 있었다. 수정해서 계승한다.
- **수명 같은 N-스케일 시간 로직은 Timer가 아니라 커널이다** (`age += dt; alive &= age < max_age`). Timer는 개별 예약(보스 등장, 리스폰)용이다.

## 이벤트 — 세 가지 문맥, 두 개의 경계

```
[바깥세상: 뷰/입력]  --wire dict-->  ‖경계 파싱‖  --Event 객체-->  [2층]  --인덱스/마스크-->  [1층]
```

1. **와이어 이벤트** (경계 밖): `{'Key': ['w', 1.0, t]}` 같은 압축 dict/바이트. 포맷은 [지침 14](14-view-boundary.md).
2. **시뮬 이벤트** (2층): 타입 있는 클래스. mvc3d event.py 계승 —
   ```python
   class Event: __slots__ = ('src', 'target')
   class Key(Event): __slots__ = ('key', 'value', 'time')     # 모든 입력장치의 일반화 (key, value)
   class Damage(Event): __slots__ = ('kind', 'amount')          # kind: pierce/blunt/...
   ```
   변환은 경계에서 정확히 한 번. *"let Events not cross this line."* — 2층 코드에 dict 이벤트가 보이면 경계가 샌 것이다.
3. **1층에는 이벤트가 없다.** 충돌 커널의 출력은 (i,j) 인덱스 배열이고, 그것을 이벤트로 바꾸는 것은 2층의 일이다.

**배달 규칙** (mvc3d `_concept_eventreceptor.py`의 결론):

- 가해자는 대상 상태를 직접 만지지 않는다. `unit.deliver(Damage('pierce', 20), target)` — **결과는 받는 쪽의 `receive(event)`가 결정한다** (불사·저항·반사는 전부 수신측 구현).
- 다만 이것은 2층 개체 간 규칙이다. "총알 5000발의 데미지 일괄 적용"은 받는 쪽 아키타입의 커널이 인덱스 배열로 처리한다 — 이벤트 5000개를 만들지 않는다. **집계는 1층, 개성은 2층.**

## Controller — 입력의 번역

mvc3d controller.py 계승: `{'w': 'move_forward*1', 's': 'move_forward*-1'}` 키맵 → Key 이벤트를 동사 호출로. 장치(키보드/패드/브라우저)는 경계 밖, 동사는 2층, 동사의 결과(속도 변경)는 1층 배열 쓰기.

## 단계별 작업

1. [ ] `world/events.py`: Event/Key/Damage + 경계 `parse(wire) -> [Event]` (M_XY→M_X,M_Y 분해 포함, mvc3d 원형 이식) + `__main__` 왕복 테스트.
2. [ ] `world/unit.py`: Unit (명시적 release, `__slots__` + object.__setattr__ 우회 패턴) + 테스트: setattr 위임, release 후 이중 release 방지.
3. [ ] `world/factory.py`: register/order + txt 기본값 로더 (cp949 폴백 포함 — soldier_unit.py의 load_txt 계승).
4. [ ] `world/behavior.py`: Behavior 베이스 + heapq Timer + 데모: 총알 Unit이 3.5초 뒤 자멸 (Timer→release 경로).
5. [ ] `world/controller.py`: 키맵 파서 + FPS 프리셋. Key 이벤트 → 동사 → 배열 쓰기까지 데모.
6. [ ] 통합 데모 (`__main__`): order('soldier',100) → 컨트롤러로 무리 이동 → Damage 배달 → hp 감소 → 0 이하 커널 마스크로 release.

## 완료 기준

- 2층 코드 어디에도 프레임당 N-루프가 없다 (리뷰 항목).
- 이벤트 dict가 world/ 안쪽에서 발견되지 않는다 (경계 준수).
- 통합 데모가 돌아가고, release 누수 없음 (active 개수 검증).

## 함정

- `__getattr__` 위임 객체에서 내부 슬롯 접근 재귀 — `object.__setattr__` 우회 패턴 필수 (unitfactory.py에서 이미 밟은 지뢰).
- Behavior에 상태를 잔뜩 쌓기 시작하면 그것은 아키타입 속성이어야 할 데이터다. "이 값이 개체 수만큼 존재하는가?"로 판별.
- 이벤트 시스템을 미리 범용으로 키우지 말 것. 지금 필요한 이벤트 종류는 Key와 Damage 둘이다. 종류가 5개를 넘을 때 일반화를 고민해도 늦지 않다.
