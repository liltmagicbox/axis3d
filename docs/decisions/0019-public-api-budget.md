---
kind: decision
id: 0019
title: The public API is a budgeted registry of ≤ 90 names; adding a name requires an ADR
status: accepted
date: 2026-09-18
decided_by: ai
confidence: medium
reversible: yes — change the cap in this ADR's successor
brief_ko: 공개 이름은 docs/spec/api_budget.md 장부에 등록된 것만. 상한 90개. 추가하려면 ADR과 장부 수정이 함께 필요하다.
---
# 0019 — Public API budget

## Question
The user warned against API explosion. How do we make growth visible and deliberate?

## Decision
`docs/spec/api_budget.md` lists every public name per package with a cap per package and a total cap of 90.
A name absent from the table is private even without an underscore. The reviewer counts additions; the architect
edits the table; an addition needs an ADR.

## Options
1. Trust and review — the usual way, and the usual result.
2. `__all__` lists only — machine-readable but invisible to a reviewer reading a diff.
3. A registry with caps checked by the reviewer role (chosen); a later `tools/check_api.py` can automate the count.

## Why
A number makes the conversation concrete: "this change adds 3 names; we have 4 left in `render`".

## Assumptions (check me)
- 87 planned names for v1 is small enough to remember and large enough to build a demo. If the demo needs more,
  the cap moves by ADR, not silently.
- Class methods are bounded by their spec, not by this count; that is a deliberate looseness.

## Consequences
- `examples/` scripts use only budgeted names; that is their test.
- Backend folders expose nothing; `create_device` is the only door.
