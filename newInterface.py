from Tkinter import *
import tkinter.tix
import tkMessageBox
import os
import idlelib
from os import listdir
from os.path import isfile, join

mypath = os.getcwd()
print mypath

framePadX=3
framePadY=3
fileSysX = 300
fileSysY=360

fileToSend = ""

slashcount = 0

window = tkinter.tix.Tk()
window.title("FTP Application")
window.resizable(0,0)

# FINDS LAST BACKSLASH AND REMOVES EVERYTHING AFTER IT
def getCdup():
	global mypath
	slashcount = mypath.count('\\')
	total = len(mypath)
	count = 0
	slashindex = 0
	index = -1
	for char in mypath:
		index = index + 1
		if char == '\\':
			count = count + 1
			if count == slashcount:
				slashindex = index
	mypath = mypath[:-(total-slashindex)]
	print mypath



def doubleClick(object):
	global mypath
	# if starts with . remove from mypath list
	if object == '...':
		getCdup()
		terminalText.insert('1.0', 'Changed directory to ' + mypath + '\n')
		terminalText.pack()
		showDirContents()
	elif "." not in object:
		mypath = mypath + '\\' + object
		terminalText.insert('1.0', 'Changed directory to ' + mypath + '\n')
		terminalText.pack()
		showDirContents()
	else:
		fileToSend = mypath + '\\' + object
		terminalText.insert('1.0','Send file: ' + fileToSend + '\n')
		terminalText.pack()
		#																		<------------------------- Upload file 'fileToSend'


def run(event):
	os.system(event.widget.get())

def showDirContents():
	global mypath
	localAdd = Label(window, text=mypath,bg='black',fg='white',width=60,anchor=E).grid(column=2,row=2,columnspan=3)
	localFrame.delete("all")
	newlist = []
	newerlist = []
	contents = os.listdir(mypath)
	goUp = "..."
	contents.insert(0,goUp)
	for index,x in enumerate(contents):
		if "." not in x or x == "...":
			newlist.append(Button(window, text=x, relief='flat',command=lambda x = x: doubleClick(x),bg='blue'))
			newerlist.append(localFrame.create_window(10, 10+index*20, anchor=NW, window=newlist[index]))
		else:
			newlist.append(Button(window, text=x, relief='flat',command=lambda x = x: doubleClick(x)))
			newerlist.append(localFrame.create_window(10, 10+index*20, anchor=NW, window=newlist[index]))

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
		terminalText.insert('1.0', "Entered port:" + portEntry.get()+"\n")
		terminalText.pack()
		
		# 										<----------------------------------------------- Run log in  with USR and PASS, etc


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
  
# Port Entry
portEntry = Entry(window)
portEntry.insert(0,"Port")
portEntry.grid(row = 0, column=3,padx=5,pady=10)

# Connect Button
connectBtn = Button(window, text="CONNECT", command=login)
connectBtn.grid(row=0,column=4,padx=50)

# Server Title
serverTitle = Label(window, text="Files Hosted Remotely").grid(column=0,row=1)
serverAdd = Label(window, text="",bg='black',fg='white',width=42).grid(column=0,row=2,columnspan=2)
# Server Title
localTitle = Label(window, text="Files Hosted Locally").grid(column=2,row=1)
localAdd = Label(window, text=mypath,bg='black',fg='white',width=60).grid(column=2,row=2,columnspan=3)

serverFrame = Canvas(width=fileSysX, height=fileSysY,relief = SUNKEN,borderwidth=2)
serverFrame.grid(row=3,column=0,columnspan=2,padx=framePadX,pady=framePadY)


terminalFrame = Frame(colormap="new",relief = SUNKEN,borderwidth=2,bg='black')
terminalFrame.grid(row=4,column=0,columnspan=5,padx=framePadX,pady=framePadY)
terminalText = Text(terminalFrame,bg='black',fg='white',height=14,width=90)
terminalText.pack()

terminalEntry = Entry(window,width=120,bg='black',fg='white')
terminalEntry.insert(0,">Enter custon command>>")
terminalEntry.grid(row=5,column=0,columnspan=5)
terminalEntry.bind('<Return>',run)

localFrame = Canvas(width=fileSysX*1.4, height=fileSysY,relief = SUNKEN,borderwidth=2)
localFrame.grid(row=3,column=2,columnspan=3,padx=framePadX,pady=framePadY)

showDirContents()
	

window.mainloop()
