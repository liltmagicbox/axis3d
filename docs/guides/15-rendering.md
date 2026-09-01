# 지침 15. 렌더링 — draw-type 테이블과 instanced draw

> 선행: [지침 14](14-view-boundary.md) · 관련 결정: D-009 · 원칙: 제6·7조

## 렌더러의 헌법 (test_renderer.py에서 확정된 것들)

1. **"Mesh는 스스로 그리지 않는다. 씬도, 윈도우도 아니다. 그리는 자는 Renderer다."**
   그리기 지식(GL 호출, 셰이더, VAO)은 Renderer 한 곳에 모인다. 시뮬은 물론이고 뷰모델도 GL을 모른다.
2. **머티리얼은 없다. draw-type이 있다.** draw-type = "필요한 attr 목록이 정해진 그리기 방식". 전부 합쳐 20종 안쪽을 목표로:
   `point / line / mesh / inst_mesh / sk_mesh / sprite / text / params(장식 이펙트)` 정도에서 시작.
3. **개성은 데이터로.** 색은 정점 컬러/팔레트 인덱스, 다양성은 인스턴스 attr로. 포토리얼 조명 체이스는 하지 않는다 — 라즈베리파이4에서 도는 것이 미덕이었다.

## 파이프라인

```
소켓 스냅샷 → ViewModel(테이블 정리·보간) → Renderer(draw-type별 그리기) → Window
```

- **ViewModel**: 받은 테이블을 draw-type별로 정리하고, 이전 프레임과의 보간을 담당 (시뮬 30Hz → 화면 144Hz). GL 무지.
- **Renderer**: draw-type → (shader, vao) 매핑 테이블. axis3d의 meshid(`matid+geoid` 문자열)를 `(draw_type, geo_id)` 튜플로 정식화. 미등록 id는 기본 리소스로 폴백 (원형의 `.get(id, default)` 계승).
- **Window**: 창/입력/이벤트만. axis3d interface.py의 WindowInterface 계승 (set_size/set_mouselock/bind_key/run...).

## instanced draw가 기본이다

같은 지오메트리 N개 = draw call 1개. 두 방식 모두 이미 실험됨:

- **uniform 배열 배치** (mvc3d snow: `uniform mat4 Model[252]` + `gl_InstanceID`): 소규모·구형 GL 호환. 252개 단위 청크.
- **인스턴스 attr 버퍼** (`glVertexAttribDivisor`): pos/quat/scale/color를 (n,·) 버퍼로 밀어넣는 정공법. 새 프로젝트의 기본.

행렬 조립은 뷰에서: 시뮬이 보낸 pos/quat/scale로 셰이더 안에서 변환하는 것을 우선 검토 (4x4 16f 대신 3+4+1=8f 전송 — 대역폭 절반).

**뷰 로컬 GPU 계산은 허용 지대다** ([지침 12](12-cpu-vs-gpu.md)): 장식 파티클은 `params` 테이블의 시드·강도만 받아 버텍스 셰이더에서 시간 함수로 움직인다. 시뮬 상태에 영향이 없으므로 합법.

## 뷰 두 종류를 유지한다

- **네이티브 뷰** (pyglet 또는 GLFW+PyOpenGL): 개발 기본. 기존 vao.py/shader.py/test_window.py를 이식 출발점으로.
- **브라우저 뷰** (three.js + websocket): threeinit에서 검증된 자산. 데모 공유·관전·VR(three.js VRButton)이 공짜로 따라온다. 같은 프로토콜의 두 번째 구독자일 뿐이므로 시뮬 쪽 코드는 0줄 추가.

## 단계별 작업

1. [ ] `view/window.py`: WindowInterface 이식 + GLFW 구현 (test_window.py 기반). 키/마우스 바인딩 → 와이어 이벤트 송신까지.
2. [ ] `view/renderer.py`: draw-type→(shader,vao) 테이블 + 폴백. point draw-type로 첫 픽셀 (10만 파티클 점 찍기).
3. [ ] `view/instanced.py`: 인스턴스 attr 버퍼 경로. 데모: 시뮬에서 받은 총알 4096개 instanced 큐브.
4. [ ] `view/viewmodel.py`: 테이블 정리 + 선형 보간 (프레임 두 개 버퍼링).
5. [ ] 셰이더에서 pos/quat/scale → 행렬 조립. uniform 배치 경로와 성능 비교 실험 1개.
6. [ ] (선택) `view/web/`: threeinit의 websocket 브로드캐스터 + three.js 클라이언트 이식. 브라우저에서 같은 씬 확인.

## 완료 기준

- 시뮬 10만 파티클이 네이티브 뷰에서 점으로, 총알 4096개가 instanced 메시로 그려진다.
- 뷰 프로세스 kill/재접속에도 시뮬 무사 (지침 14 완료 기준의 시각적 재확인).
- draw call 수가 draw-type 수에 비례하고 개체 수와 무관함을 확인.

## 함정

- 창 생성 전에 GL 호출 금지 — "윈도우 설정이 먼저, GL 설정은 나중" (pyglet 실험 파일의 교훈 주석).
- `glUniformMatrix4fv`는 column-major 평탄 리스트를 받는다 (test_renderer.py에서 한 번 밟은 지뢰 — 주석에 박제되어 있음).
- 보간 버퍼는 프레임 스킵·순서 뒤집힘(소켓)에 대비해 프레임 번호로 정렬.
- 셰이더 20종을 미리 만들지 말 것. draw-type은 데모가 요구할 때 하나씩 추가한다.
