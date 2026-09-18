---
kind: entry
brief_ko: 모든 에이전트의 진입점. 프로젝트 한 줄 소개, 읽는 순서, 명령, 모든 역할의 공통 금지사항.
---
# axis3d — agent entry point

axis3d is a data-oriented 3D simulation engine in Python (numpy + OpenGL 4.6), written to be read:
a beginner can follow the main path, and the hard parts are fenced off as `HARD ZONE` modules.

## Read next, in this order
1. `docs/README.md` — map of the document system and how context is composed.
2. The **pack** your task names (`docs/packs/*.md`). It lists exactly what to load, in order.
3. Your **task card** (`docs/tasks/todo/NNNN-*.md`) and the files under its `## Read`.
Nothing else unless the card says so. Small context is the point.

## Commands
- `uv sync` · `uv run pytest -q` (CPU only) · `AXIS3D_GPU=1 uv run pytest -q -m gpu` (GL 4.6 display, or headless: `docs/variants/gl46.md`)
- `uv run ruff check . && uv run ruff format .`
- `uv run python tools/check_docs.py` — doc budgets, frontmatter, links
- `uv run python tools/pack.py docs/packs/implement.md --task docs/tasks/todo/0003-ecs-table.md --stats`
- `uv run python tools/new.py task "title" --pack implement --role implementer`

## Non-negotiables for every role (details: `docs/rules/agent_conduct.md`)
- State lives in numpy arrays inside `World`; behaviour lives in plain functions `f(world, dt)`.
- The public API is budgeted in `docs/spec/api_budget.md`. A new public name needs a decision record.
- Never delete, skip, or weaken a test to get green.
- Only the architect edits `docs/spec`, `docs/rules`, `docs/decisions`, `docs/variants`. Others propose in reports.
- Every choice a task left open becomes one line in `docs/records/assumptions.md`.
- Report with `docs/templates/report.md`: status, files, tests run, assumptions, follow-ups. Facts and `file:line`.

## Layout
`src/axis3d/` engine · `tests/` pytest mirror of src · `bench/` benchmarks · `docs/` this system · `tools/` doc utilities
`legacy/` holds the earlier experiments (see `legacy/README.md`); do not edit or import them.
