# 00. 지금까지의 논의 — mvc3d에서 axis3d까지

두 저장소는 별개 프로젝트가 아니라 하나의 논의가 두 번에 걸쳐 진행된 기록이다.
질문은 처음부터 같았다: **"파이썬으로 3D 시뮬레이션을 만들 때, 무엇이 어디에 있어야 하는가?"**

## 1기: mvc3d (2022) — 경계를 긋다

README 한 줄이 전체 요약이다: `view-controller ----- model py 3d simulator`.

### 시도한 것

- **World–Simulator–ViewControl 분리.** `interface.py`가 계약의 전부다:
  world는 `input(event)` / `update(dt)` / `draw() -> draws` 세 개만 제공하고,
  view_control은 `get_inputs()` / `draw(draws)` 두 개만 제공한다.
  Simulator는 스레드에서 tick 루프를 돌리며 둘을 잇는다 (`mvsim/20_socket_world/simulator.py` — pause/resume/stop, 실행 중 world 교체까지 동작했다).
- **뷰를 소켓 건너편으로 추방.** `SocketViewController`는 입력 수신 포트(30020)와 그리기 송신 포트(30021)의 쌍일 뿐이다. 뷰는 붙었다 떨어졌다 하는 소모품이고, 시뮬레이션은 뷰가 없어도 돈다.
- **브라우저를 뷰로.** `threeinit/`은 flask + websocket으로 three.js를 뷰 클라이언트로 쓰는 실험. websocket 브로드캐스터를 4세대(gen1~ws4)까지 갈아엎었고, zlib 압축까지 붙여 gif 데모(`websocket_land/gen2/saved29.gif`)를 뽑았다.
- **이벤트 와이어 포맷.** `20_socket_world/event.py`. 소켓 위로는 `{'Key': ['k', 1.0, time]}` 같은 압축된 dict만 흐르고, 경계에서 단 한 번 `parse()`로 Event 클래스가 된다. 주석 그대로: *"let Events not cross this line."* 키보드·마우스·조이스틱을 전부 (key, value)로 일반화했고, `M_XY`는 경계에서 `M_X`,`M_Y`로 쪼갠다.
- **키맵 컨트롤러.** `controller.py`: `'w': 'move_up*1'` — 키를 동사×배율 문자열로 매핑하고 액터의 메서드를 호출한다. 입력 장치와 게임 동작의 분리.
- **이벤트 설계 사고실험.** `mvsim/_concept_eventreceptor.py`. 힐러가 돌에게 힐을 쓰면 어떻게 되어야 하는가? 결론의 방향: 가해자가 `target.hp -= x`로 직접 만지지 말고 `target.deliver(Damage.pierce(...))`로 보내며, **어떻게 될지는 받는 쪽이 결정한다** (미라는 hp를 복원하고, 올빼미는 speed를 복원한다). "시각·청각도 결국 충돌 볼륨"이라는 관찰도 여기서 나왔다.
- **three.js식 씬 API.** `fullcode.py`: `Geo.cube()`, `Mat.phong(color=...)`, `Mesh(geo, mat)`, Helper 팩토리. Geometry는 고정 구조체가 아니라 `{attrname: array}` dict — *"BufferGeometry는 GPU 제출용 형태다. 파이썬 안에서는 그 형태를 미리 흉내낼 필요가 없다."*
- **인스턴싱 실험.** `mvsim/rpi4_pyglet_23.8_vao_4x4batch_instanced_snow.py`: `uniform mat4 Model[252]` 배치 + `gl_InstanceID`로 눈 내리는 데모를 라즈베리파이4에서 돌렸다. 같은 지오메트리 N개는 draw call 하나로.

### 부딪힌 벽

- **"pos 전쟁"** (`ver0.1_xyz_attrreport/API.py`). `actor.pos`가 객체면: 대입하면 통째로 교체되고, 복사본을 돌려주면 `pos.x = 5`가 안 먹고, 뷰를 돌려주면 엉뚱한 곳이 같이 움직인다. property setter에서 `self._pos.set(value)`로 in-place 갱신하는 절충까지는 갔지만, **액터마다 파이썬 벡터 객체를 두는 것 자체가 근본 문제**라는 결론에 도달했다. 느리고, 소유권이 애매하고, 동기화(변경 감지)를 위해 IDVec3 같은 보고용 벡터까지 필요해진다.
- N이 커지면 `for actor in actors: actor.update(dt)`는 답이 없다.

의미심장한 흔적: 2022년의 `world.py`에 이미 `self.actorsAXIS`, `self.AXIS`, `self.AXIS.update(dt)` 슬롯이 있다. 답의 이름은 이미 정해져 있었다.

## 2기: axis3d (2023) — 데이터를 눕히다

`soldier_unit.py` 첫 줄: `#oop -> axis enlist.` 액터가 객체이기를 그만두고, 배열의 열(column)이 된다.

### 시도한 것

- **Axis** (`axis.py`): 속성-메이저 `(attr_rows, N)` float32 단일 배열. 속성은 행 슬라이스(`{'pos': slice(2,5)}`), 개체는 열 인덱스. 시스템은 타입힌트로 필요한 속성을 선언하는 순수 함수 —
  `def pos_update(pos:3, vel:3, acc:3, dt)` — 를 `add_func`로 등록하면 속성 행이 자동 생성되고, `update(dt)`가 슬라이스 뷰를 꽂아 호출한다. 함수 이름 자체가 플래그 행이 된다.
