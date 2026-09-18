---
kind: pack
brief_ko: 구현자용 기본 묶음(CPU, walk-through 코드). 규칙 전부 + 규약. GPU 작업은 implement_gpu로.
---
# Pack: implement

For `implementer` writing walk-through CPU code. Target ≤ 8k tokens with the card.

## Load
1. `AGENTS.md`
2. `docs/roles/implementer.md`
3. `docs/rules/agent_conduct.md`
4. `docs/rules/style.md`
5. `docs/rules/simplicity.md`
6. `docs/rules/education.md`
7. `docs/rules/testing.md`
8. `docs/rules/numpy.md`
9. `docs/rules/performance.md`
10. `docs/spec/conventions.md`
Then the task card and the files under its **## Read**.

## Swap points
- GPU, shader, or window work → `docs/packs/implement_gpu.md`.
- A different backend → `docs/packs/port_gles31.md` or `docs/packs/port_vulkan.md`.
