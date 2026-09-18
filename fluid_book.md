# 유체 시뮬레이션 교본

axis3d 에서 PyOpenGL compute shader 로 물을 만드는 과정을, 낮은 수준의 개념부터 한 단계씩 올라가며 설명하는 책입니다. `fluid_plan.md` 는 설계 메모이고, 이 책은 읽는 순서입니다.

**이 책의 코드는 전부 실행해서 확인했습니다.** numpy 부분은 그대로, GLSL 부분은 Mesa 소프트웨어 렌더러(llvmpipe, OpenGL 4.5 core) 위에서 numpy 쌍둥이와 비교해 같은 값이 나오는 것을 확인했습니다. 본문에 "확인" 이라고 적힌 숫자는 그 실행에서 나온 값입니다. 시간 측정은 GPU 가 없는 환경이라 하지 않았습니다.

**전제.** 지금까지 정한 것들입니다.

| 항목 | 결정 |
|---|---|
| 유체 | 물, 자유표면 있음 |
| 경로 | 입자(PBF) → 격자(MAC) → 둘을 합친 FLIP |
| 관심영역(ROI) | 거시 흐름은 항상 돌고, ROI 안에서 작은 강체 파편을 따로 |
| 장애물 | 고정 장애물 있음. 부호 거리(SDF)로 |
| 좌표 | SI 단위(m, s, kg), z 가 위, 중력 (0, 0, −9.81) |
| 환경 | Windows, OpenGL 4.5, Python 3.10 이상, numpy + PyOpenGL + glfw |
| 코드 | 4칸 들여쓰기, 영어 주석, 클래스는 목차이고 함수가 일을 한다 |
| 데이터 구조 | 열마다 numpy 배열 하나인 이름공간 (책 14장) |
| 검증 | 모든 GPU 계산에 numpy 쌍둥이가 있고, 둘을 비교한다 |

---

# 제1부. 전체 방향

## 1장. 무엇을 만드는가

최종 그림은 이렇습니다. 한 변 1m 인 수조에 물이 반쯤 차 있고, 안에 고정된 장애물이 있습니다. 물 전체의 거시적 흐름이 실시간으로 돕니다. 수조 안 한 구석 10cm 정도를 관심영역으로 잡으면, 그 안에서는 격자가 더 촘촘해지고 3mm 급의 작은 파편들이 물에 실려 움직이고 서로 부딪칩니다. 모든 계산은 GPU 에서 돌고, 같은 계산의 numpy 버전이 있어서 맞는지 확인할 수 있습니다.

유체를 계산하는 관점은 둘입니다.

**격자.** 다리 위에 서서 발밑을 지나가는 물의 속도를 재는 사람입니다. 공간의 고정된 점마다 속도 화살표 하나. 벡터장입니다. 연기, 공기, 공간을 채우는 흐름에 맞습니다. 한 스텝은 "값을 흐름을 따라 옮기고(이류), 힘을 더하고, 물이 압축되지 않도록 압력으로 바로잡는다(투영)" 입니다.

**입자.** 나뭇잎을 띄워 따라가는 사람입니다. 물 조각마다 위치와 속도. 물의 표면이 저절로 생기고 튀는 것이 자연스럽습니다. 한 스텝은 "이웃을 찾고, 밀도를 재고, 밀도가 기준(1000 kg/m³)이 되도록 위치를 밀어낸다" 입니다.

**하이브리드(FLIP).** 입자가 속도를 들고 다니고, 격자가 압축되지 않음을 풉니다. 제작용 물이 이것입니다. 두 관점을 다 알아야 하므로 마지막입니다.

우리는 입자로 시작합니다. GPU 의 기초(버퍼, 동시 실행, 원자적 더하기, 이웃 격자)를 가장 빨리 다 만나고, 그때 만든 격자가 그대로 격자 방식의 격자이기 때문입니다. "작은 공을 마구 시뮬레이션하면 충돌 처리가 부담되지 않나" 는 걱정의 답이 바로 이 격자입니다. 셀 크기를 상호작용 반경으로 잡으면 한 입자는 주변 27셀만 봅니다. 100만 개여도 입자당 200개 정도의 후보만 검사합니다.

## 2장. 어떻게 자라는가: 세로 조각

부품을 먼저 만들지 않습니다. 아주 작은 완성품을 만들고, 키우면서 반복되는 부분을 떼어냅니다. 그래야 부품이 "왜 있는지" 기억됩니다.

| 단계 | 보이는 것 | 새로 배우는 것 | 태어나는 부품 |
|---|---|---|---|
| 1 | 입자 1000개가 상자에서 떨어지고 튕긴다. 한 파일 | 버퍼, dispatch, barrier, SSBO 로 그리기, numpy 쌍둥이 | 없음 |
| 2 | 입자가 서로 밀어내며 모래처럼 쌓인다 | counting sort, 원자적 더하기, 이웃 루프 | Grid, Table, pass 짝 |
| 3 | 물이 출렁인다 (PBF) | 밀도 제약, 커널, 위치 보정 | 솔버 클래스 |
| 4 | 장애물이 생긴다 | 부호 거리(SDF), 셀 종류 | cells 테이블 |
| 5 | 연기가 격자 속도장을 따라 떠오른다 (MAC) | 면 속도, 발산, Jacobi, 반 라그랑지 이류 | 격자 pass 들 |
| 6 | 큰 격자 안에 작은 격자가 산다 (world + roi) | 경계 샘플링, 일방향 결합 | Grid 두 번째 인스턴스 |
| 7 | 거시 물이 격자로 돈다 (FLIP) | P2G, G2P, 공기 셀 | 하이브리드 솔버 |
| 8 | ROI 안 파편이 물에 실려 다닌다 | 항력, 강체 충돌 | 파편 솔버 |
| 9 | 실시간이 된다 | 측정, GPU scan, 재정렬 | 없음 (교체만) |

다섯 가지 규칙이 모든 단계에 걸립니다.

1. 모든 GPU 계산에 numpy 쌍둥이가 있다. 같은 배열 이름, 같은 파라미터. 둘을 비교하는 테스트가 있다.
2. numpy 배열의 바이트가 그대로 GPU 버퍼다. 변환 없음.
3. 숫자를 재서 주석에 남긴다.
4. SI 단위, z 가 위.
5. 읽고 있는 배열에 쓰지 않는다.

## 3장. 지도

단계 1 이 끝났을 때의 지도입니다. 상자 셋이 전부입니다.

```
 데이터 (numpy 배열)           계산 (같은 일을 두 번 쓴다)           화면
 pos (n,4) float32   ──▶   step_np(pos, vel, ...)              점으로 그리기.
 vel (n,4) float32   ──▶   STEP_GLSL + Buffer + dispatch       GPU 버퍼를 그대로 읽는다
```

단계 9 가 끝났을 때의 지도입니다. 상자가 늘었지만 화살표의 종류는 같습니다.

```
 사용자 API                 Table, Grid, PBF / Smoke / Flip / Debris .step(dt), draw
 ──────────────────────────────────────────────────────────────────────────────
 데이터                                  계산: pass = (열 목록, np 함수, GLSL 본문)
  ps    : pos vel ppred dp lam rho ...     neighbor  cell count scan scatter
  cells : u u2 p p2 div kind sdf count..   pbf       predict lam dp apply velocity
  Grid  : world, roi (origin, h, dims)     mac       advect force div jacobi grad
                                           flip      p2g g2p kinds
                                           debris    repel drag integrate
                                                 │
                                     backend.run(pass, n, **params)
                                       numpy : pass.np(열[:n], params)
                                       gpu   : 버퍼 묶기, uniform, dispatch, barrier
```

각 장은 이 지도에서 자기가 어느 상자인지 말하고 시작합니다.

---

# 제2부. 핵심 개념

각 장은 "개념, 아주 작은 코드, 실행 결과, 함정" 순서입니다. 코드는 그대로 실행됩니다.

## 4장. 배열은 바이트다

numpy 배열은 연속된 바이트 한 줄에 "어떻게 자를지(dtype)" 와 "몇 개씩 묶을지(shape)" 를 붙인 것입니다.

```python
import numpy as np
pos = np.zeros((1000, 4), dtype='float32')   # 1000 rows x 4 floats = 16000 bytes, one straight line
pos.nbytes          # 16000
pos[7]              # row 7: 4 floats at byte 7*16
pos[:, 0]           # column x: every 16th byte, 1000 of them
```

GPU 버퍼도 그냥 바이트 한 줄입니다. 그래서 `pos` 의 바이트를 그대로 올리고, GLSL 에게 "이 줄을 vec4 로 잘라 읽어라" 고 말하면 `pos[7]` 이 양쪽에서 같은 것을 가리킵니다. 이 책의 모든 데이터 설계는 이 한 문장에서 나옵니다.

