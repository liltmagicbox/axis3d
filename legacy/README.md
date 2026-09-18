# legacy — the experiments that came before axis3d

These files are the 2022–2023 prototypes that the engine grew out of. They are kept for reference and are
excluded from linting and tests (`pyproject.toml`). Nothing in `src/axis3d/` imports them.

What survived into the engine:
- `axis.py`, `soldier_unit.py` (`UnitArray`): a table of numpy columns addressed by slices → `ecs/table.py`
  (ADR 0004; benchmark B-001 measured batch insert 10× faster than per-row append).
- `highspeed/nptest.py`: the O(N²) pairwise loop and its `(3, N)` vs `(N, 3)` timing → benchmark B-002 and
  assumption A-015; replaced by the uniform grid (ADR 0016).
- `test_socket.py`: fixed-length headers, reader threads, queues, and three bugs → `net/framing.py` (ADR 0015;
  edge cases E-003, E-004, E-007).
- `test_window.py`, `shader.py`, `vao.py`: GLFW window and GL 4.1 shaders → `app/window.py`, `gpu/gl46/` (ADR 0009).
- `viewmodel.py`, `test_renderer.py` notes ("there will be no materials but draw-types", "instanced draw!") →
  the instance SSBO + multi-draw renderer (ADR 0024).
