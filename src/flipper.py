import tkinter as tk
import tkinter.font as tkFont
from tkinter import *

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
import sys

if (os.name == 'posix'):
    runningOnRaspi=1
else:
    runningOnRaspi=0


raspiPortName="/dev/ttyACM"
otherPortName="COM17"

scrollText = "         ABC-Flipper!!         Triff die Buchstaben und baue Worte!      Bitte Zoomi einwerfen ...      "

scrollSpeed= 25
BALLOST_BYPASS_TIME= 300
MIN_FLOPSOUND= 1
MAX_FLOPSOUND= 8

MAX_IDLE_TIME=2000

CMD_LCD_ROTATE='7'
CMD_LCD_GOIDLE='8'

GAMESTATE_IDLE =   'a'
GAMESTATE_FLIPPER ='b'
GAMESTATE_ANAGRAM = 'c'
GAMESTATE_WON = 'd'
GAMESTATE_LOST = 'e'
GAMESTATE_HIGHSCORE = 'x'

CMD_TRIGGER_BALL='f'
CMD_TRIGGER_BELL='g'
CMD_RANDOM_LIGHT = 'h'
CMD_BUMPER_LIGHT = 'i'
CMD_TOP_LIGHT = 'j'


screenstate = True
textcolor="yellow"
boardcolor="gray"
activeboardcolor="red"
backgroundcolor="black"
pointscolor="#FF2020"
#scrollBackgroundcolor="#600040"
#scrollBackgroundcolor="#d01010"
scrollBackgroundcolor="#0000a0"


scrollLettercolor="#c0c0ff"
scrollBrightness=50

maxLetters=5
maxTargets=5
maxLives=3
lives=0
gameState=GAMESTATE_IDLE
points=0
highScore=200
highName="DAVID"
highScoreAnim=0
winAnim=0
looseAnim=0
clockAnim=0
idleAnimCount=0
idleAnimPhase=1
scrollPos=0
autoSolve=1
lockAutoSove=0
ejectTimeout=0
ballLostBypass=0

pinballXPos=80
pinballYPos=80
pinballWidth=110

clockXPos=28
clockYPos=25
clockSize=105

letterIDs = array.array('i',(0 for i in range(0,maxLetters))) 
boardIDs = array.array('i',(0 for i in range(0,maxLetters))) 
pinballIDs = array.array('i',(0 for i in range(0,maxLives))) 
nameID = 0
brainID = 0
pointsID=0
clockID = 0
coinID=0

letterwidth=0
modifyLetter=0   
actTargets = array.array('u',('x' for i in range(0,maxTargets))) 
letterOrder=random.sample(range(5), 5)

keyPressed=""



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

  
def upLetter():
    global modifyLetter, actword
    s=list(actword)
    if ord(s[modifyLetter]) < ord('Z'):
        if s[modifyLetter]==' ':
            s[modifyLetter]='A'
        else:
            s[modifyLetter]=chr(ord(s[modifyLetter])+1)
    else:
        s[modifyLetter]=' '
    actword="".join(s)
    updateLetters(actword)

def downLetter():
    global modifyLetter, actword
    s=list(actword)
    if ord(s[modifyLetter]) > ord('A'):
        s[modifyLetter]=chr(ord(s[modifyLetter])-1)
    else:
        if s[modifyLetter]==' ':  
            s[modifyLetter]='Z'
        else:
            s[modifyLetter]=' '
    actword="".join(s)
    updateLetters(actword)

def addLetter(pos):
    global actword
    
    sendLCDLetter(pos+1,actTargets[pos])
    if (actTargets[pos] != ' '):
        if autoSolve==0:
            if len(actword)<maxLetters:
                actword=actword+actTargets[pos]
        else:
            s=list(actword)
            s[letterOrder[pos]]=goalWord[letterOrder[pos]]
            actword="".join(s)
            
        updateLetters(actword)
        playSound('f'+str(pos+1))
        actTargets[pos]=' '
        #printTargetsLCD()
        sendLCDLetter(pos+1,actTargets[pos])
    else:
        playSound('x'+str(random.randint(MIN_FLOPSOUND,MAX_FLOPSOUND)))
        

def keydown(e):
    global keyPressed
    # print ('keyDown', e.char)
    keyPressed = str(e.char)