**자르는 규칙이 std430 입니다.** GLSL 의 SSBO 배열에서 원소 사이 간격입니다.

| numpy | GLSL | 원소 간격 | |
|---|---|---|---|
| `(n,) float32` | `float a[]` | 4 | |
| `(n,) uint32` | `uint a[]` | 4 | 인덱스용. `int64` 는 GPU 에 없다 |
| `(n,4) float32` | `vec4 a[]` | 16 | 벡터의 기본. 넷째 칸은 여유 |
| `(n,3) float32` | `vec3 a[]` | **16** | 함정. 아래 |

**vec3 함정, 확인.** `(4,3)` 배열 `[[0,1,2],[3,4,5],[6,7,8],[9,10,11]]` 을 올리고 GLSL 에서 `vec3 q[]` 로 읽어 `q[i].x` 를 내려받았습니다. 기대는 `[0, 3, 6, 9]` 인데 실제는 `[0, 4, 8, 0]` 이었습니다. `q[1]` 은 16바이트째, 즉 다섯 번째 float 인 4 에서 시작하기 때문입니다. 에러도 경고도 없습니다. 그래서 벡터는 항상 `(n,4)` 입니다.

왜 float32 인가. GPU 의 기본이 32비트이고, 64비트는 느리거나 없습니다. 1m 수조에서 float32 의 정밀도는 약 1e-7 m, 0.1μm 입니다. 충분합니다. 인덱스는 uint32, 42억까지 셉니다.

## 5장. GPU 는 같은 함수를 N 번 부른다

numpy 에서 `pos += vel*dt` 는 한 줄이 N 개 행에 적용됩니다. compute shader 는 함수 하나를 쓰고, 그 함수가 N 번 동시에 불립니다. 각 호출은 "내가 몇 번째냐" 만 압니다.

```glsl
#version 430
layout(local_size_x = 256) in;                       // threads come in groups of 256
layout(std430, binding = 0) buffer B_a { float a[]; };
uniform uint n;
void main(){
    uint i = gl_GlobalInvocationID.x;                // which one am I
    if (i >= n) return;                              // the last group has leftovers
    a[i] *= 2.0;
}
```

파이썬은 그룹 수를 정해 띄웁니다. 1000개면 256개짜리 그룹 4개, 1024개 스레드이고 마지막 24개는 `return` 합니다.

```python
glDispatchCompute((n + 255)//256, 1, 1)
```

numpy 의 벡터화와 사고방식이 같습니다. 그래서 모든 pass 에 numpy 쌍둥이가 자연스럽습니다. 한쪽은 `a[:n] *= 2`, 한쪽은 `a[i] *= 2.0`.

그룹 수의 상한은 보통 65535 라서 1차원으로는 1677만 개까지입니다. 그 이상은 2차원으로 띄웁니다. 이 책의 범위에서는 만나지 않습니다.

## 6장. 버퍼: 올리기, 내리기, 묶기

이 장의 코드가 1단계 파일의 GL 부분 전부입니다. 확인했습니다.

```python
from OpenGL.GL import *
from OpenGL.GL import shaders
import ctypes

class Buffer:
    "one ssbo. same bytes as the numpy array it was made from."
    def __init__(self, nparr, usage=GL_DYNAMIC_COPY):
        self.id = glGenBuffers(1)
        self.nbytes = nparr.nbytes
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.id)
        glBufferData(GL_SHADER_STORAGE_BUFFER, nparr.nbytes, nparr, usage)   # allocate + copy
    def upload(self, nparr):
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.id)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, nparr.nbytes, nparr)
    def download(self, out):
        "map = borrow the gpu memory as a cpu address for a moment, copy, give it back."
        glMemoryBarrier(GL_BUFFER_UPDATE_BARRIER_BIT)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.id)
        ptr = glMapBufferRange(GL_SHADER_STORAGE_BUFFER, 0, out.nbytes, GL_MAP_READ_BIT)
        ctypes.memmove(out.ctypes.data, ptr, out.nbytes)
        glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
        return out
    def zero(self):
        "simplest way to clear: upload zeros. (glClearBufferData is the one-liner alternative)"
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.id)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, self.nbytes, np.zeros(self.nbytes, 'uint8'))
    def bind_base(self, binding):
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, binding, self.id)
```

세 동작입니다. 올리기는 바이트 복사. 묶기(`bind_base`)는 "이 버퍼가 셰이더의 `binding = k` 자리다" 라고 연결하는 것. 내리기는 GPU 메모리를 잠깐 CPU 주소로 빌려 복사하는 것입니다.

**내리기의 진짜 비용은 복사가 아닙니다.** 내려받으려면 GPU 가 그 버퍼에 쓰는 일을 다 끝내야 하므로 CPU 가 GPU 를 기다립니다. 보통 CPU 는 GPU 보다 한두 프레임 앞서 명령을 쌓아 두는데, 내리기가 그 줄을 비웁니다. 그래서 매 프레임 내려받는 곳은 단 하나만 허용하고(2단계의 누적합), 그것도 9단계에서 없앱니다.

**PyOpenGL 함정 하나.** `glGetBufferSubData` 에 float32 배열을 넘기면 PyOpenGL 이 바이트 배열로 변환한 복사본에 쓰고 원본은 그대로이며, 크기가 맞지 않아 프로세스가 죽을 수 있습니다. 실제로 죽었습니다. 그래서 위 코드는 map 을 씁니다.

**셰이더와 uniform.** uniform 은 모든 스레드가 같은 값으로 읽는 상수입니다. dt, 중력, 격자 크기 같은 것들입니다. 파이썬 값의 타입으로 GL 함수를 고릅니다.

```python
def set_uniform(program, name, value):
    "type by python type. int -> uint, float -> float, 3-tuple -> ivec3 / vec3."
    loc = glGetUniformLocation(program, name)
    if loc == -1:
        return                          # unused -> removed by the driver. fine.
    if isinstance(value, bool):
        glUniform1i(loc, int(value))
    elif isinstance(value, int):
        glUniform1ui(loc, value)
    elif isinstance(value, float):
        glUniform1f(loc, value)
    elif len(value) == 3 and all(isinstance(v, (int, np.integer)) for v in value):
        glUniform3i(loc, *[int(v) for v in value])
    elif len(value) == 3:
        glUniform3f(loc, *[float(v) for v in value])
    else:
        raise TypeError(name)

class ComputeShader:
    LOCAL = 256
    def __init__(self, src):
        cs = shaders.compileShader(src, GL_COMPUTE_SHADER)
        self.program = shaders.compileProgram(cs, validate=False)
    def run(self, count, **uniforms):
        glUseProgram(self.program)
        set_uniform(self.program, 'n', count)
        for k, v in uniforms.items():
            set_uniform(self.program, k, v)
        glDispatchCompute((count + self.LOCAL - 1)//self.LOCAL, 1, 1)
        glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
```

uniform 위치가 −1 이면 "셰이더가 안 써서 드라이버가 지웠다" 는 뜻입니다. 기존 `shader.py` 는 여기서 예외를 던지는데, 그러면 디버깅 중 주석 처리 한 줄에 프로그램이 죽습니다. 건너뜁니다.

**선언은 배열이 정합니다.** 버퍼 선언을 손으로 쓰다 틀리는 것이 GPU 버그 1순위입니다. 배열의 shape 와 dtype 이 GLSL 타입을 결정하게 하면 틀릴 수 없습니다.

```python
def glsl_decl(binding, name, arr):
    "the array's shape/dtype decides the glsl type. (n,4) f32 -> vec4, (n,) f32 -> float, (n,) u32 -> uint"
    if arr.dtype == np.float32 and arr.ndim == 2 and arr.shape[1] == 4:
        t = 'vec4'
    elif arr.dtype == np.float32 and arr.ndim == 1:
        t = 'float'
    elif arr.dtype == np.uint32 and arr.ndim == 1:
        t = 'uint'
    else:
        raise TypeError(f'{name}: {arr.shape} {arr.dtype}')
    return f'layout(std430, binding = {binding}) buffer B_{name} {{ {t} {name}[]; }};'

def header(**arrays):
    lines = ['#version 430', f'layout(local_size_x = {ComputeShader.LOCAL}) in;']
    for b, (name, arr) in enumerate(arrays.items()):
        lines.append(glsl_decl(b, name, arr))
    lines.append('uniform uint n;')
    return '\n'.join(lines) + '\n'

def bind_all(**buffers):
    for b, buf in enumerate(buffers.values()):
        buf.bind_base(b)
```

`header(pos=pos, vel=vel)` 는 이것을 만듭니다. 언제든 `print` 해서 읽을 수 있습니다.

```glsl
#version 430
layout(local_size_x = 256) in;
layout(std430, binding = 0) buffer B_pos { vec4 pos[]; };
layout(std430, binding = 1) buffer B_vel { vec4 vel[]; };
uniform uint n;
```