- **UnitArray** (`gunfire_unit.py`): 한 단계 현실화. 단일 거대 배열 대신 **속성별 배열 dict** (`{'pos': (3,N) f32, 'hp': (N,) f32}`) + active 불리언 마스크 + free-list 인덱스 할당 + 50% 상각 증설. `acquire(n, **kwargs)` / `release(idxs)` / `set` / `get` 네 개가 외부 인터페이스의 전부. `posx` 같은 xyz 접미사 접근도 지원.
- **Unit 파사드** (`unitfactory.py`): `(unit_array, idxs)`만 들고 `__getattr__/__setattr__`를 배열로 위임 — **배열 위에서 OOP처럼 읽고 쓰는 뷰 객체.** 1개면 개체처럼, N개면 무리처럼 다뤄진다. Behavior와 Timer(예약 실행)는 배열이 아니라 Unit 쪽에 붙는다. 즉 **수치 코어와 고급 로직의 2층 구조**가 여기서 실물이 됐다.
- **UnitFactory**: 이름 붙은 아키타입 등록(`uf.set('hamster', {'jump':1,'age':3}, behavior)`) 후 `uf.order('hamster', n, **kwargs)`로 발급. 기본값은 `ham.txt` 같은 평문 데이터 파일에서 로드 가능 (`hp:5`).
- **실측 성능 실험** (`test_np*.py`, `highspeed/`): 아래 "숫자" 절 참조. 감이 아니라 측정으로 배열 레이아웃과 인덱싱 방식을 정했다.
- **렌더러 분리** (`test_renderer.py`): *"Mesh는 스스로 그리지 않는다. 씬도, 윈도우도 아니다. 그리는 자는 Renderer다."* meshid = matid+geoid 문자열, ViewModel/ViewTable이 시뮬 데이터를 그리기용 테이블로 바꾼다. 말미의 독백에서 방향 확정: *"머티리얼은 없다. 필요한 attr 목록을 가진 draw-type이 20종쯤 있을 뿐이다"*, 군중은 instanced draw, 옷감 정점 600KB 대신 본 데이터 6.4KB를 보낸다 — **의미 있는 상태를 보내고, 정점은 뷰가 만든다.**
- **소켓용 numpy 직렬화** (`test_npbytes.py`): float를 json으로 보내는 짓을 그만두고 `np_pack` — json 헤더 `[bytelen, dtype, shape]` + `tobytes()` 원시 바이트, 받는 쪽은 `frombuffer().reshape()`.

### 남은 미완

- Axis(단일 배열)와 UnitArray(속성별 dict)의 통합안이 확정 안 됨 → [결정: guides/10에서 속성별 dict로 확정](guides/10-core-array.md).
- `Unit.__del__`에서 release하는 방식은 GC 타이밍에 생사를 맡기는 함정 (guides/13에서 명시적 release로 교정).
- 충돌은 O(N²) 실측까지만 하고 브로드페이즈 미구현 (guides/16).
- 렌더러는 단일 draw까지, instanced 경로는 스케치만 (guides/15).

## 실측으로 얻은 숫자들 (2023, 데스크톱 기준 — 새 환경에서 재측정할 것)

| 실험 | 결과 | 출처 |
|---|---|---|
| 배열 레이아웃 | `(3,N)` 속성-메이저가 `(N,3)`보다 약 2배 빠름 (N≈1000 충돌 루프 30ms vs 60ms) | `highspeed/nptest.py`, png |
| 불리언 마스크 vs 인덱스 | 1M에서 `a[bool]` ≈ 16ms, `a[nonzero_idx]` ≈ 4~5ms — **마스크는 한 번 nonzero로 바꿔 재사용** | `test_nparridxslice.py` |
| nonzero 자체 | 1M 마스크 → 인덱스 ≈ 2.5ms | `gunfire_unit.get_active` |
| 인덱스 dtype | 64비트 머신에서 int64 인덱스가 int32보다 빠름. `np.nonzero` 반환형 그대로 쓸 것 | `test_nparridxslice.py`, `make_i` |
| 증설 비용 | 1M 배열 복사-확장 ≈ 1.5ms, 3×1M hstack ≈ 5ms — 50% 상각 증설이면 충분히 싸다 | `test_npstackspd.py` |
| 일괄 생성 | 100k 개체: `extend(100k)` ≈ 100ms, `append()`×100k ≈ 1000ms — **10배** | `soldier_unit.py` 실험 |
| 순진한 충돌 | 반벡터화 O(N²): N=500 ≈ 10ms, N=1000 ≈ 28ms — 브로드페이즈 필요선 | `highspeed/` |
| 파이썬 리스트 | 1M extend ≈ 7~10ms — free-list 관리 정도는 리스트로 충분 | `test_listextend.py` |
| sleep 해상도 | 윈도우 `time.sleep` 최소 단위가 크다(≈1.5~3ms). 60fps에 0.014s 슬립 | `simulator.py` 주석 |
| int 함정 | numpy 정수 sum/prod는 조용히 오버플로 — 수치는 float32, 인덱스는 int64로 통일 | `nptest.py` |

## 한 문장 요약

> 상태는 속성-메이저 배열에 눕히고, 로직은 배열 위의 순수 함수로 쓰고,
> 개성 있는 것들(이벤트·행동·컨트롤러)은 배열 밖 2층에 두고,
> 뷰는 소켓 건너편에서 원시 바이트를 받아 알아서 그린다. GPU는 그릴 때만 쓴다.

이 문장을 규칙으로 편 것이 [01-design-principles.md](01-design-principles.md)다.
