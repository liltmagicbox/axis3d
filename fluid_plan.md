# 유체 시뮬레이션 설계 노트

- 대상: axis3d, PyOpenGL + compute shader (GL 4.3+)
- 목표: 코드를 읽고 배울 수 있는, 재사용 가능한 단위 구조. numpy 로 검증/대체 가능하고 compute 로 가속되는 구조.
- 시작 스케일: 1m 큐브. 이후 10m 이하, 관심영역은 3mm 까지.
- 문서 안의 numpy 코드와 수치는 실제로 실행해서 확인한 것 (2026-09, 이 환경 CPU 기준).

---

## 0. 결론 먼저

**경로: 입자(PBF) → 격자(MAC 스모크) → (선택) FLIP 하이브리드.**

- "작은 공을 마구 시뮬레이션" 이 걱정하는 충돌 비용은 **균일 격자 + counting sort** 로 O(N) 이 된다. 이 격자가 곧 "격자 방식" 의 격자다. 둘은 다른 세계가 아니라, *셀 안에 무엇이 사는가* 만 다르다.
- 입자 경로가 compute 의 기초(SSBO, atomics, 이웃 격자, barrier)를 가장 빨리 가르친다. PBF 는 "딱딱하게 튕기는 공" 대신 "밀도가 ρ0 가 되도록 위치를 밀어내는 공" 이라 큰 dt 에서도 안정적이고 물처럼 보인다.
- 격자(벡터장) 방식은 연기/가스에 맞고, 압력 투영(Poisson) 이 핵심이다. 물의 자유표면까지 하려면 입자와 결합(FLIP) 하게 되므로 입자를 먼저 한다.

**핵심 단위 4개.** 이것만 이해하면 나머지는 조합이다.

| 단위 | 역할 | 한 줄 |
|---|---|---|
| `Table` | N행 × 이름있는 속성. 행 = 입자 하나 또는 셀 하나 | numpy 가 소유, GPU 는 속성별 SSBO 미러. **같은 바이트** |
| `Grid` | origin, h, dims 와 인덱스 수학 | numpy 함수와 GLSL 문자열이 **같은 공식** |
| `Pass` | 한 번의 계산. numpy 쌍둥이 + `.comp` | 같은 이름의 배열, 같은 파라미터 |
| `step()` | pass 를 순서대로 부르는 평범한 함수 | 스케줄러/그래프 없음 |

**레이아웃: (N, attrs).** 속성별 배열, 벡터는 `(N,4) float32`, 인덱스는 `uint32`. 이유는 3장.

**검증: 모든 pass 는 numpy 버전이 먼저.** GPU 버전은 그것과 비교해서 통과해야 한다. GL 4.3 이 없으면 numpy 백엔드로 작게 돌아간다 (4장).

**스케일: 1m 큐브, 입자 간격 2cm (6만 개) 로 시작 → 1cm (50만 개).** 3mm 는 관심영역(ROI) 안에서만 (5장).

---

## 1. 세 갈래, 그리고 "작은 공 충돌 부담" 의 답

| 방식 | 셀에 사는 것 | 한 스텝 | 잘하는 것 | 비용 / 난이도 |
|---|---|---|---|---|
| 격자 (Euler: Stam, MAC) | 속도 벡터장 u, 압력 p, 연기 밀도 | 이류 → 외력 → 압력 투영 | 연기, 가스, 공간을 채우는 흐름. 큰 dt 에도 안정 | 셀 수에 비례. 물 표면(자유표면)은 따로 추적해야 함 |
| 입자 SPH / PBF | 이웃 탐색용 입자 목록 | 이웃 탐색 → 밀도 → 압력(제약) → 위치 보정 | 물, 튀김. 자유표면이 공짜 | 이웃 탐색이 비용의 전부. 표면 렌더링은 별도 |
| 작은 공 DEM | 같음 | 이웃 탐색 → 스프링/마찰 충돌력 | 모래, 알갱이 | 딱딱한 스프링 → 아주 작은 dt. 물처럼 안 보임 |
| 하이브리드 FLIP/PIC | 입자 + MAC 격자 둘 다 | P2G → 격자 투영 → G2P → 입자 이동 | 제작용 물 (Houdini 가 이것) | 위 둘을 다 알아야 함. 셋째 단계 |

**충돌 부담의 실제 숫자.**

- 전수 비교: N² . `highspeed/nptest.py` 에서 1000개 pairwise numpy 가 28ms 였다. 100만 개면 10⁶ 배.
- 격자: 셀 크기 = 상호작용 반경 h 로 잡으면, 한 입자는 주변 27셀만 본다. 셀당 ~8개면 후보 ~200개. 100만 입자 → 2×10⁸ 거리검사/스텝 → GPU 에서 수 ms.
- 즉 "작은 공" 은 가능하고, 그 방법이 곧 SPH/PBF 의 이웃 탐색이다. 힘 모델만 다르다 (스프링 = 모래, 밀도 제약 = 물).

**벡터장 느낌** 은 맞다. 격자 방식의 셀은 u(x) 를 샘플링한 것이고, FLIP 에서 입자는 그 벡터장을 읽고(G2P) 쓴다(P2G). 격자 인덱스 수학 하나가 네 방식 모두의 공통 기반이다.

---

## 2. 핵심 단위 구조

### 2.1 Table — `UnitArray` / `Axis` 의 후속

```python
import numpy as np

FLOAT = 'float32'
UINT = 'uint32'   # gpu index type. int64 is never uploaded.

def make_attr(n, spec):
	"spec: 1 -> (n,) float / 3,4 -> (n,4) float (vec4 padded) / 'u' -> (n,) uint"
	if spec == 'u':
		return np.zeros(n, dtype=UINT)
	if spec == 1:
		return np.zeros(n, dtype=FLOAT)
	if spec in (3,4):
		return np.zeros((n,4), dtype=FLOAT)
	raise ValueError(spec)

class Table:
	"""N rows x named attrs. a row = one particle, or one cell.
	numpy owns the data. gpu keeps a mirror (one ssbo per attr), same bytes.
	"""
	def __init__(self, schema, capacity):
		self.schema = dict(schema)          # {'pos':4, 'vel':4, 'lam':1, 'cell':'u'}
		self.capacity = capacity
		self.n = 0                          # active rows are [0, n)
		self.data = { k: make_attr(capacity, v) for k,v in self.schema.items() }
		self.gpu = {}                       # attr -> Buffer. filled by ComputeBackend.
	def __getattr__(self, key):
		"t.pos -> the array. only for keys in schema."
		try:
			return self.data[key]
		except KeyError:
			raise AttributeError(key)
	def append(self, n, **values):
		"rows [self.n, self.n+n). values broadcast into rows. returns the slice."
		s = slice(self.n, self.n+n)
		if s.stop > self.capacity:
			raise OverflowError(f'capacity {self.capacity}')
		for k,v in values.items():
			self.data[k][s] = v
		self.n = s.stop
		return s
```

