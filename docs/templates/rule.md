---
kind: template
brief_ko: 규칙 문서 템플릿. 번호 붙은 반드시/절대 항목과, 검사관이 그대로 복사하는 체크리스트.
---
# Template: rule

Copy to `docs/rules/<topic>.md` (≤ 60 lines). Every item has an id (`<letter><n>`) so verdicts can cite it.
The **Check** list is what the reviewer copies into its table, so each box must be decidable from a diff.

````
---
kind: rule
brief_ko: <한 줄: 무엇을 규제하는가>
---
# Rule: <topic>

<one line: why this rule file exists, and which spec it serves>

## Must
- X1 <obligation, observable in code or docs>

## Never
- X2 <prohibition, observable>

## Check
- [ ] <box tied to X1>  - [ ] <box tied to X2>
````
