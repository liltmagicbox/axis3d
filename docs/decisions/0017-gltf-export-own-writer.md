---
kind: decision
id: 0017
title: Scene export is glTF 2.0 .glb written by our own ~150-line writer; no import in v1
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: yes — the writer is one module
brief_ko: 씬 내보내기는 glTF 2.0 .glb를 자체 작성기(json+struct)로 만든다. 의존성 없음, 가져오기는 v1에서 제외.
---
# 0017 — Own glTF writer

## Question
The user wants glTF export as the road to Godot. Library or own code?

## Decision
`io/gltf.py: export_glb(world, meshes, path)` builds the JSON and the binary chunk with `json` and `struct`.
Nodes come from `renderables ⋈ bodies`, meshes from the registry, materials from the `color` column
(`docs/spec/gltf.md`). Import, textures, skins, animation are out.

## Options
1. `pygltflib` — correct and complete, but a dependency for ~150 lines of our own.
2. `trimesh` — heavy, pulls many transitive packages.
3. Own writer (chosen).

## Why
glTF's binary container is simple; writing it teaches the format and keeps ADR 0002's dependency list at three.

## Assumptions (check me)
- Flat node lists are enough; hierarchy arrives with a `parent` column (v2).
- Godot 4 and Blender import `.glb` with float `COLOR_0` accessors correctly (they do, per the spec).
- Vertex colours instead of textures match the user's stated taste ("paint to vertex, no photo-realism",
  `axis3d/test_renderer.py` notes).

## Consequences
- The axis conversion constant of ADR 0005 is applied here; a test checks two cubes land where expected.
- A `.glb` validator (`gltf-validator`) is a manual check, not a CI dependency.