#def keyup(e):
    #print ('keyUp', e.char)
    

'''
     Morse Code decoding
'''

def morse_code_translator(letter):
    morse_code_dict = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
        '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
        '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
        '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
        '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
        '--..': 'Z'
    }

    if letter in morse_code_dict:
        return(morse_code_dict[letter])

    return ''

spaceDuration = 0
morseDuration = 0
morseCodeActive = 0
morseCode = ""
morseText = ""
fn=getPath("/home/pi/ABC-Flipper/sounds/gong.wav") 


def processMorseCode(morseKeyActivity):
    global morseText, morseCode, morseDuration, spaceDuration, morseCodeActive, channel1
    morseSymbol=""
    
    if morseKeyActivity == "+":
        morseSound.play()
        morseCodeActive=1
        morseDuration = 0
        return 0

    if morseKeyActivity == "-":
        if morseDuration < 20:
            pygame.time.delay(50)

        morseSound.stop()
        morseCodeActive=0
        spaceDuration=0
        if morseDuration >= 50:  # long press
            morseSymbol = '-'
        else:  # short press
            morseSymbol = '.'        
        print (morseSymbol, end="", flush=True)
        morseCode+=morseSymbol
        return 0
        
    
    if (morseCodeActive==1):
        morseDuration+=1
    else:
        spaceDuration+=1
    
        if (spaceDuration > 150) and (morseCode != ""):
            playSound("x9")
            translatedCode = morse_code_translator(morseCode)
            print(f" {translatedCode}  ", end="", flush=True)
            morseText += translatedCode
            morseCode = ""
            if len(morseText)>0 and len(morseText)<6:
                sendLCDLetter(len(morseText),translatedCode)
            if len(morseText) >= 5:
                print ("got word: "+morseText)
                if morseText == "ZOOMI":
                    return(1)
                if morseText == "BRAIN":
                    return(2)
                morseText=""
        if (spaceDuration == 700) and (morseText != ""):
            print (" ... Clear!")
            for i in range (maxTargets):
                sendLCDLetter(i+1," ")
            playSound("x7")
            morseText=""
            
    return 0

    
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
    tkCanvas.itemconfigure(pointsID,text=str(points).zfill(7))   

def createScene():
    global letterIDs, nameID, pinballID, pointsID, clockID, coinID, brainID
    for i in range (maxLetters):
        letterIDs[i] = tkCanvas.create_text(lettersXPos+10+letterwidth*i, lettersYPos, text=" ", anchor="nw", font=letterfont, fill=textcolor)
        x0, y0, x1, y1 = tkCanvas.bbox(letterIDs[i])
        boardIDs[i]=tkCanvas.create_rectangle(lettersXPos+letterwidth*i, lettersYPos, lettersXPos+letterwidth*(i+1), y1, fill=boardcolor, outline="white")
        tkCanvas.lift(letterIDs[i],boardIDs[i])
    #boxID = tkCanvas.create_rectangle(lettersXPos, y1+10, lettersXPos+letterwidth, y1+20, fill="white", outline="white")
    for i in range (maxLives):
        pinballIDs[i]=tkCanvas.create_image(pinballXPos+i*pinballWidth, pinballYPos, image=pinballImg, anchor="center")

    brainID =tkCanvas.create_image(pinballXPos+100, pinballYPos, image=brainImg, anchor="center")
    pointsID=tkCanvas.create_text(int(screen_width/3*2), 40, text="0000000", anchor="nw", font=pointfont, fill=pointscolor)
    clockID =tkCanvas.create_arc(0,clockYPos, clockSize, clockYPos+clockSize, start=90, extent=0, fill="#000000")
    nameID =tkCanvas.create_image(0, 5, image=nameImg, anchor="nw")
    coinID =tkCanvas.create_image(pinballXPos+100, pinballYPos, image=coinImg, anchor="center")

