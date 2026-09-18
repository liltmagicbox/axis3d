---
kind: task
id: 0021
title: gpu/gles31 backend (mini engine)
pack: port_gles31
role: porter
model: medium
status: blocked
blocked_by: [0012]
brief_ko: 같은 Device 인터페이스를 GLES 3.1 로 구현하는 미니 엔진 카드. 변형 파일 하나만 바꾼 팩으로 실행한다.
---
# 0021 — gpu/gles31 backend

## Goal
`create_device("gles31", window)` passes `tests/gpu/test_device_contract.py` on an ES 3.1 context (ANGLE or a
mobile-class driver), with every gap recorded in `docs/variants/gles31.md`.

## Read
- `docs/spec/gpu_interface.md`
- `docs/variants/gles31.md`
- `src/axis3d/gpu/gl46/device.py` (reference implementation), `src/axis3d/render/shaders/preprocess.py`

## Write
- `src/axis3d/gpu/gles31/__init__.py`, `src/axis3d/gpu/gles31/device.py`
- `src/axis3d/render/shaders/preprocess.py` (variant header rules only)
- `docs/variants/gles31.md` (Gaps table rows only)

## Do
1. Method table first (direct / emulated / unsupported) in the report, then implement in that order.
2. Bind-to-edit emulation stays inside `gles31/`; `draw_indirect` loops `glDrawElementsIndirect` unless
   `GL_EXT_multi_draw_indirect` is present; `BASE_INSTANCE` define path for shaders.
3. Context creation through EGL (Linux) or ANGLE (Windows); document the chosen route in the variant's Context section.

## Done when
- `AXIS3D_GPU=1 AXIS3D_BACKEND=gles31 uv run pytest -q tests/gpu` passes or every failure is a row in Gaps.
- `examples/bouncing_spheres.py --backend gles31` shows the same scene.

## Out of scope
- Changing the interface, the specs, or gl46. New features.

## Notes
- This card is the user's "mini engine" scenario: the only document swapped versus `implement_gpu` is the variant.
