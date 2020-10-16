import scene_graph as sg
import easy_shaders as es
import transformations as tr
import basic_shapes as bs
import csv
from typing import List, Union
from OpenGL.GL import *

class Monkey:

    def __init__(self):
        #Variables del Mono
        #Posición
        self.x_pos=0
        self.y_pos=-0.5
        #Velocidades horizontal y vertical
        self.h_speed=0
        self.v_speed=0
        #Ganaste, perdiste o no todavía?
        self.winCond=0
        #Estás en el aire/debes caer?
        self.airborne=True
        #te mueves hacia los lados?
        self.moving_left=False
        self.moving_right=False
        #estás colisionando con algún objeto?
        self.cObj=None
        #tamaño horizontal
        self.hsize=0.16
        #variable que ayuda al movimiento
        self.k=0
        self.contador=0
        #Inicializando sprites
        gpuStandingMonke=es.toGPUShape(bs.createTextureQuad("img/monos/parado.png"),GL_REPEAT,GL_NEAREST)
        gpuJumpingStillMonke=es.toGPUShape(bs.createTextureQuad("img/monos/saltando0.png"),GL_REPEAT,GL_NEAREST)
        gpuJumpingMonke=es.toGPUShape(bs.createTextureQuad("img/monos/saltando1.png"),GL_REPEAT,GL_NEAREST)
        gpuFallingMonke=es.toGPUShape(bs.createTextureQuad("img/monos/cayendo.png"),GL_REPEAT,GL_NEAREST)
        gpuMovingMonke1=es.toGPUShape(bs.createTextureQuad("img/monos/corriendo1.png"),GL_REPEAT,GL_NEAREST)
        gpuMovingMonke2=es.toGPUShape(bs.createTextureQuad("img/monos/corriendo2.png"),GL_REPEAT,GL_NEAREST)
        #Lista de sprites para acceso en métodos
        self.sprites=[gpuStandingMonke,gpuJumpingStillMonke,gpuJumpingMonke,gpuFallingMonke,gpuMovingMonke1,gpuMovingMonke2]
        #Creando nodo del Mono
        monke=sg.SceneGraphNode('monkey')
        monke.transform=tr.scale(self.hsize,0.25,0)
        monke.childs += [gpuStandingMonke]
        #variable auxiliar para actualizar los sprites.
        self.model=monke
        #Creando nodo de posición del Mono.
        monkeyPos=sg.SceneGraphNode('monkeyPos')
        monkeyPos.childs+=[monke]
        #variable modelo del objeto.
        self.modelPos = monkeyPos

    def draw(self,pipeline):
        #Se dibuja el mono, actualizando su posición.
        glUseProgram(pipeline.shaderProgram)
        self.modelPos.transform=tr.translate(self.x_pos,self.y_pos,0)
        sg.drawSceneGraphNode(self.modelPos,pipeline,'transform')

    def stop(self):
        #se detiene si no está apretando teclas.
        self.moving_left=False
        self.moving_right=False

    def move_left(self):
        self.moving_left=True

    def move_right(self):
        self.moving_right=True
        
    def jump(self):
        #Si no se está en el aire, saltar. Se da velocidad vertical y un poco de posición.
        if self.airborne:
            return
        self.airborne=True
        self.v_speed=0.1
        self.y_pos+=0.01

    def collide(self, env: 'Environment'):
        fpos: List[Union['Floor', 'Platform', None]]
        fpos=env.factPos()
        #Si no estás colisionando, buscar en todos los posibles objetos que pueden colisionar.
        if self.cObj==None:
            for p in fpos:
                realPos=p.get_ypos()+env.y_pos
                #detectar colisión en eje x.
                if p.get_xpos()-p.size/2<=self.x_pos-self.hsize/2<=p.get_xpos()+p.size/2 or p.get_xpos()-p.size/2<=self.x_pos+self.hsize/2<=p.get_xpos()+p.size/2:
                    #si el objeto es un plátano, condición de ganar. 
                    if isinstance(p,Banana):
                        if (realPos+0.05>=(self.y_pos+0.125) and realPos-0.05<=(self.y_pos+0.125) and self.airborne) or (realPos+0.05>=(self.y_pos-0.125) and self.y_pos-0.125>=realPos-0.05 and self.airborne):
                            self.winCond=1
                            return
                    #Revisar colisión subiendo (colisión por debajo de plataforma).
                    if self.v_speed>0:
                        if realPos+0.05>=(self.y_pos+0.125) and realPos-0.05<=(self.y_pos+0.125) and self.airborne:
                            self.y_pos=realPos-0.175
                            self.v_speed=0
                    #Revisar colisión bajando (colisión por encima de plataforma).
                    if self.v_speed<0:
                        if realPos+0.05>=(self.y_pos-0.125) and self.y_pos-0.125>=realPos-0.05 and self.airborne:
                            #si se encuentra colisión, actualizar el objeto colisionador, corregir posición y matar velocidad.
                            self.y_pos=realPos+0.175 
                            self.v_speed=0
                            self.airborne=False
                            self.cObj=p

        else:
            #Si está colisionando, revisar si sigue colisionando: si no, dejar de colisionar.
            if not (self.cObj.get_xpos()-self.cObj.size/2<=self.x_pos-0.1<=self.cObj.get_xpos()+self.cObj.size/2 
            or self.cObj.get_xpos()-self.cObj.size/2<=self.x_pos+0.1<=self.cObj.get_xpos()+self.cObj.size/2) or self.airborne:
                self.cObj=None
                self.airborne=True
     
    def update(self):
        #si se gana o pierde, se deja de actualizar la posición.
        if self.winCond==1 or self.winCond==-1:
            return
        #aceleración sujeta a una velocidad máxima.
        if self.moving_right and self.h_speed<=0.05:
            self.k+=1
        if self.moving_left and self.h_speed>=-0.05:
            self.k-=1
        #fricción del suelo.
        if not self.moving_left and not self.moving_right and not self.airborne:     
            if self.k>0:
                self.k-=1
            if self.k<0:
                self.k+=1
        #Gravedad.
        if self.airborne: 
            if self.v_speed>=-0.1:
                self.v_speed-=0.005 
        #si cae del mapa, pierdes.
        if self.y_pos+0.2<-1:
            self.winCond=-1
        #Colisión con los bordes del mapa.
        if self.x_pos+self.hsize/2>1:
            self.moving_right=False
            self.x_pos=1-self.hsize/2
            self.k=0
        if self.x_pos-self.hsize/2<-1:
            self.moving_left=False
            self.x_pos=-1+self.hsize/2
            self.k=0
        #Actualización de sprites.
        if self.h_speed==0:
            if not self.airborne:
                self.hsize=0.16
                self.model.childs=[self.sprites[0]]
                self.model.transform=tr.scale(self.hsize,0.25,0)
            else:
                self.hsize=0.17
                self.model.childs=[self.sprites[1]]
                self.model.transform=tr.scale(self.hsize,0.25,0)
        if self.h_speed>0:
            if not self.airborne:
                self.hsize=0.17
                self.contador+=0.1
                self.model.childs=[self.sprites[4+int(self.contador)%2]]
            else:
                if self.v_speed>0:
                    self.hsize=0.19
                    self.model.childs=[self.sprites[2]]
                else:
                    self.hsize=0.17
                    self.model.childs=[self.sprites[3]]
            self.model.transform=tr.scale(self.hsize,0.25,0)
        if self.h_speed<0:
            if not self.airborne:
                self.hsize=0.17
                self.contador+=0.1
                self.model.childs=[self.sprites[4+int(self.contador)%2]]                
            else:
                if self.v_speed>0:
                    self.hsize=0.19
                    self.model.childs=[self.sprites[2]]
                else:
                    self.hsize=0.17
                    self.model.childs=[self.sprites[3]]
            self.model.transform=tr.scale(-self.hsize,0.25,0)   
        #Actualización de velocidad y posición.
        self.h_speed=self.k*0.005
        self.x_pos+=self.h_speed
        self.y_pos+=self.v_speed


