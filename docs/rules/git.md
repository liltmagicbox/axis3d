---
kind: rule
brief_ko: 깃 규칙. 커밋 단위는 작업 카드 하나, 메시지 형식, 이진 파일 금지, 커밋 전 검사.
---
# Rule: git

## Must
- V1 One task card = one commit (plus fix-ups from review). Subject `<area>: <what>` ≤ 60 chars, e.g. `ecs: add Table.insert and remove`.
- V2 Body says *why* and cites the card and any ADR: `Task 0003. ADR 0004.` Then the checks that ran.
- V3 Branches: `task/NNNN-<slug>` for cards, `design/<slug>` for decision work. The default branch stays green.
- V4 Commit `uv.lock`. Generated shader files (`shaders/gen/`) are ignored; they are written at startup.
- V5 Before every commit: `uv run ruff format .`, `uv run ruff check .`, `uv run pytest -q`, `uv run python tools/check_docs.py`.

## Never
- V6 No binaries, screenshots, zips, or videos in this repository.
- V7 No force-push on shared branches. No rewriting a commit a review already cites.
- V8 No commit that mixes document-system changes with engine code unless the card is about both.

## Check
- [ ] subject format  - [ ] card/ADR cited  - [ ] no binaries  - [ ] checks ran
