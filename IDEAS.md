# IDEAS — 주차장

새 파일을 여는 대신 여기 한 줄. 수직 슬라이스(ROADMAP.md) 완성 전엔 착수 금지.
착수할 땐 이 파일에서 지우고, WORKFLOW 규칙 1의 완료 조건 한 줄부터 쓴다.

## 엔진
- Actor를 Axis 슬라이스 파사드로 통합 (unitfactory.Unit 방식 확장)
- 인스턴스드 드로우: 같은 메시 1k 유닛 (test_renderer 주석의 계획)
- 파티클 drawtype: pos만 스트리밍, 그리는 방식은 viewmodel이 결정 (test_renderer 주석)
- drawtype 체계: "머티리얼은 없다, 요구 attrs를 가진 드로우 타입 ~20종" (test_renderer 주석)
- sk cloth 정점 600KB → bone 128개 6.4KB 압축 전송 아이디어 (test_renderer 주석)
- honeycomb/hexa 지오메트리 (fullcode 메모)
- Geometry.export_normalmap: seam 지정 unfold (fullcode 메모)
- 리포 통합 실행: mvc3d가 axis3d를 pip -e로 물고, 중복 gltf.py 제거

## glTF 확장 (GLTF_COMPAT.md 후속)
- 애니메이션 채널 export (TRS 키프레임) → smd 계획 대체
- 스킨(JOINTS/WEIGHTS) + SKMesh 재생
- EXT_mesh_gpu_instancing — 인스턴스드 계획과 직결
- 텍스처 export/로드 (지금은 참조만 전달)
- KHR_physics_rigid_bodies 표준화 추이 관찰 (물리 extras 규약은 그때까지 자체 정의)

## 뷰/툴
- 브라우저 뷰에 카메라 컨트롤 (vector.Camera의 yaw/pitch 로직 이식)
- 블렌더 렌더 자동화를 CI처럼: 커밋마다 씬 렌더 png 갱신
