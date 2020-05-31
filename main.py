#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

import time
import random
import math

x = 0
Running = True
Count = 0
Invader_list = []
En_Bullets = []
Pl_Bullets = []
En_Delta = 2
En_Bullet_Next_Time = 20
Px = 178/2 - 24/2
Py = 128-20
# bx = 0
# by = -1000
#isBulletShow = False
Bullet_Spd = 4
GameStep = "Init"
StartEnInterval = 15
NewEnInterval = 15
FireEnabled = True
LastFireCount = 0
FireMinInterval = 7
GameResult = "Win"

# Create your objects here.
ev3 = EV3Brick()
stick = Motor(Port.D)
FireBtn = TouchSensor(Port.S2)


# load enemys
for cur in range(5):
    for yp in range(3):
        _x = cur * (24 + 5) 
        _y = yp * (18 + 2)
        Invader_list.append([_x, _y, True])

# update enemy objs datas
def UpdateEns():
    global Count, En_Delta
    Count += 1
    if Count % 5 == 0:
        isReverseNeeded = False
        for en in Invader_list:
            en[0] += En_Delta
            en[2] = not en[2]
            if en[0] > 178-24 or en[0] < 0 :
                isReverseNeeded = True
        if isReverseNeeded:
            En_Delta *= -1

# 적과 플레이어의 총알 업데이트
def UpdateBullet():
    global En_Bullets, Pl_Bullets

    for b in En_Bullets:
        b[1] += Bullet_Spd
        if b[1] > 128:
            En_Bullets.remove(b)

    # Player의 총알 업데이트
    for bb in Pl_Bullets:
        bb[1] -= Bullet_Spd
        if bb[1] < 0:
            Pl_Bullets.remove(bb)


def UpdatePlayer(btn):
    global Px, Py
    if btn == Button.LEFT:
        Px -= 4
        if Px < 0:
            Px = 0
    elif btn == Button.RIGHT:
        Px += 4
        if Px > 178 - 24:
            Px = 178-24
    else:
        pass


def FireBullet():
    # global bx, by, isBulletShow
    # if isBulletShow == False:
    #     bx = Px + 12
    #     by = 128-20
    #     isBulletShow = True
    #     ev3.speaker.beep(600, 20)
    global Pl_Bullets, FireEnabled, LastFireCount

    if FireEnabled:
        _x = Px + 12
        _y = 128 - 20
        Pl_Bullets.append([_x, _y])
        FireEnabled = False
        LastFireCount = Count
        ev3.speaker.beep(600, 20) 

def DrawEnBullet():
    global En_Bullets, En_Bullet_Next_Time, FireEnabled 
    if len(Invader_list) == 0:
        return

    if Count == En_Bullet_Next_Time:
        en = None
        if len(Invader_list) > 1:
            en = Invader_list[random.randint(0, len(Invader_list)-1)]
        else:
            en = Invader_list[0]
        _x = en[0] + 12
        _y = 20
        En_Bullets.append([_x, _y])
        En_Bullet_Next_Time = Count + random.randint(NewEnInterval, NewEnInterval+5)
        ev3.speaker.beep(700, 20)
    
    for b in En_Bullets:
        _x = b[0]
        _y = b[1]
        ev3.screen.draw_box(_x, _y, _x+1, _y+5)

    if Count > LastFireCount + FireMinInterval:
        FireEnabled = True

def DrawPlBullet():
    global Pl_Bullets
    for bb in Pl_Bullets:
        _x = bb[0]
        _y = bb[1]
        ev3.screen.draw_box(_x, _y, _x+1, _y+5)

def DrawPlayer():
    ev3.screen.draw_image(Px, Py, "player.png")

def HandleInputs():
    global Px, Py, Running, GameStep
    ang = stick.angle()
    btns = ev3.buttons.pressed()
    if len(btns) > 0:
        if GameStep == "Intro":
            if btns[0] in (Button.LEFT, Button.RIGHT, Button.CENTER):
                Running = False
            else:
                pass
        elif GameStep == "OnGame":
            if btns[0] == Button.LEFT:
                UpdatePlayer(Button.LEFT)
            elif btns[0] == Button.RIGHT:
                UpdatePlayer(Button.RIGHT)
            elif btns[0] == Button.CENTER:
                FireBullet()
            else:
                pass

    if ang < -15:
        UpdatePlayer(Button.LEFT)
    elif ang > 15:
        UpdatePlayer(Button.RIGHT)
    
    if FireBtn.pressed():
        FireBullet()

def CheckCollide():
    global Invader_list, Pl_Bullets, En_Bullets, Running, GameResult
    # enemy 
    for e in Invader_list:
        x = e[0]+12
        y = e[1]+9
        for b in Pl_Bullets:
            d = math.sqrt( pow(b[0]-x, 2) + pow(b[1]-y, 2))
            if d < 12:
                Invader_list.remove(e)
                Pl_Bullets.remove(b)
                ev3.speaker.beep(1000, 20)

    # player
    for bb in En_Bullets:
        x = Px + 12
        y = Py+9
        d = math.sqrt(pow(bb[0]-x, 2) + pow(bb[1]-y, 2))
        if d < 12:
            GameResult = "Lose"
            Running = False
            ev3.speaker.beep(1200, 20)

def CheckGameQuit():
    global Running, NewEnInterval, En_Delta, GameResult
    if len(Invader_list) == 0 :
        GameResult = "Win"
        Running = False

    NewEnInterval = StartEnInterval - (15-len(Invader_list))
    sig = En_Delta/abs(En_Delta)
    En_Delta = sig*(2 + (15-len(Invader_list))//2)

def WaitForButton():
    pressed = []
    while len(pressed) != 1:
        pressed = ev3.buttons.pressed()
    button = pressed[0]

    # Now wait for the button to be released.
    while any(ev3.buttons.pressed()):
        pass

    return button

def DrawIntro():
    global GameStep
    GameStep = "Intro"
    ev3.screen.clear()
    ev3.screen.draw_image(0, 0, "invader_bg.png")
    ev3.speaker.say("Lets game start!!!")
    WaitForButton()


def DrawGameEnd():
    global GameStep
    GameStep = "Quit"
    ev3.screen.clear()
    ev3.screen.draw_image(0, 0, "invader_ending.png")
    
    if GameResult == "Lose":
        ev3.speaker.say("Game Over, Game Over. You loser!!! Try Again.")
    else:
        ev3.speaker.say("Congratulation, You win this game, You are great!!!")
    WaitForButton()

DrawIntro()

Running = True
GameStep = "OnGame"
while Running:
    HandleInputs()

    ev3.screen.clear()

    if Count % 5 == 0:
        ev3.speaker.beep(200, 50)
    for en in Invader_list:
        if en[2] == True:
            ev3.screen.draw_image(en[0], en[1], "invader.png")
        else :
            ev3.screen.draw_image(en[0], en[1], "invader2.png")

    DrawPlayer()
    DrawEnBullet()
    DrawPlBullet()

    CheckCollide()
    CheckGameQuit()

    UpdateEns()
    UpdateBullet()

    time.sleep(0.1)


DrawGameEnd()
