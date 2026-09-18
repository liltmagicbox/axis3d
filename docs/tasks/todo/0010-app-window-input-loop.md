---
kind: task
id: 0010
title: app: Window, Input, bindings, loop
pack: implement_gpu
role: implementer
model: medium
status: todo
blocked_by: [0004]
brief_ko: GLFW 창(GL 4.6 컨텍스트), 입력→world.inputs 행, 키 바인딩 사전, 누적기 고정 스텝 루프.
---
# 0010 — app: Window, Input, bindings, loop

## Goal
The main path's outer shell: a window with a 4.6 context, inputs written into the `inputs` table, and the
fixed-step loop, testable headless where possible.

## Read
- `docs/spec/app.md`
- `docs/variants/gl46.md` — section "Context"

## Write
- `src/axis3d/app/__init__.py`, `window.py`, `input.py`, `bindings.py`, `loop.py`
- `tests/app/test_loop.py` (CPU), `tests/app/test_input.py` (CPU), `tests/app/test_window.py` (gpu)

## Do
1. `Window(width, height, title, vsync)`: hints per variant; `handle`, `size()`, `should_close()`, `poll()`, `close()`;
   `glfw.init()` inside `__init__`; `glfw.terminate()` in `close()`.
2. `Input(window)`: key/mouse callbacks fill `keys`, `mouse_delta`, `buttons`; `write_row(world, player=0)` maps
   `bindings` to `move` (normalised, `(3,)`), `look` (`(2,)`), `buttons` (bit per binding name).
3. `bindings.py`: `bindings: dict[str, tuple[int, ...]]` for forward/back/left/right/up/down/jump/action.
4. `loop.py`: `run(world, renderer, camera, window, on_step=None)` exactly as the spec pseudo-code, plus
   `steps_for(elapsed, acc, dt) -> (n_steps, new_acc, alpha)` as a pure function so it can be unit-tested.

## Done when
- `tests/app/test_loop.py::test_steps_for_accumulates_fixed_steps` — 0.05 s at dt 1/60 → 3 steps, alpha in [0,1)
- `tests/app/test_loop.py::test_steps_for_clamps_runaway_frames` — 2 s → at most 15 steps
- `tests/app/test_input.py::test_write_row_maps_bindings_to_move_vector` — fake key array → normalised `move`
- `tests/app/test_window.py::test_window_creates_gl46_context` — hidden window reports 4.6 (gpu)
- `uv run ruff check . && uv run pytest -q` pass headless

## Out of scope
- Rendering (0012), camera controls, gamepad.

## Notes
- `Input.write_row` must be testable without GLFW: take the arrays as attributes it fills, and let the test set them.
- Wall-clock (`time.perf_counter`) only in `loop.run`; `steps_for` is pure.
