# 지침 14. 시뮬–뷰 경계 — 인터페이스, 루프, 소켓 프로토콜

> 선행: [지침 10](10-core-array.md), [13](13-events-and-units.md) · 관련 결정: D-001, D-002, D-008 · 원칙: 제1·5조

## 계약 (mvc3d interface.py의 완성형)

```python
class IWorld:            # 시뮬레이션 쪽
    def input(self, event): ...          # 경계에서 파싱된 Event
    def update(self, dt): ...
    def draw(self) -> dict: ...          # 그리기용 상태 스냅샷 (아래 포맷)

class IViewControl:      # 뷰 쪽 대리인 (시뮬 프로세스 안에 산다)
    def get_inputs(self) -> list: ...    # 와이어 이벤트 수거
    def draw(self, draws): ...           # 상태 스냅샷 송출
```

Simulator는 이 다섯 메서드만 안다:

```python
while running:
    dt = clamp(now - before, 0, DT_MAX)
    for e in parse(view_control.get_inputs()):   # 경계 파싱은 여기 한 번
        world.input(e)
    world.update(dt)
    view_control.draw(world.draw())
    sleep(frame_budget_remaining)
```

- mvc3d simulator.py의 검증된 기능 유지: pause/resume/stop, 실행 중 world 교체.
- 스레드 플래그는 `threading.Event`. 루프 시간은 `time.perf_counter`.
- sleep 해상도 주의 (윈도우 실측 ≈1.5~3ms 최소 단위): 60fps 목표면 0.014s 슬립 + dt 클램프로 방어.
- ViewControl이 없는 구성(테스트)도 1급 시민: `NullViewControl`(빈 입력, draw 무시)로 headless 실행이 항상 가능해야 한다.

## 뷰는 소모품이다

같은 IViewControl 뒤에 뭐가 붙는지 시뮬은 모른다:

- `LocalViewControl` — 같은 프로세스의 창 (개발 편의).
- `SocketViewControl` — 입력 수신/상태 송출 소켓 쌍 (mvc3d 30020/30021 구도). 뷰 프로세스는 붙었다 떨어졌다 자유.
- 브로드캐스트 — 뷰 여럿이 같은 상태 스트림 구독 (threeinit websocket 실험으로 검증). 관전자는 공짜 기능이다.

## 와이어 프로토콜

**입력 (뷰→시뮬)**: 작고 드물다. json 한 줄이면 된다.
```json
{"Key": ["w", 1.0, 4.583]}
```
mvc3d event.py의 결론 그대로 — 클래스명 키 + 위치 인자 리스트, 최소 바이트. 파싱은 [지침 13](13-events-and-units.md)의 parse가 담당.

**상태 (시뮬→뷰)**: 크고 매 프레임이다. **float를 json에 넣지 않는다** (D-008). test_npbytes.py의 np_pack 계승:

```python
def pack(arr):     # -> header(json bytes), payload(raw bytes)
    return json.dumps([len(b := arr.tobytes()), str(arr.dtype), arr.shape]).encode(), b

def unpack(header, payload):
    n, dtype, shape = json.loads(header)
    return np.frombuffer(payload, dtype=dtype).reshape(shape)   # 읽기 전용 뷰 — 복사 없음
```

프레임 메시지 = json 메타(프레임 번호, 테이블 목록) + 테이블별 pack 페이로드 연결. zlib은 측정 후에만 (threeinit에서 썼지만, 로컬/LAN에서는 압축 비용이 더 클 수 있다 — 재라).

## draw() 스냅샷 포맷 — 무엇을 보내는가

**의미 있는 상태만. 정점은 절대 보내지 않는다** (제7조). 아키타입별 테이블:

```python
{'frame': 1042,
 'tables': [
    {'draw_type': 'inst_mesh', 'geo': 'bullet', 'n': 4096,
     'pos': <(3,n) f32>, 'quat': <(4,n) f32>, 'scale': <(1,n) f32>},   # pack 대상
    {'draw_type': 'params', 'name': 'snow', 'intensity': 0.7},          # 순수 시각은 파라미터만
 ]}
```

- 보낼 열은 active 인덱스로 추출해 연속 버퍼로 복사한다 — 이 복사는 경계의 정당한 비용이다 (fancy 인덱싱 1회, 실측 ms급 @1M).
- 뷰 쪽 변환(행렬 조립, 보간, 스키닝)은 뷰의 일이다 ([지침 15](15-rendering.md)).
- 대역폭 감각 (test_renderer.py 독백의 계산): 본 100개 = 6.4KB, 10k 개체 pos+quat f32 = 280KB/frame. 60fps LAN이면 성립, WAN이면 주사율/관심영역 필터를 그때 단다.

## 단계별 작업

1. [ ] `view/protocol.py`: pack/unpack + 프레임 메시지 조립/해체 + `__main__` 왕복 테스트 (dtype/shape 보존 검증).
2. [ ] `sim/simulator.py`: 루프 + pause/resume/stop + dt 클램프 + NullViewControl. 데모: headless로 총알 10만 5초 시뮬, tick 시간 통계 출력.
3. [ ] `view/socket_vc.py`: SocketViewControl (입력 수신 스레드 + 상태 송출). mvc3d queuerecv.py의 교훈 반영 — 서버 소켓은 장수, 클라이언트 소켓은 재접속 시 새로 , b'' 수신 = 연결 종료.
4. [ ] `view/client.py`: 최소 뷰 클라이언트 — 받은 테이블의 n과 첫 개체 pos를 콘솔에 찍는 것부터 (렌더는 지침 15).
5. [ ] `experiments/bench_boundary.py`: 10만 개체 스냅샷 추출+pack+로컬 소켓 왕복 ms 측정. zlib on/off 비교 포함.

## 완료 기준

- 시뮬 프로세스와 뷰 프로세스를 따로 띄워 상태 스트림이 흐르고, 뷰를 죽였다 다시 붙여도 시뮬이 무사하다.
- headless 실행 경로가 테스트로 보장된다.
- 경계 왕복 비용이 experiments/에 수치로 남아 있다.

## 함정

- 스냅샷에 배열 뷰를 그대로 소켓 스레드에 넘기면 시뮬 스레드가 다음 tick에 덮어쓴다 — 추출 복사가 스냅샷의 일부인 이유.
- 입력 큐는 `queue.Queue` + "다 비우기" 패턴 (mvc3d inputman 계승). 프레임당 이벤트 수를 상한 두고 초과분은 버릴지 이월할지 명시.
- 프로토콜에 버전 한 자리 넣어두기 — 뷰와 시뮬을 따로 고치는 순간부터 필요해진다.