규칙:

- capacity 는 고정. 유체는 입자를 하나씩 지우지 않는다. 필요하면 마지막 행과 swap 후 `n -= 1`.
- 벡터 속성은 항상 `(n,4)`. `.w` 는 여유칸 (질량, 반지름 등을 넣어도 되지만 스키마에 적어둘 것).
- ping-pong (읽는 배열에 쓰면 안 되는 pass) 은 `'p'`, `'p2'` 두 속성을 두고 **Python 에서 이름을 바꿔 부른다**. GPU 버퍼 교체 마법 없음.
- 업로드/다운로드는 속성 단위로 명시적. `table.gpu['pos'].upload(table.pos)`.

입자도 Table, 격자 셀도 Table. 셀 Table 은 `capacity = ncell (+1)` 이고, 행 인덱스가 곧 셀 인덱스다.

### 2.2 Grid — 셀 수학의 단일 진실

```python
class Grid:
	"cell spec. origin(m), h(m), dims=(nx,ny,nz). GLSL below uses the same formulas."
	def __init__(self, origin=(0,0,0), size=(1,1,1), h=0.02):
		self.origin = np.array(origin, dtype=FLOAT)
		self.h = float(h)
		self.dims = tuple( int(round(s/h)) for s in size )
	@property
	def ncell(self):
		nx,ny,nz = self.dims
		return nx*ny*nz
	def cell_coord(self, pos):
		"pos (n,4) -> (n,3) int, clamped into the grid."
		c = np.floor( (pos[:, :3] - self.origin)/self.h ).astype('int64')
		return np.clip(c, 0, np.array(self.dims)-1)
	def cell_index(self, coord):
		"(n,3) -> (n,)   x + nx*(y + ny*z)"
		nx,ny,nz = self.dims
		return coord[:,0] + nx*(coord[:,1] + ny*coord[:,2])
	def coord_of(self, index):
		"(n,) -> (n,3). inverse of cell_index."
		nx,ny,nz = self.dims
		x = index % nx
		y = (index//nx) % ny
		z = index//(nx*ny)
		return np.stack([x,y,z], axis=1)
	def uniforms(self):
		return {'origin':tuple(self.origin), 'h':self.h, 'dims':self.dims}

GRID_GLSL = """
uniform vec3 origin; uniform float h; uniform ivec3 dims;
ivec3 cell_coord(vec3 p){ return clamp(ivec3(floor((p-origin)/h)), ivec3(0), dims-1); }
uint  cell_index(ivec3 c){ return uint(c.x + dims.x*(c.y + dims.y*c.z)); }
ivec3 coord_of(uint i){ int x=int(i)%dims.x; int y=(int(i)/dims.x)%dims.y; int z=int(i)/(dims.x*dims.y); return ivec3(x,y,z); }
"""
```

- 테스트: `cell_index(coord_of(i)) == i` 전수, 그리고 GPU `cell` pass 결과 == numpy `cell_index`.
- Grid 는 값 객체다. 솔버 상태를 갖지 않는다. 그래서 나중에 ROI 용 두 번째 Grid 를 만드는 것이 자연스럽다 (5장).
- 입자 이웃 격자와 Euler 격자가 **같은 클래스** 를 쓴다. 이웃 격자는 셀 Table 에 `count/start/sorted_idx` 를, Euler 격자는 `u/p/div/smoke` 를 얹을 뿐이다.

### 2.3 Pass — numpy 쌍둥이 + `.comp`

한 pass 는 (1) 이름, (2) 쓰는 배열 목록(바인딩 순서), (3) numpy 함수, (4) GLSL 본문. 예: PBF 의 predict.

```python
def predict_np(pos, vel, ppred, n, dt, g):
	"vel += g dt ;  ppred = pos + vel dt.   arrays are the full (capacity, 4); use [:n]."
	vel[:n, :3] += np.array(g, dtype=FLOAT)*dt
	ppred[:n, :3] = pos[:n, :3] + vel[:n, :3]*dt

PREDICT_GLSL = """
uniform float dt; uniform vec3 g;
void main(){
	uint i = gl_GlobalInvocationID.x; if (i >= n) return;
	vel[i].xyz += g*dt;
	ppred[i].xyz = pos[i].xyz + vel[i].xyz*dt;
}
"""

predict = Pass('predict', predict_np, PREDICT_GLSL,
	buffers=[('ps','pos'), ('ps','vel'), ('ps','ppred')],   # binding 0,1,2. names must be unique in a pass.
	outputs=['vel','ppred'])                               # what check_pass compares
```

GLSL 헤더는 Table 스키마에서 생성한다 (버퍼 선언을 손으로 쓰다 틀리는 것이 GPU 버그의 1순위라서). 생성 결과는 `print(pass.full_source())` 로 언제든 읽을 수 있고, 아래가 전부다:

```glsl
#version 430
layout(local_size_x = 256) in;
layout(std430, binding = 0) buffer B_pos   { vec4 pos[];   };
layout(std430, binding = 1) buffer B_vel   { vec4 vel[];   };
layout(std430, binding = 2) buffer B_ppred { vec4 ppred[]; };
uniform uint n;
// + GRID_GLSL, KERNEL_GLSL if the pass asks for them
// + your body
```

uniform 은 본문에 직접 적는다 (명시적). Python 은 값의 타입으로 `glUniform1f/1ui/3f/3i` 를 고른다. `Grid` 객체를 파라미터로 주면 `grid.uniforms()` 가 펼쳐진다.

