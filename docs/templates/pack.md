---
kind: template
brief_ko: 팩 템플릿. 어떤 역할용인지, 토큰 예산, 순서대로 읽을 파일 목록, 교체 지점.
---
# Template: pack

Copy to `docs/packs/<name>.md` (≤ 40 lines). Paths in backticks under **## Load** are what `tools/pack.py`
concatenates, in order. Only backtick a path there if it must load: prose in that section is scanned too.
Keep the pack + a card under the token target; check with `--stats`.

````
---
kind: pack
brief_ko: <한 줄: 누가 무엇을 할 때 쓰는 묶음인가>
---
# Pack: <name>

For `<role>` doing <kind of work>. Target ≤ <n>k tokens with the card.

## Load
1. `AGENTS.md`
2. `docs/roles/<role>.md`
3. `docs/rules/agent_conduct.md`
4. <more rules and specs, most general first>
Then the task card and the files under its **## Read**.

## Swap points
- <situation> → use `docs/packs/<other>.md` / replace `<file>` with `<file>`.
````
