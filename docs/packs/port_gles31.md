---
kind: pack
brief_ko: GLES 3.1 이식용 묶음. implement_gpu와 같되 변형 파일만 gles31로 바뀐다. 미니 엔진 시나리오.
---
# Pack: port_gles31

For `porter` (model medium) building `src/axis3d/gpu/gles31/`. Target ≤ 10k tokens with the card.
This is `implement_gpu` with one file swapped; the spec and rules are untouched.

## Load
1. `AGENTS.md`
2. `docs/roles/porter.md`
3. `docs/rules/agent_conduct.md`
4. `docs/rules/style.md`
5. `docs/rules/simplicity.md`
6. `docs/rules/testing.md`
7. `docs/rules/gpu_layout.md`
8. `docs/spec/conventions.md`
9. `docs/spec/gpu_interface.md`
10. `docs/spec/shaders.md`
11. `docs/variants/gles31.md`
Then the task card and the files under its **## Read** (usually the gl46 backend, for reference).
