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


screenstate = False
textcolor="yellow"
boxcolor="red"
backgroundcolor="black"
maxLetters=5
maxTargets=4

points=0
winAnim=0

ser = serial.Serial(port="/dev/ttyUSB0", baudrate=115200)
letterIDs = array.array('i',(0 for i in range(0,maxLetters))) 
boxID = 0
letterwidth=0
modifyLetter=0   
actTargets = array.array('u',('x' for i in range(0,maxTargets))) 


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

def playSound(s):
    #sound = pygame.mixer.Sound('../sounds/kling' + data_str +'.wav')
    fn='../sounds/' + s +'.wav'
    sound = pygame.mixer.Sound(fn)
    playing = sound.play()    
    #while playing.get_busy():
    #    pygame.time.delay(10)


def changeLetter():
    global modifyLetter
    modifyLetter=modifyLetter+1
    if (modifyLetter>=len(actword)):
        modifyLetter=0
    print ("button1 - move to letter " + str(modifyLetter))
    updateLetters(actword)
    

def switchLetter():
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
    else:
        s=list(actword)
        tmp=actword[modifyLetter]
        actword=tmp+actword[:-1]
        modifyLetter=0

    print ("button2 - switch letters, actword = " + actword)
    updateLetters(actword)

def kickLetter():
    global modifyLetter, actword
    actword = actword[:modifyLetter] + actword[modifyLetter+1:]
    print ("button3 - kick letter, actword = " + actword)
    updateLetters(actword)
    

def addLetter(pos):
    global actword
    if len(actword)<maxLetters:
        actword=actword+actTargets[pos]
        updateLetters(actword)
        playSound('f'+str(pos+1))
    else:
        playSound('t1')

def button1_pressed(self, event=None):
    changeLetter()
    

def button2_pressed(self, event=None):
    switchLetter()    

def updatePoints(p):
    global points
    points=points+p
    ser.write(str(points).zfill(8)[::-1].encode())

   

def createScene():
    global letterIDs, boxID 
    for i in range (maxLetters):
        letterIDs[i] = canvas.create_text(xpos+10+letterwidth*i, ypos, text=" ", anchor="nw", font=letterfont, fill=textcolor)
        x0, y0, x1, y1 = canvas.bbox(letterIDs[i])
        b=canvas.create_rectangle(xpos+letterwidth*i, ypos, xpos+letterwidth*(i+1), y1, fill=boxcolor, outline="white")
        canvas.lift(letterIDs[i],b)
    boxID = canvas.create_rectangle(xpos, y1+10, xpos+letterwidth, y1+20, fill="white", outline="white")

def updateLetters(string):
    global winAnim
    for i in range (len(string)):
        canvas.itemconfigure(letterIDs[i],text=str(string[i]))        
    for i in range(len(string),maxLetters):
        canvas.itemconfigure(letterIDs[i],text=' ')
    canvas.abs_move(boxID,xpos+modifyLetter*letterwidth, ypos+fontsize*1.7)
    if (string in lines):
        print (" *******  WORD FOUND !! ***********")
        updatePoints(1000);
        playSound("w4")
        winAnim=100
        #actword=""
        #renewTargets()
        
def animLetters():
    global winAnim, actword
    if winAnim % 10 == 0:
        for i in range (len(actword)):
            canvas.itemconfigure(letterIDs[i],fill="white")        
    if winAnim % 10 == 5:
        for i in range (len(actword)):
            canvas.itemconfigure(letterIDs[i],fill="black")        
    winAnim=winAnim-1
    if winAnim==0:
        for i in range (len(actword)):
            canvas.itemconfigure(letterIDs[i],fill=textcolor)        
        actword=""
        renewTargets()
        updateLetters(actword)


def renewTargets():
    global actTargets
    for i in range (maxTargets):
        actTargets[i]=random.choice(string.ascii_uppercase)
    print ("Act Targets:" + str(actTargets))


root = tk.Tk()
tk.Canvas.abs_move = abs_move
frame = Frame(root)
frame.pack()
canvas = tk.Canvas(root)
canvas.pack(fill="both", expand=True)
canvas.configure(bg=backgroundcolor)

if screenstate == True:
    fontsize=300
    xpos=20
    ypos=200
    root.attributes('-zoomed', True)  # This just maximizes it so we can see the window. It's nothing to do with fullscreen.
    root.attributes("-fullscreen", screenstate)
else:
    fontsize=30
    xpos=20
    ypos=100
    
tkFont.families()    
letterfont = tkFont.Font(family="Noto Mono", size = fontsize)
#letterfont = tkFont.Font(family="Carlito", size = fontsize)
letterwidth = letterfont.measure("0")+20

pygame.mixer.init()
#playSound('start')

root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", end_fullscreen)
root.bind("<F1>", button1_pressed)
root.bind("<F2>", button2_pressed)

text_file = open("worte.txt", "r")
lines = text_file.readlines()
text_file.close()
lines[:] = [x.upper().rstrip("\n") for x in lines if x.strip()]
print ("Loaded "+str(len(lines)) + " Words.")
# print (lines)


createScene()
#actword=lines[randrange(len(lines))]
#print (actword)
actword="OPATI"

renewTargets()
updateLetters(actword)



def processGameEvents():
    global actword
    if (ser.inWaiting() > 0):
        data_str = ser.read(ser.inWaiting()).decode('ascii') 
        print("Serial incoming:" + data_str) #, end='')
        i=int(data_str)
        if (i==1):
            changeLetter()
            playSound("m1")

        if (i==2):
            switchLetter()
            playSound("m2")

        if (i==3):
            kickLetter()
            playSound("t2")

        if i>=4 and i<=7:
            addLetter(i-4)
            updatePoints(10);
            
        if (i==8):
            playSound("w1")
            renewTargets()
    if winAnim>0:
        animLetters()

    canvas.after(10, processGameEvents)

processGameEvents()
root.mainloop()



# root.geometry("400x300")
# root.configure(bg='blue')
# canvas.move(myrect,1,0)
# canvas.delete("all")