def updateLetters(string):
    global winAnim, clockAnim, idleAnimPhase
    for i in range (len(string)):
        tkCanvas.itemconfigure(letterIDs[i],text=str(string[i]))        
    for i in range(len(string),maxLetters):
        tkCanvas.itemconfigure(letterIDs[i],text=' ')
    for i in range(maxLetters):
        if (gameState==GAMESTATE_IDLE):
            if (idleAnimPhase==0):  
                tkCanvas.itemconfigure(boardIDs[i],fill=scrollBackgroundcolor)
            else:
                tkCanvas.itemconfigure(boardIDs[i],fill=_from_rgb((220, 220, 220)))
            # tkCanvas.itemconfigure(letterIDs[i],fill=scrollLettercolor)
        else:
            tkCanvas.itemconfigure(letterIDs[i],fill='yellow')
            tkCanvas.itemconfigure(boardIDs[i],fill=boardcolor)
            
        if (i==modifyLetter):
            if (gameState==GAMESTATE_ANAGRAM):
                tkCanvas.itemconfigure(boardIDs[i],fill=activeboardcolor)        
            if (gameState==GAMESTATE_HIGHSCORE):
                tkCanvas.itemconfigure(boardIDs[i],fill="green")
    

def updatePinballs():
    for i in range (maxLives):
        if (i<lives):
            tkCanvas.itemconfigure(pinballIDs[i],state='normal')        
        else:
            tkCanvas.itemconfigure(pinballIDs[i],state='hidden')

def newGameRound():
    global actword, goalWord, gameState, ballLostBypass, ejectTimeout, morseText
    morseText=""
    goalWord=lines[randrange(len(lines))]
    goalWord=goalWord[:5]
    print ("GOAL="+goalWord)
    if autoSolve==0:        
        actword=""
    else:
        actword="     "
    ballLostBypass=BALLOST_BYPASS_TIME
    renewTargets()
    tkCanvas.itemconfigure(clockID,state='hidden')      
    tkCanvas.itemconfigure(coinID,state='hidden')
    tkCanvas.itemconfigure(brainID,state='hidden')
    gameState=GAMESTATE_FLIPPER
    ejectTimeout=MAX_IDLE_TIME
    updateLetters(actword)
    sendCommand(CMD_TRIGGER_BALL)
    sendCommand(GAMESTATE_FLIPPER);


def startGame():
    global lives, points
    playSound("n3")
    lives=3
    points=0
    updatePoints(0)
    newGameRound()
    updatePinballs()
    print ("GAME STARTED !! Lives left: " + str(lives))
 

def renewTargets():
    global actTargets,letterOrder
    letterOrder=random.sample(range(5), 5)
    for i in range (maxTargets):
        actTargets[i]=goalWord[letterOrder[i]]
    printTargetsLCD()

def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb   


def idleAnim():
    global idleAnimCount, scrollPos, scrollBrightness, highScoreAnim, idleAnimPhase
    idleAnimCount=idleAnimCount+1
    if idleAnimCount % 200 == 0:
        tkCanvas.itemconfigure(coinID,state='hidden')
        if autoSolve==0:
            tkCanvas.itemconfigure(brainID,state='normal')
        else:
            tkCanvas.itemconfigure(brainID,state='hidden')
        idleAnimCount=0
    if idleAnimCount % 200 == 50:
        tkCanvas.itemconfigure(coinID,state='normal')
        
    if idleAnimCount % scrollSpeed == 0:
        scrollPos=scrollPos+1
        if (idleAnimPhase==0):
            scrollDisplay=scrollText[scrollPos:scrollPos+5]
            for i in range(maxLetters):
                tkCanvas.itemconfigure(letterIDs[i],fill=_from_rgb((255, 255, 255)))
            if (scrollPos>len(scrollText)-5):
                scrollPos=0
                idleAnimPhase=1
 
        if (idleAnimPhase==1):
            scrollDisplay="HIGH "
            for i in range(maxLetters):
                tkCanvas.itemconfigure(letterIDs[i],fill=_from_rgb((255, 20, 20))) 
            if (scrollPos==4):
                scrollPos=0
                idleAnimPhase=2
 
        if (idleAnimPhase==2):
            scrollDisplay="SCORE"
            for i in range(maxLetters):
                tkCanvas.itemconfigure(letterIDs[i],fill=_from_rgb((255, 20, 20)))
            if (scrollPos==4):
                scrollPos=0
                idleAnimPhase=3

        if (idleAnimPhase==3):
            scrollDisplay=highName
            for i in range(maxLetters):
                if scrollPos%3 == 0:
                    tkCanvas.itemconfigure(letterIDs[i],fill=_from_rgb((20, 20, 100)))
                else:
                    tkCanvas.itemconfigure(letterIDs[i],fill=_from_rgb((255, 20, 20)))
            if (scrollPos==12):
                scrollPos=0
                idleAnimPhase=4

        if (idleAnimPhase==4):
            scrollDisplay=(str(highScore).zfill(5))[:5]
            for i in range(maxLetters):
                if scrollPos%3 == 0:
                    tkCanvas.itemconfigure(letterIDs[i],fill=_from_rgb((255, 20, 20)))
                else:
                    tkCanvas.itemconfigure(letterIDs[i],fill=_from_rgb((20, 20, 100)))
            if (scrollPos==12):
                scrollDisplay="     "
                scrollPos=0
                idleAnimPhase=0

        updateLetters(scrollDisplay)
            
        

