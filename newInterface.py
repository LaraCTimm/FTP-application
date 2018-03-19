from Tkinter import *
import tkMessageBox
import os

framePadX=3
framePadY=3
fileSysX = 300
fileSysY=360

window = Tk()
window.title("FTP Application")

def run(event):
	os.system(event.widget.get())



userEntry = Entry(window)
userEntry.insert(0,"Username")
userEntry.grid(row=0,column=0,padx=10,pady=10)

passEntry = Entry(window)
passEntry.insert(0,"Password")
passEntry.grid(row=0,column=1,padx=5,pady=10)

addressEntry = Entry(window)
addressEntry.insert(0,"ServerAddress")
addressEntry.grid(row=0,column=2,padx=10,pady=10)
  
connectBtn = Button(window, text="CONNECT!")
connectBtn.grid(row=0,column=3,padx=50)

serverFrame = Frame(width=fileSysX, height=fileSysY,  colormap="new",relief = SUNKEN,borderwidth=2,bg='white')
serverFrame.grid(row=1,column=0,columnspan=2,padx=framePadX,pady=framePadY)

localFrame = Frame(width=fileSysX, height=fileSysY, colormap="new",relief = SUNKEN,borderwidth=2,bg='white')
localFrame.grid(row=1,column=2,columnspan=2,padx=framePadX,pady=framePadY)

terminalFrame = Frame(colormap="new",relief = SUNKEN,borderwidth=2,height=180,width=(2*fileSysX)+(4*framePadX),bg='black')
terminalFrame.grid(row=2,column=0,columnspan=4,padx=framePadX,pady=framePadY)

terminalEntry = Entry(window,width=102,bg='black',fg='white')
terminalEntry.insert(0,">Enter custon command>>")
terminalEntry.grid(row=3,column=0,columnspan=4)
terminalEntry.bind('<Return>',run)

window.mainloop()