규칙은 하나입니다. `header(...)` 와 `bind_all(...)` 에 같은 이름을 같은 순서로 넘긴다. 이름이 binding 번호가 됩니다.

## 7장. 순서, 경쟁, 원자적 더하기

N 개가 동시에 돈다는 것은 순서가 없다는 뜻입니다. 세 가지 규칙이 생깁니다.

**규칙 1. 읽는 배열에 쓰지 않는다.** 스레드 i 가 이웃 j 의 위치를 읽는 동안 스레드 j 가 자기 위치를 고치면, i 는 옛 값을 읽었을 수도 새 값을 읽었을 수도 있습니다. 실행마다 결과가 다릅니다. 해법은 결과를 다른 배열에 쓰는 것입니다. 위치 보정 Δp 는 `dp` 배열에 쓰고, 다음 pass 가 더합니다. Jacobi 는 `p` 를 읽어 `p2` 에 쓰고, 파이썬이 두 이름을 바꿉니다. 이것을 ping-pong 이라 합니다.

**규칙 2. 같은 칸에 여럿이 더할 때는 atomicAdd.** "셀 c 의 입자 개수에 1 더하기" 를 두 스레드가 동시에 하면, 둘 다 5 를 읽고 둘 다 6 을 써서 하나가 사라집니다. `atomicAdd(count[c], 1u)` 는 읽고 더하고 쓰기를 한 번에 해서 안전합니다. 대신 누가 먼저였는지는 매번 다릅니다. 그래서 이런 pass 의 검증은 "같은 순서" 가 아니라 "같은 집합" 으로 합니다.

**규칙 3. pass 사이에 barrier.** pass A 가 쓴 것을 pass B 가 읽으려면 "A 가 다 끝날 때까지 기다려" 가 필요합니다. `glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)` 이고, 6장의 `run` 이 매번 칩니다. 빠뜨리면 가끔만 틀리는 최악의 버그가 됩니다.

이 셋으로 모든 pass 를 네 종류로 나눌 수 있습니다. 어느 종류인지 알면 규칙이 정해집니다.

| 종류 | 스레드가 하는 일 | 예 | 규칙 |
|---|---|---|---|
| map | 자기 행 읽고 자기 행 씀 | 중력 적분, Δp 더하기 | 없음 |
| gather | 남의 행들을 읽고 자기 행에 씀 | 이웃 루프, 삼선형 보간 | 규칙 1 |
| stencil | gather 의 격자판. 이웃 6셀 | 발산, Jacobi | 규칙 1 |
| scatter | 남의 행에 씀 | 셀 개수 세기, 정렬 배치 | 규칙 2 |

## 8장. 화면에 그리기, 내려받지 않고

버퍼는 그냥 바이트라서, compute 가 쓴 SSBO 를 vertex shader 가 그대로 읽을 수 있습니다. VBO 도 attribute 도 없고 빈 VAO 하나만 묶습니다. `gl_VertexID` 가 "몇 번째 점이냐" 입니다.

```glsl
// vertex shader
#version 430
layout(std430, binding = 0) buffer B_pos { vec4 pos[]; };
uniform mat4 ViewProjection;
void main(){
    gl_Position = ViewProjection * vec4(pos[gl_VertexID].xyz, 1.0);
    gl_PointSize = 3.0;
}
```

```python
glEnable(GL_PROGRAM_POINT_SIZE)
glUseProgram(point_program)
set_uniform(point_program, ...)         # ViewProjection: use glUniformMatrix4fv as shader.py does
pos_buffer.bind_base(0)
glBindVertexArray(empty_vao)            # core profile needs *a* vao, even empty
glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
glDrawArrays(GL_POINTS, 0, n)
```

확인: 200개 점을 64×64 화면에 그리고 픽셀을 읽어 699 픽셀이 켜졌습니다. 카메라는 기존 `vector.py` 의 Camera 를 그대로 쓰되 `up = (0, 0, 1)` 로 바꿉니다.

## 9장. 시간을 앞으로: 적분과 상자

가장 단순한 물리입니다. 속도에 중력을 더하고, 위치에 속도를 더합니다. 속도를 먼저 갱신하고 그 새 속도로 위치를 옮기는 순서가 안정적입니다(semi-implicit Euler). 벽에 닿으면 벽 위치로 되돌리고 속도를 반으로 줄여 뒤집습니다.

```python
def step1_np(pos, vel, n, dt, g, lo, hi):
    "gravity, move, bounce on the box walls (half the speed back)."
    p = pos[:n, :3]
    v = vel[:n, :3]
    v += np.array(g, dtype='float32')*dt
    p += v*dt
    for a in range(3):
        below = p[:, a] < lo[a]
        p[below, a] = lo[a]
        v[below, a] *= -0.5
        above = p[:, a] > hi[a]
        p[above, a] = hi[a]
        v[above, a] *= -0.5
```

```glsl
uniform float dt; uniform vec3 g; uniform vec3 lo; uniform vec3 hi;
void main(){
    uint i = gl_GlobalInvocationID.x; if (i >= n) return;
    vec3 v = vel[i].xyz + g*dt;
    vec3 p = pos[i].xyz + v*dt;
    for (int a = 0; a < 3; a++) {
        if (p[a] < lo[a]) { p[a] = lo[a]; v[a] *= -0.5; }
        if (p[a] > hi[a]) { p[a] = hi[a]; v[a] *= -0.5; }
    }
    pos[i].xyz = p;
    vel[i].xyz = v;
}
```

두 코드를 나란히 읽어 보세요. 같은 문장입니다. 확인: 1000개 입자를 120스텝 돌린 뒤 두 결과의 차이가 정확히 0 이었습니다. 둘 다 float32 로 같은 순서의 연산을 하기 때문입니다.

dt 는 1/60 초로 고정합니다. 실제 프레임 시간을 쓰면 실행마다 결과가 달라져 검증이 불가능합니다. 느리면 서브스텝을 늘립니다.

## 10장. 격자라는 자

원점, 셀 크기 h, 셀 개수 (nx, ny, nz). 이 셋이 격자이고, 격자는 "점이 어느 셀에 있나" 와 "셀 번호가 어느 칸인가" 를 답하는 자입니다.

```python
class Grid:
    def __init__(self, origin=(0,0,0), size=(1,1,1), h=0.02):
        self.origin = np.array(origin, dtype='float32')
        self.h = float(h)
        self.dims = tuple(int(round(s/h)) for s in size)
    @property
    def ncell(self):
        nx, ny, nz = self.dims
        return nx*ny*nz
    def cell_coord(self, pos):
        "pos (n,4) -> (n,3) int, clamped into the grid."
        c = np.floor((pos[:, :3] - self.origin)/self.h).astype('int64')
        return np.clip(c, 0, np.array(self.dims) - 1)
    def cell_index(self, coord):
        "(n,3) -> (n,)   x + nx*(y + ny*z)"
        nx, ny, nz = self.dims
        return coord[:, 0] + nx*(coord[:, 1] + ny*coord[:, 2])
    def uniforms(self):
        return {'origin': tuple(float(v) for v in self.origin), 'h': self.h, 'dims': self.dims}
```

```glsl
uniform vec3 origin; uniform float h; uniform ivec3 dims;
ivec3 cell_coord(vec3 p){ return clamp(ivec3(floor((p - origin)/h)), ivec3(0), dims - 1); }
uint  cell_index(ivec3 c){ return uint(c.x + dims.x*(c.y + dims.y*c.z)); }
ivec3 coord_of(uint i){ int x = int(i) % dims.x; int y = (int(i)/dims.x) % dims.y; int z = int(i)/(dims.x*dims.y); return ivec3(x, y, z); }
```

같은 공식이 두 언어로 있습니다. 셀 번호는 x 가 가장 빨리 도는 순서입니다. 그러면 `(nz, ny, nx)` 모양의 numpy 배열을 `ravel()` 한 순서와 같아서, 격자 필드의 numpy 참조 구현을 3차원 배열로 편하게 쓰고 GPU 의 1차원 버퍼와 바로 비교할 수 있습니다. 17장에서 씁니다.

이 자 하나가 세 가지 일을 합니다. 입자의 이웃 탐색(14장), 격자 속도장(17장), 관심영역의 두 번째 격자(18장). 격자는 상태를 갖지 않는 값 객체라서 인스턴스를 하나 더 만들면 두 번째 격자가 됩니다.

## 11장. numpy 쌍둥이와 검증

pass 하나는 세 가지로 이루어집니다. 쓰는 열의 목록(묶는 순서), numpy 함수, GLSL 본문. 검증은 같은 입력을 두 쪽에 넣고 출력을 비교하는 것입니다.