class Platform:
    def __init__(self):
        #Variables de plataformas.
        self.x_pos=0
        self.y_pos=0
        self.size=0.5
        #creando plataforma básica.
        gpuTextPlatform=es.toGPUShape(bs.createTextureQuad("img/plataforma.png"),GL_REPEAT,GL_NEAREST)
        #Creando nodo de plataforma.
        platform=sg.SceneGraphNode('platform')
        platform.transform=tr.scale(self.size,0.1,0)
        platform.childs += [gpuTextPlatform]
        #Creando nodo de posición de plataforma.
        platformPosition=sg.SceneGraphNode('platformPos')
        platformPosition.childs += [platform]
        #variable modelo del objeto.
        self.model=platformPosition
    
    #Getters y setters de posiciones.
    def set_xpos(self,x):
        self.x_pos=x
    def set_ypos(self,y):
        self.y_pos=y
    def get_xpos(self):
        return self.x_pos
    def get_ypos(self):
        return self.y_pos
    #Se actualiza la posición de la plataforma.
    def update(self):
        self.model.transform=tr.translate(self.x_pos,self.y_pos,0)

class Floor:
    def __init__(self):
        #Variable de posición y tamaño del piso.
        self.y_pos=-0.95
        self.size=2

        #Se crea el piso.
        gpuTextFloor=es.toGPUShape(bs.createTextureQuad("img/plataforma.png",4,1),GL_REPEAT,GL_NEAREST)
        #Creando el nodo del piso.
        floor=sg.SceneGraphNode('floor')
        floor.transform=tr.matmul([tr.translate(0,self.y_pos,0),tr.scale(self.size,0.1,0)])
        floor.childs += [gpuTextFloor]
        #Creando nodo de posición del piso.
        floorPosition=sg.SceneGraphNode('floorPos')
        floorPosition.childs += [floor]
        #variable modelo del objeto.
        self.model= floorPosition
    #getters posición
    def get_ypos(self):
        return self.y_pos
    def get_xpos(self):
        return 0

