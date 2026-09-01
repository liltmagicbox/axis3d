# 결정 로그

한 결정 = 한 줄 + (필요시) 근거 링크. 뒤집을 때는 지우지 말고 아래에 새 줄을 추가한다.

| ID | 날짜 | 결정 | 근거 |
|---|---|---|---|
| D-001 | 2022 | 시뮬과 뷰를 분리하고 좁은 인터페이스(input/update/draw ↔ get_inputs/draw)로만 통신 | mvc3d interface.py, [00 §1기](00-history-and-lessons.md) |
| D-002 | 2022 | 이벤트는 경계에서 dict ↔ Event 클래스로 한 번만 변환 | mvc3d event.py "let Events not cross this line" |
| D-003 | 2022 | 개체별 파이썬 벡터 객체 포기 ("pos 전쟁" 종전) | ver0.1_xyz_attrreport/API.py |
| D-004 | 2023 | 상태는 속성-메이저 배열, 개체는 열 인덱스 (oop→axis enlist) | axis.py, 실측 (3,N) 2× 우세 |
| D-005 | 2023 | 수치 float32 / 인덱스 int64 / 마스크 bool로 dtype 통일 | test_nparridxslice.py, 오버플로 실측 |
| D-006 | 2023 | 마스크는 np.nonzero로 인덱스화해 재사용 (bool 인덱싱 반복 금지) | 실측 16ms vs 4ms @1M |
| D-007 | 2023 | 배열 증설 50% 상각 + free-list + active 마스크, 생성은 배치 acquire | gunfire_unit.py, extend 10× 실측 |
| D-008 | 2023 | 소켓 전송은 json 헤더[len,dtype,shape]+tobytes (float json화 금지) | test_npbytes.py |
| D-009 | 2023 | 머티리얼 대신 draw-type 테이블, 군중은 instanced draw | test_renderer.py 독백 |
| D-010 | 2026-09 | 코어 배열은 단일 거대 배열(axis.py)이 아니라 **속성별 배열 dict**(gunfire_unit 계열)로 확정 — dtype 자유, 코드 단순, 속성별 연속성 유지. 단일 버퍼가 필요한 곳(소켓)은 경계에서 pack | [guides/10](guides/10-core-array.md) |
| D-011 | 2026-09 | 차기 프로젝트 지침서의 본거지는 axis3d/docs/. 새 저장소를 팔 때 docs/와 CLAUDE.md를 복사해 시작 | [README](README.md) |
| D-012 | 2026-09 | 커널은 Numba 없이 시작하되 처음부터 Numba 주입 가능 형태(배열+스칼라 순수 함수)로 작성 | [guides/11](guides/11-kernels.md) |
| D-013 | 2026-09 | GPU는 표시 전용. 시뮬 계산의 GPU 이관은 guides/12의 체크리스트를 전부 통과할 때만 | [guides/12](guides/12-cpu-vs-gpu.md) |
| D-014 | 2026-09 | 개체 삭제/해제는 명시적 release로만. `__del__` 의존 금지 | [guides/13](guides/13-events-and-units.md) |