def highAnim():
    if (highScoreAnim%50==0):
        tkCanvas.itemconfigure(pointsID,fill="white")        
    if (highScoreAnim%70==0):
        tkCanvas.itemconfigure(pointsID,fill=pointscolor)
    if (highScoreAnim%20==0):
        if (highScoreAnim>400):
            tkCanvas.abs_move(nameID,0, 5)
        else:
            tkCanvas.abs_move(nameID,0, int(highScoreAnim/2-200))        

def animLettersWon():
    if winAnim % 10 == 0:
        for i in range (len(actword)):
            tkCanvas.itemconfigure(letterIDs[i],fill="white")        
    if winAnim % 10 == 5:
        for i in range (len(actword)):
            tkCanvas.itemconfigure(letterIDs[i],fill="black")        

def animLettersLost():
    if looseAnim % 25 == 0:
        for i in range (len(actword)):
            tkCanvas.itemconfigure(letterIDs[i],fill="white")        
    if looseAnim % 25 == 11:
        for i in range (len(actword)):
            tkCanvas.itemconfigure(letterIDs[i],fill="blue")        


def ballLost():
    global lives, gameState, ballLostBypass, actword, modifyLetter, winAnim
    global highScore, highScoreAnim, scrollText, scrollPos, idleAnimPhase

    if ballLostBypass>0:
        return        
        
    ballLostBypass=BALLOST_BYPASS_TIME
    lives=lives-1
    print ("BALL LOST! Lives left: " + str(lives))
    playSound("t5")
    pygame.time.delay(1000)
    if (lives>0):
        sendCommand(CMD_TRIGGER_BALL)

    else:
        playSound("t3")
        if (points<=highScore):
            if (autoSolve==1):
                actword=goalWord
                updateLetters(goalWord)
                gameState=GAMESTATE_WON
                updateLetters(goalWord)
                winAnim=200           
            else:
                updateLetters("     ")
                gameState=GAMESTATE_IDLE

        else:
            playSound("applause")
            highScore=points
            highScoreAnim=800
            gameState=GAMESTATE_HIGHSCORE
            modifyLetter=0
            actword="A    "
            updateLetters(actword)
            tkCanvas.itemconfigure(nameID,state='normal')

        scrollPos=0
        idleAnimPhase=0
        sendCommand(CMD_LCD_GOIDLE);
        sendCommand(GAMESTATE_IDLE);
        tkCanvas.itemconfigure(clockID,state='hidden')      
        #tkCanvas.itemconfigure(coinID,state='hidden')

    updatePinballs()

def enterWonPhase():
    global gameState, winAnim
    updatePoints(1000)
    playSound("w4")
    gameState=GAMESTATE_WON
    sendCommand(GAMESTATE_WON)
    winAnim=200

def enterAnagramPhase():
    global gameState, clockAnim

    if autoSolve==0:
        gameState=GAMESTATE_ANAGRAM
        sendCommand(GAMESTATE_ANAGRAM)
        tkCanvas.itemconfigure(clockID,state='normal')
        tkCanvas.itemconfigure(clockID,extent=359)                    
        tkCanvas.abs_move(clockID,clockXPos+(lives-1)*pinballWidth-5, clockYPos)
        clockAnim=3600
        updateLetters(actword)
    else:
        enterWonPhase()



''' 
   periodic game loop (~100Hz)
'''

