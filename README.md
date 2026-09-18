# axis3d

A data-oriented 3D simulation engine in Python (numpy + OpenGL 4.6), written to be read,
and a document system that lets small AI models build, test, review and record it by role.

- Start here: `AGENTS.md` (entry) → `docs/README.md` (map of the document system).
- Run: `uv sync` · `uv run pytest -q` · `uv run python tools/check_docs.py`
- The engine code lives in `src/axis3d/`; `legacy/` holds the earlier experiments it grew out of.

## 한국어
파이썬 3D 시뮬레이션 엔진(axis3d)과, 작은 AI 모델들이 역할별(구현·테스트·규칙검사·성능·기록…)로
엔진을 만들도록 하는 문서 시스템을 함께 담은 저장소입니다. 문서는 영어이고 각 문서의 머리말
`brief_ko` 한 줄이 한국어 요약입니다. `docs/README.md` 의 한국어 요약부터 읽으세요.
