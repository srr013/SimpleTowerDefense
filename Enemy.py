import os
from pygame.locals import *
import math

import localdefs
import Utilities
import Player
import Map
import SenderClass

from kivy.graphics import *
from kivy.uix.widget import Widget

class Enemy(Widget):
    def __init__(self,**kwargs):
        super(Enemy,self).__init__()
        #if self.imgindex == 2:
            #self.animation = Animation.Animate(folder = os.path.join("enemyimgs", "Bird A"))
            #self.image = self.animation.adjust_images("right")

        self.curnode = 0
        self.size = (20, 20)
        self.image.size = self.size
        self.rect = Utilities.createRect(self.movelist[self.curnode], self.size, instance=self)
        self.pos = (self.rect_centerx, self.rect_centery)
        self.add_widget(self.image)
        Map.mapvar.enemycontainer.add_widget(self)
        self.cost = 1
        self.health = 1
        self.speed = 1
        self.starthealth = self.health
        self.startspeed = self.speed
        self.route = 1
        self.slowtimers = list()
        self.slowpercent = .2
        self.slowtime = 0
        self.poisontimer = None
        self.armor = 1
        self.points = 1
        self.distBase = self.distToBase()
        self.explosionlength = 1
        self.isair = False

        with self.canvas: #draw health bars
            Color(0,0,0,.6)
            self.healthbar = Line(points = [self.x, self.y+self.height+2, self.x+self.width, self.y+self.height+2], width = 2, cap=None)
            Color(1,1,1,1)
            self.remaininghealth = Line(points = [self.x, self.y+self.height+2, self.x+self.width, self.y+self.height+2], width = 1.4, cap=None)


    def takeTurn(self):
        '''Moves the enemy and adjusts any slow applied to it
        Frametime: the amount of time elapsed per frame'''
        self.workSlowTimers()
        self.move()
        self.updateHealthBar()

    def workSlowTimers(self):
        '''Adjust slow already applied to enemy
        Frametime: the amount of time elapsed per frame'''
        for st in self.slowtimers:
            st.slowtime -= Player.player.frametime
            if st.slowtime<=0:
                self.slowtimers.remove(st)

    def distToBase(self):
        '''Determine distance to the end point using hypotenuse of xs and ys. Returns the distance.'''
        return math.sqrt(math.pow(Map.mapvar.basepoint[0]*30-self.rect_centerx,2)+math.pow(Map.mapvar.basepoint[1]*30-self.rect_centery,2))


    def move(self):
        '''Moves the enemy down the generated move list
        Frametime: the amount of time elapsed per frame'''
        ##right now just using a for ground troops, b for flying.
        #if self.letter=='a':
        #    self.movelist = Map.mapvar.pointmovelists[0]
        if self.slowtime > 0:
            moveamt = round(self.slowpercent*Player.player.frametime*self.speed*30,2)
        else:
            moveamt = round(self.speed*Player.player.frametime*30,2)

        ##Check to see if the enemy hits the Base and remove enemy and decrement player health
        #for i in range(int(self.speed*30)):
        if self.curnode+1 >= len(self.movelist)-1:
            if Map.mapvar.baseimg.collide_widget(self.image):
                Player.player.health -= 1
                Map.mapvar.enemycontainer.remove_widget(self)
                if Player.player.health<=0:
                    Player.player.die()
                return

        #move enemy x and y based on the moveamt calculated above
        if (round(self.pos[0],0), round(self.pos[1],0))==(self.movelist[self.curnode+1]):
            self.curnode+=1
        #print ("pos,movelist", self.pos, self.movelist[self.curnode+1])
        if self.movelist[self.curnode+1][0]>self.pos[0]:
            #print ("moving right:", self.rect_centerx, self.movelist[self.curnode+1][0])
            self.rect_centerx+=moveamt
            #self.image = self.animation.adjust_images("right")
        elif self.movelist[self.curnode+1][0]<self.pos[0]:
            self.rect_centerx-=moveamt
            #self.image = self.animation.adjust_images("left")
        if self.movelist[self.curnode+1][1]>self.pos[1]:
            self.rect_centery+=moveamt
            #self.image = self.animation.adjust_images("down")
        elif self.movelist[self.curnode+1][1]<self.pos[1]:
            self.rect_centery-=moveamt
            #self.image = self.animation.adjust_images("up")
        self.pos = (self.rect_centerx,self.rect_centery)
        self.image.pos = self.pos

    def checkHealth(self):
        '''Checks enemy health and kills the enemy if health <=0'''
        if self.health<=0:
            Player.player.kill_score += self.points
            self.die()

    def die(self):
        '''If enemy runs out of health add them to explosions list, remove from enemy list, and add money to player's account'''
        if self.type == 'Splinter':
            self.splinter()
        localdefs.explosions.append([(self.rect_centerx, self.rect_centery),self.explosionlength, self])
        self.remove_widget(self.image)
        Map.mapvar.enemycontainer.remove_widget(self)
        Player.player.money+=(self.cost)

    def updateHealthBar(self):
        self.healthbar.points = [self.x, self.y + self.height + 2, self.x + self.width, self.y + self.height + 2]
        self.percentHealthRemaining = self.health/self.starthealth
        self.remaininghealth.points = [self.x, self.y+self.height+2, self.x+self.width*self.percentHealthRemaining, self.y+self.height+2]



    def dispExplosions(self, explosion):
        '''Display any explosions in the queue, then remove them.'''
        if explosion[1] == self.explosionlength:
            self.explosionimg = Utilities.imgLoad(os.path.join("enemyimgs", 'explosion.png'))
            self.explosionimg.pos = (explosion[0][0], explosion[0][1])
            self.explosionimg.size = (20, 20)
            Map.mapvar.explosioncontainer.add_widget(self.explosionimg)

        if explosion[1] < 0:
            localdefs.explosions.remove(explosion)
            Map.mapvar.explosioncontainer.remove_widget(self.explosionimg)
        else:
            explosion[1] -= 1


