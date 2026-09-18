---
kind: spec
brief_ko: 목표치와 비목표. 플랫폼, 규모(1만 바디·10만 파티클), 프레임당 ms 예산, 시작 시간, 메모리, v1 비목표 목록.
---
# Targets

Numbers here are commitments for v1 and the yardstick for `profiler`. They are estimates until a benchmark row
confirms or refutes them (see `docs/records/benchmarks.md`). Change them only through an ADR.

## Platform
| item | target |
|---|---|
| OS | Windows 10+, Linux (X11/Wayland via GLFW). macOS is out (no GL 4.6). |
| GPU | any GL 4.6 core device: NVIDIA (2014+), AMD GCN+ (2017+ drivers), Intel Gen9+ |
| Python | ≥ 3.11 (CPython) |
| deps | numpy ≥ 2.0, PyOpenGL ≥ 3.1.7, glfw ≥ 2.7; nothing else at runtime |

## Scale (v1)
| quantity | target |
|---|---|
| dynamic bodies with collision | 10 000 at 60 Hz sim |
| rendered instances (MDI) | 100 000 |
| particles (GPU compute, no collision) | 100 000 |
| meshes in the registry | 256 |
| networked clients (LAN) | 8 |

## Per-frame CPU budget at 60 Hz (ms, 10 000 bodies)
| stage | budget |
|---|---|
| `integrate` | 0.5 |
| `collide + resolve` | 4.0 |
| `gather` (tables → SSBOs) | 2.0 |
| device submit (binds + 1 indirect draw per pipeline) | 1.0 |
| `snapshot` | 1.0 |
| total step + render | ≤ 10.0 (leaves headroom to 16.6) |

## Other
| item | target |
|---|---|
| startup to first frame | ≤ 2 s |
| resident memory (10k bodies, 100k instances) | ≤ 500 MB |
| test suite (CPU) | ≤ 30 s |
| public API | ≤ 90 names (`docs/spec/api_budget.md`) |

## Non-goals for v1
Skeletal animation, audio, UI toolkit, editor, physics joints and constraints, PBR image-based lighting, shadows,
textures beyond a colour, transparency sorting, WAN networking, macOS, mobile.