- map, gather, stencil 은 `np.allclose` 로 비교합니다. 덧셈 순서가 달라 float32 끝자리가 다를 수 있으니 허용오차를 둡니다.
- scatter 는 순서가 비결정이라 집합으로 비교합니다. 정렬된 인덱스는 셀 구간마다 정렬해서 비교합니다.
- 서로 상쇄되는 항의 합(PBF 의 Δp)은 결과가 항 하나보다 훨씬 작아서 상대오차가 커 보입니다. 항의 크기에 대해 오차를 판단합니다.

디버그 절차는 하나입니다. GPU 로 k 프레임 돌리고 전부 내려받고, 같은 상태에서 numpy 로 한 스텝 돌리고, pass 마다 비교해서 처음 어긋나는 pass 를 찾습니다. GPU 코드에는 print 가 없으므로 이것이 유일한 현미경입니다.

이 책을 쓰면서 이 방법이 실제로 버그를 잡았습니다. PBF 논문은 입자 질량을 1 로 두어 수식에 질량이 안 보입니다. SI 단위로 질량 8g 을 쓰면서 그 수식을 그대로 옮기자 Δp 가 수십 m 가 나왔습니다. numpy 쌍둥이와 GPU 가 같은 틀린 값을 냈기 때문에 "둘이 같다" 는 검증으로는 못 잡고, "값의 크기가 말이 되나" 하는 검증으로 잡았습니다. 15장에 고친 수식이 있습니다. 교훈은 둘입니다. 쌍둥이 비교는 번역 오류를 잡고, 크기 검사는 수식 오류를 잡는다. 둘 다 필요합니다.

## 12장. 병목의 세 종류

GPU 가 느려지는 이유는 셋뿐이고, 이 프로젝트에서 셋을 다 만납니다.

**대역폭.** 메모리를 얼마나 옮기나. Jacobi 는 셀마다 이웃 6개를 읽고 하나를 씁니다. 100³ 셀에 50회면 프레임당 1.6GB 입니다. 해법은 덜 반복하기(red-black, multigrid) 와 덜 읽기(열을 따로 두는 것, 4장).

**지연.** 무작위 위치를 읽을 때 한 번 기다리는 시간. 이웃 루프는 셀마다 흩어진 입자를 읽습니다. 해법은 입자를 셀 순서로 재정렬해서 이웃이 메모리에서도 이웃이 되게 하는 것(9단계).

**동기화.** CPU 가 GPU 를 기다리는 것. 내려받기가 이것입니다(6장). 해법은 내려받지 않기.

측정 습관은 이렇습니다. pass 앞뒤로 `glFinish()` 를 부르고 `perf_counter()` 로 재서 함수 docstring 에 적습니다. `glFinish` 는 측정할 때만 씁니다. 평소에 부르면 그 자체가 동기화 병목입니다.

---

# 제3부. 단계적 진행

## 13장. 1단계: 떨어지는 입자

지도의 상자 셋(데이터, 계산, 화면)이 전부 이 한 파일에 있습니다. 목표는 "numpy 배열이 GPU 버퍼가 되고, compute 가 돌고, 그 버퍼가 화면에 찍힌다" 를 한 화면에서 보는 것입니다.

**보이는 것.** 입자 1000개가 1m 상자 안에서 떨어져 바닥에 튕깁니다. 키 하나로 numpy 계산과 GPU 계산을 바꿉니다. 두 모드의 결과가 같습니다.

**파일 구조.** 위에서 아래로 읽히는 순서입니다.

```
fluid/step1_fall.py
  1. constants        N, DT, G, LO, HI                       (SI, z-up)
  2. data             pos, vel : (N,4) float32               4장
  3. step_np          9장의 numpy 함수
  4. STEP_GLSL        9장의 GLSL 본문
  5. gl plumbing      Buffer, set_uniform, ComputeShader, header, bind_all     6장
  6. draw             point shader (gl_VertexID), empty vao                     8장
  7. window loop      glfw window, key toggles the mode, fixed dt
  8. tests            test_np_gl_equal : run both 120 steps, compare
```

**핵심 코드.** 6, 8, 9장의 코드가 그대로입니다. 새로 붙는 것은 조립뿐입니다.

```python
pos = np.zeros((N, 4), 'float32'); pos[:, :3] = np.random.rand(N, 3)
vel = np.zeros((N, 4), 'float32')
buf_pos, buf_vel = Buffer(pos), Buffer(vel)
step_gl = ComputeShader(header(pos=pos, vel=vel) + STEP_GLSL)

def update_np():
    step1_np(pos, vel, N, DT, G, LO, HI)
    buf_pos.upload(pos)                      # numpy is the owner; show its result

def update_gl():
    bind_all(pos=buf_pos, vel=buf_vel)
    step_gl.run(N, dt=DT, g=G, lo=LO, hi=HI)  # gpu is the owner now; nothing comes back
```

두 함수의 차이가 이 단계의 요점입니다. numpy 모드는 매 프레임 올립니다. GPU 모드는 아무것도 내려받지 않습니다. 화면은 8장의 방법으로 `buf_pos` 를 직접 읽습니다.

**창.** 기존 `test_window.py` 는 키 입력마다 print 하고 `run()` 끝에 glfw 를 종료해서 테스트에 쓰기 어렵습니다. 40줄짜리 창을 새로 둡니다. 숨긴 창을 만드는 옵션(`glfw.window_hint(glfw.VISIBLE, False)`) 이 있어야 화면 없이 테스트가 돕니다.

**검증.** 두 모드를 같은 초기 상태에서 120 스텝 돌려 비교합니다. 확인: 차이 0. 그리고 모든 z 가 0 과 1 사이인지 봅니다.

**함정.** GL 함수는 창을 만든 뒤에만 부를 수 있습니다. `Buffer` 를 모듈 수준에서 만들면 죽습니다. 창의 GL 버전이 4.3 미만이면 `#version 430` 에서 컴파일이 실패합니다. 첫 줄에 `glGetString(GL_VERSION)` 을 찍어 두세요.

**확인 질문.**
1. GPU 모드에서 numpy 배열 `pos` 는 몇 프레임 뒤에 얼마나 틀린 값을 갖고 있을까요. 답: 첫 프레임부터 전부 옛 값입니다. GPU 가 주인일 때 numpy 배열은 아무 뜻이 없습니다.
2. 스레드 1024개를 띄우고 `if (i >= n) return` 을 지우면 무슨 일이 생길까요. 답: 1000 번 이후의 24개가 버퍼 밖을 읽고 씁니다. 운이 좋으면 0, 나쁘면 다른 버퍼의 내용을 망칩니다.
3. `(N,3)` 으로 만들면 어디서 어떻게 틀릴까요. 답: 4장. 두 번째 입자부터 x 가 첫 입자의 두 번째 값이 됩니다. 에러는 없습니다.

## 14장. 2단계: 이웃 찾기

지도의 "계산" 상자에 neighbor 가 켜지고, 데이터에 cells 가 생깁니다. 이 단계 끝에서 Table 과 Grid 가 파일로 독립합니다.

**개념: 우체국.** 입자 i 의 이웃(거리 h 안)을 찾을 때 모든 입자와 비교하면 N² 입니다. 1000개가 numpy 로 28ms 였고(`highspeed/nptest.py`), 100만 개면 백만 배입니다. 대신 셀 크기를 h 로 잡은 격자에 입자를 분류합니다. 반경 h 안의 입자는 자기 셀과 주변 26셀 안에만 있습니다. 편지를 우편번호로 분류하는 것과 같아서 4단계입니다.

```python
cell = grid.cell_index(grid.cell_coord(pos))          # 1. write the zip code on each letter
count = np.bincount(cell, minlength=grid.ncell)        # 2. count letters per zip code
start = np.zeros(grid.ncell + 1, 'int64')
start[1:] = np.cumsum(count)                           # 3. where each zip code's pile starts
sorted_idx = np.argsort(cell, kind='stable')           # 4. put letters on their pile
# neighbors of i: for the 27 cells c around i -> sorted_idx[start[c]:start[c+1]] -> distance check
```

이것이 counting sort 입니다. GPU 에서는 같은 네 단계가 pass 넷이 됩니다. 확인했습니다.

```glsl
// cell : map.  buffers ppred, cell  (+ 10장의 GRID_GLSL)
void main(){ uint i = gl_GlobalInvocationID.x; if (i >= n) return;
    cell[i] = cell_index(cell_coord(ppred[i].xyz)); }

// count : scatter.  buffers cell, count.  count must be zeroed first
void main(){ uint i = gl_GlobalInvocationID.x; if (i >= n) return;
    atomicAdd(count[cell[i]], 1u); }

// scan : on the cpu for now.  download count -> cumsum -> upload start   (the one readback per frame)

// scatter : scatter.  buffers cell, start, fill, sorted.  fill must be zeroed first
void main(){ uint i = gl_GlobalInvocationID.x; if (i >= n) return;
    uint c = cell[i];
    uint slot = atomicAdd(fill[c], 1u);           // my seat inside the pile, claimed atomically
    sorted[start[c] + slot] = i; }
```

