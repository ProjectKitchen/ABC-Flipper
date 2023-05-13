import tkinter as tk
import tkinter.font as tkFont
from tkinter import *

# from tkextrafont import Font

import random
from random import randrange
import pygame
import serial
import time
import array
import string
from pathlib import Path
from PIL import ImageFont, Image, ImageTk
import os

if (os.name == 'posix'):
    runningOnRaspi=1
else:
    runningOnRaspi=0


raspiPortName="/dev/ttyACM0"
otherPortName="COM17"


CMD_LCD_ROTATE='7'
CMD_LCD_GOIDLE='8'

GAMESTATE_IDLE =   'a'
GAMESTATE_FLIPPER ='b'
GAMESTATE_ANAGRAM = 'c'
GAMESTATE_WON = 'd'
GAMESTATE_LOST = 'e'

CMD_TRIGGER_BALL='f'
CMD_TRIGGER_BELL='g'


screenstate = True
textcolor="yellow"
boardcolor="gray"
activeboardcolor="red"
backgroundcolor="black"
maxLetters=5
maxTargets=5
maxLives=3
lives=0
gameState=GAMESTATE_IDLE
points=0
winAnim=0
looseAnim=0
clockAnim=0
coinAnim=0

pinballXPos=80
pinballYPos=70
pinballWidth=110
clockSize=105

letterIDs = array.array('i',(0 for i in range(0,maxLetters))) 
boardIDs = array.array('i',(0 for i in range(0,maxLetters))) 
pinballIDs = array.array('i',(0 for i in range(0,maxLives))) 
boxID = 0
pointsID=0
clockID = 0
coinID=0

letterwidth=0
modifyLetter=0   
actTargets = array.array('u',('x' for i in range(0,maxTargets))) 
keyPressed=""
ballLostBypass=0

def getPath(name):
    return (str(Path(__file__).resolve().parent.joinpath(name)))


def sendLCDLetter(pos,letter):
    if runningOnRaspi==0:
        return   
    sendString=str(pos)+letter
    #print("sending to Serial:"+sendString)
    ser.write(sendString.encode())
    return

def sendCommand(cmd):
    if runningOnRaspi==0:
        return   
    sendString=cmd
    print("sending command to Serial:"+sendString)
    ser.write(sendString.encode())
    return
    
def printTargetsLCD():
    print ("Act Targets:", end="")
    for i in range (maxTargets):
        print (str(actTargets[maxTargets-1-i]) , end="")
        sendLCDLetter(i+1,actTargets[i])
    print (" ")


def playSound(s):
    fn=getPath("../sounds/"+ s +".wav") 
    sound = pygame.mixer.Sound(fn)
    playing = sound.play()    
    #while playing.get_busy():
    #    pygame.time.delay(10)


'''
     game control routines
'''

def changeLetter():
    global modifyLetter
    modifyLetter=modifyLetter+1
    if (modifyLetter>=len(actword)):
        modifyLetter=0
    print ("button3 - change letter: " + str(modifyLetter))
    updateLetters(actword)
    
def switchLetterLeft():
    global modifyLetter, actword
    if (len(actword)<1):
        return
    if (modifyLetter>0):
        nextLetter=modifyLetter-1;
        if (nextLetter>=len(actword)):
            nextLetter=0
        s=list(actword)
        tmp=s[nextLetter]
        s[nextLetter]=s[modifyLetter]
        s[modifyLetter]=tmp
        actword="".join(s)
        modifyLetter=nextLetter    

    print ("button2 - switch letters left, actword = " + actword)
    updateLetters(actword)

def switchLetterRight():
    global modifyLetter, actword
    if (len(actword)<1):
        return
    if (modifyLetter<len(actword)-1):
        nextLetter=modifyLetter+1;
        if (nextLetter>=len(actword)):
            nextLetter=0
        s=list(actword)
        tmp=s[nextLetter]
        s[nextLetter]=s[modifyLetter]
        s[modifyLetter]=tmp
        actword="".join(s)
        modifyLetter=nextLetter    

    print ("button4 - switch letters right, actword = " + actword)
    updateLetters(actword)


