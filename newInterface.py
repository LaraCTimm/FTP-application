from Tkinter import *
import tkMessageBox
import os

framePadX=3
framePadY=3
fileSysX = 300
fileSysY=360

window = Tk()
window.title("FTP Application")

folderContent = {	'filename': 'example',
					'filetype': 'folder',
					'filesize': 1024}

def run(event):
	os.system(event.widget.get())

# START SERVER
# *TO DO* Check if server is running OR exit server with exit of app
os.system("start cmd /k python FTPserver.py")

# START CLIENT
def login():
	if userEntry.get() == 'Username' or passEntry.get() == 'Password' or addressEntry.get() == 'ServerAddress':
		tkMessageBox.showinfo("Login Error", "Please enter a username, password and address.")
	else:
		print 'Entered username:' + userEntry.get() + '\n'
		print 'Entered password:' + passEntry.get() + '\n'
		print 'Entered address:' + addressEntry.get() + '\n'
		# To be replaced with login functions


# TKINTER WIDGET SETUP

# Username Entry
userEntry = Entry(window)
userEntry.insert(0,"Username")
userEntry.grid(row=0,column=0,padx=10,pady=10)

passEntry = Entry(window)
passEntry.insert(0,"Password")
passEntry.grid(row=0,column=1,padx=5,pady=10)

addressEntry = Entry(window)
addressEntry.insert(0,"ServerAddress")
addressEntry.grid(row=0,column=2,padx=10,pady=10)
  
connectBtn = Button(window, text="CONNECT", command=login)
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