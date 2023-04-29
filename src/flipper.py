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
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7735
from PIL import ImageFont, Image, ImageTk



lcdInterface = spi(devcie=0, port=0)

#device = ssd1306(lcdInterface)
device = st7735(lcdInterface)

def make_font(name, size):
    font_path = str(Path(__file__).resolve().parent.joinpath('fonts', name))
    return ImageFont.truetype(font_path, size)

#font = make_font("fontawesome-webfont.ttf", device.height - 10)
font = make_font("code2000.ttf", device.height - 10)
  
screenstate = True
textcolor="yellow"
boardcolor="gray"
activeboardcolor="red"
backgroundcolor="black"
maxLetters=5
maxTargets=5
maxLives=3
lives=0
points=0
winAnim=0

ser = serial.Serial(port="/dev/ttyUSB0", baudrate=115200)
letterIDs = array.array('i',(0 for i in range(0,maxLetters))) 
boardIDs = array.array('i',(0 for i in range(0,maxLetters))) 
pinballIDs = array.array('i',(0 for i in range(0,maxLives))) 
boxID = 0
letterwidth=0
modifyLetter=0   
actTargets = array.array('u',('x' for i in range(0,maxTargets))) 


def displayLCD(pos,msg):
    #draw=canvas(device)
    if (pos==1):
        with canvas(device) as draw:
            # w, h = draw.textsize(text=msg, font=font)
            
            l, t, r, b = draw.textbbox((0,0),msg, font)
            w=r - l
            h=b
            
            
            left = (device.width - w) / 2
            top = (device.height - h) / 2 - 15
            draw.text((left, top), text=msg, font=font, fill="yellow")


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
    if (len(actword)<maxLetters) and (actTargets[pos] != ' '):
        actword=actword+actTargets[pos]
        updateLetters(actword)
        playSound('f'+str(pos+1))
        actTargets[pos]=' '
        printTargets()
        #displayLCD(pos,actTargets[pos])

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
    global letterIDs, boxID, pinballID
    for i in range (maxLetters):
        letterIDs[i] = tkCanvas.create_text(xpos+10+letterwidth*i, ypos, text=" ", anchor="nw", font=letterfont, fill=textcolor)
        x0, y0, x1, y1 = tkCanvas.bbox(letterIDs[i])
        boardIDs[i]=tkCanvas.create_rectangle(xpos+letterwidth*i, ypos, xpos+letterwidth*(i+1), y1, fill=boardcolor, outline="white")
        tkCanvas.lift(letterIDs[i],boardIDs[i])
    boxID = tkCanvas.create_rectangle(xpos, y1+10, xpos+letterwidth, y1+20, fill="white", outline="white")
    for i in range (maxLives):
        pinballIDs[i]=tkCanvas.create_image(50+i*100, 40, image=pinballImg, anchor="center")




def updateLetters(string):
    global winAnim
    for i in range (len(string)):
        tkCanvas.itemconfigure(letterIDs[i],text=str(string[i]))        
    for i in range(len(string),maxLetters):
        tkCanvas.itemconfigure(letterIDs[i],text=' ')
    for i in range(maxLetters):
        if i==modifyLetter:
            tkCanvas.itemconfigure(boardIDs[i],fill=activeboardcolor)
        else:
            tkCanvas.itemconfigure(boardIDs[i],fill=boardcolor)
        
    tkCanvas.abs_move(boxID,xpos+modifyLetter*letterwidth, ypos+fontsize*1.7)
    if (string in lines):
        print (" *******  WORD FOUND !! ***********")
        updatePoints(1000);
        playSound("w4")
        winAnim=100      # start winning animation, see processGameEvents()

def updatePinballs():
    for i in range (maxLives):
        if (i<lives):
            tkCanvas.itemconfigure(pinballIDs[i],state='normal')        
        else:
            tkCanvas.itemconfigure(pinballIDs[i],state='hidden')


