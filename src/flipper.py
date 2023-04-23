import tkinter as tk
import tkinter.font as tkFont
from tkinter import *
from random import randrange

screenstate = False
textcolor="yellow"
boxcolor="grey"
backgroundcolor="darkblue"
maxLetters=5


def toggle_fullscreen(self, event=None):
    global screenstate
    global root
    screenstate = not screenstate  # Just toggling the boolean
    root.attributes("-fullscreen", screenstate)

def end_fullscreen(self, event=None):
    global screenstate
    global root
    screenstate = False
    root.attributes("-fullscreen", False)
    return "break"

def abs_move(self, _object, new_x, new_y):
    # Get the current object position
    x, y, *_ = self.bbox(_object)
    # Move the object
    self.move(_object, new_x-x, new_y-y)


def button1_pressed(self, event=None):
    global modifyLetter
    global actword, xpos, ypos, textcolor, boxcolor
    modifyLetter=modifyLetter+1
    if (modifyLetter>=maxLetters):
        modifyLetter=0
    print ("button1 pressed, modifyLetter = " + str(modifyLetter))
    animate(actword, xpos, ypos, textcolor, boxcolor)
    

def button2_pressed(self, event=None):
    global modifyLetter
    global actword, xpos, ypos, textcolor, boxcolor
    if (modifyLetter<maxLetters-1):
        nextLetter=modifyLetter+1;
        if (nextLetter>=maxLetters):
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

    print ("button2 pressed, actword = " + actword)
    animate(actword, xpos, ypos, textcolor, boxcolor)
    


root = tk.Tk()


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

tk.Canvas.abs_move = abs_move
frame = Frame(root)
frame.pack()
root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", end_fullscreen)
root.bind("<F1>", button1_pressed)
root.bind("<F2>", button2_pressed)

canvas = tk.Canvas(root)
canvas.pack(fill="both", expand=True)
canvas.configure(bg=backgroundcolor)

letterfont = tkFont.Font(size = fontsize)
width = letterfont.measure("0")

def draw(char, x, y, textcolor, boxcolor):
    """Draw one character in a box at the given coordinate"""
    global canvas,varitext

    text_id = canvas.create_text(x, y, text=char, anchor="nw", font=letterfont, fill=textcolor)
    x0, y0, x1, y1 = canvas.bbox(text_id)
    box_id = canvas.create_rectangle(x0-1, y0-1, x1+1, y1+1, fill=boxcolor, outline="white")
    canvas.lift(text_id, box_id)

def animate(string, x, y, textcolor, boxcolor):
    """Draw each character in the string at one second intervals. """
    global modifyLetter, canvas
    
    canvas.delete("all")
    # canvas.update_idletasks()
    for i in range (len(string)):
        draw(string[i], x, y, textcolor, boxcolor)
        width=letterfont.measure(string[i])+10
        if i==modifyLetter:
            box_id = canvas.create_rectangle(x, y-30, x+width-10, y-10, fill="white", outline="white")
        x=x+width
    
    

#    if len(string) > 1:
#        width = letterfont.measure(string[0]) +10
#        string = string[1:]
#        canvas.after(100, animate, canvas, string, x+width, y, textcolor, boxcolor)



text_file = open("worte.txt", "r")
lines = text_file.readlines()
text_file.close()

lines[:] = [x.upper() for x in lines if x.strip()]
# print (lines)
print (len(lines))

#actword="LIADS"
actword=lines[randrange(len(lines))].rstrip()
print (actword)

modifyLetter=0   

animate(actword, xpos, ypos, textcolor, boxcolor)

myrect = canvas.create_rectangle(10, 10, 20, 20, fill="red", outline="white")

pos=0

def film():
    global pos, text
    canvas.move(myrect,1,0)
    canvas.after(100, film)
    pos=pos+1
    if pos==50:
        pos=0
        canvas.abs_move(myrect,10,10)


film()
root.mainloop()




# root.geometry("400x300")
# root.configure(bg='blue')
