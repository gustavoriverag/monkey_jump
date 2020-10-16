###############################
# MONKEY JUMP: RETURN TO MONKE#
###############################
# A GAME BY: GUSTAVO RIVERA   #
###############################
#Version 0.5

#Imports
import glfw # Usada para interactuar con un usuario (mouse, teclado, etc)
from OpenGL.GL import * # importa las funciones de OpenGL
import OpenGL.GL.shaders # importa el set de shaders de OpenGL.
import numpy as np
import sys 
import os
import csv

import transformations as tr
import easy_shaders as es
import basic_shapes as bs
import scene_graph as sg

from controller import Controller
from modelos import *

controller=Controller()
    
if __name__ == "__main__":
    if sys.argv[1] != None:
        mapa=sys.argv[1]

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 800
    height = 800


    window = glfw.create_window(width, height, "Monkey Jump", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controller.on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipeline=es.SimpleTransformShaderProgram()
    pipeline_text=es.SimpleTextureTransformShaderProgram()
    # Telling OpenGL to use our shader programa


    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # Setting up the clear screen color
    glClearColor(0.3, 0.85, 0.3, 1.0)

    #guardar figuras en memoria
    monkey=Monkey()
    controller.setModel(monkey)
    environment=Environment(mapa)
    cam=Camera(monkey,environment)
    controller.bindCamera(cam)
    anim=EndAnimation()

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        #Aquí se dibuja todo todillo
        #Se dibuja y actualiza el ambiente
        if monkey.winCond==0:
            environment.update()
            environment.draw(pipeline_text)
            #Se actualiza, dibuja y detectan colisiones del mono
            monkey.collide(environment)
            monkey.update()
            monkey.draw(pipeline_text)
            #Se actualiza la cámara
            cam.update()
        #si se pierde, animar la muerte
        if monkey.winCond==-1:
            anim.deathAnimate(pipeline,pipeline_text)
        #si se gana animar la victoria
        if monkey.winCond==1:
            anim.winAnimate(pipeline,pipeline_text)
        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    
    glfw.terminate()