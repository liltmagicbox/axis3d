---
kind: template
brief_ko: 읽기 경로(tour) 템플릿. 10–20단계, 각 단계는 "파일을 열고, 이것을 보고, 이것을 알아채라".
---
# Template: tour

Copy to `docs/tour/<subsystem>.md` (≤ 120 lines). Written by the teacher role for a human reader.

````
---
kind: tour
brief_ko: <한 줄: 무엇을 어떤 순서로 읽게 하는가>
---
# Tour: <subsystem> (about <n> minutes)

For a reader who knows Python and numpy indexing and has not seen this engine.

1. Open `src/axis3d/<file>.py`. Look at `<function>`. Notice <the one idea this step teaches>.
2. …

## Where the hard parts are
- `src/axis3d/<module>.py` — HARD ZONE because <why>; you use it through `<name>`, `<name>`.

## Try it
```
uv run python examples/<script>.py
```
````