```python
class NumpyBackend:
	def __init__(self, tables):
		self.tables = tables                 # {'ps': Table, 'cells': Table}
	def run(self, p, count, **params):
		arrays = { attr: self.tables[t].data[attr] for t,attr in p.buffers }
		p.np(n=count, **arrays, **params)

class ComputeBackend:
	def __init__(self, tables):
		self.tables = tables
		self.programs = {}
		for t in tables.values():
			for attr, arr in t.data.items():
				t.gpu[attr] = Buffer(arr)    # one ssbo per attr
	def run(self, p, count, **params):
		prog = self.programs.get(p.name) or self._compile(p)   # header(schema) + snippets + body
		for b,(t,attr) in enumerate(p.buffers):
			self.tables[t].gpu[attr].bind_base(b)
		prog.bind()
		prog.set_uint('n', count)
		prog.set_uniforms(params)            # by python type. Grid -> grid.uniforms()
		prog.dispatch(count)                 # groups = ceil(count/256)
		glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
```

`axis.py` 의 "함수의 type hint 로 어떤 속성이 필요한지 선언한다" 는 아이디어가 `Pass.buffers` 로 명시화된 것이다.

### 2.4 step() 은 그냥 순서 나열

```python
class PBF:
	def step(self, dt):
		run = self.backend.run
		ps, n = self.ps, self.ps.n
		run(predict, n, dt=dt, g=self.g)
		self.neighbor.build(ps, 'ppred')                 # cell -> count -> scan -> scatter
		for _ in range(self.iters):
			run(lam, n, grid=self.grid, h=self.h, mass=self.mass, rho0=self.rho0, eps=self.eps)
			run(dp, n, grid=self.grid, h=self.h, rho0=self.rho0, k_corr=0.1, dq=0.2*self.h)
			run(apply, n, lo=self.lo, hi=self.hi)
		run(velocity, n, dt=dt)
		run(xsph, n, grid=self.grid, h=self.h)           # writes dv
		run(finish, n, c=0.01)                            # vel += c dv ; pos = ppred
```

읽으면 알고리즘이 그대로 보인다. 새 방법은 pass 몇 개 + step 함수 하나다. 사용자 API (`PBF`, `Smoke`) 는 이 위의 50줄짜리 껍데기라서, 나중에 API 만 다시 짜도 pass 는 그대로 쓴다.

### 2.5 네 가지 통신 패턴

모든 pass 는 이 넷 중 하나다. 어느 패턴인지 알면 GPU 에서의 규칙(경쟁 조건, 결정성)이 정해진다.

| 패턴 | 예 | GPU | 규칙 |
|---|---|---|---|
| map (행별 독립) | predict, apply, Jacobi 한 회 | 스레드 = 행 | 읽는 배열에 쓰지 말 것 → ping-pong |
| scatter 입자 → 셀 | count, scatter, P2G | `atomicAdd` | 순서 비결정. 검증은 집합/허용오차. float atomic 은 core 에 없음 |
| gather 셀 → 입자 | 이웃 루프, G2P 삼선형 | 27셀 / 8꼭짓점 루프 | 읽기만. 결정적. 결과는 다른 배열에 쓴다 (`dp`, `dv`) |
| stencil 셀 ↔ 셀 | 발산, Jacobi, 기울기 | 이웃 6셀 읽기 | 경계 처리는 헬퍼 함수 하나(`P(q)`, `UX(q)`) 로 통일 |

---

## 3. 메모리 레이아웃 결정: (N, attrs)

"(N, attrs) 가 나을 것 같다" 는 직감이 맞다. 다만 **하나의 (N,K) 표가 아니라 속성별 배열** 로 한다.

std430 규칙 (SSBO 배열의 원소 간격):

| numpy | GLSL | stride | 비고 |
|---|---|---|---|
| `(n,)  float32` | `float a[]` | 4 | |
| `(n,)  uint32` | `uint a[]` | 4 | `int64` 는 절대 올리지 말 것 |
| `(n,4) float32` | `vec4 a[]` | 16 | 기본 벡터. `.w` 여유칸 |
| `(n,3) float32` | `vec3 a[]` | **16** | 바이트 불일치. 함정. 쓰지 말 것 |
| `(n,K) float32` | `float a[]`, `a[i*K+j]` | 4 | 되지만 이웃 gather 때 K 배 대역폭 낭비 |

속성별 `(n,4)` 를 고른 이유:

- 이웃 gather 는 `pos[j].xyz` 한 번 (16B 정렬 읽기). (attrs,N) 이면 x,y,z 세 번, (N,K) 면 64B 를 읽어 12B 를 쓴다.
- counting sort 재정렬이 행 복사 한 번.
- `uint` 인덱스와 `float` 을 섞을 수 있다. 하나의 float 표에서는 불가능.
- 속성 단위 업로드/다운로드/ping-pong 이 자연스럽다.
- GLSL 이 읽기 쉽다: `vel[i].xyz += g*dt`.
- 기존 `(3,N)` 이 빨랐던 `nptest.py` 의 실험은 입자마다 Python 루프를 도는 경우였다. 이 설계는 그 루프를 하지 않는다.

Buffer (PyOpenGL 3.1.10 시그니처 확인함):

```python
from OpenGL.GL import *

class Buffer:
	"one ssbo. mirrors one Table attr. same bytes. array must be C-contiguous."
	def __init__(self, nparr, usage=GL_DYNAMIC_COPY):
		self.id = glGenBuffers(1)
		self.nbytes = nparr.nbytes
		glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.id)
		glBufferData(GL_SHADER_STORAGE_BUFFER, nparr.nbytes, nparr, usage)
	def upload(self, nparr):
		glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.id)
		glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, nparr.nbytes, nparr)
	def download(self, out):
		"out: nparr of same shape/dtype, filled in place. returns it."
		glMemoryBarrier(GL_BUFFER_UPDATE_BARRIER_BIT)
		glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.id)
		glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, out.nbytes, out)
		return out
	def bind_base(self, binding):
		glBindBufferBase(GL_SHADER_STORAGE_BUFFER, binding, self.id)
```

그리기는 readback 없이 SSBO 를 vertex shader 에서 직접 읽는다. VBO 도 attribute 도 없고, 빈 VAO 하나만 바인딩한다:

