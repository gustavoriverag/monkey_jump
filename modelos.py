import scene_graph as sg
import easy_shaders as es
import transformations as tr
import basic_shapes as bs
import csv
from typing import List, Union

class Monkey:

    def __init__(self):
        self.x_pos=0.7
        self.y_pos=0.2
        self.h_speed=0
        self.v_speed=0
        self.airborne=False
        self.moving_left=False
        self.moving_right=False
        self.k=0
        self.isColliding=False
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
    # def collide(self, env: 'Environment'):
    #     fpos: List[Union['Floor', 'Platform', None]]
    #     fpos=env.factPos()
    #     for p in fpos:
    #         if p.get_xpos()-p.size/2<=self.x_pos-0.1<=p.get_xpos()+p.size/2 or p.get_xpos()+p.size/2>=self.x_pos+0.1>=p.get_xpos()-p.size/2:
    #             if p.get_ypos()<=(self.y_pos-0.2) and p.get_ypos()+0.05>=(self.y_pos-0.2) and self.v_speed<=0:
    #                 print('platpos=',p.get_ypos()+0.05,'\n','playerpos=',self.y_pos-0.2)
    #                 self.y_pos=p.get_ypos()+0.25
    #                 self.v_speed=0
    #                 self.airborne=False
    #         else:
    #             self.airborne=True

    def update(self):
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
        if self.airborne:
            self.v_speed-=0.005
            # if self.h_speed>0:
            #     self.k-=1
            
        # print(self.h_speed)
        self.h_speed=self.k*0.01
        self.x_pos+=self.h_speed
        # if self.x_pos>=0.9:
        #     print('choque')
        #     self.moving_right=False
        #     self.h_speed=0
        #     self.x_pos=0.9
        # if self.x_pos<-0.9:
        #     self.moving_left=False
        #     self.h_speed=0
        #     self.x_pos=-0.9
        # if self.y_pos<-0.7 and self.airborne:
        #     self.v_speed=0
        #     self.y_pos=-0.7
        #     self.airborne=False
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
        self.y_pos=-1
        self.size=2
        #Floor
        floor=sg.SceneGraphNode('floor')
        floor.transform=tr.matmul([tr.translate(0,self.y_pos,0),tr.scale(self.size,0.2,0)])
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
#ambiente
class Environment:

    def __init__(self,mapa):
        #piso
        floor=Floor()
        #plataformas
        k=0
        self.objects=[floor]

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
                        print(platform.get_ypos())
                        platform.update()
                        self.objects.append(platform)
                        environmentPos.childs+=[platform.model]
                
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