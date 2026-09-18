---
kind: record
brief_ko: 가정 장부. AI가 지시 없이 내린 판단을 한 줄씩 남긴다. 사람이 훑어보고 숨은 가정·편향을 찾아 ADR로 올리는 곳.
---
# Assumptions ledger (append-only)

One row per judgement call that was not spelled out by a human. Ids `A-NNN`. Status `open | confirmed | rejected → ADR NNNN`.
A rejected row is never deleted; it gets a status and a pointer.

| id | date | where | assumption | how to verify | status |
|---|---|---|---|---|---|
| A-001 | 2026-09-18 | ADR 0001 | The new engine belongs in `axis3d`, not a new repo or `new3dkatsu`. | Ask the user. | open |
| A-002 | 2026-09-18 | ADR 0001 | Legacy scripts may stay at the repo root, excluded from lint/tests, until a human approves task 0020. | Task 0020. | confirmed 2026-09-18 (user) |
| A-003 | 2026-09-18 | module_map | The math package is named `linalg` (not `math`) to avoid shadowing the stdlib for beginners. | Teacher review. | open |
| A-004 | 2026-09-18 | ADR 0002 | Python floor is 3.11, not 3.12; nothing in the plan needs 3.12. | Confirm the user's interpreter. | open |
| A-005 | 2026-09-18 | ADR 0025 | 4-space indentation replaces the tabs used in the earlier `axis3d` files. | Ask the user. | confirmed 2026-09-18 (user) |
| A-006 | 2026-09-18 | ADR 0005 | "maybe Z-up for math education" is a real preference; Z-up is chosen. | Ask the user; flip one constant if not. | confirmed 2026-09-18 (user) |
| A-007 | 2026-09-18 | ADR 0005 | Forward is +Y (Blender), not +X (ROS). | Ask the user. | confirmed 2026-09-18 (user) |
| A-008 | 2026-09-18 | ADR 0013 | 60 Hz fixed step is the right default. | Bench 0017; user taste. | open |
| A-009 | 2026-09-18 | spec/targets | Every number in `targets.md` is an estimate. | Task 0017 replaces guesses with rows. | open |
| A-010 | 2026-09-18 | ADR 0015 | One snapshot per 3 ticks (20 Hz) is enough for LAN play. | Task 0015 round-trip test + feel. | open |
| A-011 | 2026-09-18 | docs/README | 8k tokens is the right ceiling for a small-model implementation prompt. | First cards' reports. | open |
| A-012 | 2026-09-18 | .claude/agents | Model sizes per role: haiku for implement/test/review/style/scribe, sonnet for the rest, opus for architect. | Compare card outcomes by model. | open |
| A-013 | 2026-09-18 | ADR 0025 | "docs in English" implies English-only code; the user's Korean inline notes move to records. | Ask the user. | confirmed 2026-09-18 (user) |
| A-014 | 2026-09-18 | ADR 0020 | Line budgets (role 70, rule 60, spec 140, ADR 50, pack 40, task 60) are the right sizes. | Adjust after the first sprint. | open |
| A-015 | 2026-09-18 | ADR 0004 | `(N, 3)` layout is fine because systems are vectorised; the user's `(3, N)` win (B-002) came from a per-row loop. | Task 0017 `bench_step.py` both layouts. | open |
| A-016 | 2026-09-18 | ADR 0004 | Ids are never reused in a run; a growing `_row_of_id` array is acceptable below ~10 M spawns. | Edge hunt 0018. | open |
| A-017 | 2026-09-18 | ADR 0012 | A strided `[:, :3]` write into persistent-mapped memory is not pathologically slow. | Task 0017 `bench_gather.py`. | open |
| A-018 | 2026-09-18 | ADR 0019 | 90 public names is enough for a v1 demo. | Count after task 0016. | open |
| A-019 | 2026-09-18 | ADR 0001 | `new3dkatsu` receives no changes in this work. | Ask the user. | open |
| A-020 | 2026-09-18 | .github | A minimal CI workflow was added without being asked; it only runs the listed checks. | Ask the user; delete if unwanted. | confirmed 2026-09-18 (user) |
| A-021 | 2026-09-18 | ADR 0009 | macOS is out of scope (no GL 4.6). | Ask the user. | open |
| A-022 | 2026-09-18 | ADR 0002 | Three runtime dependencies; `numba` deferred until a benchmark fails. | Task 0017. | open |
| A-023 | 2026-09-18 | ADR 0017 | Vertex colours, not textures, match the user's taste ("paint to vertex"). | Ask the user. | open |
| A-024 | 2026-09-18 | ADR 0026 | 8 players (input rows) is enough for v1. | Ask the user. | open |
| A-025 | 2026-09-18 | spec/app | An `examples/` folder holds the startup sequence scripts (not in the user's list). | Ask the user. | open |
| A-026 | 2026-09-18 | roles | Eleven roles (the user named ~6) is the right granularity; teacher, planner, porter, architect were added. | Merge roles that never get used. | open |
| A-027 | 2026-09-18 | ADR 0016 | Spheres-only collision is an acceptable v1 (AABB, capsule later). | Ask the user. | open |
| A-028 | 2026-09-18 | spec/network | TCP before UDP, threads before asyncio, mirrors the user's working prototype. | Task 0015. | open |
| A-029 | 2026-09-18 | sprint | "계속 진행" means: run the first sprint with sub-models by role (implementer → reviewer → scribe), committing one card per commit on the designated branch instead of `task/NNNN` branches (git rule V3), because the user's branch instruction takes precedence. | User reads `docs/tasks/done/` outcomes. | open |
| A-030 | 2026-09-18 | board | Card 0008 does not depend on 0005 (the device interface uses no Struct); its `blocked_by` was corrected to 0001 so GPU work can start in parallel with the core cards. | Card 0008 report. | open |
