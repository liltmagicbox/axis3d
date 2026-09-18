---
kind: decision
id: 0022
title: The Godot path is glTF export of scene data; behaviour is rewritten by hand, nothing in the engine targets Godot
status: accepted
date: 2026-09-18
decided_by: ai
confidence: medium
reversible: yes — no code depends on it
brief_ko: Godot 이식은 glTF로 씬(메시·변환·색)을 넘기는 방식. 시스템(동작)은 GDScript로 다시 쓴다. 엔진 코드는 Godot을 모른다.
---
# 0022 — Godot port path

## Question
The user wants to port to Godot "once stable" for distribution. What must the engine do now to make that cheap?

## Decision
Nothing Godot-specific in the engine. The port is: export `.glb` (ADR 0017) for meshes, transforms, colours; keep
scene *data* engine-agnostic (tables, mesh registry, names); accept that systems are rewritten in GDScript.
Y-up conversion is already in the exporter (ADR 0005). Quaternion order already matches Godot (ADR 0008).

## Options
1. Generate GDScript from systems — a compiler project; out of scope.
2. Embed Python in Godot — fragile toolchains, not a distribution story.
3. Data through glTF, behaviour by hand (chosen).

## Why
Godot imports glTF well and the user's aim for Godot is distribution, not engine reuse.

## Assumptions (check me)
- "Stable" means the simulation rules are settled, so rewriting them once in GDScript is acceptable.
- A replay (`snapshot` + `inputs`) is a useful thing to bring to Godot as baked animation later (v2 idea: export
  per-tick transforms as glTF animation channels).

## Consequences
- Names of entities and meshes are kept human-readable (`names` argument of `export_glb`).
- No feature is added to the engine "because Godot has it".