```glsl
#version 430
layout(std430, binding = 0) buffer B_pos { vec4 pos[]; };
uniform mat4 ViewProjection;
void main(){
	gl_Position = ViewProjection * vec4(pos[gl_VertexID].xyz, 1.0);
	gl_PointSize = 3.0;
}
```

```python
ps.gpu['pos'].bind_base(0)
glBindVertexArray(empty_vao)
glDrawArrays(GL_POINTS, 0, ps.n)
```

---

## 4. numpy 검증 / fallback 구조

- 백엔드 두 개, pass 는 하나. `PBF(grid, ps, backend=NumpyBackend(tables))` 로 바꾸면 같은 `step()` 이 numpy 로 돈다.
- numpy 쪽의 이웃 계산은 **전수 비교 행렬** 로 쓴다. 가장 명백하게 맞는 참조이고, n ≤ 5000 에서 충분히 빠르다.

```python
def neighbors_brute(pos, n, radius):
	"(n,n) bool. the most obviously-correct reference. n <= ~5k."
	p = pos[:n, :3]
	d = p[:,None,:] - p[None,:,:]
	r2 = np.sum(d*d, axis=2)
	near = r2 < radius*radius
	np.fill_diagonal(near, False)
	return near

def lam_np(ppred, rho, lam, n, h, mass, rho0, eps, **_):
	"density + lambda, brute force. self term (r=0) is included in density."
	p = ppred[:n, :3]
	d = p[:,None,:] - p[None,:,:]
	r2 = np.sum(d*d, axis=2)
	rho[:n] = mass*poly6(r2, h).sum(axis=1)
	# ... gradients from spiky_grad(d) with the same formulas as glsl
```

- pass 단위 일치 검사. 한 함수로 모든 pass 를 같은 방식으로 검사한다:

```python
def check_pass(p, np_be, gl_be, count, atol=1e-5, **params):
	"same input -> numpy and gpu -> compare outputs. both backends share the same Table objects."
	before = { attr: gl_be.tables[t].data[attr].copy() for t,attr in p.buffers }
	np_be.run(p, count, **params)
	expect = { attr: gl_be.tables[t].data[attr].copy() for t,attr in p.buffers if attr in p.outputs }
	for t,attr in p.buffers:                                     # restore, upload
		gl_be.tables[t].data[attr][:] = before[attr]
		gl_be.tables[t].gpu[attr].upload(before[attr])
	gl_be.run(p, count, **params)
	for t,attr in p.buffers:
		if attr not in p.outputs: continue
		got = gl_be.tables[t].gpu[attr].download( np.empty_like(before[attr]) )
		assert np.allclose(expect[attr][:count], got[:count], atol=atol), (p.name, attr)
```

- scatter 계열 (`count`, `scatter`) 은 원소 순서가 비결정적이다. `count` 는 그대로 비교되고, `sorted_idx` 는 셀 구간별로 정렬해서 집합으로 비교한다. 밀도 합처럼 덧셈 순서만 다른 것은 `atol` 로 흡수.
- 디버그 절차: GPU 로 k 프레임 → 전체 다운로드 → 같은 상태에서 numpy 로 한 스텝 → pass 별 비교 → **처음 어긋나는 pass** 가 범인.
- fallback: GL 4.3 이 없는 곳(macOS 는 4.1 까지)에서는 numpy 백엔드로 n=2000 정도를 돌린다. 느리지만 맞고, `print` 와 breakpoint 가 된다.
- 성능 기록 습관 유지: pass 마다 `glFinish()` 후 `perf_counter()` 로 재고 docstring 에 숫자를 남긴다. 나중에 `glQueryCounter` 로 바꾼다.

---

## 5. 스케일과 관심영역(ROI)

단위는 SI (m, s, kg) 로 통일. `Grid.h` 도 m.

**1m 큐브, 입자 (물을 절반 채움, h = 2d):**

| 간격 d | 입자 수 | 셀 h | 셀 수 | 판단 |
|---|---|---|---|---|
| 2cm | 62.5K | 4cm | 25³ = 15.6K | 시작점. 어느 GPU 든 60fps |
| 1cm | 500K | 2cm | 50³ = 125K | 2차 목표. 데스크톱 GPU 실시간 |
| 5mm | 4M | 1cm | 100³ = 1M | 가능하나 프레임 시간 한계 |
| 3mm | 18.5M | 6mm | 167³ = 4.6M | 전체 영역에는 불가. ROI 만 |

**1m 큐브, 격자 스모크 (u vec4 + p, div, smoke + ping-pong ≈ 48B/셀):**

| h | 셀 수 | 메모리 | 판단 |
|---|---|---|---|
| 2cm | 125K | 6MB | 즉시 |
| 1cm | 1M | 48MB | Jacobi 50회 포함 수 ms ~ 10ms 대. 실시간 |
| 5mm | 8M | 384MB | 부담 시작 |
| 3mm | 37M | 1.8GB | 불가 |

**10m 과 3mm 를 같이 만족하는 방법은 중첩 격자뿐이다.** 10m/3mm = 3333³ 셀은 존재할 수 없다.

- 단계별 100³: `10m @ 10cm` → `1m @ 1cm` → `10cm @ 1mm` (또는 `30cm @ 3mm`). 각 단계가 같은 크기의 Grid 인스턴스.
- 격자 방식의 ROI 는 정석이 있다: 안쪽 fine Grid 의 경계 속도를 바깥 coarse Grid 에서 샘플링해 준다 (일방향 결합). 양방향은 나중.
- 입자 방식의 ROI(반지름 가변, 분열/병합) 는 연구 주제에 가깝다. ROI 가 중요해지면 격자 또는 FLIP 경로가 맞다.
- **지금 결정할 것은 하나뿐:** Grid 를 값 객체로 두고 모든 pass 가 grid uniform 을 받게 한다. 그러면 두 번째 Grid 는 인스턴스 하나 더다. ROI 자체는 지금 만들지 않는다.

---

## 6. 기존 코드 개선 제안

오래된 코드이므로 유체용으로 다시 세울 때 같이 정리하면 좋은 것들.

**`gunfire_unit.UnitArray`, `axis.Axis` → `Table`**

