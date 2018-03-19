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
#os.system("start cmd /k python FTPserver.py")

# START CLIENT
def login():
	if userEntry.get() == 'Username' or passEntry.get() == 'Password' or addressEntry.get() == 'ServerAddress':
		tkMessageBox.showinfo("Login Error", "Please enter a username, password and address.")
	else:
		terminalText.insert('1.0', "Entered username:" + userEntry.get()+"\n")
		terminalText.pack()
		terminalText.insert('1.0', "Entered password:" + passEntry.get()+"\n")
		terminalText.pack()
		terminalText.insert('1.0', "Entered address:" + addressEntry.get()+"\n")
		terminalText.pack()
		#print 'Entered username:' + userEntry.get() + '\n'
		#print 'Entered password:' + passEntry.get() + '\n'
		#print 'Entered address:' + addressEntry.get() + '\n'
		
		# To be replaced with login functions


# TKINTER WIDGET SETUP

# Username Entry
userEntry = Entry(window)
userEntry.insert(0,"Username")
userEntry.grid(row=0,column=0,padx=10,pady=10)

# Password Entry
passEntry = Entry(window)
passEntry.insert(0,"Password")
passEntry.grid(row=0,column=1,padx=5,pady=10)

# Address Entry
addressEntry = Entry(window)
addressEntry.insert(0,"ServerAddress")
addressEntry.grid(row=0,column=2,padx=10,pady=10)
  
# Connect Button
connectBtn = Button(window, text="CONNECT", command=login)
connectBtn.grid(row=0,column=3,padx=50)

serverFrame = Frame(width=fileSysX, height=fileSysY,  colormap="new",relief = SUNKEN,borderwidth=2,bg='')
serverFrame.grid(row=1,column=0,columnspan=2,padx=framePadX,pady=framePadY)

localFrame = Frame(width=fileSysX, height=fileSysY, colormap="new",relief = SUNKEN,borderwidth=2,bg='')
localFrame.grid(row=1,column=2,columnspan=2,padx=framePadX,pady=framePadY)

terminalFrame = Frame(colormap="new",relief = SUNKEN,borderwidth=2,bg='black')
terminalFrame.grid(row=2,column=0,columnspan=4,padx=framePadX,pady=framePadY)
terminalText = Text(terminalFrame,bg='black',fg='white',height=14,width=75)
terminalText.pack()
#terminalText.insert('1.0', "Just a new text Widget\nin two lines\n")
#terminalText.pack()

terminalEntry = Entry(window,width=102,bg='black',fg='white')
terminalEntry.insert(0,">Enter custon command>>")
terminalEntry.grid(row=3,column=0,columnspan=4)
terminalEntry.bind('<Return>',run)

window.mainloop()




# buffer = io.StringIO()

# print("something", file=buffer)
# print("something more", file=buffer)

# output = buffer.getvalue()
# text.insert(END, output)