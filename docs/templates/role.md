---
kind: template
brief_ko: 역할 문서 템플릿. 임무 두 줄, 모델 크기, 입력, 절차(≤ 8단계), 반드시/절대, 보고 형식.
---
# Template: role

Copy to `docs/roles/<name>.md` (≤ 70 lines) and add a wrapper in `.claude/agents/<name>.md` (frontmatter: name,
description, tools, model). The body is what the model reads first, so every line must change what it does.

````
---
kind: role
brief_ko: <한 줄: 이 역할이 하는 일과 하지 않는 일>
---
# Role: <name>

**Mission.** <two lines: the outcome this role owns>

**Model.** small | medium | large — <why>

## Inputs
- Pack `docs/packs/<pack>.md` and <what the card provides>.

## Procedure
1. <step>
2. <step>

## Must
- <observable obligation>

## Never
- <observable prohibition>

## Report
<what the report contains beyond docs/templates/report.md>
````