def newGameRound():
    global actword, goalWord
    goalWord=lines[randrange(len(lines))]
    print ("GOAL="+goalWord)
    actword=""
    renewTargets()
    updateLetters(actword)
    lives=3

        
def animLetters():
    global winAnim, actword
    if winAnim % 10 == 0:
        for i in range (len(actword)):
            tkCanvas.itemconfigure(letterIDs[i],fill="white")        
    if winAnim % 10 == 5:
        for i in range (len(actword)):
            tkCanvas.itemconfigure(letterIDs[i],fill="black")        

def printTargets():
    print ("Act Targets:", end="")
    for i in range (maxTargets):
        print (str(actTargets[maxTargets-1-i]) , end="")
        displayLCD(i,actTargets[i])
    print (" ")
    # displayLCD(1,codes[randrange(len(codes))])


def renewTargets():
    global actTargets
    samp=random.sample(range(5), 5)
    for i in range (maxTargets):
        #actTargets[i]=random.choice(string.ascii_uppercase)
        actTargets[i]=goalWord[samp[i]]
    printTargets()

root = tk.Tk()
tk.Canvas.abs_move = abs_move
frame = Frame(root)
frame.pack()
tkCanvas = tk.Canvas(root)
tkCanvas.pack(fill="both", expand=True)
tkCanvas.configure(bg=backgroundcolor)

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
pinballImg=ImageTk.PhotoImage(file="../img/pinball2.png")

pygame.mixer.init()
playSound("w5")

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

goalWord=lines[randrange(len(lines))]
createScene()
newGameRound()
updateLetters("*****")
updatePinballs()


def processGameEvents():
    global winAnim, lives
    if (ser.inWaiting() > 0):
        data_str = ser.read(ser.inWaiting()).decode('ascii') 
        #print("Serial incoming:" + data_str) #, end='')
        try:
            i=int(data_str)
            #if (i==3):
            #    kickLetter()
            #    playSound("t2")
            if (i==0) and (lives==0):
                playSound("n3")
                lives=3
                print ("GAME STARTED !! Lives left: " + str(lives))
                newGameRound()
                updatePinballs()


            if (lives>0):
                
                if (i==1):
                    lives=lives-1
                    print ("BALL LOST! Lives left: " + str(lives))
                    if (lives>0):
                        playSound("t5")
                    else:
                        playSound("t3")
                        updateLetters("*****")
                    updatePinballs()


                if (i==2):
                    changeLetter()
                    playSound("m1")

                if (i==3):
                    switchLetter()
                    playSound("m2")

                if i>=4 and i<4+maxTargets:
                    addLetter(i-4)
                    updatePoints(10);
                    
                if (i==9):         # TBD
                    playSound("w1")
                    renewTargets()
                    
        except ValueError as e:
            s=str(data_str)
            if (s=='s'):
                print ("start signal received")
                updatePoints(0)


    if winAnim>0:
        animLetters()
        winAnim=winAnim-1
        if winAnim==0:
            for i in range (len(actword)):
                tkCanvas.itemconfigure(letterIDs[i],fill=textcolor)        
            newGameRound()

    tkCanvas.after(10, processGameEvents)

processGameEvents()
root.mainloop()



# root.geometry("400x300")
# root.configure(bg='blue')
# tkCanvas.move(myrect,1,0)
# tkCanvas.delete("all")


