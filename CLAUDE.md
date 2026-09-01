# CLAUDE.md

## 이 저장소는 무엇인가

axis3d는 파이썬 3D 시뮬레이션 실험장(2023)이자, **차기 프로젝트 설계 문서의 본거지**다.
전작 mvc3d(MVC 분리·소켓 뷰 실험, 2022)의 논의가 여기서 데이터지향 구조로 진화했고, 그 전체 정리가 `docs/`에 있다.

- `docs/` — **이 저장소에서 살아있는 부분.** 설계 방침, AI 워크플로, 스케줄, 주제별 작업 지침서(guides/10~17). 여기서부터 읽는다: [docs/README.md](docs/README.md)
- 루트 `*.py`, `highspeed/`, `scr/` — 2023년 실험 산출물. **참조 자료이며 리팩터링·린트 대상이 아니다.** 지침서들이 이 파일들을 근거로 인용한다 (axis.py, gunfire_unit.py, unitfactory.py, test_np*.py 등). 고치지 말고 읽어라.
- 새 코드를 이 저장소에 쓰게 되면 `core/`, `world/`, `view/`, `experiments/` 디렉터리를 새로 파서 쓴다 — 루트에 섞지 않는다.

## 매 세션

1. **시작**: [docs/STATUS.md](docs/STATUS.md) → 작업 주제의 `docs/guides/XX` 순서로 읽는다. STATUS와 요청이 어긋나면 짚고 시작한다.
2. **작업**: 가이드의 단계와 완료 기준을 따른다. [설계 방침](docs/01-design-principles.md)과 충돌하는 요청이면 조용히 우회하지 말고 묻는다.
3. **종료**: 돌아가는 상태로 커밋 + STATUS.md 갱신(한 일/다음 것/막힌 것). 설계가 바뀌었으면 해당 가이드와 [docs/decisions.md](docs/decisions.md)도 같이.

## 규칙 요약 (전문: docs/01-design-principles.md)

- 상태는 아키타입별 **속성-메이저 배열** `(dims, N)`: 수치 float32, 인덱스 int64(np.nonzero 반환형 그대로), 판별 bool.
- **핫패스에 파이썬 객체·개체 루프 금지.** 커널은 배열+스칼라만 받는 순수 함수 — 그 형태가 Numba 확장 경로다.
- 이벤트·Behavior·컨트롤러 등 **고급 로직은 2층**(배열 밖 객체 세계). 1층은 인덱스와 마스크로만 만진다.
- **GPU는 그리기 전용.** 시뮬은 headless로 돌 수 있어야 한다. 이관 검토는 guides/12 체크리스트로만.
- 이벤트는 경계에서 한 번만 변환: 소켓 위 dict/바이트 ↔ 시뮬 안 Event 클래스. float를 json에 넣지 않는다(np_pack).
- **성능 주장에는 측정 수치.** 실험은 `experiments/`에, 결론은 파일 주석 + docs/00 숫자 표 + decisions.md에.
- 모든 모듈에 `if __name__ == '__main__':` 데모. import 부수효과 금지.

## 관례

- 대화·문서는 한국어, 코드·식별자·커밋 메시지는 영어.
- 커밋: `영역: 무엇을 왜` 한 줄. 실험 커밋은 결론을 메시지에 담는다.
- 새 프로젝트 저장소를 시작할 때: `docs/`와 이 파일을 복사하고, [docs/02-ai-workflow.md](docs/02-ai-workflow.md)의 CLAUDE.md 씨앗으로 교체한다.
