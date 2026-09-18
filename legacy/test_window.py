from interface import WindowInterface
from glfw.GLFW import *
from OpenGL.GL import *
glfwInit()

class Window(WindowInterface):
    def __init__(self, size = (640,480), title = 'a window'):
        width,height = size
        window = glfwCreateWindow(width, height, title, None, None)
        glfwMakeContextCurrent(window)

        glfwSwapInterval(1)#x1 x2 x3.. of hz. 0 seems fullspeed..

        glfwSetWindowAttrib(window, GLFW_RESIZABLE, False)
        
        if glfwRawMouseMotionSupported():
            glfwSetInputMode(window, GLFW_RAW_MOUSE_MOTION, GLFW_TRUE)
        #===
        self.window = window
        self.size = size
        self._fullscreen = False
        self._mouselock = True
        #==========
        def keyfunc(*args):
            if args[0] == 256:
                self.close()
            print('k',*args)
        self.bind_key(keyfunc)
        def mfunc(*args):
            print('m',*args)
        self.bind_mouse(mfunc)
        def mbfunc(*args):
            print('mb',*args)
        self.bind_mousebutton(mbfunc)
        self.bind_mousewheel(lambda x:print('wheel',x))
        #======================
        def FramebufferSizeCallback(window, width,height):
            glViewport(0, 0, width, height)
            self.size = (width,height)
            #w,h = glfwGetFramebufferSize(self.window)
        glfwSetFramebufferSizeCallback(window, FramebufferSizeCallback)

    #==============================
    def bind_key(self, keyfunc):
        def KeyCallback(window, key, scancode, action, mods):
            #key a:65 1:49/ mods 0 1 2 4 "" shift ctrl alt   chr(key)
            #print(key, scancode, action, mods)
            keyfunc(key, scancode, action, mods)
        glfwSetKeyCallback(self.window, KeyCallback)

    def bind_mouse(self, mousefunc):
        def CursorPosCallback(window, xpos,ypos):
            mousefunc(xpos,ypos)
        glfwSetCursorPosCallback(self.window, CursorPosCallback)

    def bind_mousebutton(self, mousebuttonfunc):
        def MouseButtonCallback(window, button, action, mods):
            mousebuttonfunc(button,action,mods)
        glfwSetMouseButtonCallback(self.window, MouseButtonCallback)
    def bind_mousewheel(self, mwheelfunc):
        def ScrollCallback(window, dnotknow, up):
            mwheelfunc(up)
        glfwSetScrollCallback(self.window, ScrollCallback)
    def bind_filedrop(self, dropfunc):
        def DropCallback(window, *args):
            dropfunc(*args)
        glfwSetDropCallback(self.window, DropCallback)

    #============================
    def set_icon(self, image):
        "16 32 48/ https://www.glfw.org/docs/3.3/group__window.html#ga5d877f09e968cef7a360b513306f17ff"
        #image 32bit RGBA
        glfwSetWindowIcon(self.window, 1, image)
    def set_opacity(self, alpha):
        glfwSetWindowOpacity(self.window, alpha)
        


    def set_title(self, title):
        glfwSetWindowTitle(self.window, title)
    def set_size(self, size):
        width,height = size
        glfwSetWindowSize(self.window, width,height)
        #glfwSetWindowSizeLimits(self.window, 100, 100, GLFW_DONT_CARE, GLFW_DONT_CARE)
        self.size = size

    def set_fullscreen(self, value):
        if value:
            self._fullscreen = True
            glfwMaximizeWindow(self.window)
        else:
            if self._fullscreen:
                self._fullscreen = False
                glfwIconifyWindow(self.window)

    def set_top(self,value):
        glfwSetWindowAttrib(self.window, GLFW_FLOATING, value)
    def set_mouselock(self, value):
        if value:
            if not self._mouselock:
                glfwSetInputMode(self.window, GLFW_CURSOR, GLFW_CURSOR_DISABLED)
                self._mouselock = True
        else:
            if self._mouselock:
                glfwSetInputMode(self.window, GLFW_CURSOR, GLFW_CURSOR_NORMAL)
                self._mouselock = False

    #=============================
    def process_input(self):
        1
    def update(self, dt):
        1#print(dt)
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    #======================

    def run(self):
        window = self.window
        t0 = glfwGetTime()
        while not glfwWindowShouldClose(window):
            t1 = glfwGetTime()
            dt = t1-t0
            t0 = t1

            self.process_input()
            self.update(dt)
            self.draw()

            glfwSwapBuffers(window)
            glfwPollEvents()
        glfwTerminate()
    
    def close(self):
        glfwSetWindowShouldClose(self.window,True)



"""
#glfwSetErrorCallback(self_callback)#instead glfwGetError()
#glfwSetCharCallback(window, self_callback)
#glfwSetCharModsCallback(window, self_callback)

#glfwSetWindowCloseCallback(self.window, self_callback)        
#https://www.glfw.org/docs/3.3/group__input.html#ga1ab90a55cf3f58639b893c0f4118cb6e

"""


def main():
    w = Window()
    w.run()

if __name__ == '__main__':
    main()