# ARCHITECTURE — 구조 결정사항

한번 정한 것은 여기 적고, 다시 고민하지 않는다. 바꿀 땐 이 파일을 고치는 커밋과 함께.

## 리포 역할
- **axis3d = 코어 라이브러리.** Axis(SoA), 지오메트리 생성(cylinder 등), gltf.py, GL 디버그 뷰(vao/shader).
- **mvc3d = 제품.** 시뮬 서버(simulator/world) + 웹 뷰(threeinit websocket + three.js). axis3d를 import해서 쓴다.
- 같은 개념을 양쪽에 두 번 만들지 않는다. (현재 gltf.py 두 벌은 임시 — 통합 시 axis3d 것만 남김)

## 데이터 규약 (모든 모듈의 공통 통화)
- 지오메트리 = attrs dict: `{'position':[...], 'normal':[...], 'uv':[...], 'color':[...], 'index':[...]}`
  - VAO(attrs), Geometry, gltf.py 전부 이 형태. glTF 왕복 검증 완료.
- 트랜스폼 = pos(x,y,z) / rot(euler xyz, radians) / scale. 쿼터니언 변환은 gltf.euler_to_quat.
- 좌표계 = Z-up, RH, 미터. (외부 전달 시 변환은 gltf.py의 zup_root가 담당)

## 성능 경계 (파이썬에서 살아남는 법)
- **매 프레임 × 매 유닛으로 도는 코드는 Axis(numpy SoA) 안에서만.** 벌크 연산으로.
- Vec3/Euler 같은 프로퍼티 클래스는 API/스크립팅 편의용. 핫루프 반입 금지.
- Actor(OOP)와 Axis(SoA)는 경쟁하지 않는다: **Actor는 Axis 슬라이스 위의 파사드**로 수렴
  (unitfactory.Unit이 이미 그 방식). mvc3d Actor의 per-object 물리 갱신은 이 방향으로 흡수.

## 뷰 전략
- 주력 뷰 = three.js(브라우저, websocket 스트리밍). PyOpenGL은 로컬 디버그 뷰로 유지.
- 렌더 품질 경쟁은 하지 않는다: 버텍스 컬러 / 로우폴리 / 인스턴싱. ("no photorealistic, that's not my world")
- 최종 퀄리티 렌더가 필요하면 glTF로 내보내 블렌더에 맡긴다 (검증 완료).

## 씬 전달
- 정적 씬(배치/지오메트리/재질/조명/카메라) = **.glb 파일**. 상세와 실측: GLTF_COMPAT.md.
- 동적 상태(pos/rot, hp 등) = **websocket 스트림**. 매칭 키 = glb 노드의 extras.id.
- 게임 데이터를 glTF 본문에 싣지 않는다. extras까지만. (UE 기본 파이프라인은 extras를 버림)

## 조명/카메라 규약
- 조명 값은 photometric 단위(sun=lux, point/spot=candela), 수천 lux대 기준. 실측표: GLTF_COMPAT.md.
- 카메라 fov는 수직, degrees (vector.Camera와 동일).