- `(attrs, N)` → 속성별 `(N,·)`. 이유는 3장.
- `free_idxs` + `active` 마스크 → `capacity` + `n`. 유체는 개별 해제가 없다. 필요하면 swap-with-last.
- `set('posx', …)` 의 `parse_xyz` 는 코어에서 뺀다. `t.pos[:,0]` 이 이미 그 뜻이다. 편의 API 가 필요하면 껍데기 층에.
- `make_i` 의 `int64` → `uint32`. GPU 에 올라가는 인덱스는 전부 `uint32`.
- `Axis.add_func` 의 "함수가 필요한 속성을 선언" 은 `Pass.buffers` 로 살아남는다. 명시적이 되었을 뿐.
- `Axis.__str__` 의 표 출력은 `Table.__repr__` 로 가져오면 좋다 (디버깅에 유용했다).

**`shader.py`**

- `Shader` 에서 공통부(uniform 위치 캐시, `bind`, `set_*`)를 `Program` 으로 뽑고, `Shader(vert, frag)` 와 `ComputeShader(comp)` 가 상속. `ComputeShader.dispatch(count)` 가 `ceil(count/256)` 그룹을 계산.
- `_get_location` 이 -1 에 `KeyError` 를 던지는 것은 너무 엄격하다. 드라이버가 안 쓰는 uniform 을 지우면 -1 이 정상이다. 한 번 경고하고 건너뛰게.
- `set_uint`, `set_ivec3`, `set_uniforms(dict)` 추가 (Python 타입으로 분기).
- `#version 410` → `430`. 첫 실행에서 `glGetString(GL_VERSION)` 을 찍어 4.3 이상인지 확인.
- `vertn` 의 `gl_Position` 이 두 번 대입되어 `Model` 이 무시된다. 한 줄 삭제.
- `shaders.compileProgram(..., validate=False)` 옵션이 있다. compute 프로그램 validate 가 일부 드라이버에서 헛되게 실패하면 이걸 쓴다.

**`vao.py`**

- 메시용으로는 그대로. 입자는 VBO 가 필요 없다 (3장의 `gl_VertexID` 방식). `Buffer` 를 형제 파일로.
- `_last_bound` 캐시 습관은 `Program` 에도 그대로.

**`interface.py`**

- ABC 는 구현이 둘인 곳에만: `Backend` (numpy / compute). `Table`, `Grid` 는 ABC 없이 구체 클래스 하나.

**테스트**

- 파일 안 `test_*` + `_tests` 리스트 (`cylinder.py` 방식) 유지. GL 테스트는 창이 필요하므로 `glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE)` 로 숨긴 컨텍스트를 만드는 헬퍼 하나.
- `test_window.py` 가 import 시 `glfwInit()`, `run()` 끝에 `glfwTerminate()` 를 부르므로 한 프로세스에서 창을 두 번 못 만든다. 테스트 헬퍼는 `Terminate` 를 부르지 않게.

**스타일**

- 새 패키지는 탭 (최근 파일들 기준). `float32` / `uint32`. SI 단위. 실측 숫자는 docstring 에.

---

## 7. 파일 구성과 사용자 API

```
fluid/
  table.py       Table, make_attr
  grid.py        Grid, GRID_GLSL
  glbuf.py       Buffer, Program, ComputeShader        (shader.py / vao.py 의 형제)
  passes.py      Pass, NumpyBackend, ComputeBackend, check_pass
  neighbor.py    cell/count/scan/scatter 4 pass + numpy oracle + NEIGHBOR_LOOP 스니펫
  kernels.py     poly6 / spiky (numpy + KERNEL_GLSL)
  pbf.py         PBF 의 pass 들 + class PBF(step)
  mac.py         MAC 격자 pass 들 + class Smoke(step)
  draw.py        입자 점 그리기, 셀 점 그리기(연기 미리보기)
  glsl/          긴 .comp 본문은 파일로. 짧은 것은 .py 안의 문자열
  test_*.py      단계별 데모 + 검증
```

사용자가 만지는 것:

```python
grid = Grid(origin=(0,0,0), size=(1,1,1), h=0.04)
ps = Table(PBF.SCHEMA, capacity=100_000)
ps.append(*fill_box(lo=(0.05,0.05,0.05), hi=(0.5,0.9,0.5), spacing=0.02))   # 62.5k rows
sim = PBF(grid, ps, rho0=1000, spacing=0.02, iters=4, backend=ComputeBackend({'ps':ps, 'cells':cells}))

def update(dt):
	sim.step(dt)
def draw():
	drawer.points(ps, 'pos', camera.get_ViewProjection())
```

추상화는 여기까지. `PBF` 는 파라미터를 들고 `step()` 을 나열하는 클래스이고, pass 는 모듈 함수/문자열이다. API 를 다시 짜도 pass 와 Table/Grid 는 그대로 남는다.

---

## 8. 단계별 진행

각 단계에 "완료 기준" 이 있다. 기준을 통과하기 전에 다음으로 가지 않는다.

### Phase 0 — compute 기반

만들 것: `Buffer`, `Program`/`ComputeShader`, 숨긴 창 헬퍼, `Table`, `Grid`.

```python
class ComputeShader(Program):
	LOCAL = 256
	def __init__(self, src):
		cs = shaders.compileShader(src, GL_COMPUTE_SHADER)
		super().__init__( shaders.compileProgram(cs) )
	def dispatch(self, count):
		groups = (count + self.LOCAL - 1)//self.LOCAL
		glDispatchCompute(groups, 1, 1)
```

- 완료 기준: `(1M,4) float32` 를 올리고 `a[i] *= 2` compute 를 돌려 내려받은 것이 `np*2` 와 같다. 100만 원소 왕복 시간을 기록.
- 배울 것: SSBO, `local_size`/dispatch, `glMemoryBarrier`, uniform.
- 함정: GL 호출은 창 생성 뒤에 (`shader.py` 의 `assert bool(glCreateShader)` 습관 유지). 그룹 수 상한(보통 65535) → 1D 로 1670만 원소까지, 그 이상은 2D dispatch.

### Phase 1 — 입자 + 격자 이웃 탐색 (+ "작은 공")

