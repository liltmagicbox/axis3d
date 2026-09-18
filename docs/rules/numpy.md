---
kind: rule
brief_ko: 넘파이 작성법. (N,k) 모양 규약, 뷰/복사 명시, 인덱스 gather/scatter, 명시적 dtype, 순서 결정성, 오버플로.
---
# Rule: numpy usage

## Must
- N1 A column of N vectors is `(N, k)`: `x = pos[:, 0]`. Per-entity scalars are `(N,)`. Never `(k, N)`.
- N2 Docstrings say whether a function returns a view or a copy. `Table.col()` returns a view of live rows.
- N3 Gather with index arrays (`b.row_of(a.ids)`); scatter with `np.add.at` / `np.put`. Sort-based joins over hashing.
- N4 Masks are boolean arrays; `np.flatnonzero(mask)` when the indices or the count matter.
- N5 `dtype=np.float32` explicit in every `np.zeros / ones / empty / array`. `np.float32(0.5)` when a literal meets an array.
- N6 Reductions that must be deterministic use a fixed order (sort pairs first). `np.sum` on float32 is order-dependent.
- N7 Ranges: ids and rows `int32` (< 2^31), counts and byte sizes `int64`, time accumulators `float64`, state `float32`.

## Never
- N8 No `np.matrix`, `np.vectorize`, object dtype, or structured arrays in tables (structured dtypes only in `layout/`).
- N9 No in-place op on a view the caller may believe is a copy; state it or copy.
- N10 No implicit float64: `np.array([1, 2, 3])` is int64, `np.linspace` is float64. Always pass `dtype`.

## Check
- [ ] shapes `(N, k)`  - [ ] dtype explicit  - [ ] view/copy stated  - [ ] deterministic order where summed
