---
kind: template
brief_ko: 논의 요약 템플릿. 질문, 선택지, 결과, 열린 질문, 의견 차이. 사람의 말은 원문 언어로 인용한다.
---
# Template: discussion digest

`uv run python tools/new.py discussion "<title>"` copies the block below to
`docs/records/discussions/YYYY-MM-DD-<slug>.md`. Keep it ≤ 80 lines. Quote the human where wording matters.

````
---
kind: discussion
date: {{date}}
title: {{title}}
brief_ko: <한 줄: 무엇을 논의했고 결론은 무엇인가>
---
# {{title}} ({{date}})

## Asked
<the question; quote the human in their language when the wording matters>

## Options raised
- <option> — <who favoured it and why>

## Outcome
<decided or deferred; link `docs/decisions/NNNN-*.md`>

## Open questions
- <question> → <who answers, when>

## Disagreements (one line per side)
- <side A> / <side B>
````