```python
class NeighborGPU:
    "the 4 passes. cpu scan in the middle."
    def __init__(self, grid, ps, cells):
        self.grid, self.ps, self.cells = grid, ps, cells
        self.cs_cell = ComputeShader(header(ppred=ps['ppred'], cell=ps['cell']) + GRID_GLSL + CELL_GLSL)
        self.cs_count = ComputeShader(header(cell=ps['cell'], count=cells['count']) + COUNT_GLSL)
        self.cs_scatter = ComputeShader(header(cell=ps['cell'], start=cells['start'], fill=cells['fill'], sorted=ps['sorted']) + SCATTER_GLSL)
    def build(self, n, gpu):
        g = self.grid
        bind_all(ppred=gpu['ppred'], cell=gpu['cell']);            self.cs_cell.run(n, **g.uniforms())
        gpu['count'].zero(); gpu['fill'].zero()
        bind_all(cell=gpu['cell'], count=gpu['count']);            self.cs_count.run(n)
        count = gpu['count'].download(np.empty(g.ncell + 1, 'uint32'))        # cpu scan
        start = np.zeros(g.ncell + 1, 'uint32'); start[1:] = np.cumsum(count[:-1])
        gpu['start'].upload(start)
        bind_all(cell=gpu['cell'], start=gpu['start'], fill=gpu['fill'], sorted=gpu['sorted']); self.cs_scatter.run(n)
        return count, start
```

`start` 는 셀 수보다 하나 깁니다. 마지막 칸이 전체 개수라서 `start[c+1]` 이 항상 있습니다. cells 테이블의 모든 열을 `ncell + 1` 길이로 잡습니다.

**이웃 루프.** 이후 모든 gather pass 가 이 틀을 복사합니다.

```glsl
    vec3 p = ppred[i].xyz;
    ivec3 c0 = cell_coord(p);
    for (int dz = -1; dz <= 1; dz++)
    for (int dy = -1; dy <= 1; dy++)
    for (int dx = -1; dx <= 1; dx++) {
        ivec3 c = c0 + ivec3(dx, dy, dz);
        if (any(lessThan(c, ivec3(0))) || any(greaterThanEqual(c, dims))) continue;
        uint ci = cell_index(c);
        for (uint k = start[ci]; k < start[ci + 1]; k++) {
            uint j = sorted[k];
            if (j == i) continue;
            vec3 d = p - ppred[j].xyz;
            float r2 = dot(d, d);
            if (r2 >= h*h) continue;
            // ... per neighbor j, with d and r2
        }
    }
```

확인: 이 루프로 이웃 수를 세는 pass 를 만들어 전수 비교와 맞췄습니다. 3000개 입자, 8000 셀, 전 입자 일치.

**작은 공.** 이웃 루프에 스프링 하나를 넣으면 공이 됩니다. 겹친 깊이에 비례해 밀어냅니다.

```glsl
// repel : gather.  reads pos, writes vel only -> no race.  uniform float r (ball radius), k, dt
    vec3 f = vec3(0.0);
    // neighbor loop with h = 2r:
    //     float dist = sqrt(r2); f += k*(2.0*r - dist) * (d/dist);
    vel[i].xyz += f*dt;
// then the map pass of chapter 9 moves pos and bounces on the box.
```

중력을 주면 모래처럼 쌓입니다. 이 단계의 목적은 물리가 아니라 이웃 기계입니다. 스프링은 딱딱해서 서브스텝 4 ~ 8 이 필요합니다.

**여기서 태어나는 부품.** 파일에 같은 모양이 세 번 반복됩니다. "이름 있는 배열들 + 개수 n" 이 입자와 셀에 각각 있고, "격자 수학" 이 numpy 와 GLSL 에 각각 있고, "np 함수 + GLSL + 열 목록" 이 pass 마다 있습니다. 셋을 떼어냅니다.

Table 은 같은 길이의 numpy 배열 몇 개와 n 을 가진 이름공간입니다. 숨은 것이 없습니다. `vars(t)` 로 전부 보입니다.

```python
KINDS = {'float': ((), 'float32'), 'vec4': ((4,), 'float32'), 'uint': ((), 'uint32')}

def make_array(capacity, kind):
    shape, dtype = KINDS[kind]
    return np.zeros((capacity, *shape), dtype=dtype)

class Table:
    "a namespace of same-length numpy arrays, plus n. nothing else."
    def __init__(self, capacity, **kinds):
        self.capacity = capacity
        self.n = 0
        self.names = tuple(kinds)
        for name, kind in kinds.items():
            setattr(self, name, make_array(capacity, kind))

def append(t, n, **values):
    "rent rows [t.n, t.n+n), fill from values. returns the slice."
    rows = slice(t.n, t.n + n)
    if rows.stop > t.capacity:
        raise OverflowError(f'capacity {t.capacity} < {rows.stop}')
    for name, value in values.items():
        getattr(t, name)[rows] = value
    t.n = rows.stop
    return rows

ps = Table(100_000, pos='vec4', vel='vec4', ppred='vec4', cell='uint', sorted='uint')
cells = Table(grid.ncell + 1, count='uint', start='uint', fill='uint')
```

capacity 가 고정인 이유는 GPU 버퍼가 크기를 못 바꾸기 때문이고, 활성 행이 앞에서부터 연속인 이유는 정확히 n 개의 스레드만 띄우기 위해서입니다. 입자를 지울 일이 생기면 마지막 행과 바꿔치기하고 n 을 줄입니다. 이 두 가지 때문에 기존 UnitArray 의 free list 와 active 마스크가 필요 없습니다.

GPU 미러는 백엔드가 `(table, name)` 을 키로 들고 있습니다. Table 은 GL 을 모릅니다. Grid 는 10장 그대로 `grid.py` 로 갑니다. pass 는 세 값을 묶은 작은 객체가 되고, 백엔드 둘이 그것을 돌립니다.

```python
class Pass:
    def __init__(self, name, buffers, np_func, glsl, snippets=()):
        self.name, self.buffers, self.np, self.glsl, self.snippets = name, buffers, np_func, glsl, snippets

class NumpyBackend:
    def run(self, p, tables, count, **params):
        arrays = {name: getattr(tables[t], name) for t, name in p.buffers}
        p.np(n=count, **arrays, **params)

class ComputeBackend:
    def run(self, p, tables, count, **params):
        prog = self.programs.get(p.name) or self.compile(p, tables)     # header from the arrays + snippets + body
        bind_all(**{name: self.buffer(tables[t], name) for t, name in p.buffers})
        if 'grid' in params:
            params = {**params, **params.pop('grid').uniforms()}
        prog.run(count, **params)
```

**검증.** (1) `count` 가 `np.bincount` 와 같다. (2) 셀 구간별 `sorted` 의 집합이 numpy 와 같다. (3) 이웃 수가 전수 비교와 같다. 셋 다 확인했습니다.

**함정.** `count` 와 `fill` 을 매 스텝 0 으로 만드는 것을 잊으면 조용히 누적됩니다. `cell_coord` 의 clamp 는 상자 밖으로 나간 입자를 경계 셀에 몰아넣습니다. 상자 충돌이 안에 가둔다는 전제가 깨지면 경계 셀이 비대해집니다.

**확인 질문.**
1. scan 이 없으면 무엇을 모를까요. 답: 각 셀의 더미가 정렬 배열의 어디서 시작하는지.
2. `scatter` 에서 `atomicAdd` 를 그냥 `fill[c]++` 로 바꾸면. 답: 두 입자가 같은 자리를 받아 하나가 사라집니다. 가끔만.
3. 셀 크기를 h 의 절반으로 하면 루프는 몇 셀을 봐야 할까요. 답: 5×5×5 = 125셀. 셀당 입자는 1/8 이라 후보 수는 비슷하지만 루프 오버헤드가 늡니다. 셀 크기 = h 가 기준입니다.

## 15장. 3단계: 물이 되다 (PBF)

계산 상자에 pbf 가 켜집니다. ps 에 `ppred dp lam rho` 열이 늡니다.

**개념.** 입자마다 반경 h 안 이웃의 빽빽함을 잽니다. 그것이 밀도입니다. 밀도가 1000 kg/m³ 보다 높으면 이웃이 너무 가까운 것이니 서로 밀어내도록 위치를 고칩니다. 힘과 가속을 거치지 않고 위치를 직접 고치기 때문에 큰 dt 에도 안 터집니다. 이것이 Position Based Fluids 입니다.

