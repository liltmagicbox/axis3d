---
kind: spec
brief_ko: 공개 API 예산 장부. 패키지별 이름 목록과 상한. 이름 추가는 ADR + 이 파일 수정이 동시에 필요하다.
---
# Public API budget

A public name is any `def`, `class`, or constant without a leading underscore that a user or another package imports.
Cap for v1: **90 names**. Reviewer counts; architect edits. (ADR 0019)

| package | cap | names (v1 plan) |
|---|---|---|
| `axis3d` | 6 | `World`, `Table`, `run`, `snapshot`, `restore`, `DT` |
| `axis3d.conventions` | 8 | `DT`, `GRAVITY`, `WORLD_TO_VIEW`, `UP`, `FORWARD`, `RIGHT`, `QUAT_IDENTITY`, `COLUMNS` |
| `axis3d.linalg` | 14 | `quat_identity`, `quat_multiply`, `quat_from_axis_angle`, `quat_from_euler`, `quat_normalize`, `quat_rotate`, `quat_to_matrix`, `trs`, `look_at`, `perspective`, `orthographic`, `translate`, `scale`, `rotate` |
| `axis3d.ecs` | 5 | `Table`, `World`, `System`, `SYSTEMS`, `join` |
| `axis3d.layout` | 10 | `Struct`, `LayoutError`, `f32`, `i32`, `u32`, `vec2`, `vec4`, `mat4`, `STRUCTS`, `all_glsl` |
| `axis3d.sim` | 8 | `integrate`, `collide`, `resolve`, `bounds`, `expire`, `candidate_pairs`, `sphere_pairs`, `resolve_pairs` |
| `axis3d.gpu` | 10 | `Device`, `PipelineState`, `Buffer`, `Texture`, `Pipeline`, `ComputePipeline`, `RenderTarget`, `Unsupported`, `create_device`, `BACKENDS` |
| `axis3d.render` | 9 | `Meshes`, `Renderer`, `Camera`, `gather`, `preprocess`, `cube`, `sphere`, `grid`, `PIPELINES` |
| `axis3d.io` | 5 | `snapshot`, `restore`, `schema_hash`, `SnapshotSchemaError`, `export_glb` |
| `axis3d.net` | 6 | `Server`, `Client`, `encode`, `read_frames`, `Kind`, `DEFAULT_PORT` |
| `axis3d.app` | 6 | `Window`, `Input`, `run`, `bindings`, `Loop`, `DEFAULT_SIZE` |
| **total** | **87** | |

## Rules
- A name not in this table is private, even without an underscore, until an ADR adds it here.
- Re-exports (`axis3d.World` is `axis3d.ecs.World`) count once, in the package that defines them, plus the
  top-level re-export slot.
- Removing a name needs no ADR but needs a changelog line and a test update.
- Backend folders (`gpu/gl46/`, `gpu/gles31/`, `gpu/vulkan/`) expose nothing public; `create_device` is the door.
- Methods of the listed classes are bounded by `docs/rules/simplicity.md` P6 and by the spec that defines them.
