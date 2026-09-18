from test_window import Window
from inputmanager import Inputmap, get_keymap

from test_socket import Server
from test_socket_client import Client
from vector import Camera

from viewmodel import ViewModel
from test_renderer import Renderer

#=================================
#fill this:
key_translate_map = {
    ',':44,
    '.':46,

    '0':48,
    '9':57,
    'a':65,
    'z':90,

    '[':91,
    ']':93,

    'shift':340,
    'ctrl':341,
    'alt':342,

    'esc':256,
    'enter':257,
    'tab':258,
    'backspace':259,
    
    'space':32,
    'right':262,
    'left':263,
    'down':264,
    'up':265,
}

key_map = get_keymap(key_translate_map)
#=================================



class InputWindow(Window):
    def __init__(self):
        super().__init__()
        self.set_size( (960,640) )
        self.set_top(True)
        self.set_mouselock(False)
        #self.set_fullscreen(True)
        self.inputmap = Inputmap()
        self._cursor_pos = (0,0)
        self._cursor_pos_before = (0,0)
        self._cursor_changed = False
        self.camera = Camera()

        def keyfunc(key,code,action,mods):
            if action == 2:
                return
            if key in key_map:
                k = key_map[key]
                v = action
                self.inputmap.set(k,v)
        self.bind_key(keyfunc)

        def mfunc(x,y):
            self._cursor_pos = x,y
            self._cursor_changed = True
        self.bind_mouse(mfunc)

        def mbfunc(button,action,mods):
            if button == 0:
                key = 'ml'
            elif button == 1:
                key = 'mr'
            elif button == 2:
                key = 'mm'
            else:
                return
            self.inputmap.set(key,action)
        self.bind_mousebutton(mbfunc)

        def mwfunc(up):
            self.inputmap.set('mw',up)
        self.bind_mousewheel(mwfunc)
    
    #=================================
    def _process_cursor(self):
        if not self._cursor_changed:
            return
        
        self._cursor_changed = False
        
        width,height = self.size
        x,y = self._cursor_pos
        bx,by = self._cursor_pos_before
        self._cursor_pos_before = x,y
                        
        dx = (x - bx)/width
        dy = (y - by)/height
        
        if self._mouselock:
            self.camera.set_dxdy(dx,dy)
            #look, local cam front should firm. not by model.
            fx,fy,fz = self.camera.front
            self.inputmap.set('cfx', fx)
            self.inputmap.set('cfy', fy)
            self.inputmap.set('cfz', fz)
        else:
            if x>width:
                x = width
            if y>height:
                y = height
            #lets this only free-cursor. if locked, front 'ray' will do.
            self.inputmap.set( 'mx', x/width )
            self.inputmap.set( 'my', y/height )
        #xx,yy =  x/w , 1-y/h
        #if (0<=xx<=1) and (0<=yy<=1):
        #self.inputmap.set( 'mx', xx )
        #self.inputmap.set( 'my', yy )


#====================================

class Window(InputWindow):
    def __init__(self):
        super().__init__()
        #self.input_sender = Client()
        #self.view_getter = Server(port = 44443)

        self.view_model = ViewModel()
        self.renderer = Renderer()
    def process_input(self):
        self._process_cursor()
        #we need to put camera's front, position.

        if self.inputmap.get('ml')==1:
            self.set_mouselock(True)
        if self.inputmap.get('esc')==1:
            self.set_mouselock(False)

        #for flying cam only.
        W = self.inputmap.get('w')
        if W==1:
            self.camera.speed= 1
        elif W == 0:
            self.camera.speed = 0
        S = self.inputmap.get('s')
        if S==1:
            self.camera.speed= -1
        elif S==0:
            self.camera.speed = 0
        

        instr = self.inputmap.flush()
        # if instr:
        #     self.input_sender.send('input,arglen120max' , instr.encode() )

    def update(self, dt):
        self.camera.move( self.camera.speed * dt)
        1# for addr,data in self.view_getter.get():
        #     self.view_model.update(data)

        #view_model has cam info, of pos.
        #self.view_model.camera_position
        #attach to the object?? -> model gets front data, set one's front. / move->move..etc.
        #focused
        #self.view_model.focused / None or object.
        #if not is None:
        #focused.position / focused.front(will not overwritten)
        #table No -> object No
        #anyway we need both focused ID, only. right??
        #view only need position to set of cam,  'selected' of object..kinds.




    def draw(self):
        ViewProjection = self.camera.get_ViewProjection()
        self.renderer.clear()
        #self.renderer.render(self.view_model, ViewProjection)
        for table in self.view_model.get_tables():
            self.renderer.render(table, ViewProjection)











def main():
    win = Window()
    win.run()

if __name__ == '__main__':
    main()

