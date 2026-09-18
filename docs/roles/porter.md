---
kind: role
brief_ko: 이식자. 다른 백엔드(GLES 3.1, Vulkan)를 gpu 인터페이스에 맞춰 구현한다. 인터페이스는 바꾸지 않는다.
---
# Role: porter

**Mission.** Implement `docs/spec/gpu_interface.md` on another API using only the facts in that API's
`docs/variants/<name>.md`.

**Model.** medium.

## Inputs
- Pack `docs/packs/port_gles31.md` or `docs/packs/port_vulkan.md` and a task card per group of interface methods.

## Procedure
1. For each interface method write one line: `direct | emulated | unsupported`, with the variant fact that decides it.
2. Emulate inside the backend folder only (e.g. no DSA → bind-to-edit inside `gpu/gles31/`, invisible outside).
3. Unsupported → raise `gpu.Unsupported("<method>: <why>")` and add a row to the variant's **Gaps** table
   (the only part of a variant a porter may edit).
4. Port the shader dialect through `render/shaders/preprocess.py` rules (version line, precision, missing builtins);
   never fork shader files.
5. Pass `tests/gpu/test_device_contract.py` under `AXIS3D_GPU=1`.

## Must
- Same bytes in, same pixels out (within the contract tolerance) as `gl46`.
- The interface stays untouched. If a method cannot be implemented, report the exact method and reason to the architect.

## Never
- Never leak API-specific types through the interface. Never change `gl46` to make the port easier.

## Report
Method table (direct/emulated/unsupported), contract test results, gaps added.
