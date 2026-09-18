---
kind: template
brief_ko: 결정 기록(ADR) 템플릿. tools/new.py decision "제목" 이 아래 4-백틱 블록을 복사해 채운다. 가정(check me)은 필수.
---
# Template: decision (ADR)

`uv run python tools/new.py decision "<title>"` copies the block below to `docs/decisions/NNNN-<slug>.md`.
Keep the result ≤ 50 lines. **Assumptions (check me)** is mandatory: every belief about the user, the hardware,
or the future that the decision leans on, each with a way to verify it.

````
---
kind: decision
id: {{id}}
title: {{title}}
status: proposed
date: {{date}}
decided_by: ai
confidence: medium
reversible: yes — <what reversing costs>
brief_ko: <한 줄: 무엇을 왜 결정했는가>
---
# {{id}} — {{title}}

## Question
<one line>

## Decision
<what is now true; name the spec sections that change>

## Options
1. <option> — <one-line cost>
2. <option> — <one-line cost>
3. <option> (chosen)

## Why
<two lines at most>

## Assumptions (check me)
- <belief> — <how to verify>

## Consequences
- <what changes in spec, rules, code, or cards>
````
