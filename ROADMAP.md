# ROADMAP — 수직 슬라이스

목표 하나: **유닛들이 브라우저에서 걸어다니는 걸 본다.** 그 전까지 다른 전선 금지.
부품은 전부 이미 있다. 없는 건 연결뿐이다.

```
Axis(유닛 N명 행진) → World 스냅샷 → websocket → three.js 뷰
                                  └→ (아무 프레임) gltf export → 블렌더 렌더
```

각 스텝은 한 세션 분량이고, 완료 조건은 전부 "눈에 보이는 것"이다.
분업 표기: [나] = 설계/판단, [C] = Claude에게 넘길 배선 작업.

## 0. 이음새 수리 [C]
지금까지 발견된, 모듈 사이가 안 맞는 지점들. 한 번에 고친다.
- [ ] mvc3d simulator.py: `SLEEPTIME` 15.9초 → 0.0159초, `world.get_draw()` 전역 참조 → `self.world`, World/Viewman import 누락
- [ ] mvc3d world.py: IWorld 계약(get_draw/put_input)과 메서드명 통일, `put()`의 미정의 `value`
- [ ] mvc3d actor.py: `grav_acc` → `gravity` (또는 simulate_physics 분기 정리)
- [ ] mvc3d controller.py: `parse()`가 `mul`을 쓰지도, `*` 분기에서 함수를 부르지도 않음
- [ ] axis3d vao.py: attrs 루프가 'index'까지 버텍스 속성으로 등록하는 문제
- [ ] axis3d axis.py / unitfactory.py: import 시 실행되는 테스트 코드를 main() 가드로
- **완료 = `python3 simulator.py`가 예외 없이 틱을 돈다 (헤드리스).**

## 1. 행진 데모 [나: 유닛 수/움직임 정의, C: 배선]
- mvc3d에 demo.py: Axis 기반 유닛 50명이 pos_update로 움직이는 World.
- axis3d는 라이브러리로 import (sys.path 또는 `pip install -e ../axis3d`).
- **완료 = 터미널에 유닛 pos가 매 틱 변해서 찍힌다.**

## 2. 스트림 [C]
- threeinit의 ws_broadcaster 계열 중 하나를 채택(판결문 남기기), demo.py에 연결.
- **완료 = 브라우저 콘솔에 pos 패킷이 흐른다.**

## 3. 뷰 — 슬라이스 완성점 [나: 보고 판단, C: 배선]
- three.js 뷰어에 GLTFLoader 추가, gltf_out/demo_scene.glb 로드.
- extras.id ↔ 스트림 패킷 매칭으로 유닛 오브젝트를 움직인다.
- **완료 = 브라우저에서 유닛들이 걸어다닌다. ← 여기가 목표.**

## 4. 스냅샷 보너스 [C]
- 돌아가는 월드에서 키 하나로 `gltfview.export_actors()` → .glb → 블렌더 렌더.
- **완료 = 움직이던 그 순간의 렌더 png 한 장.**

## 5. 그 다음 (슬라이스 완성 전엔 착수 금지)
- 인스턴싱(EXT_mesh_gpu_instancing), gltf 애니메이션 채널, 리포 역할 분리 실행(ARCHITECTURE.md),
  성능 스케일업(50 → 900+) — 전부 IDEAS.md에 있다. 순서는 그때 정한다.
