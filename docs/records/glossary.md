---
kind: record
brief_ko: 용어집. 이 저장소에서 쓰는 단어의 뜻 한 줄씩. 새 용어는 기록자가 추가한다.
---
# Glossary

| term | meaning here |
|---|---|
| table | one `Table`: SoA numpy columns plus an `ids` column; a row is one entity's component |
| column | one numpy array of a table, shape `(N, *shape)`; `pos[:, 2]` is z |
| entity / id | an `int32` number from `world.spawn`; it has components wherever a table holds its id |
| row | the position of an id inside one table; changes on `remove`; never stored across a step |
| system | a function `f(world, dt)` that reads/writes columns; listed in `ecs/schedule.SYSTEMS` |
| world | the one object holding tables, `tick`, `rng`, `inputs`, and pending removals |
| tick | the integer count of fixed steps since the last restore |
| snapshot | `bytes` of the world (header + raw columns); also save, network message, and replay base |
| join | rows of two tables for ids present in both; one gather and a mask |
| walk-through | a module a beginner can read top to bottom |
| HARD ZONE | a fenced module whose docstring says why it is hard and which ≤ 3 names to use it through |
| role | a job description for a sub-model (`docs/roles/`) |
| rule | an atomic must/never list with a reviewer checklist (`docs/rules/`) |
| spec | the current contract for a subsystem (`docs/spec/`) |
| variant | backend facts that can be swapped in a pack (`docs/variants/`) |
| decision / ADR | a small record of one choice with options, assumptions, and confidence (`docs/decisions/`) |
| pack | an ordered list of documents that `tools/pack.py` turns into one prompt |
| card | a task card: one unit of work a small model finishes from pack + card alone |
| ledger | an append-only table in `docs/records/` (assumptions, edge cases, benchmarks) |
| brief_ko | the one-line Korean summary in every document's frontmatter |
| DSA | Direct State Access: GL functions that edit objects by name without binding them |
| AZDO | "Approaching Zero Driver Overhead": persistent mapping, indirect multi-draw, few binds |
| MDI | multi-draw indirect: one call draws many meshes from a `DrawCommand[]` buffer |
| SSBO / UBO | shader storage / uniform buffer object; slots fixed in `docs/spec/shaders.md` |
| std430 | the buffer layout rules we generate from `layout.Struct` |
| reversed-Z | depth where near = 1 and far = 0 in a `[0, 1]` clip range; test `GREATER` |
| stream ring | a persistent-mapped buffer split into 3 per-frame slices guarded by fences |
| gather | the per-frame array pass that turns tables into `Frame`, `Instance`, `DrawCommand` rows |
| Struct | a Python declaration that yields a numpy dtype and a GLSL struct with identical bytes |