def addLetter(pos):
    global actword
    if (len(actword)<maxLetters) and (actTargets[pos] != ' '):
        actword=actword+actTargets[pos]
        updateLetters(actword)
        playSound('f'+str(pos+1))
        actTargets[pos]=' '
        printTargetsLCD()
    else:
        playSound('t1')

def keydown(e):
    global keyPressed
    print ('keyDown', e.char)
    keyPressed = str(e.char)

def keyup(e):
    print ('keyUp', e.char)
    
    
'''
     Drawing / Tk rountines
'''

def toggle_fullscreen(self, event=None):
    global screenstate, root
    screenstate = not screenstate  # Just toggling the boolean
    root.attributes("-fullscreen", screenstate)

def end_fullscreen(self, event=None):
    global screenstate, root
    screenstate = False
    root.attributes("-fullscreen", False)
    return "break"

def abs_move(self, _object, new_x, new_y):
    # Get the current object position
    x, y, *_ = self.bbox(_object)
    # Move the object
    self.move(_object, new_x-x, new_y-y)
    
def updatePoints(p):
    global points
    points=points+p
    tkCanvas.itemconfigure(pointsID,text=str(points).zfill(8))   

def createScene():
    global letterIDs, boxID, pinballID, pointsID, clockID, coinID
    for i in range (maxLetters):
        letterIDs[i] = tkCanvas.create_text(lettersXPos+10+letterwidth*i, lettersYPos, text=" ", anchor="nw", font=letterfont, fill=textcolor)
        x0, y0, x1, y1 = tkCanvas.bbox(letterIDs[i])
        boardIDs[i]=tkCanvas.create_rectangle(lettersXPos+letterwidth*i, lettersYPos, lettersXPos+letterwidth*(i+1), y1, fill=boardcolor, outline="white")
        tkCanvas.lift(letterIDs[i],boardIDs[i])
    boxID = tkCanvas.create_rectangle(lettersXPos, y1+10, lettersXPos+letterwidth, y1+20, fill="white", outline="white")
    for i in range (maxLives):
        pinballIDs[i]=tkCanvas.create_image(pinballXPos+i*pinballWidth, pinballYPos, image=pinballImg, anchor="center")

    pointsID=tkCanvas.create_text(int(screen_width/3*2), 40, text="000000000", anchor="nw", font=pointfont, fill="#FF2020")
    clockID =tkCanvas.create_arc(0,pinballYPos, clockSize,pinballYPos+clockSize, start=90, extent=0, fill="#000000")
    coinID =tkCanvas.create_image(pinballXPos, pinballYPos, image=coinImg, anchor="center")

def updateLetters(string):
    global winAnim, clockAnim
    for i in range (len(string)):
        tkCanvas.itemconfigure(letterIDs[i],text=str(string[i]))        
    for i in range(len(string),maxLetters):
        tkCanvas.itemconfigure(letterIDs[i],text=' ')
    for i in range(maxLetters):
        if (i==modifyLetter) and (gameState==GAMESTATE_ANAGRAM):
            tkCanvas.itemconfigure(boardIDs[i],fill=activeboardcolor)
        else:
            tkCanvas.itemconfigure(boardIDs[i],fill=boardcolor)
        
    if gameState==GAMESTATE_ANAGRAM:
        tkCanvas.itemconfigure(boxID,state='normal') 
        tkCanvas.abs_move(boxID,lettersXPos+modifyLetter*letterwidth, lettersYPos+letterFontSize*1.7)
    else:
        tkCanvas.itemconfigure(boxID,state='hidden') 
    

def updatePinballs():
    for i in range (maxLives):
        if (i<lives):
            tkCanvas.itemconfigure(pinballIDs[i],state='normal')        
        else:
            tkCanvas.itemconfigure(pinballIDs[i],state='hidden')

def newGameRound():
    global actword, goalWord, gameState
    goalWord=lines[randrange(len(lines))]
    print ("GOAL="+goalWord)
    actword=""
    renewTargets()
    tkCanvas.itemconfigure(clockID,state='hidden')      
    tkCanvas.itemconfigure(coinID,state='hidden')
    gameState=GAMESTATE_FLIPPER
    updateLetters(actword)
    sendCommand(CMD_TRIGGER_BALL)
    sendCommand(GAMESTATE_FLIPPER);