**커널.** 거리에 따른 가중치입니다. 가까우면 크고 h 에서 0 입니다. 밀도에는 부드러운 poly6 를, 미는 방향에는 중심 근처에서 기울기가 살아 있는 spiky 를 씁니다.

```glsl
const float PI = 3.14159265;
float poly6(float r2){ float x = max(h*h - r2, 0.0); return 315.0/(64.0*PI*pow(h, 9.0)) * x*x*x; }
vec3 spiky_grad(vec3 d){ float r = length(d); if (r < 1e-6) return vec3(0.0); float x = h - r; return -45.0/(PI*pow(h, 6.0)) * x*x * (d/r); }
```

`h` 는 GRID_GLSL 이 선언한 uniform 을 같이 씁니다. 셀 크기와 커널 반경이 같은 값이기 때문입니다.

**수식.** d = p_i − p_j, 입자 질량 m 은 모두 같습니다.

- 밀도 `ρ_i = m Σ_j W(|d|)`. 자기 자신 포함. 루프는 j = i 를 건너뛰므로 `m·W(0)` 을 루프 밖에서 더합니다.
- 제약 `C_i = max(ρ_i/ρ0 − 1, 0)`. 표면에서 밀도가 모자라 서로 당기는 것을 막으려고 0 아래를 자릅니다.
- `∇_i = (m/ρ0) Σ_j ∇W(d)`, `S = |∇_i|² + Σ_j |(m/ρ0) ∇W(d)|²`
- `λ_i = −C_i / (S + ε)`
- `Δp_i = (m/ρ0) Σ_j (λ_i + λ_j + s_corr) ∇W(d)`, `s_corr = −k (W(|d|)/W(Δq))⁴`, Δq = 0.2h

**논문과 다른 곳이 m 입니다.** 논문은 질량을 1 로 두어 m 이 안 보입니다. SI 에서 m = 8g 을 쓰면서 m 을 빼면 λ 가 만 배 넘게 작아지고 s_corr 가 상대적으로 거대해져 Δp 가 수십 m 가 됩니다. 실제로 그렇게 나왔습니다(11장). 또 s_corr 는 λ 와 같은 단위(m²)라서 논문의 k = 0.1 을 그대로 쓰면 안 됩니다. λ 를 내려받아 그 전형값의 1/10 로 잡습니다.

**GLSL.** 두 pass 입니다. 확인: 전수 비교 numpy 와 같았습니다(상대오차 3e-7).

```glsl
// lam : gather.  buffers ppred, start, sorted, rho, lam.  uniforms mass, rho0, eps  (+ GRID + KERNEL)
void main(){ uint i = gl_GlobalInvocationID.x; if (i >= n) return;
    vec3 p = ppred[i].xyz;
    float r = mass*poly6(0.0);            // density includes myself
    vec3 gi = vec3(0.0); float s = 0.0;
    // neighbor loop:
            r += mass*poly6(r2);
            vec3 gr = mass*spiky_grad(d) / rho0;      // grad C = (m/rho0) sum gradW
            gi += gr; s += dot(gr, gr);
    // end loop
    rho[i] = r;
    float C = max(r/rho0 - 1.0, 0.0);
    lam[i] = -C / (dot(gi, gi) + s + eps); }

// dp : gather.  buffers ppred, start, sorted, lam, dp.  uniforms mass, rho0, k_corr, dq
void main(){ uint i = gl_GlobalInvocationID.x; if (i >= n) return;
    vec3 p = ppred[i].xyz;
    vec3 acc = vec3(0.0);
    float wq = poly6(dq*dq);
    // neighbor loop:
            float corr = -k_corr * pow(poly6(r2)/wq, 4.0);
            acc += (lam[i] + lam[j] + corr) * spiky_grad(d);
    // end loop
    dp[i].xyz = mass*acc / rho0; }
```

**numpy 쌍둥이는 전수 비교 행렬입니다.** n ≤ 5000 에서 가장 명백하게 맞는 참조입니다.

```python
def lam_np(ppred, n, h, mass, rho0, eps):
    p = ppred[:n, :3].astype('float64')
    d = p[:, None, :] - p[None, :, :]
    r2 = (d*d).sum(2)
    W = poly6_np(r2, h); W[r2 >= h*h] = 0
    rho = mass*W.sum(1)                         # includes self (r2 = 0)
    G = mass*spiky_grad_np(d, h)/rho0; G[r2 >= h*h] = 0
    gi = G.sum(1)
    S = (gi*gi).sum(1) + (G*G).sum((1, 2))
    C = np.maximum(rho/rho0 - 1, 0)
    return rho, -C/(S + eps), S
```

**파라미터.** 확인한 값입니다. 간격 d = 2cm, h = 2d = 4cm, m = ρ0 d³ = 8g 로 15³ 격자 배치를 살짝 흔든 것.

| 항목 | 값 | 비고 |
|---|---|---|
| 내부 밀도 | 1010.9 | ρ0 대비 +1%. 커널 합의 성질 |
| S 의 중앙값 | 1.07e3 | ε = 그 1% = 10.7 |
| λ 의 중앙값 | 2.5e-5 m² | k = 그 1/10 = 2.5e-6 |
| Δp 최대 | 2.5 mm | 1% 과밀 상태에서 한 번의 보정. s_corr 유무 차이 0.002 mm |
| 반복 | 3 ~ 4 | dt = 1/60, 서브스텝 1 ~ 2 |

**한 스텝.** 파이썬 함수 하나가 순서 그 자체입니다.

```python
def step(self, dt):
    run = self.backend.run
    ps, n = self.ps, self.ps.n
    run(predict, n, dt=dt, g=self.g)                     # map    : vel += g dt ; ppred = pos + vel dt
    self.neighbor.build(ps, 'ppred')                     # 14장의 4 pass, ppred 기준
    for _ in range(self.iters):
        run(lam, n, grid=self.grid, mass=self.mass, rho0=self.rho0, eps=self.eps)
        run(dp, n, grid=self.grid, mass=self.mass, rho0=self.rho0, k_corr=self.k, dq=0.2*self.grid.h)
        run(apply, n, lo=self.lo, hi=self.hi)            # map    : ppred += dp ; clamp to box
    run(velocity, n, dt=dt)                              # map    : vel = (ppred - pos)/dt
    run(xsph, n, grid=self.grid, c=0.01)                 # gather : dv = c sum (vel_j - vel_i) W
    run(finish, n)                                       # map    : vel += dv ; pos = ppred
```

`lam` 은 ppred 를 읽고 rho, lam 에 씁니다. `dp` 는 ppred, lam 을 읽고 dp 에 씁니다. `apply` 가 ppred 를 고칩니다. 7장의 규칙 1 이 pass 경계를 정했습니다.

**검증.** (1) lam, dp 가 전수 비교와 같다. (2) 안정 후 내부 rho 평균이 1000 ± 5%. (3) dt = 1/60 에서 터지지 않고 출렁인다. 6.25만 개(2cm)에서 시작해 50만 개(1cm)로.

**확인 질문.**
1. 밀도 합에 자기 자신을 빼면 어떻게 될까요. 답: 내부 밀도가 약 200 낮게 나와(m·W(0) ≈ 196) 모든 입자가 과소 밀도가 되고 물이 수축합니다.
2. `apply` 를 `dp` pass 안에 합치면. 답: 이웃이 읽는 ppred 를 쓰는 중에 고치게 되어 규칙 1 위반입니다.
3. 이웃 격자를 pos 로 만들고 ppred 로 λ 를 계산하면. 답: 예측 이동만큼 이웃이 빠집니다. 항상 ppred 기준입니다.

## 16장. 4단계: 벽과 장애물

cells 테이블에 `kind`, `sdf` 열이 생깁니다. 이후 격자와 파편이 같은 것을 씁니다.

**부호 거리(SDF).** 한 점에서 물체 표면까지의 거리인데 안이면 음수입니다. 구는 `length(p − c) − r`, 상자는 조금 길지만 한 줄입니다. 장애물을 SDF 함수로 정의하고, 격자 셀마다 값을 미리 구워 둡니다(`sdf` 열). 셀 종류(`kind`)는 sdf 가 0 이하면 고체, 아니면 공기이고 7단계에서 유체가 추가됩니다.

**입자 밀어내기.** 입자 위치의 sdf 를 삼선형 보간으로 읽어 음수면 기울기 방향으로 그만큼 밀어냅니다. 기울기는 sdf 의 이웃 셀 차이입니다. 상자 벽도 같은 방법으로 통일할 수 있지만, 상자는 clamp 가 더 싸고 명확해서 남겨 둡니다.

**격자 경계.** 17장의 Jacobi 와 발산은 고체 셀에서 "속도 0, 압력은 이웃 복사" 로 처리합니다. 벽 처리를 하는 헬퍼 함수(`P(q)`, `UX(q)`)가 `kind` 를 보게 하면 됩니다. 나머지 코드는 안 바뀝니다.