입자 Table: `pos(4) vel(4) cell(u)`. 셀 Table (capacity `ncell+1`): `count(u) start(u) fill(u)`, 그리고 입자 Table 에 `sorted_idx(u)`.

numpy 참조 (실행 확인함):

```python
def neighbor_np(pos, grid):
	"oracle for the 4 gpu passes. returns cell(n,), cell_start(ncell+1,), sorted_idx(n,)"
	cell = grid.cell_index( grid.cell_coord(pos) )
	cell_count = np.bincount(cell, minlength=grid.ncell)
	cell_start = np.zeros(grid.ncell+1, dtype='int64')
	cell_start[1:] = np.cumsum(cell_count)          # exclusive scan
	sorted_idx = np.argsort(cell, kind='stable')     # particles ordered by cell
	return cell, cell_start, sorted_idx
# neighbors of i: for each of 27 cells c around i -> sorted_idx[cell_start[c]:cell_start[c+1]] -> distance check
# 3000 particles, h=0.05: == brute force for every sampled i.
# 1M particles, 125k cells: 177 ms (numpy, this machine). cumsum of 125k cells alone: 0.6 ms.
```

GPU 4 pass:

```glsl
// cell.comp    buffers: pos, cell   (+GRID_GLSL)
void main(){ uint i = gl_GlobalInvocationID.x; if (i >= n) return;
	cell[i] = cell_index(cell_coord(pos[i].xyz)); }

// count.comp   buffers: cell, count        (count zeroed first: a 'zero' pass over the cell table)
void main(){ uint i = gl_GlobalInvocationID.x; if (i >= n) return;
	atomicAdd(count[cell[i]], 1u); }

// scan: numpy first.  start[0] = 0; start[c+1] = start[c] + count[c]  -> upload.   (0.6 ms for 125k cells)
//       later: gpu prefix sum (Blelloch, 2 pass). only when readback shows up in the profile.

// scatter.comp buffers: cell, start, fill, sorted_idx   (fill zeroed first)
void main(){ uint i = gl_GlobalInvocationID.x; if (i >= n) return;
	uint c = cell[i];
	uint slot = atomicAdd(fill[c], 1u);
	sorted_idx[start[c] + slot] = i; }
```

이웃 루프 (모든 gather pass 가 이 형태를 복사한다):

```glsl
vec3 p = pos[i].xyz;
ivec3 c0 = cell_coord(p);
for (int dz = -1; dz <= 1; dz++)
for (int dy = -1; dy <= 1; dy++)
for (int dx = -1; dx <= 1; dx++) {
	ivec3 c = c0 + ivec3(dx,dy,dz);
	if (any(lessThan(c, ivec3(0))) || any(greaterThanEqual(c, dims))) continue;
	uint ci = cell_index(c);
	for (uint k = start[ci]; k < start[ci+1]; k++) {
		uint j = sorted_idx[k];
		if (j == i) continue;
		vec3 d = p - pos[j].xyz;
		float r2 = dot(d, d);
		if (r2 >= h*h) continue;
		// ... per neighbor
	}
}
```

"작은 공" 은 여기서 바로 된다: gather pass 하나 (`repel`: 겹침 × k 스프링 힘을 `vel` 에 누적. `pos` 는 읽기만, `vel` 에만 쓰므로 경쟁 없음) + map pass 하나 (`integrate`: `pos += vel dt`, 상자 벽에서 반사/감쇠). 중력을 주면 모래처럼 쌓인다.

- 완료 기준: (1) `count` == `np.bincount`. (2) 셀 구간별 `sorted_idx` 집합 == oracle. (3) 샘플 입자의 이웃 목록 == 전수 비교. (4) 10만 개 공이 상자에 쌓이고 60fps. 100만 개도 시도.
- 함정: 스프링은 딱딱해서 `dt = 1/60` 에 서브스텝 4~8 이 필요하다. 이 단계의 목적은 물리가 아니라 이웃 기계다. 정렬 안 하고 `sorted_idx` 간접 참조로 시작하고, 프로파일에 나오면 행 재정렬 pass 를 추가.
- 격자 밖으로 나간 입자는 `cell_coord` 의 clamp 때문에 경계 셀에 몰린다. 상자 충돌이 안에 가둔다는 전제. 전제가 깨지면 경계 셀이 비대해져 느려진다.

### Phase 2 — PBF (Position Based Fluids)

입자 Table 에 추가: `ppred(4) dp(4) dv(4) lam(1) rho(1)`.

커널 (Müller 2003):

```glsl
uniform float h;
float poly6(float r2){ float x = max(h*h - r2, 0.0); return 315.0/(64.0*3.14159265*pow(h,9.0)) * x*x*x; }
vec3  spiky_grad(vec3 d){ float r = length(d); if (r < 1e-6) return vec3(0.0);
	float x = h - r; return -45.0/(3.14159265*pow(h,6.0)) * x*x * (d/r); }
```

수식 (Macklin & Müller 2013). `d = p_i - p_j`, 질량 동일 m:

- 밀도: `ρ_i = m Σ_j W(|d|)`. **자기 자신 포함** (`W(0)`).
- 제약: `C_i = ρ_i/ρ0 - 1`. 실전에서는 `max(C_i, 0)` (표면에서 밀도가 모자라 당기는 것을 막음).
- `∇_i = (m/ρ0) Σ_{j≠i} ∇W(d)`,  `S = |∇_i|² + Σ_{j≠i} |(m/ρ0) ∇W(d)|²`  (논문은 단위 질량이라 m 이 안 보인다. SI 에서는 붙는다)
- `λ_i = -C_i / (S + ε)`
- `Δp_i = (m/ρ0) Σ_{j≠i} (λ_i + λ_j + s_corr) ∇W(d)`,  `s_corr = -k (W(|d|)/W(Δq))⁴`, Δq = 0.2h. **k 는 λ 와 같은 단위(m²)** 라서 SI 에서 0.1 을 쓰면 수십 m 씩 튄다. λ 전형값의 1/10 정도로 잡는다 (실행 확인: h=4cm 에서 λ ~ 1e-6 m² 자릿수)
- XSPH: `v_i += c Σ_j (v_j - v_i) W(|d|)`, c = 0.01

