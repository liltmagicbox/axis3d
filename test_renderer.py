from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np

#mesh is combi of mat, geo.
from test_window import Window
from vector import Camera

from vao import VAO
from shader import Shader

class Renderer:
    "is 'drawer'. Mesh shallnot draw itself, nor scene, nor window."
    def __init__(self):
        "here gl--kinds."
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1,0.0,0.3, 1)
        glPointSize(5)
    
    def clear(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def render(self, view_table, view_projection ):
        #view_projection = [1,0,0,0, 0,1,0,0,  0,0,1,0, 0,0,0,1]
        #column major.
        sha = Shader()
        vao = VAO()

        sha.bind()
        sha.set_mat4('ViewProjection' , view_projection)
        vao.draw()
        #mesh.material.set_mat4('Model',mesh.mat_Model())




def main():
    import glm

    view_projection = [
            1.1027, 0, 0, 0,
            0, 1.83049, 0, 0,
            0, 0, -1.00002, -1,
            0, 0, 0.98002, 1
            ]
    vp=view_projection

    view = glm.lookAt( glm.vec3(0,0,1),glm.vec3(0,0,0), glm.vec3(0,1,0))
    pers = glm.perspective(1, 1.66,0.01,1000)
    vp = glm.mul(pers,view)
    vp = vp.to_list()
    print(vp)
    #glUniformMatrix4fv(location,1,False, mat4) accepts,
    #column majored,flatten. downward list. [...px,py,pz,1].
    #so below is same:
    #[[1.1027034521102905, 0.0, 0.0, 0.0], [0.0, 1.8304877281188965, 0.0, 0.0], [0.0, 0.0, -1.0000200271606445, -1.0], [0.0, 0.0, 2.980059862136841, 3.0]]
    #vp = [ 1.1027034521102905, 0.0, 0.0, 0.0, 0.0, 1.8304877281188965, 0.0, 0.0, 0.0, 0.0, -1.0000200271606445, -1.0, 0.0, 0.0, 2.980059862136841, 3.0]

    
    vvp = []
    [ vvp.extend(i) for i in vp]
    vp = vvp

    cam = Camera()
    cam.position = (0,0,5)
    vp = cam.get_ViewProjection()



    class Win(Window):
        def __init__(self):
            super().__init__()
            self.ren = Renderer()
        def draw(self):
            self.ren.clear()
            self.ren.render(1, vp)

    win = Win()
    win.run()

if __name__ == '__main__':
    main()

    #modelmatrix as attr0
    #attr1 0
    #attr2 (0,1,1)
    #uvcoord (0,0)
    #texture coords


    #vpy models
    # matrix color opacity

    #90% is same mat, diff geo... not that much.
    #dist2 shall be.. explode-factor?


    # sk model..
    #some vertex model..
    #pose 128..
    # tex1 tex2.
    # no opacity.


    #particles
    #pos only , color, ..anyway.
    #1. data is created axis,
    #2. draw-method is  ...viewmodel?

    #hair himesh..? -no need 3x3, but vec(x,y,z) / quat. ..or pos.simple.!


    #===================
    #mat requires, shader- uniform attrs.
    #vao is just vao, don't care geometry.

    # t-shirts, diff.coliors, uniform-attrs.
    # .. complex dress, with colors, shall be done, sameway. same mat!   color1,2,,N.

    #...cloth vertex data 600kb??
    # -> bone data 128  , 16*4B 64B, 100, 6.4KB.. enough.  (but via network, 600B. )
    # 40rings, 20 stack, 800points, of pos. 3B, 2400B, 2.4KB. fine.


    #THERE WILL BE NO MATEIRLAS
    #BUT ..DRAW-TYPES. WITH REQUIRED ATTRS. MAYBE 20 KINDS.

    #drawtype: already-known renderer or viewmodel.
    #  vao, requires , attrs set. 
    # viewmodel, has axis, matid, vaoid. -> all batch instanced draw.

    # 1k diff. humans, same mat, -colorsmap, pose,etc.. / sk-scale??, INSTANCED DRAW!!
    # pAINT to vertex! great. no photo-reallistic.. that's not my world.
    # and, not instanced, individuals, with each mat-geo combi, but same 4x4mat. fine. maybe use only textures. fine.

    #don't care lights..for now.
    #xxxxyyyy for mesh data, UE if done.