codes = [
    "\uf001", "\uf002", "\uf003", "\uf004", "\uf005", "\uf006", "\uf007",
    "\uf008", "\uf009", "\uf00a", "\uf00b", "\uf00c", "\uf00d", "\uf00e",
    "\uf010", "\uf011", "\uf012", "\uf013", "\uf014", "\uf015", "\uf016",
    "\uf017", "\uf018", "\uf019", "\uf01a", "\uf01b", "\uf01c", "\uf01d",
    "\uf01e", "\uf021", "\uf022", "\uf023", "\uf024", "\uf025", "\uf026",
    "\uf027", "\uf028", "\uf029", "\uf02a", "\uf02b", "\uf02c", "\uf02d",
    "\uf02e", "\uf02f", "\uf030", "\uf031", "\uf032", "\uf033", "\uf034",
    "\uf035", "\uf036", "\uf037", "\uf038", "\uf039", "\uf03a", "\uf03b",
    "\uf03c", "\uf03d", "\uf03e", "\uf040", "\uf041", "\uf042", "\uf043",
    "\uf044", "\uf045", "\uf046", "\uf047", "\uf048", "\uf049", "\uf04a",
    "\uf04b", "\uf04c", "\uf04d", "\uf04e", "\uf050", "\uf051", "\uf052",
    "\uf053", "\uf054", "\uf055", "\uf056", "\uf057", "\uf058", "\uf059",
    "\uf05a", "\uf05b", "\uf05c", "\uf05d", "\uf05e", "\uf060", "\uf061",
    "\uf062", "\uf063", "\uf064", "\uf065", "\uf066", "\uf067", "\uf068",
    "\uf069", "\uf06a", "\uf06b", "\uf06c", "\uf06d", "\uf06e", "\uf070",
    "\uf071", "\uf072", "\uf073", "\uf074", "\uf075", "\uf076", "\uf077",
    "\uf078", "\uf079", "\uf07a", "\uf07b", "\uf07c", "\uf07d", "\uf07e",
    "\uf080", "\uf081", "\uf082", "\uf083", "\uf084", "\uf085", "\uf086",
    "\uf087", "\uf088", "\uf089", "\uf08a", "\uf08b", "\uf08c", "\uf08d",
    "\uf08e", "\uf090", "\uf091", "\uf092", "\uf093", "\uf094", "\uf095",
    "\uf096", "\uf097", "\uf098", "\uf099", "\uf09a", "\uf09b", "\uf09c",
    "\uf09d", "\uf09e", "\uf0a0", "\uf0a1", "\uf0f3", "\uf0a3", "\uf0a4",
    "\uf0a5", "\uf0a6", "\uf0a7", "\uf0a8", "\uf0a9", "\uf0aa", "\uf0ab",
    "\uf0ac", "\uf0ad", "\uf0ae", "\uf0b0", "\uf0b1", "\uf0b2", "\uf0c0",
    "\uf0c1", "\uf0c2", "\uf0c3", "\uf0c4", "\uf0c5", "\uf0c6", "\uf0c7",
    "\uf0c8", "\uf0c9", "\uf0ca", "\uf0cb", "\uf0cc", "\uf0cd", "\uf0ce",
    "\uf0d0", "\uf0d1", "\uf0d2", "\uf0d3", "\uf0d4", "\uf0d5", "\uf0d6",
    "\uf0d7", "\uf0d8", "\uf0d9", "\uf0da", "\uf0db", "\uf0dc", "\uf0dd",
    "\uf0de", "\uf0e0", "\uf0e1", "\uf0e2", "\uf0e3", "\uf0e4", "\uf0e5",
    "\uf0e6", "\uf0e7", "\uf0e8", "\uf0e9", "\uf0ea", "\uf0eb", "\uf0ec",
    "\uf0ed", "\uf0ee", "\uf0f0", "\uf0f1", "\uf0f2", "\uf0a2", "\uf0f4",
    "\uf0f5", "\uf0f6", "\uf0f7", "\uf0f8", "\uf0f9", "\uf0fa", "\uf0fb",
    "\uf0fc", "\uf0fd", "\uf0fe", "\uf100", "\uf101", "\uf102", "\uf103",
    "\uf104", "\uf105", "\uf106", "\uf107", "\uf108", "\uf109", "\uf10a",
    "\uf10b", "\uf10c", "\uf10d", "\uf10e", "\uf110", "\uf111", "\uf112",
    "\uf113", "\uf114", "\uf115", "\uf118", "\uf119", "\uf11a", "\uf11b",
    "\uf11c", "\uf11d", "\uf11e", "\uf120", "\uf121", "\uf122", "\uf123",
    "\uf124", "\uf125", "\uf126", "\uf127", "\uf128", "\uf129", "\uf12a",
    "\uf12b", "\uf12c", "\uf12d", "\uf12e", "\uf130", "\uf131", "\uf132",
    "\uf133", "\uf134", "\uf135", "\uf136", "\uf137", "\uf138", "\uf139",
    "\uf13a", "\uf13b", "\uf13c", "\uf13d", "\uf13e", "\uf140", "\uf141",
    "\uf142", "\uf143", "\uf144", "\uf145", "\uf146", "\uf147", "\uf148",
    "\uf149", "\uf14a", "\uf14b", "\uf14c", "\uf14d", "\uf14e", "\uf150",
    "\uf151", "\uf152", "\uf153", "\uf154", "\uf155", "\uf156", "\uf157",
    "\uf158", "\uf159", "\uf15a", "\uf15b", "\uf15c", "\uf15d", "\uf15e",
    "\uf160", "\uf161", "\uf162", "\uf163", "\uf164", "\uf165", "\uf166",
    "\uf167", "\uf168", "\uf169", "\uf16a", "\uf16b", "\uf16c", "\uf16d",
    "\uf16e", "\uf170", "\uf171", "\uf172", "\uf173", "\uf174", "\uf175",
    "\uf176", "\uf177", "\uf178", "\uf179", "\uf17a", "\uf17b", "\uf17c",
    "\uf17d", "\uf17e", "\uf180", "\uf181", "\uf182", "\uf183", "\uf184",
    "\uf185", "\uf186", "\uf187", "\uf188", "\uf189", "\uf18a", "\uf18b",
    "\uf18c", "\uf18d", "\uf18e", "\uf190", "\uf191", "\uf192", "\uf193",
    "\uf194", "\uf195", "\uf196", "\uf197", "\uf198", "\uf199", "\uf19a",
    "\uf19b", "\uf19c", "\uf19d", "\uf19e", "\uf1a0", "\uf1a1", "\uf1a2",
    "\uf1a3", "\uf1a4", "\uf1a5", "\uf1a6", "\uf1a7", "\uf1a8", "\uf1a9",
    "\uf1aa", "\uf1ab", "\uf1ac", "\uf1ad", "\uf1ae", "\uf1b0", "\uf1b1",
    "\uf1b2", "\uf1b3", "\uf1b4", "\uf1b5", "\uf1b6", "\uf1b7", "\uf1b8",
    "\uf1b9", "\uf1ba", "\uf1bb", "\uf1bc", "\uf1bd", "\uf1be", "\uf1c0",
    "\uf1c1", "\uf1c2", "\uf1c3", "\uf1c4", "\uf1c5", "\uf1c6", "\uf1c7",
    "\uf1c8", "\uf1c9", "\uf1ca", "\uf1cb", "\uf1cc", "\uf1cd", "\uf1ce",
    "\uf1d0", "\uf1d1", "\uf1d2", "\uf1d3", "\uf1d4", "\uf1d5", "\uf1d6",
    "\uf1d7", "\uf1d8", "\uf1d9", "\uf1da", "\uf1db", "\uf1dc", "\uf1dd",
    "\uf1de", "\uf1e0", "\uf1e1", "\uf1e2", "\uf1e3", "\uf1e4", "\uf1e5",
    "\uf1e6", "\uf1e7", "\uf1e8", "\uf1e9", "\uf1ea", "\uf1eb", "\uf1ec",
    "\uf1ed", "\uf1ee", "\uf1f0", "\uf1f1", "\uf1f2", "\uf1f3", "\uf1f4",
    "\uf1f5", "\uf1f6", "\uf1f7", "\uf1f8", "\uf1f9", "\uf1fa", "\uf1fb",
    "\uf1fc", "\uf1fd", "\uf1fe", "\uf200", "\uf201", "\uf202", "\uf203",
    "\uf204", "\uf205", "\uf206", "\uf207", "\uf208", "\uf209", "\uf20a",
    "\uf20b", "\uf20c", "\uf20d", "\uf20e", "\uf210", "\uf211", "\uf212",
    "\uf213", "\uf214", "\uf215", "\uf216", "\uf217", "\uf218", "\uf219",
    "\uf21a", "\uf21b", "\uf21c", "\uf21d", "\uf21e", "\uf221", "\uf222",
    "\uf223", "\uf224", "\uf225", "\uf226", "\uf227", "\uf228", "\uf229",
    "\uf22a", "\uf22b", "\uf22c", "\uf22d", "\uf230", "\uf231", "\uf232",
    "\uf233", "\uf234", "\uf235", "\uf236", "\uf237", "\uf238", "\uf239",
    "\uf23a", "\uf23b", "\uf23c", "\uf23d", "\uf23e", "\uf240", "\uf241",
    "\uf242", "\uf243", "\uf244", "\uf245", "\uf246", "\uf247", "\uf248",
    "\uf249", "\uf24a", "\uf24b", "\uf24c", "\uf24d", "\uf24e", "\uf250",
    "\uf251", "\uf252", "\uf253", "\uf254", "\uf255", "\uf256", "\uf257",
    "\uf258", "\uf259", "\uf25a", "\uf25b", "\uf25c", "\uf25d", "\uf25e",
    "\uf260", "\uf261", "\uf262", "\uf263", "\uf264", "\uf265", "\uf266",
    "\uf267", "\uf268", "\uf269", "\uf26a", "\uf26b", "\uf26c", "\uf26d",
    "\uf26e", "\uf270", "\uf271", "\uf272", "\uf273", "\uf274", "\uf275",
    "\uf276", "\uf277", "\uf278", "\uf279", "\uf27a", "\uf27b", "\uf27c",
    "\uf27d", "\uf27e", "\uf280", "\uf281", "\uf282", "\uf283", "\uf284",
    "\uf285", "\uf286", "\uf287", "\uf288", "\uf289", "\uf28a", "\uf28b",
    "\uf28c", "\uf28d", "\uf28e", "\uf290", "\uf291", "\uf292", "\uf293",
    "\uf294", "\uf295", "\uf296", "\uf297", "\uf298", "\uf299", "\uf29a",
    "\uf29b", "\uf29c", "\uf29d", "\uf29e", "\uf2a0", "\uf2a1", "\uf2a2",
    "\uf2a3", "\uf2a4", "\uf2a5", "\uf2a6", "\uf2a7", "\uf2a8", "\uf2a9",
    "\uf2aa", "\uf2ab", "\uf2ac", "\uf2ad", "\uf2ae", "\uf2b0", "\uf2b1",
    "\uf2b2", "\uf2b3", "\uf2b4", "\uf2b5", "\uf2b6", "\uf2b7", "\uf2b8",
    "\uf2b9", "\uf2ba", "\uf2bb", "\uf2bc", "\uf2bd", "\uf2be", "\uf2c0",
    "\uf2c1", "\uf2c2", "\uf2c3", "\uf2c4", "\uf2c5", "\uf2c6", "\uf2c7",
    "\uf2c8", "\uf2c9", "\uf2ca", "\uf2cb", "\uf2cc", "\uf2cd", "\uf2ce",
    "\uf2d0", "\uf2d1", "\uf2d2", "\uf2d3", "\uf2d4", "\uf2d5", "\uf2d6",
    "\uf2d7", "\uf2d8", "\uf2d9", "\uf2da", "\uf2db", "\uf2dc", "\uf2dd",
    "\uf2de", "\uf2e0"
]

