---
kind: spec
brief_ko: ECS 계약. Table(SoA 열 + id, swap-remove), World(테이블·tick·rng·inputs), 시스템 함수와 스케줄, 조인, 지연 삭제.
---
# ECS: tables, world, systems

Entity = an id. Component = a row in a table. System = a function. That is the whole model. (ADR 0004)

## Table — `src/axis3d/ecs/table.py` (walk-through)
```python
Table(name: str, columns: dict[str, tuple[tuple[int, ...], np.dtype]], capacity: int = 1024)
# columns example: {"pos": ((3,), np.float32), "mass": ((), np.float32), "mesh": ((), np.int32)}
t.n                       -> int                 # live rows
t.ids                     -> int32 (n,) view     # entity ids of live rows, dense in [0, n)
t.col("pos")              -> float32 (n, 3) view # live rows of one column
t.insert(ids, **values)   -> None                # ids int32 (k,); values broadcast to (k, *shape); missing → zeros
t.remove(ids)             -> None                # swap-remove; row order changes; unknown ids are ignored
t.row_of(ids)             -> int32 (k,)          # row per id, -1 when the id is not in this table
t.has(ids)                -> bool (k,)
```
Storage: one preallocated array per column, shape `(capacity, *shape)`; `col()` returns `array[:n]`.
`_row_of_id` is an `int32` array indexed by id (grown on demand, `-1` = absent). Inserting an id twice raises `ValueError`.
Capacity doubles when full and never shrinks. Views from `col()` are invalidated by `insert` (growth) and `remove`;
fetch them at the top of a system and do not keep them across calls.

## World — `src/axis3d/ecs/world.py` (walk-through)
```python
World(seed: int = 0, dt: float = DT)
w.tables: dict[str, Table]   w.tick: int   w.dt: float   w.rng: np.random.Generator   w.inputs: Table
w.add_table(name, columns, capacity=1024) -> Table
w.spawn(count) -> int32 (count,)     # fresh ids; you insert them into tables
w.despawn(ids) -> None               # queued; removed from every table at the end of the current step
w.step() -> None                     # runs schedule.SYSTEMS in order, applies removals, tick += 1
```
`w.inputs` is a table with columns `move (N,3) look (N,2) buttons (N,) uint32`, one row per player, so inputs
snapshot, network, and replay like everything else.

## Systems and schedule — `src/axis3d/ecs/schedule.py` (walk-through)
```python
System = Callable[[World, float], None]
SYSTEMS: list[System] = [integrate, collide, resolve, bounds, expire]   # imported from axis3d.sim
```
A system reads and writes columns of tables it names by string, draws randomness from `world.rng`, and removes
through `world.despawn`. It never does I/O, never allocates per-entity objects, never stores row indices.

## Join — `src/axis3d/ecs/query.py` (walk-through)
```python
join(a: Table, b: Table) -> tuple[int32 (m,), int32 (m,)]   # rows in a and in b for ids present in both
```
Implementation is four lines: `rows_b = b.row_of(a.ids); keep = rows_b >= 0; return np.flatnonzero(keep), rows_b[keep]`.

## Lifecycle rules
- Insert is immediate. Removal inside a step is deferred (`world.despawn`) so no system sees its own holes.
- Direct `table.remove` is allowed only outside `step()`: setup, tests, network apply.
- Every function accepts `n == 0` and `k == 0` inputs.

## Not in v1
Archetypes, generation-tagged ids, parallel systems, change tracking, hierarchies (a `parent` column is just a column).
