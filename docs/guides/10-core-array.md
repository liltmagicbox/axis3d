# 지침 10. 씬 연산 코어 — ECS 대신 속성-메이저 배열 풀

> 선행: 없음 (첫 번째 구현 대상) · 관련 결정: D-004, D-005, D-007, D-010

## 왜 ECS가 아닌가

정통 ECS는 "엔티티 id → 컴포넌트 저장소 조회 → 시스템이 쿼리로 순회" 구조다. C++/Rust에서는 캐시 지역성을 위한 설계지만, 파이썬에서 그대로 하면:

- 컴포넌트 조회·순회가 전부 파이썬 레벨 간접 참조다 — 개체당 수백 ns씩 새고, N=10만이면 그것만으로 프레임이 끝난다.
- 컴포넌트 동적 부착/탈착은 배열 재배치를 부르거나 희소 저장소를 부른다. 둘 다 numpy 벡터화와 상극이다.

우리 답 (axis3d에서 검증된 방향):

- **아키타입 = ArchetypeArray 하나.** 같은 속성 집합을 가진 개체들('병사', '총알', '눈')이 하나의 배열 묶음을 공유한다.
- **속성 = 속성별 배열.** `{'pos': (3,N) f32, 'hp': (N,) f32}` — 속성-메이저(SoA). 실측으로 (N,3)보다 2배 빠르다.
- **개체 = 열 인덱스.** 개체 객체는 존재하지 않는다 (2층의 Unit 파사드는 [지침 13](13-events-and-units.md)).
- **"컴포넌트 있음/없음" = bool 마스크 행.** 탈부착 대신 스위치. 쿼리는 마스크 AND — numpy 그 자체다.
- **시스템 = 배열을 받는 순수 함수** ([지침 11](11-kernels.md)).

ECS가 쿼리로 푸는 문제를 우리는 구조로 없앤다: 조회가 없고, 순회가 없고, 벡터 연산만 있다.

## 설계 스펙

axis.py(단일 거대 배열)와 gunfire_unit.py(속성별 dict)의 대결은 **속성별 dict의 승리**로 확정한다(D-010).
이유: 속성마다 dtype을 가질 수 있고(hp는 f32, team은 i8, alive는 bool), 코드가 단순하며, 속성별 연속성은 유지된다. 단일 버퍼가 필요한 소켓 전송은 경계에서 pack한다([지침 14](14-view-boundary.md)).

```python
# core/archetype.py
DTYPE_F = np.float32   # 수치
DTYPE_I = np.int64     # 인덱스/ID — np.nonzero 반환형 그대로 (실측: i32 변환이 오히려 손해)
GROW = 0.5             # 상각 증설 비율
MAX_N = 2_000_000      # 폭주 방지 상한 (gunfire_unit 계승)

class ArchetypeArray:
    """속성별 배열 묶음. 외부 인터페이스는 4+2개가 전부다."""
    def __init__(self, schema: dict, n: int = 64, fixed: bool = False):
        # schema 예: {'pos': 3, 'vel': 3, 'hp': 1, 'team': ('i8', 1)}
        ...
    # --- 생명주기
    def acquire(self, n=1, **overrides) -> np.ndarray:  # int64 idxs
    def release(self, idxs) -> None
    # --- 접근
    def get(self, attr, idxs=None) -> np.ndarray        # 기본은 뷰/원본, 복사 아님
    def set(self, attr, value, idxs=None) -> None
    # --- 프레임 보조
    def active_idxs(self) -> np.ndarray                 # np.nonzero(self.active)[0], 프레임당 1회 캐시
    def arrays(self, *attrs) -> tuple                   # 커널에 꽂을 원본 배열들
```

구현 규칙 (전부 실측 근거 있음, [00 문서의 숫자 표](../00-history-and-lessons.md) 참조):

1. **증설**: free 슬롯 부족 시 `max(요청량, N*GROW)`만큼 hstack 확장. 1M 확장 실측 1.5ms — 망설일 비용이 아니다. `fixed=True`면 증설 대신 예외 (총알처럼 상한이 설계인 아키타입용).
2. **free-list**: 파이썬 리스트로 충분 (1M extend 7ms 실측). pop/extend만 쓴다.
3. **active 마스크**: release는 `active[idxs]=False`가 전부. 압축(compaction)은 하지 않는다 — 인덱스 안정성이 더 귀하다.
4. **배치 우선**: `acquire(1000)`이 기본형. 낱개 append 루프는 10배 느리다.
5. **acquire 시 초기화**: schema 기본값 + overrides로 해당 열을 덮어쓴다. 재활용 슬롯의 이전 값 잔류가 대표적 버그 원인이다 — acquire가 모든 속성을 초기화하는 것을 테스트로 못박는다.
6. **xyz 슈가**: `set('pos.x', v)` 정도는 편의로 허용하되 (axis.py의 `attr.x` 파싱 계승), 핫패스에서는 쓰지 않는다.

## 단계별 작업

1. [ ] `core/archetype.py`에 ArchetypeArray 골격 + schema 파싱 (int → f32 dims, ('i8',1) 같은 dtype 지정 지원).
2. [ ] acquire/release + free-list + active 마스크 + 상각 증설. `__main__` 데모: 병사 스키마로 5개 → 10만 개 acquire, 절반 release, 재acquire.
3. [ ] get/set (idxs 유무 4경로: 전체/부분 × 1d/nd). gunfire_unit의 `set_arr_nd` transpose 처리(`(1,2,3)` → 열 브로드캐스트)를 계승.
4. [ ] `active_idxs()` 프레임 캐시 + 무효화(acquire/release 시). 실측 재현: 1M 마스크 nonzero ≈ ms급인지 확인.
5. [ ] 초기화 보장 테스트: release된 슬롯 재acquire 시 이전 값이 보이지 않는다.
6. [ ] 벤치 파일 `experiments/bench_archetype.py`: acquire 10만 배치 vs 루프, get/set 처리량, 증설 비용. 수치를 파일 주석으로 박제.

## 완료 기준

- 10만 개체 acquire(배치) < 200ms, release+재acquire 누수 없음 (active 수 검증).
- `python core/archetype.py` 데모가 스키마·상태를 사람이 읽을 수 있게 출력 (axis.py의 `__str__` 정성 계승).
- 벤치 수치가 experiments/에 기록되어 있고 STATUS.md에 한 줄 요약.

## 함정

- **fancy 인덱싱은 복사다.** `arr[:, idxs]`를 받은 쪽에서 고쳐도 원본은 안 변한다 (test_nparridxslice의 copytest 교훈). 쓰기는 반드시 `arr[:, idxs] = v` 형태의 직접 대입으로. get이 복사를 돌려준다는 것을 docstring에 명시.
- **bool 마스크로 반복 인덱싱 금지.** 한 번 nonzero 해서 int64 인덱스로 재사용 (16ms vs 4ms @1M).
- **정수 배열에 수치를 섞지 말 것.** np.sum/prod의 조용한 오버플로 실측 있음. 수치는 f32, 판별은 bool, 인덱스는 i64.
- schema에 없는 속성을 런타임에 추가하고 싶어지면 — 그것은 다른 아키타입이다. 쪼개라.
