---
kind: decision
id: 0008
title: Rotations are unit quaternions stored (x, y, z, w) in glTF order; Euler angles are input-only
status: accepted
date: 2026-09-18
decided_by: ai
confidence: high
reversible: yes — a helper and a docstring
brief_ko: 회전은 (x,y,z,w) 순서의 단위 쿼터니언(glTF·Unity 순서). 오일러각은 입력 변환용으로만 쓴다.
---
# 0008 — Quaternion storage order

## Question
`(w, x, y, z)` (Blender, most textbooks) or `(x, y, z, w)` (glTF, Unity, DirectXMath)?

## Decision
`(x, y, z, w)`; identity `(0, 0, 0, 1)`; column `rot (N, 4) float32`. `linalg/quaternion.py` provides
`quat_identity, quat_multiply, quat_from_axis_angle, quat_from_euler(roll, pitch, yaw), quat_normalize,
quat_rotate(q, v), quat_to_matrix(q) -> (N, 3, 3)`, all vectorised over `(N, 4)`.

## Options
1. `(w, x, y, z)` — matches textbooks and Blender's Python API; needs a swap at every glTF/Godot boundary.
2. `(x, y, z, w)` (chosen) — bytes go into glTF and Godot unchanged.

## Why
The export path (ADR 0017) and the Godot path (ADR 0022) are the places where a silent order bug would hide longest.
Choosing their order removes the swap and the bug class.

## Assumptions (check me)
- Users who read textbooks will accept `w` last if the docstring shows it in the first line. The `rot` column's
  docstring and `conventions.py` both state the order.
- Euler input order roll (X), pitch (Y), yaw (Z), applied yaw·pitch·roll, is what the user's earlier notes call
  "turn on drill, head up, turn to enemy" (`new3dkatsu/code/matrix.py`).

## Consequences
- `quat_to_matrix` is what `trs()` uses; there is no rotation-matrix column anywhere.
- Normalisation happens at input (`quat_from_*`) and after integration of angular velocity (v2), not per frame.
