from modelos import Monkey
import glfw
import sys
from typing import Union


class Controller:
    model: Union['Monkey',None]
    def __init__(self):
        self.model=None
        self.env=None
    def setModel(self,model):
        self.model=model
    def bindEnvironment(self,env):
        self.env=env
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
        if key==glfw.KEY_SPACE:
            if action==glfw.PRESS:
                self.env.move(-1)
        if key == glfw.KEY_ESCAPE:
            sys.exit()