class Banana:
    def __init__(self):
        #variables posición y tamaño
        self.y_pos=0
        self.size=0.2
        #se crea la banana
        gpuTextBanana=es.toGPUShape(bs.createTextureQuad("img/bananas.png"),GL_REPEAT,GL_NEAREST)
        #nodo de la banana
        banana=sg.SceneGraphNode('banana')
        banana.transform=tr.scale(0.2,0.2,0)
        banana.childs+=[gpuTextBanana]
        #nodo de posición de la banana
        bananaPos=sg.SceneGraphNode('bananaPos')
        bananaPos.childs+=[banana]
        #variable modelo del objeto
        self.model=bananaPos
    #setters y getters
    def set_ypos(self,y):
        self.y_pos=y
        self.model.transform=tr.translate(0,y,0)
    def get_xpos(self):
        return 0
    def get_ypos(self):
        return self.y_pos

class Fondo:
    def __init__(self,mitades):
        #variable para identificar cuántas mitades de pantalla se deben dibujar
        self.mitades=mitades+4
        #se crea el nodo
        fondo=sg.SceneGraphNode('fondo')
        for k in range(self.mitades):
            #para cada mitad se va armando el fondo. Si es muy alto, se dibujan cielos.
            nodo=sg.SceneGraphNode("fondo_%s"%(k))
            nodo.transform=tr.matmul([tr.translate(0,k-1,0),tr.scale(2,1,0)])
            if k>=4:
                gpuBasicBG=es.toGPUShape(bs.createTextureQuad("img/fondos/fondo4.png"),GL_REPEAT,GL_NEAREST)
            else:
                gpuBasicBG=es.toGPUShape(bs.createTextureQuad("img/fondos/fondo%s.png"%k),GL_REPEAT,GL_NEAREST)
            nodo.childs+=[gpuBasicBG]
            fondo.childs+=[nodo]
        #variable modelo del objeto
        self.model=fondo
        