def renewTargets():
    global actTargets
    samp=random.sample(range(5), 5)
    for i in range (maxTargets):
        #actTargets[i]=random.choice(string.ascii_uppercase)
        actTargets[i]=goalWord[samp[i]]
    printTargetsLCD()

        
def animCoin():
    global coinAnim
    coinAnim=coinAnim+1
    if coinAnim % 200 == 0:
        tkCanvas.itemconfigure(coinID,state='hidden')      
        coinAnim=0
    if coinAnim % 200 == 50:
        tkCanvas.itemconfigure(coinID,state='normal')      

def animLettersWon():
    global winAnim
    if winAnim % 10 == 0:
        for i in range (len(actword)):
            tkCanvas.itemconfigure(letterIDs[i],fill="white")        
    if winAnim % 10 == 5:
        for i in range (len(actword)):
            tkCanvas.itemconfigure(letterIDs[i],fill="black")        

def animLettersLost():
    global looseAnim
    if looseAnim % 25 == 0:
        for i in range (len(actword)):
            tkCanvas.itemconfigure(letterIDs[i],fill="yellow")        
    if looseAnim % 25 == 11:
        for i in range (len(actword)):
            tkCanvas.itemconfigure(letterIDs[i],fill="red")        


def ballLost():
    global lives, gameState
    lives=lives-1
    print ("BALL LOST! Lives left: " + str(lives))
    if (lives>=0):
        playSound("t5")
        pygame.time.delay(1000)
        sendCommand(CMD_TRIGGER_BALL)

    else:
        playSound("t5")
        pygame.time.delay(1000)
        playSound("t3")
        updateLetters("*****")
        sendCommand(CMD_LCD_GOIDLE);
        sendCommand(GAMESTATE_IDLE);
        gameState=GAMESTATE_IDLE
        tkCanvas.itemconfigure(clockID,state='hidden')      
        tkCanvas.itemconfigure(coinID,state='normal')

    updatePinballs()


''' 
   periodic game loop (~100Hz)
'''

def processGameEvents():
    global winAnim, looseAnim, clockAnim, lives, keyPressed, points, gameState, ballLostBypass
    
    userInput=""
    if (serialPortOpen==1) and (ser.inWaiting() > 0):
        userInput = ser.read(ser.inWaiting()).decode('ascii') 
        #print("Serial incoming:" + userInput) #, end='')
    else:
        if (keyPressed != ""):
            userInput=keyPressed
            print ("press detected")
            keyPressed=""
        
    if userInput != "":
        try:
            inputNumber=int(userInput)
            if (inputNumber==0) and (gameState==GAMESTATE_IDLE):
                playSound("n3")
                lives=3
                points=0
                updatePoints(0)
                print ("GAME STARTED !! Lives left: " + str(lives))
                newGameRound()
                lives=3
                updatePinballs()

            if (gameState==GAMESTATE_ANAGRAM):
                
                if (inputNumber==2):
                    switchLetterRight()
                    playSound("move")

                if (inputNumber==3):
                    changeLetter()
                    playSound("trommel")

                if (inputNumber==4):
                    switchLetterLeft()
                    playSound("move")

                if (actword in lines):
                    print (" *******  WORD FOUND !! ***********")
                    clockAnim=0
                    tkCanvas.itemconfigure(clockID,extent=0)
                    tkCanvas.itemconfigure(clockID,state='hidden')      
                    updatePoints(1000);
                    playSound("w4")
                    gameState=GAMESTATE_WON
                    winAnim=100      # start winning animation, see processGameEvents()


            if (gameState==GAMESTATE_FLIPPER):

                if (inputNumber==1) and (ballLostBypass==0):
                    ballLostBypass=200
                    ballLost()

                if inputNumber>=5 and inputNumber<5+maxTargets:
                    addLetter(inputNumber-5)
                    updatePoints(10);
                    if (len(actword) == maxLetters):
                        gameState=GAMESTATE_ANAGRAM
                        sendCommand(GAMESTATE_ANAGRAM);
                        playSound("gong")
                        updateLetters(actword)
                        tkCanvas.itemconfigure(clockID,state='normal')      
                        tkCanvas.abs_move(clockID,pinballXPos+(lives-1)*pinballWidth-5, int(pinballYPos-clockSize/2)-5)
                        clockAnim=3600
                        
                    
        except ValueError as e:
            print ("string detected")
            inputString=str(userInput)
            if (inputString=='s'):
                print ("start signal received")
                updatePoints(0)


    if clockAnim>0:
        clockAnim=clockAnim-1
        tkCanvas.itemconfigure(clockID,extent=360-int(clockAnim/10))
        if (clockAnim==0):
            playSound("n2")
            gameState=GAMESTATE_LOST
            updateLetters(goalWord)
            looseAnim=200           

    if ballLostBypass>0:
        ballLostBypass=ballLostBypass-1

    if (gameState==GAMESTATE_IDLE):
        animCoin()

    if (gameState==GAMESTATE_LOST):
        animLettersLost()
        looseAnim=looseAnim-1
        if looseAnim==0:
            ballLost()
            for i in range (len(actword)):
                tkCanvas.itemconfigure(letterIDs[i],fill=textcolor)        
            if (lives>0):
                newGameRound()
                # tkCanvas.itemconfigure(clockID,extent=0)

    if (gameState==GAMESTATE_WON):
        animLettersWon()
        winAnim=winAnim-1
        if winAnim==0:
            for i in range (len(actword)):
                tkCanvas.itemconfigure(letterIDs[i],fill=textcolor)        
            newGameRound()




    tkCanvas.after(10, processGameEvents)



