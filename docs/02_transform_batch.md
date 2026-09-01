# 02. 트랜스폼 배치 — 저장 구조와 연산

## 요지

**(N,4,4) float32 C-contiguous**로 저장한다.
(N,16)은 같은 메모리다: `reshape(N,16)`은 zero-copy(같은 주소, base 공유).
GPU 업로드(glBufferSubData)는 어느 모양이든 같은 바이트를 그대로 넘기면 되고, 변환 비용이란 것이 존재하지 않는다.
구조 선택은 순전히 연산 API 문제이고, matmul/einsum 배치 시맨틱을 그대로 쓰는 (N,4,4)가 답이다.

## 실측 (N=10만, float32, ms)

| 방식 | 시간 |
|---|---|
| `np.matmul` (N,4,4)@(N,4,4) | 6.0 |
| `einsum('nij,njk->nik')` optimize 없이 | 54.5 |
| `einsum(..., optimize=True)` | 5.6 |
| (N,16) 컬럼별 수동 산술 (strided) | 54.5 |
| (16,N) 전치 배열 수동 산술 | 5.2 |
| affine 분해 (3x3 R + t 따로) | 8.2 |
| 점 10만 개 변환 `einsum('nij,nj->ni')` | 2.9 |
| 점 10만 개 변환 matmul 방식 | 6.5 |

## 규칙

- 행렬 합성 = `np.matmul(A, B, out=O)`. 행렬×행렬은 matmul이 이긴다.
- 점 변환 = `np.einsum('nij,nj->ni', R, p)`. 행렬×점은 einsum이 2배 빠르다 — 승자가 반대다.
- einsum엔 **optimize=True 필수** (없으면 9배 느림). 단 이 순위는 numpy 버전 따라 뒤집혀온 역사가 있으니(1.x 시절엔 einsum 우세) 버전 바뀌면 재측정.
- affine 분해(3x3 R + t)는 이론상 flops가 적어도 커널 호출이 쪼개지는 비용이 더 커서 손해. 하지 않는다.
- float32/float64 속도 차이는 작지만(6.0 vs 6.8) 업로드가 절반이니 float32.
- (N,16)에서 컬럼별 산술은 stride 64B 접근이라 캐시가 깨져 9배 느리다. (16,N) 전치는 빠르지만 코드 16배 + 업로드 전 interleave 필요 — 의미 없음.

## BLAS가 없는 이유, 그리고 회수

4x4 소형 행렬 배치는 BLAS gemm 경로를 못 탄다(numpy 내부 gufunc 루프, 싱글코어, SIMD 미흡).
하지만 gemm의 이득은 큰 행렬에서 데이터를 O(n)번 재사용하는 캐시 블로킹인데, **4x4엔 재사용할 것이 없다**.
이 연산의 천장은 "메모리 대역폭 + SIMD"이고, 거긴 numba로 닿는다:

| | N=10만 | N=100만 |
|---|---|---|
| np.matmul | 3.5 ms | 37.8 ms |
| numba serial | 1.5 ms | 23.3 ms |
| **numba parallel 4코어** | **0.28 ms** | **2.85 ms** (~68 GB/s = 대역폭 한계) |

```python
from numba import njit, prange

@njit(parallel=True, fastmath=True, nogil=True, cache=True)
def compose(A, B, O):
    for n in prange(A.shape[0]):
        for i in range(4):
            for j in range(4):
                s = A[n, i, 0] * B[n, 0, j]
                for k in range(1, 4):
                    s += A[n, i, k] * B[n, k, j]
                O[n, i, j] = s
```

- `nogil=True`: 워커 스레드에서 돌려도 메인 스레드 지연 0.1~1.5ms (측정).
- `cache=True`: JIT 컴파일(첫 호출 ~1초)은 두 번째 실행부터 사라진다.
- `fastmath`: IEEE 연산 순서 완화 — 게임 트랜스폼엔 무해.
- 이 지점부터 병목은 진짜 대역폭이다. 다음 최적화는 코어가 아니라 **바이트**:
  생성+합성+점변환을 numba 루프 하나로 융합해 중간 배열의 RAM 왕복을 없앤다. numpy로는 불가능한 최적화.
