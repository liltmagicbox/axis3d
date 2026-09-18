---
kind: spec
brief_ko: 패키지 트리. 모듈별 한 줄 설명, 구역(walk/HARD), 상태(planned/done). 구현 카드가 파일 경로를 여기서 복사한다.
---
# Module map

Zone: `walk` = walk-through, readable by a beginner; `HARD` = fenced, documented at the top, used through ≤ 3 names.
Status moves from `planned` to `done` by the scribe when the card closes. (ADR 0001, 0018)

```
src/axis3d/
  __init__.py            walk   done     public re-exports and __version__
  conventions.py         walk   planned  DT, GRAVITY, WORLD_TO_VIEW, axis constants, COLUMNS (task 0002)
  linalg/
    quaternion.py        walk   planned  quat_* functions on (N,4) float32 arrays (0002)
    transform.py         walk   planned  trs, translate, scale, rotate, look_at → (4,4) / (N,4,4) (0002)
    projection.py        walk   planned  perspective (reversed-Z, [0,1]), orthographic (0002)
  ecs/
    table.py             walk   planned  Table: SoA columns + ids + row_of (0003)
    world.py             walk   planned  World: tables, tick, rng, inputs, spawn/despawn/step (0004)
    schedule.py          walk   planned  SYSTEMS list and the step order (0004)
    query.py             walk   planned  join(a, b) (0004)
  layout/
    struct.py            HARD   planned  Struct → dtype + GLSL, std430 rules, LayoutError (0005)
    structs.py           walk   planned  Frame, Instance, MeshInfo, DrawCommand declarations (0005)
  sim/
    integrate.py         walk   planned  semi-implicit Euler, prev_pos (0007)
    lifetime.py          walk   planned  ttl countdown → despawn (0007)
    bounds.py            walk   planned  world box reflection (0007)
    collide/
      grid.py            HARD   planned  candidate_pairs via uniform grid hashing (0013)
      narrow.py          walk   planned  sphere_pairs (0014)
      resolve.py         walk   planned  positional correction + impulses (0014)
  gpu/
    device.py            walk   planned  Device Protocol, PipelineState, handles, Unsupported (0008)
    gl46/
      device.py          HARD   planned  GL 4.6 DSA implementation of Device (0008, 0009)
      debug.py           walk   planned  KHR_debug callback, once-per-id messages (0009)
    gles31/              —      variant  docs/variants/gles31.md (0021)
    vulkan/              —      variant  docs/variants/vulkan.md
  render/
    meshes.py            walk   planned  single VBO/IBO registry + MeshInfo SSBO (0011)
    primitives.py        walk   planned  cube, sphere, grid generators (0011)
    gather.py            walk   planned  tables → Frame, Instances, DrawCommands (0011)
    camera.py            walk   planned  view/proj matrices with WORLD_TO_VIEW (0012)
    renderer.py          walk   planned  pipelines, one pass, one indirect draw (0012)
    shaders/
      preprocess.py      walk   planned  #include, version header, #line, gen/structs.glsl (0009)
      mesh.vert unlit.frag lambert.frag line.vert integrate.comp   planned (0012, later)
  io/
    snapshot.py          walk   planned  snapshot/restore/schema_hash (0006)
    gltf.py              walk   planned  export_glb (0016)
  net/
    framing.py           walk   planned  encode/read_frames (0015)
    server.py            walk   planned  Server (0015)
    client.py            walk   planned  Client (0015)
  app/
    window.py            walk   planned  GLFW window + GL 4.6 context (0010)
    input.py             walk   planned  Input → world.inputs row (0010)
    bindings.py          walk   planned  key names → glfw codes (0010)
    loop.py              walk   planned  fixed-step accumulator loop (0010)
examples/                walk   planned  bouncing_spheres.py, snapshot_replay.py, lan_sync.py
bench/                   —      planned  bench_table.py, bench_step.py, bench_collide.py, bench_gather.py (0017)
tests/                   —      mirror   one test file per module above; tests/gpu/ holds the device contract
```
