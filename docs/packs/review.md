---
kind: pack
brief_ko: 규칙 검사관용 묶음. 규칙 파일 전부 + API 예산. 변경분과 카드는 프롬프트로 전달.
---
# Pack: review

For `reviewer`. Target ≤ 6k tokens plus the diff.

## Load
1. `AGENTS.md`
2. `docs/roles/reviewer.md`
3. `docs/rules/agent_conduct.md`
4. `docs/rules/style.md`
5. `docs/rules/simplicity.md`
6. `docs/rules/education.md`
7. `docs/rules/testing.md`
8. `docs/rules/numpy.md`
9. `docs/rules/performance.md`
10. `docs/rules/documentation.md`
11. `docs/rules/git.md`
12. `docs/spec/api_budget.md`
13. `docs/templates/report.md`
Then the task card and the diff (or file list).

## Swap points
- GPU code in the diff → add `docs/rules/gpu_layout.md` and `docs/variants/gl46.md` (or the active variant).
