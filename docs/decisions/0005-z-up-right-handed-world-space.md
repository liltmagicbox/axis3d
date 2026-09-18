---
kind: decision
id: 0005
title: World space is Z-up right-handed; the Y-up conversion happens once, in the camera and the glTF exporter
status: accepted
date: 2026-09-18
decided_by: ai
confidence: medium
reversible: yes — one constant (WORLD_TO_VIEW) and two call sites
brief_ko: 월드는 Z-up 오른손(X 오른쪽, Y 앞, Z 위). GL/glTF의 Y-up 변환은 카메라 뷰 행렬과 glTF 내보내기 두 곳에서만 한다.
---
# 0005 — Z-up world space

## Question
GL clip space, glTF, and Godot are Y-up; math textbooks and Blender are Z-up. The user asked which to use and noted
that a simulation for math education leans Z-up, while GL leans Y-up.

## Decision
World and simulation: right-handed, +X right, +Y forward, +Z up. View space stays GL's Y-up, −Z forward.
`conventions.WORLD_TO_VIEW` (rotation −90° about X) is the basis `Camera.view_matrix()` reaches through `look_at`
with `up = +Z`, and the constant `io/gltf.py` applies. Shaders receive world-space Z-up positions and see the basis
change only through `view_proj`.

## Options
1. Y-up everywhere: no conversion, but every physics formula and every "height" reads as `y`, which teaches the
   GL habit rather than the math one.
2. Configurable up axis: two code paths to test, and a beginner cannot tell which one is active.
3. Z-up world with one conversion (chosen).

## Why
The user's stated purpose includes math education; Z-up matches paper, Blender, and robotics. The cost is one
constant matrix in two places, which is also exactly the seam that "separating later" needs.

## Assumptions (check me)
- The user's "maybe Z-up" leaning is a preference, not a hard requirement; if they want Y-up, flip the constant to
  identity and update this ADR's successor. Nothing else changes.
- Lighting directions and gravity are expressed in world Z-up in shaders and systems; nobody writes a shader that
  assumes view-space up.
- Forward is +Y (Blender), not +X (ROS). Camera "look at" uses `up = (0, 0, 1)`.

## Consequences
- `GRAVITY = (0, 0, -9.81)`. Height is `pos[:, 2]`.
- glTF export rotates translations, rotations, and vertex positions by the same constant; Godot imports Y-up unchanged.
