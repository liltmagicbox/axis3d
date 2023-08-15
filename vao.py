from OpenGL.GL import *
import numpy as np

def_attrs = {
'position':[0,0,0, 0.5,0,0, 0,0.5,0],
'color':[1,0,0, 0,1,0, 0,0,1],
'index':[0,1,2],
}

class VAO:
    _last_bound = None
    "attrs={'position':[]} "
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = def_attrs
        indices = attrs.get('index', list(range( len(attrs['position'])//3 )))
        indices = np.array(indices).astype('uint32')

        vertices = self._get_vertices(attrs)

        VAO = glGenVertexArrays(1) # create a VA. if 3, 3of VA got. #errs if no window.
        VBO = glGenBuffers(1) #it's buffer, for data of vao.fine.
        EBO = glGenBuffers(1) #indexed, so EBO also. yeah.
        glBindVertexArray(VAO) #gpu bind VAO
        glBindBuffer(GL_ARRAY_BUFFER, VBO) #gpu bind VBO in VAO
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        #--------attrs
        #glVertexAttribPointer(attr_index, size, datatype, normalized, stride, offset)
        points = len(attrs['position'])//3
        fsize = np.float32(0.0).nbytes #to ensure namespace-safe.        
        offset = ctypes.c_void_p(0)
        loc = 0  # NOTE:opengl core no attr 0.
        for data_array in attrs.values():
            data_len = len(data_array)
            size = data_len//points#size 2,3,4            
            #loc = glGetAttribLocation(shader.ID, attrname)            
            glVertexAttribPointer(loc, size, GL_FLOAT, GL_FALSE, 0, offset)
            glEnableVertexAttribArray(loc)
            offset = ctypes.c_void_p(data_len*fsize)
            loc+=1

        self.vao = VAO
        self.vbo = VBO
        self.ebo = EBO
        self.points = len(indices)

    def _get_vertices(self, attrs):        
        # make np array
        
        # attrlist=[]
        # for key, data_array in attrs.items():
        #     if key != 'index':
        #         attrlist.append(data_array)
        
        attrlist = [data_array for key,data_array in attrs.items() if key != 'index']
        vertices = np.concatenate(attrlist).astype('float32')
        return vertices

    def update(self,attrs):
        "keep the length same."
        VAO = self.vao
        VBO = self.vbo
        vertices = self._get_vertices(attrs)
        glBindVertexArray(VAO) #gpu bind VAO
        glBindBuffer(GL_ARRAY_BUFFER, VBO) #gpu bind VBO in VAO
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

#    def bind(self):    
#        glBindVertexArray(self.vao)
#    def unbind(self):
#        glBindVertexArray(0)
    def draw(self):
        if VAO._last_bound != self:
            VAO._last_bound = self
            glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.points, GL_UNSIGNED_INT, None)





def we_dont_even_need_this():
    #origin data
    vertices = {'vertex':[1,2,3, 4,5,6, 7,8,9],
    'normal':[11,22,33, 44,55,66, 77,88,99],
    'uv':[10,20, 30,40, 50,60],
    }
    #keep indices same.
    indices =  [0,1,2,0]

    #data to merged
    points = len(vertices['vertex'])//3        
    attr_length = { key:len(value)//points for key,value in vertices.items()}

    merged_vertices = []
    for index in indices:
        single_vertex = []
        for attr,data in vertices.items():
            data_length = attr_length[attr]
            idx_left = data_length * index #0,0*3 1,1*3
            idx_right = idx_left + data_length
            single_vertex.extend( data[idx_left : idx_right] )
        merged_vertices.extend(single_vertex)
    print(merged_vertices)

    exit()