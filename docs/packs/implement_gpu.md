---
kind: pack
brief_ko: 구현자용 GPU 묶음. 기본 묶음 + GPU 레이아웃 규칙 + 장치 인터페이스 + 셰이더 규약 + GL 4.6 변형 사실.
---
# Pack: implement_gpu

For `implementer` (model medium) touching `gpu/`, `render/`, shaders, or `app/window.py`. Target ≤ 10k tokens.

## Load
1. `AGENTS.md`
2. `docs/roles/implementer.md`
3. `docs/rules/agent_conduct.md`
4. `docs/rules/style.md`
5. `docs/rules/simplicity.md`
6. `docs/rules/testing.md`
7. `docs/rules/performance.md`
8. `docs/rules/gpu_layout.md`
9. `docs/spec/conventions.md`
10. `docs/spec/gpu_interface.md`
11. `docs/spec/shaders.md`
12. `docs/variants/gl46.md`
Then the task card and the files under its **## Read**.

## Swap points
- GLES 3.1 → replace `docs/variants/gl46.md` with `docs/variants/gles31.md` (that is `docs/packs/port_gles31.md`).
- Vulkan → replace it with `docs/variants/vulkan.md` (`docs/packs/port_vulkan.md`).
