---
kind: map
brief_ko: 문서 시스템의 지도. 폴더 역할, 컨텍스트 조합법(pack+task), 무엇이 바뀌면 어떤 문서만 고치는지, 길이 예산.
---
# The document system

## 한국어 요약
이 저장소는 파이썬 3D 시뮬레이션 엔진(axis3d)과, 그 엔진을 **작은 AI 모델들이 역할별로** 개발·검사·기록하도록
만드는 문서 시스템을 함께 담는다. 모든 문서는 영어이고, 머리말의 `brief_ko` 한 줄이 한국어 요약이다.
- `roles/` 누가: 구현자, 테스터, 규칙검사관, 스타일, 성능평가, 엣지케이스 수집, 기록자, 설계자, 계획자, 교육검토, 이식자
- `rules/` 반드시/절대: 짧고 원자적. 파일 하나를 바꾸면 그 규칙만 바뀐 채 에이전트가 동작한다
- `spec/` 현재 계약: 무엇을 만드는가, 시그니처, 바인딩 번호. 구현자가 읽는 "지금의 진실"
- `variants/` 백엔드 사실(GL 4.6 / GLES 3.1 / Vulkan): 팩에서 파일 하나만 바꿔 끼우면 다른 백엔드용 에이전트가 된다
- `decisions/` 왜: 잘게 쪼갠 ADR. AI가 내린 결정은 `decided_by: ai`, 가정(check me)과 확신도를 같이 적는다
- `packs/` 조합: 어떤 문서를 어떤 순서로 읽힐지. `tools/pack.py`가 한 개의 프롬프트로 이어 붙인다
- `tasks/` 작업 카드: 작은 모델이 카드 하나만 보고 끝낼 수 있는 단위. `todo/` → `done/`
- `records/` 누적 장부: 가정, 엣지케이스, 벤치마크, 논의 요약, 용어, 변경 이력. 추가만 하고 고치지 않는다
길이 예산은 `tools/check_docs.py`가 강제하므로 핵심 문서는 짧게 유지된다.

## One picture
```
human ⇄ architect ──writes──▶ decisions/ ──shape──▶ spec/ + rules/ + variants/
                                                          │
planner ──writes──▶ tasks/todo/NNNN ──▶ tools/pack.py ──▶ one prompt ──▶ sub-model in a role
                                                          │
                       code + tests + report ◀────────────┘──▶ reviewer · stylist · profiler · edge_hunter
                                                          │
scribe ──appends──▶ records/ (assumptions, edge cases, benchmarks, discussions), moves card to done/
```

## Folders
| folder | holds | who edits | budget (lines) |
|---|---|---|---|
| `AGENTS.md` | entry point (`CLAUDE.md` imports it) | architect | 60 |
| `docs/roles/` | one file per role: mission, procedure, must/never | architect | 70 |
| `docs/rules/` | atomic must/never lists with a reviewer checklist | architect | 60 |
| `docs/spec/` | current contracts and signatures | architect | 140 |
| `docs/variants/` | backend facts, swappable | architect, porter (gaps table) | 90 |
| `docs/decisions/` | ADRs; supersede, never edit | architect | 50 |
| `docs/packs/` | ordered load lists | architect, planner | 40 |
| `docs/tasks/` | task cards `todo/` `done/` + board | planner, scribe | 60 |
| `docs/records/` | append-only ledgers and discussion digests | any role appends; scribe curates | none / 80 |
| `docs/templates/` | skeletons for every kind above | architect | 60 |
| `docs/tour/` | reading paths for humans | teacher | 120 |

## Composing context
`prompt = pack files (in order) + task card + files under the card's "## Read"`.
```
uv run python tools/pack.py docs/packs/implement.md --task docs/tasks/todo/0003-ecs-table.md --stats
```
Targets: ≤ 8k tokens for implement/test packs, ≤ 5k for review/style packs (`--stats` shows the estimate).
Swap a backend: `packs/port_gles31.md` loads `variants/gles31.md` instead of `variants/gl46.md`. Nothing else moves.
Claude Code users: `.claude/agents/<role>.md` are thin wrappers that read `docs/roles/<role>.md` first.

## When X changes, edit Y (and only Y)
| change | edit |
|---|---|
| code style | `rules/style.md` (+ `[tool.ruff]` in `pyproject.toml`) |
| what counts as simple, API caps | `rules/simplicity.md`, `spec/api_budget.md` |
| a subsystem's contract | that `spec/*.md` + one new `decisions/NNNN-*.md` |
| GL version or backend facts | `variants/*.md` (+ `rules/gpu_layout.md` if a rule changes) |
| how a role behaves | `roles/<role>.md` (+ `.claude/agents/<role>.md` only for tools/model) |
| which docs a job needs | `packs/<pack>.md` |
| performance or scale targets | `spec/targets.md` |
| coordinate/unit conventions | `spec/conventions.md` + ADR, then `src/axis3d/conventions.py` |
| a mini engine for another API | new `variants/<api>.md` + `packs/port_<api>.md`; spec and rules unchanged |

## Frontmatter
```
---
kind: entry | map | role | rule | spec | variant | decision | pack | task | record | template | discussion | tour
brief_ko: <one Korean line saying what this document is for>
---
```
Decisions add `id title status date decided_by confidence reversible`. Tasks add `id pack role model status`.

## Lifecycle of a change
1. Architect writes or supersedes a decision; spec/rules/variants follow it.
2. Planner cuts task cards (`tools/new.py task ...`), each doable from pack + card alone.
3. A sub-model runs one pack + card and returns a report.
4. Reviewer and stylist give verdicts; profiler and edge_hunter run when the card asks.
5. Scribe appends records, moves the card to `done/`, adds a changelog line.
6. The human reads `records/assumptions.md` now and then and challenges entries; challenged ones become ADRs.
