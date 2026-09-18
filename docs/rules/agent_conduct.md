---
kind: rule
brief_ko: 모든 역할의 공통 행동 규칙. 범위 준수, 테스트 보존, 가정 기록, 보고 형식.
---
# Rule: agent conduct (all roles)

## Must
- C1 Do only what the task card says. Finish it fully, or report `BLOCKED` / `PARTIAL` with the reason.
- C2 Read only the pack, the card, and the card's **Read** list. If you needed more, name it in the report.
- C3 A choice the card left open → one row in `docs/records/assumptions.md` (id, date, where, assumption, how to verify).
- C4 Run the commands in `AGENTS.md` before reporting. Paste failures verbatim.
- C5 Report with `docs/templates/report.md`: facts, `file:line`, test names. No narration.
- C6 When a rule blocks a sensible change, follow the rule and write "rule feedback" in the report.

## Never
- C7 Never delete, skip, weaken, or `xfail` an existing test (edge_hunter may `xfail(strict=True)` *new* tests only).
- C8 Never edit `docs/spec`, `docs/rules`, `docs/decisions`, `docs/variants` unless your role file allows it.
- C9 Never add a dependency, a public name, a backend, or a config file without a decision record.
- C10 Never guess a number (budget, size, tolerance). Find it in the spec or report `BLOCKED`.
- C11 Never touch files outside the card's **Write** list (the tests it names are inside it).

## Check
- [ ] files changed ⊆ card's Write list (+ named tests)  - [ ] no test removed, skipped, or weakened
- [ ] no new public names, or an ADR is cited  - [ ] assumptions logged  - [ ] report present, in format