파라미터 (실행 확인: 격자 간격 d, h = 2d, m = ρ0 d³ 일 때 내부 밀도 = 1009.8, 즉 ρ0 대비 +1%, 이웃 26개):

| 항목 | 값 | 비고 |
|---|---|---|
| 간격 d | 2cm → 1cm | |
| h | 2d | 셀 크기도 h. 셀당 8개 |
| m | ρ0 d³ | 2cm: 8g, 1cm: 1g |
| ρ0 | 1000 | |
| iters | 3~4 | |
| dt | 1/60, 서브스텝 1~2 | |
| ε | 측정해서 정함 | 단위에 따라 크게 변한다. `S` 를 readback 해서 그 전형값의 1% 정도 |
| k (s_corr) | 측정해서 정함 | λ 와 같은 단위. λ 전형값의 1/10. 논문의 0.1 은 단위 질량, h≈1 기준 |

pass 와 순서는 2.4 의 `step()` 그대로. gather pass (`lam`, `dp`, `xsph`) 는 읽는 배열에 쓰지 않는다: `lam` 은 `ppred` 를 읽고 `rho, lam` 에 쓴다. `dp` 는 `ppred, lam` 을 읽고 `dp` 에 쓴다. `apply` 가 `ppred += dp` 후 상자 clamp. 이웃 격자는 `ppred` 기준으로 만든다.

- 완료 기준: (1) `rho` readback 평균이 내부에서 1000 ± 5%. (2) `dt = 1/60` 에서 터지지 않고 출렁인다. (3) 6.25만 → 50만 개.
- 함정: ε 단위. 표면 밀도 부족(clamp 또는 s_corr). `lam` 을 다 계산하기 전에 `dp` 를 돌리면 안 됨 (barrier 는 백엔드가 pass 마다 친다).

### Phase 3 — MAC 격자 스모크 (벡터장)

셀 Table (capacity ncell): `u(4) u2(4) p(1) p2(1) div(1) smoke(1) smoke2(1)`.

**MAC 압축 저장:** 셀 c 가 자기 **마이너스 쪽 면 셋** 을 소유한다. `u[c].x` = c 의 -x 면의 x 속도, `.y` = -y 면, `.z` = -z 면. 도메인 +쪽 벽 면과 첫 셀들의 -쪽 벽 면은 0 (고체 벽). Table 하나, Grid 하나로 MAC 이 된다.

- -x 면 중심: `origin + h*(i, j+.5, k+.5)`. 셀 중심: `origin + h*(i+.5, j+.5, k+.5)`.
- 어떤 점에서 속도 샘플: 성분마다 자기 오프셋 격자로 삼선형. `sample_ux(p)`: `g = (p-origin)/h - vec3(0,.5,.5)`; `q = floor(g)`; 8꼭짓점 `UX(q+corner)` 보간. `UX(q)` 는 범위 밖이면 0 (벽).

numpy 참조 (실행 확인함, 16³, h = 1/16):

```python
def divergence(u, h):
	"div[c] = (u[c+x].x - u[c].x + ...)/h.  u at the + wall = 0."
	n = u.shape[0]
	ux = np.zeros((n+1,n,n), dtype='float32'); ux[:n] = u[...,0]     # ux[n] = 0 : +x wall
	uy = np.zeros((n,n+1,n), dtype='float32'); uy[:,:n] = u[...,1]
	uz = np.zeros((n,n,n+1), dtype='float32'); uz[:,:,:n] = u[...,2]
	return (ux[1:]-ux[:-1] + uy[:,1:]-uy[:,:-1] + uz[:,:,1:]-uz[:,:,:-1])/h

def jacobi(p, div, h, iters):
	"solve lap(p) = div, 7 point. neumann walls: outside p = inside p."
	for _ in range(iters):
		pp = np.pad(p, 1, mode='edge')
		s = (pp[:-2,1:-1,1:-1] + pp[2:,1:-1,1:-1] + pp[1:-1,:-2,1:-1]
		   + pp[1:-1,2:,1:-1] + pp[1:-1,1:-1,:-2] + pp[1:-1,1:-1,2:])
		p = (s - h*h*div)/6.0
	return p

def subtract_gradient(u, p, h):
	"u[c].x -= (p[c]-p[c-x])/h on interior faces. wall faces stay 0."
	u = u.copy()
	u[1:,:,:,0] -= (p[1:]-p[:-1])/h
	u[:,1:,:,1] -= (p[:,1:]-p[:,:-1])/h
	u[:,:,1:,2] -= (p[:,:,1:]-p[:,:,:-1])/h
	return u
```

| Jacobi 반복 | \|div\| rms (시작 37.9) |
|---|---|
| 20 | 0.86 |
| 50 | 0.24 |
| 100 | 0.066 |
| 300 | 0.0084 |
| 3000 | ~1e-5 (float32 바닥) |

비교: Stam/GPU Gems 식 collocated (셀 중심 속도 + 중앙차분) 는 같은 Jacobi 3000회에도 rms 19 → 13.5 에서 멈춘다 (checkerboard 모드가 7점 라플라시안과 중앙차분 사이에 끼어 있음). 튜토리얼은 그래도 보기엔 괜찮아서 그렇게 하지만, **검증 가능한 기준("발산 → 0") 을 원하면 처음부터 MAC** 이다. 코드 차이는 반 셀 오프셋뿐이다.

GPU pass (모두 dispatch `ncell`):

```glsl
// stencil helpers. wall handling in one place.
float P(ivec3 q){ q = clamp(q, ivec3(0), dims-1); return p[cell_index(q)]; }           // neumann
float UX(ivec3 q){ if (any(lessThan(q,ivec3(0))) || any(greaterThanEqual(q,dims))) return 0.0; return u[cell_index(q)].x; }

// div.comp     buffers: u, div
ivec3 q = coord_of(c);
div[c] = ( UX(q+ivec3(1,0,0)) - u[c].x + UY(q+ivec3(0,1,0)) - u[c].y + UZ(q+ivec3(0,0,1)) - u[c].z ) / h;

// jacobi.comp  buffers: p, div, p2      (python swaps the names p <-> p2 each iteration)
ivec3 q = coord_of(c);
float s = P(q+ivec3(1,0,0)) + P(q-ivec3(1,0,0)) + P(q+ivec3(0,1,0)) + P(q-ivec3(0,1,0)) + P(q+ivec3(0,0,1)) + P(q-ivec3(0,0,1));
p2[c] = (s - h*h*div[c]) / 6.0;

// grad.comp    buffers: p, u            (writes only u[c]; reads only p -> no race)
ivec3 q = coord_of(c);
u[c].x = (q.x > 0) ? u[c].x - (p[c] - P(q-ivec3(1,0,0)))/h : 0.0;   // same for y, z
```