**두 격자 준비.** SDF 는 함수라서 격자마다 자기 해상도로 굽습니다. 18장의 roi 격자가 같은 장애물을 더 정밀하게 갖게 됩니다.

**검증.** 구 장애물 위에 입자를 떨어뜨려 안으로 들어가는 입자가 0 인지 셉니다. sdf 를 내려받아 numpy 로 구운 것과 비교합니다.

## 17장. 5단계: 격자 속도장 (MAC)

계산 상자에 mac 이 켜집니다. cells 에 `u u2 p p2 div smoke smoke2` 가 생깁니다. 입자는 잠시 쉬고, 연기로 격자를 배웁니다.

**개념.** 셀마다 속도 화살표가 있는 벡터장입니다. 한 스텝은 세 동작입니다. 값을 흐름을 따라 옮기고(이류), 힘을 더하고, 압축되지 않게 압력으로 바로잡습니다(투영).

**면에 두는 이유.** 속도를 셀 중심에 두면 발산을 양옆 셀 차이로 재야 하는데, 한 칸 건너뛴 셀만 보게 되어 짝수 셀과 홀수 셀이 서로 모르는 두 무리로 갈라집니다. 체스판 무늬가 남고 발산이 0 으로 가지 않습니다. 확인: 셀 중심 방식은 Jacobi 3000회에도 발산 rms 가 19 에서 13.5 에 멈췄습니다. 속도를 셀의 면에 두면(MAC) 발산이 "오른쪽 면 빼기 왼쪽 면" 으로 정확히 정의되고 0 으로 갑니다.

**압축 저장.** 셀 c 가 자기 마이너스 쪽 면 셋을 소유합니다. `u[c].x` 는 c 의 −x 면의 x 속도, `.y` 는 −y 면, `.z` 는 −z 면. 도메인의 + 쪽 벽 면과 첫 셀들의 − 쪽 벽 면은 0 입니다. Table 하나, Grid 하나로 MAC 이 됩니다.

**세 pass.** 모두 stencil, dispatch 는 ncell. 확인: numpy 참조와 같았습니다(최대 차이 3.6e-7).

```glsl
// div : buffers u, div.   UX(q) = 0 outside the grid (solid wall)
float UX(ivec3 q){ if (any(lessThan(q, ivec3(0))) || any(greaterThanEqual(q, dims))) return 0.0; return u[cell_index(q)].x; }
float UY(ivec3 q){ if (any(lessThan(q, ivec3(0))) || any(greaterThanEqual(q, dims))) return 0.0; return u[cell_index(q)].y; }
float UZ(ivec3 q){ if (any(lessThan(q, ivec3(0))) || any(greaterThanEqual(q, dims))) return 0.0; return u[cell_index(q)].z; }
void main(){ uint c = gl_GlobalInvocationID.x; if (c >= n) return;
    ivec3 q = coord_of(c);
    div[c] = (UX(q + ivec3(1,0,0)) - u[c].x + UY(q + ivec3(0,1,0)) - u[c].y + UZ(q + ivec3(0,0,1)) - u[c].z) / h; }

// jacobi : buffers p, div, p2.   P(q) clamps = neumann wall (copy the neighbor)
float P(ivec3 q){ q = clamp(q, ivec3(0), dims - 1); return p[cell_index(q)]; }
void main(){ uint c = gl_GlobalInvocationID.x; if (c >= n) return;
    ivec3 q = coord_of(c);
    float s = P(q + ivec3(1,0,0)) + P(q - ivec3(1,0,0)) + P(q + ivec3(0,1,0)) + P(q - ivec3(0,1,0)) + P(q + ivec3(0,0,1)) + P(q - ivec3(0,0,1));
    p2[c] = (s - h*h*div[c]) / 6.0; }

// grad : buffers p, u.   writes only u[c], reads only p -> no race
float P(ivec3 q){ q = clamp(q, ivec3(0), dims - 1); return p[cell_index(q)]; }
void main(){ uint c = gl_GlobalInvocationID.x; if (c >= n) return;
    ivec3 q = coord_of(c);
    vec4 uc = u[c];
    uc.x = (q.x > 0) ? uc.x - (p[c] - P(q - ivec3(1,0,0)))/h : 0.0;
    uc.y = (q.y > 0) ? uc.y - (p[c] - P(q - ivec3(0,1,0)))/h : 0.0;
    uc.z = (q.z > 0) ? uc.z - (p[c] - P(q - ivec3(0,0,1)))/h : 0.0;
    u[c] = uc; }
```

Jacobi 는 이렇게 읽습니다. "내 압력은 이웃 여섯의 평균에서 내 발산만큼 보정한 값". 모든 셀이 동시에 이것을 수십 번 반복합니다. 정보가 한 칸씩 퍼지므로 국소 오류는 빨리, 전체 불균형은 느리게 사라집니다.

```python
src, dst = buf_p, buf_p2
for _ in range(50):
    bind_all(p=src, div=buf_div, p2=dst); cs_jacobi.run(ncell, **grid.uniforms())
    src, dst = dst, src                       # ping-pong: python swaps the names
```

**numpy 참조.** 배열을 `(nz, ny, nx)` 로 두면 `ravel()` 이 셀 번호 순서입니다(10장).

```python
def div_np(u, h):
    nz, ny, nx, _ = u.shape
    ux = np.zeros((nz, ny, nx + 1), 'float32'); ux[:, :, :nx] = u[..., 0]     # ux[..., nx] = 0 : +x wall
    uy = np.zeros((nz, ny + 1, nx), 'float32'); uy[:, :ny, :] = u[..., 1]
    uz = np.zeros((nz + 1, ny, nx), 'float32'); uz[:nz, :, :] = u[..., 2]
    return (ux[:, :, 1:] - ux[:, :, :-1] + uy[:, 1:, :] - uy[:, :-1, :] + uz[1:, :, :] - uz[:-1, :, :]) / h

def jacobi_np(p, div, h, iters):
    for _ in range(iters):
        pp = np.pad(p, 1, mode='edge')
        s = (pp[1:-1, 1:-1, :-2] + pp[1:-1, 1:-1, 2:] + pp[1:-1, :-2, 1:-1] + pp[1:-1, 2:, 1:-1] + pp[:-2, 1:-1, 1:-1] + pp[2:, 1:-1, 1:-1])
        p = ((s - h*h*div) / 6.0).astype('float32')
    return p

def grad_np(u, p, h):
    u = u.copy()
    u[:, :, 1:, 0] -= (p[:, :, 1:] - p[:, :, :-1]) / h
    u[:, 1:, :, 1] -= (p[:, 1:, :] - p[:, :-1, :]) / h
    u[1:, :, :, 2] -= (p[1:, :, :] - p[:-1, :, :]) / h
    return u
```

확인, 16³ 격자에 무작위 속도:

| Jacobi 반복 | 발산 rms (시작 38.2) |
|---|---|
| 50 | 0.28 |
| 300 | 0.008 |
| 3000 | 1e-5, float32 바닥 |

**이류와 부력.** 면 위치 fp 에서 속도 v 를 읽고, `fp − v·dt` 위치의 값을 읽어 옵니다. 속도 성분마다 자기 면 격자에서 삼선형 보간을 합니다. −x 면의 중심은 `origin + h·(i, j+.5, k+.5)` 입니다. 연기 밀도는 셀 중심(`+.5, +.5, +.5`)에서 같은 방법입니다. 부력은 연기가 있는 셀의 위쪽 면(z)에 `dt·α·smoke` 를 더하는 map 입니다. 이류는 값이 조금씩 뭉개집니다. 보이는 데 문제없고, 나중에 MacCormack 으로 바꿀 수 있습니다.

**한 스텝.** `advect_u(u → u2)` → `force(u2)` → `div` → `jacobi × K` → `grad` → `advect_smoke(smoke → smoke2)`. 파이썬이 `u/u2`, `p/p2`, `smoke/smoke2` 이름을 바꿉니다.

**보기.** 새 인프라 없이 봅니다. 셀마다 점 하나(`gl_VertexID` → `coord_of` → 셀 중심), 밝기 = smoke, additive blend. 나중에 ray-march.

**검증.** (1) 세 pass 가 numpy 와 같다. (2) 100³ 에서 Jacobi 50회 후 발산 rms 가 1/100 이하. (3) 연기가 상자 안에서 떠오르고 소용돌이친다.

**확인 질문.**
1. `grad` 에서 `q.x > 0` 조건을 빼면. 답: 벽 면의 속도가 0 이 아니게 되어 물이 벽을 통과합니다.
2. Jacobi 50회로 부족하면 어떤 순서로 바꿀까요. 답: red-black Gauss-Seidel(같은 코드, 두 번 나눠 호출, 약 2배), 그 다음 multigrid.
3. `div` 에서 `+x` 이웃이 격자 밖이면 왜 0 인가. 답: 그 면이 벽이라 그 면의 법선 속도가 0 이기 때문입니다.