#ambiente
class Environment:
    #se crea el objeto con instrucción hacia el archivo del mapa
    def __init__(self,mapa):
        #piso
        floor=Floor()
        #banana
        banana=Banana()
        #variable de posición
        self.y_pos=0
        #lista auxiliar con plataformas y piso.
        self.objects=[floor,banana]

        #se generan las plataformas
        k=0
        #lectura del archivo csv
        with open(mapa) as csv_file:
            csv_reader=csv.reader(csv_file,delimiter=',')
            for row in csv_reader:
                k+=1
                for i in range(len(row)):
                    if row[i]=='1':
                        platform=Platform()
                        platform.set_xpos(0.7*(i-1))
                        platform.set_ypos(-0.1+(k-1)*0.7)
                        platform.update()
                        self.objects.append(platform)
        k+=1
        #se pone la banana al final
        banana.set_ypos(0.7*(k-1))
        #se crea el fondo con k mitades
        fondo=Fondo(k)
        #se crea el nodo de posición del ambiente
        environmentPos=sg.SceneGraphNode('environmentPos')
        environmentPos.childs+=[fondo.model]
        self.model=environmentPos

    #se dibuja el nodo (plataformas, fondo, piso y banana)
    def draw(self,pipeline):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.model, pipeline,'transform')
    #mueve el ambiente en y
    def move(self,y):
        self.y_pos=y
    #se actualiza la posición, solo se dibujan los elementos en pantalla.
    def update(self):
        drawableObjs=[]
        for x in self.objects:
            if x.get_ypos()+self.y_pos<=1.05 and x.get_ypos()+self.y_pos>=-1:
                drawableObjs+=[x.model]
        fondo=sg.findNode(self.model,'fondo')         
        self.model.childs=[fondo]+drawableObjs
        #se actualiza la posición
        self.model.transform=tr.translate(0,self.y_pos,0)
    #retorna una lista con los objetos con los que el mono puede colisionar.
    def factPos(self):
        factiblePositions=[]
        for x in self.objects:
            if x.get_ypos()+self.y_pos<=1 and x.get_ypos()+self.y_pos>=-1:
                factiblePositions+=[x]
        return factiblePositions

class Camera:
    def __init__(self,monke: 'Monkey',env: 'Environment'):
        #se crea el objeto con un mono y un ambiente
        self.monkey=monke
        self.env=env

    def update(self):
        #si no se ha ganado y el mono está suficientemente alto se mueve la cámara.
        if self.monkey.winCond==0:
            if self.monkey.y_pos>0.25:
                self.move()
    def move(self):
        #se baja el mono y el ambiente en igual cantidad
        self.monkey.y_pos-=0.02
        self.env.y_pos-=0.02

class EndAnimation:

    def __init__(self):
        gpuBlackBG=es.toGPUShape(bs.createColorQuad(0,0,0))
        self.fondo=sg.SceneGraphNode('BG')
        self.fondo.childs+=[gpuBlackBG]
        self.fondo.transform=tr.scale(2,2,0)
        self.k=0
    
    def deathAnimate(self,pipeline,pipeline_text):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.fondo,pipeline,'transform')
        letras=sg.SceneGraphNode('letras')

        letras.childs+=[es.toGPUShape(bs.createTextureQuad('img/death/muerte.png'),GL_REPEAT,GL_LINEAR)]
        if self.k<=10:
            letras.transform=tr.scale(self.k/10,self.k/20,0)
            self.k+=0.5
        else:
            letras.transform=tr.scale(1,1/2,0)
        glUseProgram(pipeline_text.shaderProgram)
        sg.drawSceneGraphNode(letras,pipeline_text,'transform')
    def winAnimate(self,pipeline,pipeline_text):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.fondo,pipeline,'transform')
        letras=sg.SceneGraphNode('letras')

        letras.childs+=[es.toGPUShape(bs.createTextureQuad('img/win/ganar.png'),GL_REPEAT,GL_LINEAR)]
        if self.k<=10:
            letras.transform=tr.scale(self.k/10,self.k/20,0)
            self.k+=0.5
        else:
            letras.transform=tr.scale(1,1/2,0)
        glUseProgram(pipeline_text.shaderProgram)
        sg.drawSceneGraphNode(letras,pipeline_text,'transform')