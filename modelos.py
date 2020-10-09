import scene_graph as sg
import easy_shaders as es
import transformations as tr
import basic_shapes as bs
import csv
from typing import List, Union

class Monkey:

    def __init__(self):
        self.x_pos=0
        self.y_pos=-0.5
        self.h_speed=0
        self.v_speed=0
        self.winCond=0
        self.airborne=True
        self.moving_left=False
        self.moving_right=False
        self.cObj=None
        self.k=0

        gpuBasicMonke=es.toGPUShape(bs.createColorQuad(117/255,73/255,29/255))
    
        monke=sg.SceneGraphNode('monkey')
        monke.transform=tr.scale(0.2,0.4,0)
        monke.childs += [gpuBasicMonke]

        monkeyPos=sg.SceneGraphNode('monkeyPos')
        monkeyPos.childs+=[monke]
        self.model = monkeyPos

    def draw(self,pipeline):
        self.model.transform=tr.translate(self.x_pos,self.y_pos,0)
        sg.drawSceneGraphNode(self.model,pipeline,'transform')

    def stop(self):
        self.moving_left=False
        self.moving_right=False

    def move_left(self):
        self.moving_left=True

    def move_right(self):
        self.moving_right=True
        
    def jump(self):
        if self.airborne:
            return
        self.airborne=True
        self.v_speed=0.1
        self.y_pos+=0.01

    def collide(self, env: 'Environment'):
        fpos: List[Union['Floor', 'Platform', None]]
        fpos=env.factPos()
        #print(self.cObj)
        if self.cObj==None:
            for p in fpos:
                realPos=p.get_ypos()+env.y_pos
                if p.get_xpos()-p.size/2<=self.x_pos-0.1<=p.get_xpos()+p.size/2 or p.get_xpos()-p.size/2<=self.x_pos+0.1<=p.get_xpos()+p.size/2:
                    if isinstance(p,Banana):
                        if (realPos+0.05>=(self.y_pos+0.2) and realPos-0.05<=(self.y_pos+0.2) and self.airborne) or (realPos+0.05>=(self.y_pos-0.2) and self.y_pos-0.2>=realPos-0.05 and self.airborne):
                            self.winCond=1
                            return
                    if self.v_speed>0: ##Subiendo Colisión por abajo
                        if realPos+0.05>=(self.y_pos+0.2) and realPos-0.05<=(self.y_pos+0.2) and self.airborne:
                            # print('up collision')
                            self.y_pos=realPos-0.25
                            self.v_speed=0
                    
                    if self.v_speed<0:
                        if realPos+0.05>=(self.y_pos-0.2) and self.y_pos-0.2>=realPos-0.05 and self.airborne:
                            # print('down collision')                        
                            self.y_pos=realPos+0.25
                            self.v_speed=0
                            self.airborne=False
                            self.cObj=p

        else:
            if not (self.cObj.get_xpos()-self.cObj.size/2<=self.x_pos-0.1<=self.cObj.get_xpos()+self.cObj.size/2 
            or self.cObj.get_xpos()-self.cObj.size/2<=self.x_pos+0.1<=self.cObj.get_xpos()+self.cObj.size/2) or self.airborne:
                self.cObj=None
                self.airborne=True
     
    def update(self):
        if self.winCond==1 or self.winCond==-1:
            return
        #aceleración sujeta a una velocidad máxima
        if self.moving_right and self.h_speed<=0.05:
            self.k+=1
        if self.moving_left and self.h_speed>=-0.05:
            self.k-=1
        #fricción del suelo
        if not self.moving_left and not self.moving_right and not self.airborne:     
            if self.k>0:
                self.k-=1
            if self.k<0:
                self.k+=1
        #Gravedad
        if self.airborne: 
            if self.v_speed>=-0.1:
                self.v_speed-=0.005 
        if self.y_pos+0.2<-1:
            self.winCond=-1
            print('You Died')
        # print(self.h_speed)
        self.h_speed=self.k*0.01
        self.x_pos+=self.h_speed
        self.y_pos+=self.v_speed