def processGameEvents():
    global winAnim, looseAnim, clockAnim, lives, keyPressed, autoSolve, lockAutoSove, ejectTimeout
    global points, highScore, highScoreAnim, highName, gameState, ballLostBypass,actword
    
    userInput=""
    try:
        if (serialPortOpen==1) and (ser.inWaiting() > 0):
            userInput = ser.read(ser.inWaiting()).decode('ascii') 
            #print("Serial incoming:" + userInput) #, end='')
        else:
            if (keyPressed != ""):
                userInput=keyPressed
                #print ("press detected")
                keyPressed=""
    except:
        print ("Serial error - exiting!")
        sys.exit()
            
    if userInput != "":
        try:
            inputNumber=int(userInput)
            if (gameState==GAMESTATE_IDLE):
                if (inputNumber==0):
                    startGame()
                if (inputNumber==3):
                    processMorseCode("+")
                    

            if (gameState==GAMESTATE_ANAGRAM):
                
                if (inputNumber==2):
                    switchLetterRight()
                    clockAnim=3600
                    playSound("move")

                if (inputNumber==3):
                    clockAnim=3600
                    changeLetter()
                    playSound("trommel")

                if (inputNumber==4):
                    clockAnim=3600
                    switchLetterLeft()
                    playSound("move")

                if (actword in lines):
                    print (" *******  WORD FOUND !! ***********")
                    clockAnim=0
                    tkCanvas.itemconfigure(clockID,extent=0)
                    tkCanvas.itemconfigure(clockID,state='hidden')
                    enterWonPhase()

            if (gameState==GAMESTATE_FLIPPER):

                if inputNumber==1:
                    if (ballLostBypass>0):
                        sendCommand(CMD_TRIGGER_BALL)  # retrigger ball release!
                    else:
                        ballLost()
                    ejectTimeout=MAX_IDLE_TIME

                if inputNumber>=5 and inputNumber<5+maxTargets:
                    addLetter(inputNumber-5)
                    updatePoints(random.randrange(10,20))
                    if (len(actword.replace(" ", "")) == maxLetters):
                        if autoSolve==0:
                            playSound("gong")
                        enterAnagramPhase()
                    else:
                        sendCommand(CMD_RANDOM_LIGHT)
                        sendCommand(CMD_TOP_LIGHT);
                        ejectTimeout=MAX_IDLE_TIME

            if (gameState==GAMESTATE_HIGHSCORE):
                if (inputNumber==2):
                    upLetter()
                    playSound("move")
                    highScoreAnim=800

                if (inputNumber==3):
                    changeLetter()
                    playSound("trommel")
                    highScoreAnim=800

                if (inputNumber==4):
                    downLetter()
                    playSound("move")                     
                    highScoreAnim=800
                    
        except ValueError as e:
            inputString=str(userInput)
            if (inputString=='=') and (lockAutoSove==0):
                autoSolve=1
                print ("autosolve enabled")
            if (inputString=='>') and (lockAutoSove==0):
                autoSolve=0
                print ("autosolve disabled")
            if (inputString=='s'):
                print ("start signal received")
                updatePoints(0)
            if (inputString=='.'):
                processMorseCode("-")


            if (gameState==GAMESTATE_FLIPPER):
                if (inputString==':'):
                    print ("joker hit!")
                    updatePoints(200) 
                    playSound('joker')
                    if autoSolve==1:
                        actword=goalWord
                        updateLetters(actword)
                    for i in range (maxLetters):
                        if (actTargets[i] != ' '):
                            if autoSolve==0:
                                actword=actword+actTargets[i]
                            actTargets[i]=' '
                    printTargetsLCD()
                    enterAnagramPhase()
                    
                if (inputString==';') or (inputString=='<'):
                    updatePoints(random.randrange(10,20))
                    playSound('x'+str(random.randint(MIN_FLOPSOUND,MAX_FLOPSOUND)))
                    ejectTimeout=MAX_IDLE_TIME

                    
    if clockAnim>0:
        if (clockAnim%200 == 0):
            tkCanvas.itemconfigure(clockID,extent=360-int(clockAnim/10))
        if (clockAnim%200 == 120):
            tkCanvas.itemconfigure(clockID,extent=359)
        clockAnim=clockAnim-2
            
        if (clockAnim<=0):
            playSound("n2")
            gameState=GAMESTATE_LOST
            updateLetters(goalWord)
            looseAnim=200           

    if ballLostBypass>0:
        ballLostBypass=ballLostBypass-1

    if (gameState==GAMESTATE_IDLE):
        idleAnim()
        morse=processMorseCode(" ")
        if (morse==1):
            startGame()            
        if (morse==2):
            playSound("bells")
            lockAutoSove=1
            if autoSolve==1:
                autoSolve=0
            else:
                autoSolve=1
        
    if (gameState==GAMESTATE_HIGHSCORE):
        highAnim()
        highScoreAnim=highScoreAnim-1
        if highScoreAnim==0:
            highName=actword
            gameState=GAMESTATE_IDLE
            tkCanvas.itemconfigure(nameID,state='hidden')
            tkCanvas.itemconfigure(pointsID,fill=pointscolor)

    if (gameState==GAMESTATE_LOST):
        animLettersLost()
        looseAnim=looseAnim-1
        if looseAnim<=0:
            ballLost()
            for i in range (len(actword)):
                tkCanvas.itemconfigure(letterIDs[i],fill=textcolor)        
            if (lives>0):
                newGameRound()

    if (gameState==GAMESTATE_WON):
        animLettersWon()
        winAnim=winAnim-1
        if winAnim<=0:
            for i in range (len(actword)):
                tkCanvas.itemconfigure(letterIDs[i],fill=textcolor)        
            if (lives>0):
                newGameRound()
            else:
                gameState=GAMESTATE_IDLE

    
    if (gameState==GAMESTATE_FLIPPER):
        ejectTimeout=ejectTimeout-1
        if (ejectTimeout <= 0):
            ejectTimeout=MAX_IDLE_TIME
            ballLostBypass=BALLOST_BYPASS_TIME
            print ("TRYING TO EJECT LOST BALL!")
            sendCommand(CMD_TRIGGER_BALL)

    tkCanvas.after(10, processGameEvents)  # next game loop iteration in 10 milliseconds



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

