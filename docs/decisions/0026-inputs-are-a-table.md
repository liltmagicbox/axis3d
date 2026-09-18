---
kind: decision
id: 0026
title: Player input is a table inside World, written once per frame by the app and read by systems
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: yes — one table and one write path
brief_ko: 입력도 World 안의 테이블(플레이어당 한 행: move, look, buttons). 시스템은 키보드가 아니라 이 표를 읽으므로 리플레이·네트워크가 공짜다.
---
# 0026 — Inputs are a table

## Question
Where do keyboard and mouse go so that replays, network clients, and tests all drive the simulation the same way?

## Decision
`world.inputs` is a `Table` with columns `move (N,3) look (N,2) buttons (N,) uint32`, one row per player.
`app/input.py` writes row 0 from GLFW state once per frame; the network server writes rows from `INPUT` messages;
a replay writes rows from a recording. Systems read only the table (`docs/spec/app.md`, `spec/ecs.md`).

## Options
1. Systems poll GLFW — cannot replay, cannot run headless, cannot network.
2. An event queue of key presses — replays possible, but every system parses events; state is easier to reason about.
3. A table of the current input state (chosen) — snapshots, networks, and replays for free (ADR 0003).

## Why
It turns three features into one write path and makes `test_step_with_inputs` a five-line test.

## Assumptions (check me)
- Edge-triggered input (a key *press* rather than *held*) can be derived by systems from `buttons` and a
  `prev_buttons` column; if that proves clumsy, add a small event column by ADR.
- 8 players (rows) is enough for v1 (`spec/targets.md`).

## Consequences
- `Input.write_row(world, player)` is the only bridge between GLFW and simulation state.
- The `inputs` table is included in snapshots; a replay file is `snapshot + inputs rows per tick`.
