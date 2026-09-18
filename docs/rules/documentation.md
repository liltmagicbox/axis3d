---
kind: rule
brief_ko: 문서 규칙. 영어 본문과 brief_ko 한 줄, 길이 예산, 복사 대신 링크, 결정은 ADR로, 장부는 추가만.
---
# Rule: documentation

## Must
- D1 Every doc starts with frontmatter: `kind`, `brief_ko` (one Korean line). Decisions and tasks add their fields (`docs/README.md`).
- D2 Body in English. Korean only in `brief_ko` and in `docs/records/discussions/*` when quoting the human.
- D3 Line budgets per kind are enforced by `tools/check_docs.py`. Over budget → split, or move detail into a decision or record.
- D4 Link, don't repeat: a rule cites a spec section, a spec cites a decision id, a task cites both.
- D5 Any "we chose X" sentence lives in `docs/decisions/` with options and **Assumptions (check me)**.
- D6 Code docstrings follow `rules/style.md` S4; module docstrings state the zone (walk-through or `HARD ZONE:`).
- D7 Ledgers in `docs/records/` are append-only tables with ids: `A-017`, `E-004`, `B-009`.
- D8 A doc a sub-model loads is self-sufficient with its pack: no "as discussed", no "see chat".

## Never
- D9 No process prose in code files. No design rationale in docstrings (cite the ADR id).
- D10 No table that exists twice (the binding table lives once, in `spec/shaders.md`).
- D11 No editing a superseded decision; write a new one.

## Check
- [ ] frontmatter ok  - [ ] within budget  - [ ] cites, not copies  - [ ] decisions carry assumptions