class Platform:

    def __init__(self):
        self.x_pos=0
        self.y_pos=0
        self.size=0.5
        gpuBasicPlatform=es.toGPUShape(bs.createColorQuad(102/255,51/255,0/255))

        #creating the platform
        platform=sg.SceneGraphNode('platform')
        platform.transform=tr.scale(self.size,0.1,0)
        platform.childs += [gpuBasicPlatform]

        platformPosition=sg.SceneGraphNode('platformPos')
        platformPosition.childs += [platform]
        self.model=platformPosition
    
    def draw(self,pipeline):
        sg.drawSceneGraphNode(self.model,pipeline,'transform')

    def set_xpos(self,x):
        self.x_pos=x
    def set_ypos(self,y):
        self.y_pos=y
    def get_xpos(self):
        return self.x_pos
    def get_ypos(self):
        return self.y_pos
    def update(self):
        self.model.transform=tr.translate(self.x_pos,self.y_pos,0)

class Floor:

    def __init__(self):
        gpuBasicFloor=es.toGPUShape(bs.createColorQuad(102/255,52/255,0/255))
        self.y_pos=-0.95
        self.size=2
        #Floor
        floor=sg.SceneGraphNode('floor')
        floor.transform=tr.matmul([tr.translate(0,self.y_pos,0),tr.scale(self.size,0.1,0)])
        floor.childs += [gpuBasicFloor]

        #floor position
        floorPosition=sg.SceneGraphNode('floorPos')
        floorPosition.childs += [floor]

        self.model= floorPosition

    def draw(self,pipeline):
        sg.drawSceneGraphNode(self.model,pipeline,'transform')
    def get_ypos(self):
        return self.y_pos
    def get_xpos(self):
        return 0

class Banana:
    def __init__(self):
        gpuBasicBanana=es.toGPUShape(bs.createColorQuad(255/255,255/255,52/255))
        self.y_pos=0
        self.size=0.2
        banana=sg.SceneGraphNode('banana')
        banana.transform=tr.scale(0.2,0.2,0)
        banana.childs+=[gpuBasicBanana]
        
        bananaPos=sg.SceneGraphNode('bananaPos')
        bananaPos.childs+=[banana]
        self.model=bananaPos
    def set_ypos(self,y):
        self.y_pos=y
        self.model.transform=tr.translate(0,y,0)
    def get_xpos(self):
        return 0
    def get_ypos(self):
        return self.y_pos

#ambiente
class Environment:

    def __init__(self,mapa):
        #piso
        floor=Floor()
        #banana
        banana=Banana()
        #plataformas
        k=0
        self.objects=[floor,banana]

        environmentPos=sg.SceneGraphNode('environmentPos')
        environmentPos.childs+=[floor.model]
        with open(mapa) as csv_file:
            csv_reader=csv.reader(csv_file,delimiter=',')
            for row in csv_reader:
                k+=1
                for i in range(len(row)):
                    if row[i]=='1':
                        platform=Platform()
                        platform.set_xpos(0.7*(i-1))
                        platform.set_ypos(-0.1+(k-1)*0.7)
                        # print(platform.get_ypos())
                        platform.update()
                        self.objects.append(platform)
                        environmentPos.childs+=[platform.model]
        k+=1
        banana.set_ypos(0.7*(k-1))
        environmentPos.childs+=[banana.model]
        self.model=environmentPos
        self.y_pos=0

    def draw(self,pipeline):
        sg.drawSceneGraphNode(self.model,pipeline,'transform')
    
    def move(self,y):
        self.y_pos=y

    def update(self):
        self.model.transform=tr.translate(0,self.y_pos,0)
    
    def factPos(self):
        factiblePositions=[]
        for x in self.objects:
            if x.get_ypos()+self.y_pos<=1 and x.get_ypos()+self.y_pos>=-1:
                #print(x.get_ypos())
                factiblePositions+=[x]
        #print(factiblePositions)
        return factiblePositions

class Camera:
    def __init__(self,monke: 'Monkey',env: 'Environment'):
        self.monkey=monke
        self.env=env

    def update(self):
        if self.monkey.winCond==0:
            if self.monkey.y_pos>0.25:
                self.move()
    def move(self):
        self.monkey.y_pos-=0.02
        self.env.y_pos-=0.02