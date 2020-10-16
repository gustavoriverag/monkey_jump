from modelos import Monkey
import glfw
import sys
from typing import Union


class Controller:
    model: Union['Monkey',None]
    cam: Union['Camera',None]
    def __init__(self):
        self.model=None
        self.cam=None
    def setModel(self,model):
        self.model=model
    def bindCamera(self,cam):
        self.cam=cam
    def on_key(self, window, key, scancode, action, mods):
        if key==glfw.KEY_A:
            if action==glfw.PRESS:
                self.model.move_left()
            if action==glfw.RELEASE:
                self.model.stop()
        if key==glfw.KEY_D:
            if action==glfw.PRESS:
                self.model.move_right()
            if action==glfw.RELEASE:
                self.model.stop()
        if key==glfw.KEY_W and action==glfw.PRESS:
            self.model.jump()               
        if key == glfw.KEY_ESCAPE:
            glfw.terminate()
            sys.exit()

