---
kind: spec
brief_ko: 렌더러. 메시 레지스트리(단일 VBO/IBO), gather(테이블→인스턴스 SSBO와 MDI 명령, 벡터화), 한 패스 한 indirect draw, 카메라.
---
# Renderer

`src/axis3d/render/` turns tables into one multi-draw per pipeline. All walk-through. (ADR 0024)

## Meshes — `render/meshes.py`
```python
Meshes(device: Device)                 # owns ONE vertex buffer, ONE index buffer, and the MeshInfo SSBO
m.add(vertices: (V, 12) float32, indices: (I,) uint32) -> int      # appends; returns the mesh id
m.info -> MeshInfo structured array    # first_index, index_count, base_vertex per mesh
m.upload() -> None                     # (re)writes the static buffers after adds; never inside the frame loop
```
Vertex row = `pos(3) normal(3) uv(2) color(4)` = 12 floats (`docs/spec/shaders.md`). Primitive generators in
`render/primitives.py`: `cube()`, `sphere(rings, slices)`, `grid(size, step)`, each returning `(vertices, indices)`.

## Gather — `render/gather.py`
```python
gather(world: World, meshes: Meshes, alpha: float, frame_out, instances_out, commands_out) -> int   # draw count
```
The three `*_out` arguments are the mapped stream slices (structured views with the `Frame`, `Instance`,
`DrawCommand` dtypes). Steps, all array operations, no per-instance loop:
1. `rows_b, rows_r = join(world.tables["bodies"], world.tables["renderables"])`.
2. `p = prev_pos[rows_b] + (pos[rows_b] - prev_pos[rows_b]) * alpha`.
3. `model = linalg.transform.trs(p, rot[rows_b], scale[rows_b])` → `(m, 4, 4)`.
4. `order = np.argsort(mesh[rows_r], kind="stable")`; write `Instance` rows in that order.
5. `counts = np.bincount(mesh[rows_r], minlength=len(meshes.info))`; for meshes with `counts > 0` write a
   `DrawCommand`: `count = index_count`, `instance_count = counts`, `first_index`, `base_vertex`,
   `base_instance = cumulative start`. Return the number of commands.
6. Write `Frame`: `view`, `proj`, `view_proj`, `time = (t, dt, alpha, 0)`, `camera_pos`.

## Renderer — `render/renderer.py`
```python
Renderer(device: Device, meshes: Meshes)
r.pipelines: dict[str, Pipeline]       # "unlit", "lambert", "lines" built from docs/spec/shaders.md
r.draw(world: World, camera: Camera, alpha: float, width: int, height: int) -> None
```
```
device.begin_frame()
n = gather(world, meshes, alpha, device.map(frame_buf), device.map(instance_buf), device.map(command_buf))
device.begin_pass(None, clear_color=(0.05, 0.05, 0.08, 1.0), clear_depth=0.0)
device.bind_pipeline(r.pipelines["lambert"])
device.bind_buffer(0, frame_buf); bind_buffer(1, instance_buf); bind_buffer(2, meshes.info_buf); bind_buffer(3, command_buf)
device.bind_geometry(meshes.vertex_buf, meshes.index_buf)
device.draw_indirect(command_buf, count=n, stride=DrawCommand.size)
device.end_pass(); device.end_frame()
```
One pass, one pipeline per material family, one indirect draw each. Debug lines use the `lines` pipeline
with a second `draw_indirect` fed from a `lines` table (planned).

## Camera — `render/camera.py`
```python
Camera(pos: (3,), target: (3,), up=(0.0, 0.0, 1.0), fov_y=math.radians(60), near=0.05, far=None)
c.view_matrix() -> (4, 4) float32      # look-at in world Z-up, then WORLD_TO_VIEW (conventions.md)
c.proj_matrix(aspect: float) -> (4, 4) float32   # reversed-Z, [0, 1] clip
```
Orbit and fly controls live in `app/`, not here.

## Not in v1
Frustum culling (planned as `cull.comp` writing DrawCommands), shadows, textures, transparency sorting, post-processing.