''' 
   Main Program starts here!
'''

root = tk.Tk()
root.configure(bg=backgroundcolor)
#root.wm_geometry("1920x1080")
tk.Canvas.abs_move = abs_move
frame = Frame(root)
frame.pack()
tkCanvas = tk.Canvas(root,highlightthickness=0)
tkCanvas.pack(fill="both", expand=True)
tkCanvas.configure(bg=backgroundcolor)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
print ("Screen size = "+str (screen_width) + "/" + str (screen_height)) 

letterFontSize=int(screen_height/5)
#pointFontSize=int(screen_height/20)
pointFontSize=int(screen_height/12)

lettersXPos=int(screen_width/4)
lettersYPos=int(screen_height/3*1.7)
root.attributes("-fullscreen", screenstate)
    
tkFont.families()    
letterfont = tkFont.Font(family="Noto Mono", size = letterFontSize)
pointfont = tkFont.Font(family="Noto Mono", size = pointFontSize)

#pointfont = Font(file=getPath("../fonts/segment.ttf"), family="segment", size=pointFontSize)

letterwidth = letterfont.measure("0")+20
pinballImg=ImageTk.PhotoImage(file=getPath("../img/pinball1.png"))
coinImg=ImageTk.PhotoImage(file=getPath("../img/coin.jpg"))

pygame.mixer.init()
playSound("w5")

root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", end_fullscreen)
root.bind("<KeyPress>", keydown)
root.bind("<KeyRelease>", keyup)

text_file = open(getPath("worte.txt"), "r")
lines = text_file.readlines()
text_file.close()
lines[:] = [x.upper().rstrip("\n") for x in lines if x.strip()]
print ("Loaded "+str(len(lines)) + " Words.")
# print (lines)

if (runningOnRaspi==1):
    print("Running on Raspi! - Init LCD!")
    #initLCD()

if (runningOnRaspi==1):
    portName=raspiPortName  
else:
    portName=otherPortName

serialPortOpen=0
try:
    ser = serial.Serial(port=portName, baudrate=115200)
    serialPortOpen=1

except serial.SerialException as e:
    print("Could not init Serial Port - please connect Arduino / check port settings!")

goalWord=lines[randrange(len(lines))]
createScene()
updateLetters("*****")
updatePinballs()

processGameEvents()
root.mainloop()


# root.configure(bg='blue')
# tkCanvas.move(myrect,1,0)
# tkCanvas.delete("all")