한 스텝: `advect_u (u → u2, 반 라그랑지: 면 위치 fp 에서 v = sample_u(fp), u2 = sample_u(fp - v dt))` → `force (부력: smoke 에 비례해 .y 면에 +)` → `div` → `jacobi × K` → `grad` → `advect_smoke (smoke → smoke2, 셀 중심 오프셋)`. Python 이 `u/u2`, `p/p2`, `smoke/smoke2` 이름을 바꾼다.

렌더: 새 인프라 없이 먼저 본다. 셀마다 점 하나 (`gl_VertexID` → `coord_of` → 셀 중심), alpha = smoke, additive blend. 그 다음 큐브 ray-march.

- 완료 기준: (1) numpy 참조와 pass 별 일치. (2) 100³ 에서 Jacobi 50회 후 `|div|` rms 가 1/100 이하 (readback). (3) 연기가 상자 안에서 떠오르고 소용돌이친다.
- 함정: 반 라그랑지 이류는 뭉개진다 (BFECC/MacCormack 은 나중). Jacobi 는 저주파에 느리다. 100³ 에서 부족하면 red-black Gauss-Seidel (compute 로 쉬움, 2배) → multigrid. 압력 단위: `∇²φ = div, u -= ∇φ` 로 dt/ρ 를 φ 에 흡수한 것. 벽 처리는 헬퍼 함수 밖에서 하지 말 것.

### Phase 4 — FLIP (선택, 물 + 격자)

Phase 1 의 입자/이웃 격자 + Phase 3 의 MAC 투영. 입자가 속도를 들고 다니고 격자가 비압축을 푼다.

- P2G: 면마다 주변 셀의 입자를 **gather** 해서 삼선형 가중 평균 속도. Phase 1 의 counting sort 를 그대로 쓰므로 atomics 가 없고 결정적이다. (scatter 로 하려면 float atomic 이 필요한데 core GLSL 에 없다. 고정소수 `uint atomicAdd` 가 우회.)
- 격자: 입자가 있는 셀만 유체. 공기 셀 p = 0 (Dirichlet), 벽은 Neumann. `P(q)` 가 셀 종류로 분기.
- G2P: `v_p += sample(u_new - u_old)` (FLIP) 와 `v_p = sample(u_new)` (PIC) 를 0.95 : 0.05 로 섞는다. `u_old` 는 속성 하나 더.
- 입자 이동: `p += sample_u(p) dt` (RK2 가 낫다), 벽 밖이면 밀어 넣기.
- 완료 기준: 물이 수평으로 가라앉고, 유체 셀 수가 ±10% 안에서 유지된다.
- 다른 선택지: MLS-MPM (Hu 2018) 은 여러 재료를 한 틀로 다루지만 이 문서의 범위 밖.

---

## 9. 함정 목록

- `vec3[]` in std430. `(n,3)` 을 올리면 조용히 어긋난다. 항상 `(n,4)`.
- `int64` 업로드. 인덱스는 `uint32`.
- uniform 위치 -1 은 "안 쓰여서 지워짐" 일 수 있다. 예외 대신 경고.
- pass 사이 `glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)`. readback 전 `GL_BUFFER_UPDATE_BARRIER_BIT`.
- `count`, `fill` 을 매 스텝 0 으로. `zero` pass 를 잊으면 누적된다.
- gather pass 가 읽는 배열에 쓰면 경쟁. 항상 다른 속성(`dp`, `dv`, `u2`) 에 쓴다.
- atomics 는 순서 비결정. 테스트는 집합/허용오차로.
- dispatch 그룹 상한 65535. 1D 는 1670만 원소까지.
- float atomicAdd 는 core 에 없다 (NV 확장). gather 로 설계.
- `cell_coord` clamp 는 밖으로 나간 입자를 경계 셀에 몰아넣는다. 상자 충돌이 전제.
- PBF ε 는 단위 의존. 측정해서 정한다.
- collocated 격자는 발산이 0 이 안 된다 (숫자는 8장). MAC.
- 반 라그랑지 이류의 소산, Jacobi 의 저주파 수렴.
- DEM 스프링의 dt. 서브스텝 없이 터진다.
- GL 호출은 컨텍스트 뒤. `#version 430`. macOS 는 compute 불가.

---

## 10. 참고 자료

- Stam, "Stable Fluids", SIGGRAPH 1999 — 반 라그랑지 이류 + 투영의 원형.
- Harris, "Fast Fluid Dynamics Simulation on the GPU", GPU Gems ch.38 (2D). Crane, Llamas, Tariq, "Real-Time Simulation and Rendering of 3D Fluids", GPU Gems 3 ch.30 (3D, ray-march 포함).
- Bridson, *Fluid Simulation for Computer Graphics* 2판 — MAC 격자, 투영, FLIP 의 교과서.
- Müller, Charypar, Gross, "Particle-Based Fluid Simulation for Interactive Applications", SCA 2003 — poly6/spiky 커널.
- Macklin, Müller, "Position Based Fluids", SIGGRAPH 2013 — Phase 2 의 수식 전부.
- Green, "Particle Simulation using CUDA", NVIDIA 2010 — counting sort 이웃 격자의 원형.
- Koschier, Bender, Solenthaler, Teschner, "SPH Techniques for the Physics Based Simulation of Fluids and Solids", Eurographics tutorial 2019 — SPH 전반, SPlisHSPlasH.
- Zhu, Bridson, "Animating Sand as a Fluid", SIGGRAPH 2005 — FLIP.
- Müller, Ten Minute Physics #18 "How to write a FLIP water simulator" — 가장 짧은 FLIP 구현.
- Hu et al., "A Moving Least Squares Material Point Method…", SIGGRAPH 2018 — MLS-MPM.
