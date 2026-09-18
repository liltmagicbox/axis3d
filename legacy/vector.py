from math import sqrt , acos, sin,cos, atan2, asin , radians, tan

def _dot(x1,y1,z1, x2,y2,z2):
    return x1*x2 + y1*y2 + z1*z2
def _cross(ax,ay,az, bx,by,bz):
    #xyzzy
    cx = ay*bz-az*by
    cy = az*bx-ax*bz
    cz = ax*by-ay*bx
    return cx,cy,cz
def _mag(x,y,z):
    "is norm, also."
    return sqrt(x**2+y**2+z**2)
def _mag2(x,y,z):
    return x**2+y**2+z**2
def _angle(a,b,c,  d,e,f):
    #costh = _dot(a,b,c, d,e,f) / ( _mag(a,b,c) * _mag(d,e,f) )
    costh = (a*d + b*e + c*f) / sqrt( (a**2+b**2+c**2)*(d**2+e**2+f**2)  )
    return acos(costh)

def _normalize(x,y,z):
    mag = sqrt(x**2+y**2+z**2)
    return x/mag, y/mag, z/mag



class Vec:
    __slots__ = ('x','y','z')
    EPS = 1e-6#0.000001 EPSILON
    DEFAULT_AXIS = (0,1,0)
    def __init__(self, x,y,z):
        self.x = x
        self.y = y
        self.z = z
    def set(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
    def copy(self):
        return self.__class__(self.x,self.y,self.z)

    def __str__(self):
        return f"{self.__class__.__name__} {self.x:.6f} {self.y:.6f} {self.z:.6f}"
    def __getitem__(self,idx):
        if idx == 0:
            return self.x
        elif idx == 1:
            return self.y
        elif idx == 2:
            return self.z
        else:
            raise IndexError('Vec idx 2 max')
    
    #=== operands
    def __add__(self, other):
        return self.__class__(self.x+other.x,self.y+other.y,self.z+other.z)
    def __sub__(self, other):
        return self.__class__(self.x-other.x,self.y-other.y,self.z-other.z)
    def __iadd__(self, other):
        self.set(self.x+other.x, self.y+other.y, self.z+other.z)
        return self
    def __isub__(self, value):
        self.set(self.x-other.x, self.y-other.y, self.z-other.z)    
        return self
    
    def __mul__(self, value):
        return self.__class__(self.x*value, self.y*value, self.z*value)
    def __truediv__(self, value):
        return self.__class__(self.x/value, self.y/value, self.z/value)
    def __floordiv__(self, value):
        return self.__class__(self.x//value, self.y//value, self.z//value)
    def __imul__(self, value):
        self.set(self.x*value, self.y*value, self.z*value)
        return self
    def __itruediv__(self, value):
        self.set(self.x/value, self.y/value, self.z/value)
        return self
    def __ifloordiv__(self, value):
        self.set(self.x//value, self.y//value, self.z//value)
        return self
    #=================    
    
    #=== additional
    def __neg__(self):
        return self * -1
    def equal(self, other):
        "sef Vec.EPS if needed. 1e-6 0.000_001"
        return (self-other).mag < self.EPS
    def __eq__(self, other):
        return self.equal(other)
    def __ne__(self, other):
        return not self.equal(other)

    def __len__(self):
        #print('getting len to *vec')
        return self.mag
    def __bool__(self):#simple fast 0 checker.
        return self.mag > EPS

    #=== vector property
    #NOTE: norm = mag = len
    #normalized = hat
    def normalize(self):
        try:
            return self / self.mag
        except ZeroDivisionError:
            return 0
    @property
    def hat(self):
        return self.normalized
    @property
    def norm(self):
        return self.mag
        
    @property
    def mag2(self):
        "before sqrt-ed"
        return self.x**2+self.y**2+self.z**2
    @property
    def mag(self):
        "magnitude =norm =length"
        return sqrt(self.x**2+self.y**2+self.z**2)

    #=== vector operations
    def dot(self,other):
        "sum( x1x2, y1y2, z1z2 )"
        return _dot(self.x,self.y,self.z,  other.x,other.y,other.z)
    def cross(self,other):
        "RH NON-normalized"
        cx,cy,cz = _cross(self.x,self.y,self.z,  other.x,other.y,other.z)
        return self.__class__(cx,cy,cz)
    
    #=== vector calculations
    def angle(self, other):
        "angle between vecs[0-pi]. cos() = a.b/|a||b|"
        #return _angle(self.x,self.y,self.z, other.x,other.y,other.z)
        return _angle(self.x,self.y,self.z, other.x,other.y,other.z)
        
    def lookat(self,other):
        axis = self.cross(other)
        angle = self.angle(other)
        self.rotate(angle, axis)

    def rotate(self, rad, axis=None):
        "pos vector shall rotated"
        #https://gaussian37.github.io/vision-concept-axis_angle_rotation/
        #https://en.wikipedia.org/wiki/Category:Rotation_in_three_dimensions
        #https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation
        #https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
        if axis is None:
            x,y,z = self.DEFAULT_AXIS
        else:
            x,y,z = axis.x,axis.y,axis.z

        #easy and safe..
        #mag = _mag(x,y,z)
        #x,y,z = x/mag, y/mag, z/mag
        x,y,z = _normalize(x,y,z)
        #get quat
        qw,qx,qy,qz = _angle_axis_to_quat(rad, x,y,z)
        #get xyzdir
        rx,ry,rz = _quat_rotate_xyz(qw, qx,qy,qz,  self.x,self.y,self.z)
        self.x = rx
        self.y = ry
        self.z = rz







#https://en.wikipedia.org/wiki/Rotation_matrix
#ROTMAT. there were form axisangle, directly.!
#.. usually pose data is from 1,0,0, rotated x,y,z.
# and what about physics? x,y,z rotation speed..






#============================== CAMERA
#============================== CAMERA
#============================== CAMERA
#============================== CAMERA

def glperspective(fov, ratio, near, far):
    "fov=rad, perspective list is platten col-major mat."
    #import glm
    #print( glm.perspective(radians(40), 1.96,0.1,200).to_list() )
    #x = glperspective(40, 1.96, 0.1, 200)
    #print(x)
    #fov = radians(fov)
    f = 1/tan(fov/2)
    mat = [ f/ratio, 0, 0, 0,
      0,   f,  0, 0, 
      0,   0,  (far+near)/(near-far), -1,
      0,  0,   (2*far*near)/(near-far),  0]
    return mat


def gllookat(eye:Vec,center:Vec,up:Vec):
    """
    https://www.khronos.org/opengl/wiki/GluLookAt_code
    https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluLookAt.xml
    """
    #forawrd = center-eye
    forward = (center-eye).normalize()    
    side = forward.cross(up).normalize()# lh,rh, both fine. thats why side..
    up = side.cross(forward).normalize()
    
    sx,sy,sz = side
    ux,uy,uz = up
    fx,fy,fz = forward
    ex,ey,ez = eye
    #px,py,pz = eye.dot(side), eye.dot(up), eye.dot(forward)#simulates M1*M2
    px,py,pz = -eye.dot(side), -eye.dot(up), eye.dot(forward)#not right, side-effected.
    
    mixed = [
    sx,ux,-fx,0,
    sy,uy,-fy,0,
    sz,uz,-fz,0,
    px,py,pz, 1.0
    ]
    return mixed

def _gllookattest():
    import glm
    view = glm.lookAt( glm.vec3(0,0,1),glm.vec3(0,0,0), glm.vec3(0,1,0))
    print(view.to_list())    
    x = gllookat( Vec(0,0,1), Vec(0,0,0), Vec(0,1,0) )
    print(x)

    view = glm.lookAt( glm.vec3(1,2,3),glm.vec3(0.5,-0.2,0.3), glm.vec3(0,0,1))
    print(view.to_list())    
    x = gllookat( Vec(1,2,3), Vec(0.5,-0.2,0.3), Vec(0,0,1) )
    print(x)


def dot4(A,B):
    a,b,c,d = A
    x,y,z,w = B
    return a*x+b*y+c*z+d*w
def matmul4(A,B):
    a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,a13,a14,a15 = A
    b0,b1,b2,b3,b4,b5,b6,b7,b8,b9,b10,b11,b12,b13,b14,b15 = B
    
    row0 = a0,a1,a2,a3
    row1 = a4,a5,a6,a7
    row2 = a8,a9,a10,a11
    row3 = a12,a13,a14,a15
    
    col0 = b0,b4,b8,b12
    col1 = b1,b5,b9,b13
    col2 = b2,b6,b10,b14
    col3 = b3,b7,b11,b15

    m0 = dot4(row0,col0)
    m1 = dot4(row0,col1)
    m2 = dot4(row0,col2)
    m3 = dot4(row0,col3)
    
    m4 = dot4(row1,col0)
    m5 = dot4(row1,col1)
    m6 = dot4(row1,col2)
    m7 = dot4(row1,col3)
    
    m8 = dot4(row2,col0)
    m9 = dot4(row2,col1)
    m10 = dot4(row2,col2)
    m11 = dot4(row2,col3)
    
    m12 = dot4(row3,col0)
    m13 = dot4(row3,col1)
    m14 = dot4(row3,col2)
    m15 = dot4(row3,col3)
    return [m0,m1,m2,m3,m4,m5,m6,m7,m8,m9,m10,m11,m12,m13,m14,m15]


#def get_vpmat(eye, center, up_vector, fov,ratio,near,far):    

def _vpmat_test():
    import glm
    view = glm.lookAt( glm.vec3(0,0,1),glm.vec3(0,0,0), glm.vec3(0,1,0))
    pers = glm.perspective(1, 1.66,0.01,1000)
    #print(pers.to_list())
    x = glm.mul(pers,view)
    print(x.to_list())
        #view = gllookat(eye, center, up_vector)
        #projection =  glperspective(fov,ratio,near,far)
        #return mul4x4(view,projection)
    vv = gllookat( Vec(0,0,1), Vec(0,0,0), Vec(0,1,0) )
    pp = glperspective( 1, 1.66, 0.01, 1000)

    xx = matmul4(vv,pp)
    print(xx)

    print('#===')
    view = glm.lookAt( glm.vec3(5,6,7),glm.vec3(-1,-2,3), glm.vec3(0,0,1))
    pers = glm.perspective(1.25, 1.96,0.2,300)
    #print(pers.to_list())
    x = glm.mul(pers,view)
    print(x.to_list())
        #view = gllookat(eye, center, up_vector)
        #projection =  glperspective(fov,ratio,near,far)
        #return mul4x4(view,projection)
    vv = gllookat( Vec(5,6,7), Vec(-1,-2,3), Vec(0,0,1) )
    pp = glperspective( 1.25, 1.96, 0.2, 300)

    xx = matmul4(vv,pp)
    print(xx)
    
#_vpmat_test()


class Camera:
    """without vector. fastest-python.
    x front, all moving objects are.
    but screen coords is zup, RH, y is depth.
    """
    def __init__(self, fov=70, ratio=1.66, near=0.01,far=1000):
        self.fov = fov
        self.ratio = ratio
        self.near = near
        self.far = far

        #RH Z-up, y is depth. x right.
        self.up = (0,1,0)#simpliy change this to zup..

        self.position = (0,0,1)
        self.front = (0,0,-1)
        self.target = (0,0,0)

        self.sensitivity = 1.0
        self.yaw = radians(90)
        self.pitch = 0.0

        self.speed = 0

    def set_dxdy(self, dx,dy):
        "dx,dy range -1~1. y+up."
        yaw = self.yaw
        pitch = self.pitch
        mag = self.sensitivity
        yaw -= dx * mag
        pitch -= dy * mag

        r89 = radians(89)
        if pitch > r89:
            pitch = r89
        elif pitch < -r89:
            pitch = -r89

        vx = cos(yaw) * cos(pitch)
        vy = sin(pitch)
        vz = -sin(yaw) * cos(pitch)
        
        norm = sqrt(vx**2 + vy**2 + vz**2)
        direction = (vx/norm,vy/norm,vz/norm)
        
        self.front = direction
        self.yaw = yaw
        self.pitch = pitch

    def move(self, speed):
        vx,vy,vz = self.front
        px,py,pz = self.position
        self.position = px+vx*speed, py+vy*speed, pz+vz*speed

    def get_ViewProjection(self):
        vx,vy,vz = self.front
        px,py,pz = self.position
        target = vx+px, vy+py, vz+pz
        
        return get_vpmat(self.position, target, self.up,  self.fov,self.ratio,self.near,self.far)

def get_vpmat(position, target, up,  fov,ratio,near,far):
    eye = Vec(*position)
    center = Vec(*target)
    up = Vec(*up)

    vv = gllookat( eye, center, up )
    pp = glperspective( fov,ratio,near,far)
    vp = matmul4(vv,pp)
    return vp

def _camtest():
    cam = Camera()
    print(cam.front)

    cam.set_dxdy(0,0)
    print(cam.front)

    cam.set_dxdy(0.1,0)
    print(cam.front)

    print(cam.get_ViewProjection())
    #[1.2714033832196738, 0.0, 0.0, 0.0,
    # 0.0, 2.1105296161446585, 0.0, 0.0, 
    #0.0, 0.0, -1.000020000200002, -1.0,
    # 0.0, 0.0, 0.980019800198002, 1.0]
    view_projection = [
            1.1027, 0, 0, 0,
            0, 1.83049, 0, 0,
            0, 0, -1.00002, -1,
            0, 0, 0.98002, 1
            ]


#============================== CAMERA
#============================== CAMERA
#============================== CAMERA
#============================== CAMERA



#=========quat
#=========quat
#=========quat
#=========quat
#=========quat
#=========quat
def _quat_normalize(qw, qx, qy, qz):
    magnitude = sqrt(qw**2 + qx**2 + qy**2 + qz**2)
    normalized_qw = qw / magnitude
    normalized_qx = qx / magnitude
    normalized_qy = qy / magnitude
    normalized_qz = qz / magnitude
    return normalized_qw, normalized_qx, normalized_qy, normalized_qz

def _euler_to_quat(x,y,z):
    #https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
    #Euler angles to quaternion conversion
    cy = cos(z/2)
    sy = sin(z/2)
    cp = cos(y/2)
    sp = sin(y/2)
    cr = cos(x/2)
    sr = sin(x/2)

    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    return w,x,y,z

def _quat_axis_y(theta):
    "yaw, says zup is y.."
    qw = cos(theta/2)
    qx = 0
    qy = sin(theta/2)
    qz = 0

def _quat_axis_x(theta):
    "pitch."
    qw = cos(theta/2)
    qx = sin(theta/2)
    qy = 0
    qz = 0

def _quat_axis_x(theta):
    "z axis, roll.."
    qw = cos(theta/2)
    qx = sin(theta/2)
    qy = 0
    qz = 0



def _angle_axis_to_quat(angle, x,y,z):
    "axis should be normalized.. since x*[0-1.0]"
    #https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
    #q = q0,1,2,3
    w = cos(angle/2)
    sin_th2 = sin(angle/2)
    #https://math.stackexchange.com/questions/40164/how-do-you-rotate-a-vector-by-a-unit-quaternion
    #says x,y,z unit vec.. just x.
    #x = cos(x) * sin_th2
    #y = cos(y) * sin_th2
    #z = cos(z) * sin_th2
    x = x * sin_th2
    y = y * sin_th2
    z = z * sin_th2
    # mag = sqrt(w**2+x**2+y**2+z**2)
    # w /=mag
    # x/=mag
    # y/=mag
    # z/=mag
    return w,x,y,z

def _quat_to_angle_axis(w,x,y,z):
    """
    https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
    It is worth noting that there are several ways to conv..
    """
    angle = 2*acos(w)

    sin_th2 = sin(angle/2)
    if sin_th2 <0.001:#0.06deg
        return 0, 1,0,0
    ax = x/sin_th2
    ay = y/sin_th2
    az = z/sin_th2
    return angle, ax,ay,az

def _quat_to_euler(w,x,y,z):
    "roll pitch yaw"
    #https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
    #roll (x-axis rotation)
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = atan2(sinr_cosp, cosr_cosp)

    #pitch (y-axis rotation)
    sinp = 2 * (w * y - z * x)
    if abs(sinp) >= 1:
        pitch = 1.57 #use 90 degrees if out of range
    else:
        pitch = asin(sinp)

    #yaw (z-axis rotation)
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = atan2(siny_cosp, cosy_cosp)
    return roll,pitch,yaw


def _quat_rotate_xyz(qw,qx,qy,qz, x,y,z):
    """
    rotate position x,y,z
    returns not normalized. #1.5-8x faster than qpq way.
    https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
    https://www.vcalc.com/wiki/vector-rotation
    
    was before was below,there were times v*v -> v.
    v + qw*tv +qv*tv
    rx = x + qw*tx +qx*tx
    ry = y + qw*ty +qy*ty
    rz = z + qw*tz +qz*tz
    """

    #qhat requires normlized?
    # mag = sqrt(qw**2+ qx**2+ qy**2+ qz**2)
    # qw /= mag
    # qx /= mag
    # qy /= mag
    # qz /= mag

    # v=xyz  v'= rotated xyz
    # quat ->  qw, qv
    # t = 2* (q X v)
    # v' = v + qw*t + (qv X t)
    
    #tx,ty,tz = _cross(qx,qy,qz, x,y,z)
    #tx *=2
    #ty *=2
    #tz *=2
    #cross acts like this..
    tx,ty,tz = _cross(qx*2,qy*2,qz*2, x,y,z)

    ctx,cty,ctz = _cross(qx,qy,qz, tx,ty,tz)
    rx = x + qw*tx + ctx
    ry = y + qw*ty + cty
    rz = z + qw*tz + ctz
    return rx,ry,rz


def _quat_to_xyz(qw,qx,qy,qz):
    "1,0,0 to rotated. 1.35 faster"
    #tx,ty,tz = _cross(qx*2,qy*2,qz*2, x,0,0)
    # 0 = ay*0-az*0
    # cy = az*1-ax*0
    # cz = ax*0-ay*1
    # return 0,cy,cz
    tx,ty,tz = 0, qz, qy

    #ctx,cty,ctz = _cross(qx,qy,qz, tx,ty,tz)
    ctx = qy*tz-qz*ty
    cty = qx*tz
    ctz = qx*ty
    rx = 1 + qw*tx + ctx
    ry = 0 + qw*ty + cty
    rz = 0 + qw*tz + ctz
    return rx,ry,rz


def _quat_mul(w1,x1,y1,z1, w2,x2,y2,z2):
    """https://en.wikipedia.org/wiki/Quaternion
    hamilton product, q1->q2.
    ..and it was grassman!
    """
    # grassman
    # cx,cy,cz = _cross(x1,y1,z1, x2,y2,z2)
    # w = w1*w2 - _dot(x1,y1,z1, x2,y2,z2)
    # x = w1*x2+ w2*x1 + cx
    # y = w1*y2+ w2*y1 + cy
    # z = w1*z2+ w2*z1 + cz

    w = w1*w2 - x1*x2 - y1*y2 - z1*z2
    x = w1*x2 + x1*w2 + y1*z2 - z1*y2
    y = w1*y2 - x1*z2 + y1*w2 + z1*x2
    z = w1*z2 + x1*y2 - y1*x2 + z1*w2
    return w,x,y,z

def _quat_inverse(w,x,y,z):
    """
    conjugation is -q.
    -q / mag2(q)
    https://en.wikipedia.org/wiki/Quaternion
    """
    mag2 = w**2+x**2+y**2+z**2
    w /= mag2
    x /= -mag2
    y /= -mag2
    z /= -mag2
    return w,x,y,z


# def _quat_to_quat(w1,x1,y1,z1, w2,x2,y2,z2):
#   "p,q, q->-p. final -> inverses last rotation."
#   #easy imagine  0.2,(0,1,0) -> 0,2,(1,0,0).
#   rw1,rx1,ry1,rz1 = _quat_inverse(w1,x1,y1,z1)
#   return _quat_mul(w2,x2,y2,z2, rw1,rx1,ry1,rz1)


def _quat_to_rotmat(w,x,y,z):
    """rows x0->x1
    https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation"""
    r0 = 1 - 2*y**2 - 2*z**2
    r1 = 2*x*y - 2*z*w
    r2 = 2*x*z + 2*y*w
    r3 =  0    
    r4 = 2*x*y + 2*z*w
    r5 = 1 - 2*x**2 - 2*z**2
    r6 = 2*y*z - 2*x*w
    r7 = 0
    r8 = 2*x*z - 2*y*w
    r9 = 2*y*z + 2*x*w
    r10 = 1 - 2*x**2 - 2*y**2
    r11 = 0
    
    r12 = 0
    r13 = 0
    r14 = 0
    r15 = 1
    return (r0,r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12,r13,r14,r15)


def _quat_slerp(w1, x1, y1, z1, w2, x2, y2, z2, t):
    """
    Perform Spherical Linear Interpolation (SLERP) between two quaternions.

    Parameters:
        w1, x1, y1, z1 (float): Components of the first quaternion (w, x, y, z).
        w2, x2, y2, z2 (float): Components of the second quaternion (w, x, y, z).
        t (float): The interpolation parameter in the range [0, 1].

    Returns:
        tuple: The interpolated quaternion (w, x, y, z).
    """
    # Normalize the input quaternions
    magnitude1 = sqrt(w1**2 + x1**2 + y1**2 + z1**2)
    magnitude2 = sqrt(w2**2 + x2**2 + y2**2 + z2**2)
    w1 /= magnitude1
    x1 /= magnitude1
    y1 /= magnitude1
    z1 /= magnitude1
    w2 /= magnitude2
    x2 /= magnitude2
    y2 /= magnitude2
    z2 /= magnitude2

    # Calculate the dot product of the quaternions
    dot_product = w1*w2 + x1*x2 + y1*y2 + z1*z2

    # Ensure the shortest path interpolation
    if dot_product < 0.0:
        w2 = -w2
        x2 = -x2
        y2 = -y2
        z2 = -z2
        dot_product = -dot_product

    # Calculate the interpolation angle
    theta = acos(dot_product)

    # Perform spherical linear interpolation
    if abs(theta) < 1e-6:
        return w1, x1, y1, z1  # Avoid division by zero
    else:
        sin_theta = sin(theta)
        w1 = sin((1 - t) * theta) / sin_theta
        w2 = sin(t * theta) / sin_theta

        # Interpolate the quaternion components
        w = w1 * w1 + w2 * w2
        x = x1 * w1 + x2 * w2
        y = y1 * w1 + y2 * w2
        z = z1 * w1 + z2 * w2

        # Normalize the interpolated quaternion
        magnitude = sqrt(w**2 + x**2 + y**2 + z**2)
        w /= magnitude
        x /= magnitude
        y /= magnitude
        z /= magnitude

        return w, x, y, z



class Quaternion:
    "doesn't knows Vec class. only x,y,z!"
    #https://personal.utdallas.edu/~sxb027100/dock/quaternion.html
    __slots__ = ('w', 'x','y','z')
    def __init__(self, w=1, x=0,y=0,z=0):
        self.w = w
        self.x = x
        self.y = y
        self.z = z
    def __str__(self):
        return f"{self.__class__.__name__} {self.w:.6f} {self.x:.6f} {self.y:.6f} {self.z:.6f}"

    def mul(self, other):
        "rot afters. product X. ab != ba . p->q."
        s,o = self,other
        w,x,y,z = _quat_mul(s.w, s.x,s.y,s.z, o.w, o.x,o.y,o.z)
        return self.__class__(w,x,y,z)

    def __neg__(self):
        "seems conjugate"
        #https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
        return self.__class__(self.w, -self.x,-self.y,-self.z)
    
    #usually for mag..ha.
    def __mul__(self, value):
        w=self.w * value
        x=self.x * value
        y=self.y * value
        z=self.z * value
        return self.__class__(w,x,y,z)
    def __imul__(self, value):
        self.w *= value
        self.x *= value
        self.y *= value
        self.z *= value
    def __truediv__(self, value):
        w=self.w / value
        x=self.x / value
        y=self.y / value
        z=self.z / value
        return self.__class__(w,x,y,z)
    def __itruediv__(self, value):
        self.w /= value
        self.x /= value
        self.y /= value
        self.z /= value
    def __floordiv__(self, value):
        w=self.w // value
        x=self.x // value
        y=self.y // value
        z=self.z // value
        return self.__class__(w,x,y,z)
    def __ifloordiv__(self, value):
        self.w //= value
        self.x //= value
        self.y //= value
        self.z //= value

    def _rotateqpq(self, x,y,z):
        "but seems slower"
        P = self.__class__(0, x,y,z)
        #p_ = -self.mul(P).mul(self)#active
        p_ = self.mul(P).mul(-self)
        return p_.x,p_.y,p_.z

    def normalize(self):
        mag = sqrt(self.w**2, self.x**2, self.y**2, self.z**2)
        self.x/=mag
        self.y/=mag
        self.z/=mag     
    #=== trasformation
    @classmethod
    def from_euler(cls, x,y,z):
        "yaw (Z), pitch (Y), roll (X)"
        w, x,y,z = _euler_to_quat(x,y,z)
        #return self.__class__(w, x,y,z)
        return cls(w, x,y,z)
    @classmethod
    def from_angle_axis(cls, rad, x,y,z):
        "1,0,0 Axis-Angle-> quat[4] / x,y,z is v-hat, normalized."
        w, x,y,z = _angle_axis_to_quat(rad, x,y,z)
        return cls(w, x,y,z)
    @classmethod
    def from_xyz(cls,x,y,z):
        "normalized -> 0,x,y,z"
        return cls(0, x,y,z)

    def to_angle_axis(self):
        "1,0,0 -> AA"
        return _quat_to_angle_axis(self.w,self.x,self.y,self.z)
    def to_euler(self):
        "by each axis , but what order?"
        return _quat_to_euler(self.w,self.x,self.y,self.z)
    def to_matrix(self):
        "calc rotation matrix (row major x0>x1)"
        return _quat_to_rotmat(self.w, self.x,self.y,self.z)

    #=== rotation
    def rotate(self, x,y,z):
        "rotate pos x,y,z , by quat."
        #not sure it can rotate big vector..
        return _quat_rotate_xyz(self.w,self.x,self.y,self.z,  x,y,z)
    
    def to_front(self):
        "returns x,y,z pos of front from 1,0,0"
        return _quat_to_xyz(self.w,self.x,self.y,self.z)

    #def get_angle_axis_to(self, w,x,y,z):
        #"get AA represent by quat."
        #qw,qx,qy,qz = _quat_to_quat(self.w,self.x,self.y,self.z, w,x,y,z)
        #angle, x,y,z = _quat_to_angle_axis(qw,qx,qy,qz)
        #self.__class__.from_angle_axis(angle*ratio, x,y,z)
        #NO! quat is , rotational position.
        #angle,axis is just from 1,0,0.

    def _cant_slerp(self, quat, ratio=1.0):
        w,x,y,z = quat.w,quat.x,quat.y,quat.z

        "using AA, maybe slow. returns quat. q=0,x,y,z"
        x1,y1,z1 = _quat_to_xyz(self.w,self.x,self.y,self.z)
        x2,y2,z2 = _quat_to_xyz(w,x,y,z)
        ax,ay,az = _cross(x1,y1,z1, x2,y2,z2)
        angle = _angle(x1,y1,z1, x2,y2,z2)
        #..and we get pos.
        ##wow! normalized pos -> quat is just 0,x,y,z/ ..but seems can't use..

        #qw,qx,qy,qz = _angle_axis_to_quat(angle*ratio, ax,ay,az)#so it from 1,0,0... not a->b.
        #rx,ry,rz = _quat_rotate_xyz(qw, qx,qy,qz,  x1,y1,z1)
        return self.__class__.from_xyz(rx,ry,rz)

    def slerp(self, quat, ratio=1.0):
        w,x,y,z = _quat_slerp(self.w,self.x,self.y,self.z, quat.w,quat.x,quat.y,quat.z, ratio)
        return self.__class__(w,x,y,z)


def test_slerp():
    a = Quaternion.from_angle_axis(0.2, 0,1,0)
    b = Quaternion.from_angle_axis(1.5, 0,0,1)

    x=a.slerp(b,0.91)
    print(x.to_angle_axis())
    print(x.to_front())
#test_slerp()
#exit()









#=test



def test_vecspd():
    a = Vec(1,2,3)
    b = Vec(3,2,1)
    import time
    t1=time.time()
    for i in range(100_000):
        a.lookat(b)
        #print(a) #...lookat need normalized
    t2= time.time()
    print(t2-t1)
    #... 680 700ms funcs
    #650 560 encoded, no procedure.
    #20% speed up. extreamly!
    #...now all, 960ms. for 100k.
    #means if 10k objects, look at me, takes 0.1s. quite slow.
    #while 100k loop takes 4ms.




def test_degree():
    from math import degrees
    a=Vec(0,0,-1)
    b=Vec(1,0,0)
    #b.rotate(45)
    b=Vec(0.707,0,-0.707)
    print(a.dot(b))
    print( degrees(a.angle(b)) )


def test_product():
    a = Vec(0,0,0)
    print(a.norm)
    a = Vec(1,0,0)
    b = Vec(1,1,0)
    print(a.cross(b))#z1

    a = Vec(1,0,0)
    b = Vec(0,0,-1)
    print(a.cross(b))#y1

    a = Vec(1,0,0)
    b = Vec(0,0,-1)
    print(a.dot(b))


def test_normalized():
    a = Vec(1,2,3)
    print(a.norm)
    print(a.normalize(), a.normalize().x, a.normalize()[1], a.normalize().z)
    x,y,z = a.normalize()
    print(x**2+y**2+z**2)

def test_eq():
    a = Vec(0,0,0)
    b = Vec(0.00000001,0,0)
    print(a.equal(b) , a==b, not (a!=b) )


def test_vecop():
    a = Vec(1,2,1)
    print(a.mag)

def test_str():
    class M:
        def __str__(self):
            return 'xxx'
    a = M()
    x = str(a)
    print(x)

def test_str2():
    a = Vec(1,2,3)
    b = Vec(3,2,1)

    print(a)
    print(a+b)
    a += b
    print(a)
    print(str(a),'x')

class _Vec_list:
    def __init__(self, x,y,z):
        self._data = [x,y,z]
    @property
    def x(self):
        return self._data[0]
    @property
    def y(self):
        return self._data[1]
    @property
    def z(self):
        return self._data[2]
    @x.setter
    def x(self, value):
        self._data[0] = value
    @y.setter
    def y(self, value):
        self._data[1] = value
    @z.setter
    def z(self, value):
        self._data[2] = value
    #===
    def __iter__(self,idx):
        return self._data[idx]
    
    #=== operands
    def __add__(self, other):
        x,y,z = self._data
        ox,oy,oz = other._data
        return self.__class__(x+ox, y+oy, z+oz)
    def __iadd__(self, other):
        x,y,z = self._data
        ox,oy,oz = other._data
        self._data = [x+ox, y+oy, z+oz]
        # seems slower
        # self._data[0] += other._data[0]
        # self._data[1] += other._data[1]
        # self._data[2] += other._data[2]



def test_vec_spd():
    from time import perf_counter
    "seems same"
    #Vec_list
    v = Vec(0,0,0)
    nv = Vec(1,1,1)

    ts = []
    for i in range(20):
        a = perf_counter()
        for i in range(100000):
            v + nv
        b = perf_counter()
        ts.append(b-a)
    print(sum(ts)/len(ts))

def test_vec():
    vec = Vec
    a = vec(0,0,1)
    print(a, a.x)










def test_quatrotaa():
    def quat_test(angle, axis , truth):
        print('+++++TEST+++')
        x,y,z = _normalize(*axis)
        quatel = _angle_axis_to_quat(angle, x,y,z)
        a = Quaternion(*quatel)
        print(a,'quat')

        x = a.rotate(1,0,0)
        print('TRUTH',truth)
        print(x,'result')
        print('')
    quat_test(0.2, (0,1,0), (0.98007,0, -0.19867) )
    quat_test(0.2, (0,0.5,0), (0.98007,0, -0.19867))
    quat_test(0.2, (0,0,1), (0.98007,0.19867,0))
    quat_test(0.2, (1,0,0), (1,0,0))
    quat_test(0.2, (0.7,0.7,0), (0.99,0.00997,-0.14048))
    quat_test(0.2, (0.7,0.7,0), (0.99,0.00997,-0.14048))
    quat_test(0.2, (0.54,0.54,0.54), (0.986,0.121,-0.108))
    quat_test(0.2, (0.1,0.2,0.3), (0.981,0.1621,-0.10192))



def test_quattransform():
    a = Quaternion()
    a = Quaternion.from_angle_axis(0.2, 0,1,0)
    print(a)
    print(a.to_angle_axis())
    print(a.to_matrix())
    a = Quaternion.from_euler(0.3,1,0.5)
    print(a)
    print(a.to_euler())


def test_quat_mul():
    p = Quaternion.from_angle_axis(0.2, 0,1,0)
    q = Quaternion.from_angle_axis(0.2, 1,0,0)

    print(p.mul(q).to_angle_axis())
    #print(q.mul_grassman(p).to_angle_axis())
    print(q.mul(p).to_angle_axis())
    #(0.28260659739224686, 0.7053338522473815, 0.7053338522473815, -0.07076944077600865)
    #so it seems same..

    import time
    t = time.time()
    for i in range(100_000):
        p.mul(q)
    print(time.time()-t)

    #t = time.time()
    #for i in range(100_000):
    #   p.mul_grassman(q)
    #print(time.time()-t)

    # .33 .34 ..  somehow mul product is, seems faster.
    #found grassman=hamilton. case closed,.


def test_quat_topos():
    "190ms vs 320ms.needit."
    import time
    t = time.time()
    for i in range(100_000):
        _quat_to_xyz(0.1,0.2,0.3,0.4)
    print(time.time()-t)
    t = time.time()
    for i in range(100_000):
        _quat_rotate_xyz(0.1,0.2,0.3,0.4, 1,0,0)
    print(time.time()-t)


def main():
    test_vec()
    test_str2()
    test_str()
    test_vecop()
    test_eq()
    test_normalized()
    test_product()
    test_degree()
    test_vecspd()
    test_vec_spd()
    test_quatrotaa()
    test_quattransform()
    test_quattransform()
    test_quat_mul()
    test_quat_topos()

#vec = Vec
Quat = Quaternion
#quat = Quaternion

if __name__ == '__main__':
    main()
