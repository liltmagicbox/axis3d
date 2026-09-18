---
kind: spec
brief_ko: 앱. GLFW 창과 GL 4.6 컨텍스트, 누적기 기반 고정 스텝 루프, 입력을 테이블로, 키 바인딩 사전, 시작 시퀀스.
---
# App: window, loop, input

`src/axis3d/app/` (walk-through). The main path starts here. (ADR 0013)

## Window — `app/window.py`
```python
Window(width: int = 1280, height: int = 720, title: str = "axis3d", vsync: bool = True)
w.handle                      # glfw window pointer for the device
w.size() -> tuple[int, int]   # framebuffer size in pixels
w.should_close() -> bool
w.poll() -> None              # glfw.poll_events, then updates the inputs snapshot below
w.close() -> None
```
Creates a GL 4.6 core, forward-compatible context; debug context when `AXIS3D_DEBUG=1` (`docs/variants/gl46.md`).
`glfw.init()` is called inside `Window.__init__`, never at import.

## Input — `app/input.py`
```python
Input(window: Window)
i.keys: uint8 (512,)          # 1 while held; index = glfw key code
i.mouse_delta: float32 (2,)   # since last poll, pixels
i.buttons: uint8 (8,)
i.write_row(world: World, player: int = 0) -> None   # fills world.inputs: move (3,), look (2,), buttons (u32 bits)
bindings: dict[str, tuple[int, ...]] = {"forward": (glfw.KEY_W,), "back": (glfw.KEY_S,), ...}  # in app/bindings.py
```
Systems never read the keyboard; they read `world.inputs`. That is why replays and network clients need no special path.

## Loop — `app/loop.py`
```python
run(world: World, renderer: Renderer, camera: Camera, window: Window, on_step: Callable[[World], None] | None = None) -> None
```
```
acc = 0.0; last = time.perf_counter()
while not window.should_close():
    now = time.perf_counter(); acc += min(now - last, 0.25); last = now       # clamp: no spiral of death
    window.poll(); input.write_row(world)
    while acc >= world.dt:  world.step(); acc -= world.dt; if on_step: on_step(world)
    alpha = acc / world.dt
    renderer.draw(world, camera, alpha, *window.size())
```
Max 15 steps per frame (0.25 s / DT). Wall-clock is read here and nowhere else.

## Startup sequence (`axis3d.run`, the one public entry point)
1. `Window()` → 2. `gpu.create_device("gl46", window)` → 3. `Meshes(device)` + primitives → 4. `Renderer(device, meshes)`
→ 5. `World()` with `bodies`, `renderables`, `inputs` tables → 6. `Camera(...)` → 7. `loop.run(...)`.
`examples/` scripts show the sequence with 10 lines each (`examples/bouncing_spheres.py` first).

## Not in v1
Multiple windows, gamepad, text input, resizing the swapchain mid-frame (handled next frame), high-DPI scaling.
