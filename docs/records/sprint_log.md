---
kind: record
brief_ko: 스프린트 로그. 카드마다 어떤 모델이 몇 번 만에 끝냈고 검토 판정이 무엇이었는지. 소형 모델 운용 가정(A-011, A-012)의 근거.
---
# Sprint log (append-only)

One row per card run. `model` is the actual model used (card's `small` → haiku, `medium` → sonnet, `large` → opus).
`attempts` counts implementer rounds before the reviewer accepted. `prompt tokens` is `tools/pack.py --stats` for
pack + card. Notes hold what the orchestrator had to add or fix by hand; an empty notes cell is the goal.

| card | role | model | prompt tokens | attempts | review | tests added | notes |
|---|---|---|---|---|---|---|---|
| 0001 | implementer | (architect, large) | — | 1 | — | 4 | Bootstrapped by the architect while building the document system. |
| 0020 | scribe | (architect, large) | — | 1 | — | 0 | Executed by hand after user approval. |