## 18장. 6단계: 두 격자 (world + roi)

Grid 인스턴스가 둘이 됩니다. 이 단계의 코드는 거의 없고, 대부분이 "어떤 값을 어디서 읽나" 의 결정입니다.

**구조.** world 는 1m 를 2cm 로 나눈 50³, roi 는 그 안 10cm 를 2mm 로 나눈 50³. 같은 Table 종류, 같은 pass, 다른 grid 파라미터. 17장의 pass 들은 `grid` 를 uniform 으로 받으므로 두 번 호출하면 됩니다.

**결합.** roi 의 경계 면 속도를 world 의 속도장에서 삼선형 보간으로 읽어 고정합니다(Dirichlet 경계). 그 안쪽은 roi 가 스스로 풉니다. world 는 roi 를 모릅니다(일방향). 이것이 "거시 흐름은 항상 돈다" 의 구현입니다. roi 를 끄면 world 만 남습니다.

**검증.** roi 없는 world 의 흐름을, roi 를 켜고 roi 안에서 world 값으로 초기화했을 때 roi 가 같은 흐름을 (더 세밀하게) 재현하는지. 발산이 roi 안에서도 0 으로 가는지.

**함정.** 두 격자의 h 비율이 정수(여기선 10)여야 면이 정렬됩니다. roi 경계에서 world 의 셀 종류(고체)가 roi 의 sdf 와 일치해야 합니다. 같은 SDF 함수를 각자 굽기 때문에 자동으로 맞습니다.

## 19장. 7단계: FLIP (거시 물)

입자(14장)와 격자(17장)를 합칩니다. 입자가 속도를 들고 다니고, 격자가 압축 불가를 풉니다. 15장의 PBF 는 그대로 두고, 거시 물은 이것으로 갑니다.

**한 스텝.**
1. 입자 → 격자 (P2G). 면마다 주변 셀의 입자를 gather 해서 삼선형 가중 평균 속도를 만듭니다. 14장의 counting sort 를 그대로 쓰므로 atomicAdd 가 필요 없고 결정적입니다. (scatter 로 하면 float 원자 덧셈이 필요한데 core GLSL 에 없습니다.)
2. 셀 종류. 입자가 하나라도 있는 셀은 유체, 아니면 공기, sdf 로 고체.
3. 격자에서 힘, 발산, Jacobi, 기울기. 공기 셀은 압력 0(Dirichlet), 고체는 이웃 복사(Neumann). `P(q)` 헬퍼가 `kind` 로 분기합니다.
4. 격자 → 입자 (G2P). FLIP 은 `v_p += sample(u_new − u_old)`, PIC 는 `v_p = sample(u_new)`. 0.95 : 0.05 로 섞습니다. `u_old` 열이 하나 더 필요합니다.
5. 입자 이동 `p += sample_u(p)·dt` (RK2 가 낫습니다), 고체 밖으로 밀어내기.

**검증.** 물이 수평으로 가라앉고 유체 셀 수가 ±10% 안에서 유지됩니다.

## 20장. 8단계: ROI 의 파편

14장의 "작은 공" 이 진짜 목적을 만납니다. 파편 테이블은 입자 테이블과 같은 모양이고, pass 는 셋입니다.

- `repel` : 공끼리 스프링(14장). 파편 반지름의 2배를 h 로 하는 자기 격자.
- `drag` : roi 속도장을 삼선형으로 읽어 `v += k_d (u − v) dt`. 물이 파편을 밉니다. 파편은 물을 밀지 않습니다(일방향).
- `integrate` : 중력, 이동, 상자 clamp, sdf 밀어내기(16장).

**검증.** 흐름을 끄면 파편이 바닥에 쌓이고, 흐름을 켜면 흐름을 따라 갑니다. 장애물을 통과하는 파편이 0 입니다.

## 21장. 9단계: 실시간으로

바꾸는 것뿐이고 새로 배우는 것은 측정뿐입니다. 12장의 순서로 갑니다.

1. 측정표. pass 마다 `glFinish` 후 시간을 재고 표를 만듭니다. 추정하지 말고 잽니다.
2. 동기화 제거. CPU 누적합을 GPU prefix sum(두 pass)으로 바꿉니다. 프레임당 유일한 내려받기가 사라집니다.
3. 지연 개선. 입자 열들을 `sorted` 순서로 복사하는 pass 를 추가합니다. 이웃이 메모리에서도 이웃이 됩니다. 이웃 루프의 `sorted[k]` 간접 참조가 사라집니다.
4. 대역폭 개선. Jacobi 를 red-black 으로, 그래도 부족하면 multigrid.

각 교체 뒤에 11장의 검증을 다시 돌립니다. 빨라진 코드가 같은 답을 내는지가 유일한 기준입니다.

---

# 부록

## A. 함정 목록

- `(n,3)` 을 올리고 `vec3[]` 로 읽기. 확인: `[0,3,6,9]` 가 `[0,4,8,0]` 이 됩니다.
- `int64` 인덱스 업로드. GPU 는 uint32.
- `glGetBufferSubData` 에 float 배열 넘기기. 원본은 안 채워지고 죽을 수 있습니다. map 을 씁니다.
- uniform 위치 −1 에서 예외 던지기. 안 쓰는 uniform 은 사라집니다.
- pass 사이 barrier 누락. 가끔만 틀립니다.
- `count`, `fill` 을 0 으로 안 만들기.
- gather 가 읽는 배열에 쓰기. 항상 `dp`, `dv`, `u2` 같은 다른 열에.
- PBF 수식에서 질량 빼먹기, k 를 0.1 로 쓰기. Δp 가 수십 m 가 됩니다.
- 이웃 격자를 pos 로 만들고 ppred 로 계산하기.
- 셀 중심에 속도 두기. 발산이 0 으로 안 갑니다.
- `glFinish` 를 평소에 부르기. 그 자체가 동기화 병목입니다.
- GL 호출을 창 만들기 전에 하기. macOS 는 4.3 이 없어 compute 불가.

## B. 용어

| 용어 | 뜻 |
|---|---|
| SSBO | shader storage buffer object. 셰이더가 읽고 쓰는 바이트 버퍼 |
| std430 | SSBO 배열의 원소 간격 규칙 |
| dispatch | compute shader 를 그룹 수만큼 띄우기 |
| local_size | 한 그룹의 스레드 수. 여기선 256 |
| barrier | 앞 pass 의 쓰기가 끝난 뒤 다음 pass 가 읽게 하는 울타리 |
| atomicAdd | 읽고 더하고 쓰기를 한 번에. 동시 더하기 안전 |
| ping-pong | 읽는 배열과 쓰는 배열을 둘 두고 이름을 바꿔 가며 쓰기 |
| map / gather / scatter / stencil | pass 의 네 종류. 7장 |
| counting sort | 셀별 개수, 누적합, 배치의 3단계 정렬. 이웃 탐색의 뼈대 |
| 커널 W | 거리에 따른 가중치 함수. poly6, spiky |
| PBF | position based fluids. 밀도 제약을 위치 보정으로 푸는 입자 물 |
| MAC | 속도를 셀 면에 두는 격자 |
| 반 라그랑지 이류 | 뒤로 추적해서 값을 읽어 오는 안정한 이류 |
| Jacobi | 이웃 평균으로 압력을 반복 계산하는 가장 단순한 Poisson 해법 |
| SDF | 부호 거리. 표면까지 거리, 안이면 음수 |
| FLIP / PIC | 입자가 속도를 들고 격자가 압력을 푸는 하이브리드. 두 가지 되돌리기 방식 |
| P2G / G2P | 입자에서 격자로, 격자에서 입자로 값을 옮기기 |

## C. 참고 자료

- Stam, "Stable Fluids", SIGGRAPH 1999. 이류와 투영의 원형.
- Bridson, *Fluid Simulation for Computer Graphics* 2판. MAC, 투영, FLIP 의 교과서.
- Müller, Charypar, Gross, "Particle-Based Fluid Simulation for Interactive Applications", SCA 2003. poly6, spiky.
- Macklin, Müller, "Position Based Fluids", SIGGRAPH 2013. 15장의 수식(단위 질량 기준).
- Green, "Particle Simulation using CUDA", NVIDIA 2010. counting sort 이웃 격자.
- Crane, Llamas, Tariq, "Real-Time Simulation and Rendering of 3D Fluids", GPU Gems 3 ch.30. 3D 격자와 ray-march.
- Zhu, Bridson, "Animating Sand as a Fluid", SIGGRAPH 2005. FLIP.
- Müller, Ten Minute Physics #18, "How to write a FLIP water simulator". 가장 짧은 FLIP.
