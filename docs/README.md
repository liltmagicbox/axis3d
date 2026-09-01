# docs/ — 차기 3D 시뮬레이션 프로젝트 설계 문서

mvc3d(2022) → axis3d(2023)에서 이어진 논의를 정리한 문서 묶음이다.
다음 프로젝트는 이 문서를 읽는 것에서 시작한다.

## 읽는 순서

| 문서 | 내용 | 언제 읽나 |
|---|---|---|
| [STATUS.md](STATUS.md) | 현재 상태, 다음 할 일 | **매 세션 시작 시** |
| [00-history-and-lessons.md](00-history-and-lessons.md) | mvc3d/axis3d에서 무엇을 시도했고 무엇을 배웠나 | 처음 합류할 때 |
| [01-design-principles.md](01-design-principles.md) | 설계 방침 10조 | 처음 + 설계 결정 때마다 |
| [02-ai-workflow.md](02-ai-workflow.md) | AI(Claude)와 일하는 방식 | 처음 + 새 세션 열 때 |
| [03-schedule.md](03-schedule.md) | 마일스톤과 일정 관리 | 계획 세울 때 |
| [decisions.md](decisions.md) | 결정 로그 (한 줄씩) | 결정을 내리거나 뒤집을 때 |
| [ideas.md](ideas.md) | 아이디어 주차장 | 아이디어가 떠오를 때 (여기 적고 하던 일 계속) |

## 작업 지침서 (guides/)

주제별로 나뉘어 있고, 각 지침서는 **읽으면서 그대로 작업할 수 있게** 배경 → 설계 → 단계별 작업 → 완료 기준 순서로 쓰여 있다. 번호 순서가 곧 권장 구현 순서다.

| # | 지침서 | 주제 |
|---|---|---|
| 10 | [core-array](guides/10-core-array.md) | 씬 연산 코어: ECS 대신 속성-메이저 배열 풀 |
| 11 | [kernels](guides/11-kernels.md) | 커널 작성 규칙: Numba 없이 빠르게, Numba 준비된 형태로 |
| 12 | [cpu-vs-gpu](guides/12-cpu-vs-gpu.md) | 계산은 CPU, GPU는 그리기 — 배치 결정 기준 |
| 13 | [events-and-units](guides/13-events-and-units.md) | 이벤트와 고급 객체를 코어에서 분리 |
| 14 | [view-boundary](guides/14-view-boundary.md) | 시뮬–뷰 경계: 인터페이스와 소켓 프로토콜 |
| 15 | [rendering](guides/15-rendering.md) | 렌더링: draw-type 테이블과 instanced draw |
| 16 | [collision](guides/16-collision.md) | 충돌: 실측 기반 브로드페이즈 |
| 17 | [profiling-and-numba](guides/17-profiling-and-numba.md) | 측정 습관과 Numba 확장 경로 |

## 새 프로젝트를 시작할 때

1. 새 저장소를 만들고 이 `docs/` 폴더와 루트 `CLAUDE.md`를 복사한다.
2. `STATUS.md`를 초기화한다 (마일스톤 M0부터).
3. `guides/10`부터 순서대로 진행한다. 각 가이드의 "완료 기준"을 통과해야 다음으로 간다.
4. 결정이 바뀌면 `decisions.md`에 한 줄 추가한다. 문서를 조용히 고치지 않는다.