#letterFontSize=int(screen_height/8)
letterFontSize=int(screen_height/5)
pointFontSize=int(screen_height/20)

lettersXPos=int(screen_width/4)
lettersYPos=int(screen_height/3*2.0)
root.attributes("-fullscreen", screenstate)
    
tkFont.families()    
#letterfont = tkFont.Font(family="Noto Sans Mono", size = letterFontSize)
letterfont = tkFont.Font(family="Noto Mono", size = letterFontSize)

pointfont = tkFont.Font(family="segment", size = pointFontSize)

letterwidth = letterfont.measure("W")+20
pinballImg=ImageTk.PhotoImage(file=getPath("../img/pinball1.png"))
coinImg=ImageTk.PhotoImage(file=getPath("../img/coin.jpg"))
nameImg=ImageTk.PhotoImage(file=getPath("../img/name.jpg"))
brainImg=ImageTk.PhotoImage(file=getPath("../img/brain_small.png"))

pygame.mixer.init()
playSound("w5")
morseSound = pygame.mixer.Sound("../sounds/morse.wav")

root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", end_fullscreen)
root.bind("<KeyPress>", keydown)
#root.bind("<KeyRelease>", keyup)

text_file = open(getPath("worte.txt"), "r")
lines = text_file.readlines()
text_file.close()
lines[:] = [x.upper().rstrip("\n") for x in lines if x.strip()]
print ("Loaded "+str(len(lines)) + " Words.")
# print (lines)

serialPortOpen=0
serialNum=0

while (serialNum<10) and (serialPortOpen==0):
    if (runningOnRaspi==1):
        portName=raspiPortName+str(serialNum)
    else:
        portName=otherPortName

    try:
        ser = serial.Serial(port=portName, baudrate=115200)
        serialPortOpen=1

    except serial.SerialException as e:
        print("Could not init Serial Port "+ str(serialNum) + "- please connect Arduino / check port settings!")
        serialNum=serialNum+1

goalWord=lines[randrange(len(lines))]
createScene()
updateLetters("     ")
updatePinballs()
tkCanvas.itemconfigure(nameID,state='hidden')
tkCanvas.itemconfigure(coinID,state='hidden')
tkCanvas.itemconfigure(brainID,state='hidden')
 
sendCommand(GAMESTATE_IDLE);
processGameEvents()
root.mainloop()


