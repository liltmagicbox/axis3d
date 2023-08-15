from OpenGL.GL import *
from OpenGL.GL import shaders

vertn = """
#version 410 core
layout (location = 0) in vec3 pos;
layout (location = 1) in vec3 color;
out vec3 out_color;

uniform mat4 Model;
uniform mat4 ViewProjection;

void main() 
{
    gl_Position = ViewProjection * Model * vec4(pos, 1);
    gl_Position = ViewProjection * vec4(pos, 1);
    //gl_Position = vec4(pos, 1);
    out_color = color;
}
"""

fragn = """
#version 410 core

uniform vec3 unicolor;

in vec3 out_color;
out vec4 FragColor;
void main()
{
    FragColor = vec4(out_color,1);
    //FragColor = vec4(unicolor,1);
}
"""


class Shader:
    #__slots__ = ['program']#not that effective!
    _last_bound = 0
    def __init__(self, vertstr=None, fragstr=None):
        if vertstr is None and fragstr is None:            
            vertstr, fragstr = vertn,fragn
        assert bool(glCreateShader)#compile error occurs, before window() 
        vshader = shaders.compileShader( vertstr, GL_VERTEX_SHADER)
        fshader = shaders.compileShader( fragstr, GL_FRAGMENT_SHADER)
        program = shaders.compileProgram( vshader,fshader)
        glDeleteShader(vshader)
        glDeleteShader(fshader)
        self.program = program
        self.locations = {}

    def bind(self):
        if Shader._last_bound != self:
            Shader._last_bound = self
            glUseProgram(self.program)
    # def unbind(self):
    #     "do we need it?"
    #     glUseProgram(0)
    #     Shader.last = 0        

    def _get_location(self, uniform_name):
        if not uniform_name in self.locations:
            location = glGetUniformLocation(self.program, uniform_name)
            if location == -1:
                raise KeyError(f'location {uniform_name} not in shader program.')
            self.locations[uniform_name] = location

        location = self.locations[uniform_name]
        return location

    def set_int(self, uniform_name, value):
        location = self._get_location(uniform_name)
        glUniform1i(location,value)
    def set_float(self, uniform_name, value):
        location = self._get_location(uniform_name)
        glUniform1f(location,value)
    def set_vec2(self, uniform_name, vec2):
        location = self._get_location(uniform_name)
        glUniform2f(location, *vec2)
    def set_vec3(self, uniform_name, vec3):
        location = self._get_location(uniform_name)
        glUniform3f(location, *vec3)
    def set_mat4(self, uniform_name, mat4):
        """bind shader first.
        glUniformMatrix4fv(location,1,False, mat)#location count transpose data(nparr)
        True for row major..[1,2,3,4, ,]
        """
        location = self._get_location(uniform_name)
        glUniformMatrix4fv(location,1,False, mat4)