class Standard(Enemy):
    defaultNum = 10
    deploySpeed = 1
    health = 100
    speed = 20
    armor = 0
    reward = 5
    points = 10

    def __init__(self,**kwargs):
        self.type = 'Standard'
        self.defaultNum = Standard.defaultNum
        self.deploySpeed = Standard.deploySpeed
        self.health = Standard.health #100 HP per enemy
        self.speed = Standard.speed
        self.armor = Standard.armor
        self.reward = Standard.reward #cash granted per kill
        self.points = Standard.points #points granted per kill
        self.image = Utilities.imgLoad(os.path.join("enemyimgs","explosion.png"))
        self.movelist = Map.mapvar.pointmovelists[0] #0 for ground, 1 for air
        self.isair = False
        self.isBoss = False
        super(Standard, self).__init__(**kwargs)


class Airborn(Enemy):
    defaultNum = 10
    deploySpeed = 1
    health = 100
    speed = 30
    armor = 0
    reward = 5
    points = 10
    def __init__(self, **kwargs):
        self.type = 'Airborn'
        self.defaultNum = Airborn.defaultNum  # 10 enemies per wave
        self.deploySpeed = Airborn.deploySpeed
        self.health = Airborn.health  # 100 HP per enemy
        self.speed = Airborn.speed
        self.armor = Airborn.armor
        self.reward = Airborn.reward  # cash granted per kill
        self.points = Airborn.points  # points granted per kill

        self.image = Utilities.imgLoad(os.path.join("enemyimgs", "Bird A","frame-1.png"))
        self.movelist = Map.mapvar.pointmovelists[1]  # 0 for ground, 1 for air
        self.isair = True
        self.isBoss = False
        super(Airborn, self).__init__(**kwargs)


class Splinter(Enemy):
    defaultNum = 5
    deploySpeed = 3
    health = 400
    speed = 10
    armor = 5
    reward = 10
    points = 20
    def __init__(self, **kwargs):
        self.type = 'Splinter'
        self.defaultNum = Splinter.defaultNum  # 10 enemies per wave
        self.deploySpeed = Splinter.deploySpeed
        self.health = Splinter.health  # 100 HP per enemy
        self.speed = Splinter.speed
        self.armor = Splinter.armor
        self.reward = Splinter.reward  # cash granted per kill
        self.points = Splinter.points  # points granted per kill
        self.image = Utilities.imgLoad(os.path.join("enemyimgs", "Bird A","frame-1.png"))
        self.movelist = Map.mapvar.pointmovelists[0]  # 0 for ground, 1 for air
        self.isBoss = False
        super(Splinter, self).__init__(**kwargs)

    #break the Splinter apart when it dies. 15 Crowd are released.
    def splinter(self):
        SenderClass.Sender(specialSend = True, enemytype='Crowd', pos=self.pos, number=15)


class Strong(Enemy):
    defaultNum = 5
    deploySpeed = 3
    health = 600
    speed = 10
    armor = 10
    reward = 10
    points = 20

    def __init__(self,**kwargs):
        self.type = 'Strong'
        self.defaultNum = Strong.defaultNum
        self.deploySpeed = Strong.deploySpeed
        self.health = Strong.health #100 HP per enemy
        self.speed = Strong.speed
        self.armor = Strong.armor
        self.reward = Strong.reward #cash granted per kill
        self.points = Strong.points #points granted per kill
        self.image = Utilities.imgLoad(os.path.join("enemyimgs","explosion.png"))
        self.movelist = Map.mapvar.pointmovelists[0] #0 for ground, 1 for air
        self.isair = False
        self.isBoss = False ###is this needed?
        super(Strong, self).__init__(**kwargs)

class Crowd (Enemy):
    defaultNum = 30
    deploySpeed = 5
    health = 50
    speed = 15
    armor = 0
    reward = 3
    points = 6

    def __init__(self,**kwargs):
        self.type = 'Crowd'
        self.defaultNum = Crowd.deploySpeed
        self.health = Crowd.health #100 HP per enemy
        self.speed = Crowd.speed
        self.armor = Crowd.armor
        self.reward = Crowd.reward #cash granted per kill
        self.points = Crowd.points #points granted per kill
        self.image = Utilities.imgLoad(os.path.join("enemyimgs","explosion.png"))
        self.movelist = Map.mapvar.pointmovelists[0] #0 for ground, 1 for air
        self.isair = False
        self.isBoss = False
        super(Crowd, self).__init__(**kwargs)
