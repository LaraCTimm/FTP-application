# AUTHORED BY SASHA BERKOWITZ ###############################################################################
from Tkinter import *
import Tkinter as tk
import Tix
import tkMessageBox
import os
import idlelib
from os import listdir
from os.path import isfile, join
import ttk
import socket
from FTPclient_logic import clientLogic 

# Constants for formatting file sizes
KB = 1024.0
MB = KB * KB
GB = MB * KB


# Get initial path
mypath = os.getcwd()

# Interface constants
framePadX=3
framePadY=3
fileSysX = 300
fileSysY=360

# Initialised variables
fileToSend = ""
slashcount = 0
customCommand = ""
selectedLocal = ""
selectedRemote = ""
remoteList=[]
isConnected = False
isLoggedIn = False

# Set up window variables
window = Tix.Tk()
window.title("FTP Application")
window.resizable(0,0)

# Finds last backslach and removes everything after
# to get new directory
def getCdup():
	global mypath
	slashcount = mypath.count('\\')
	if slashcount > 2:
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

# Function to print to displayed terminal
def printToTerminal(sentence):
	terminalText.insert(END, sentence + '\n')
	terminalText.see(END)
	terminalText.pack()

# Function to delete local file
def delLocalButton():
	global mypath
	global selectedLocal
	if(len(selectedLocal) < 1):
		tkMessageBox.showinfo("Deletion Error", "No file selected!")
	elif os.path.isfile(mypath+'\\'+selectedLocal) == False:
		tkMessageBox.showinfo("Deletion Error", "Directories cannot be deleted. \n Please select a file.")
	else:
		if os.path.isfile(mypath+'\\'+selectedLocal) == True:
			# printToTerminal(logic.reply)
			os.remove(mypath+'\\'+selectedLocal)
			contents = os.listdir(mypath)
			populateListBox(contents)
		else:
			tkMessageBox.showinfo("Deletion Error", "Cannot delete directory. Please select file instead.")

# Function to upload local file
def uplLocalButton():
	global selectedLocal
	global mypath
	if isConnected == True:
		if(len(selectedLocal) < 1):
			tkMessageBox.showinfo("Upload Error", "No file selected!")
		elif selectedLocal[0] == '>':
			tkMessageBox.showinfo("Upload Error", "Directories cannot be Uploaded. \n Please select a file.")
		else:
			
			logic.TYPE(mypath + '\\' + selectedLocal)
			logic.PASV()
			printToTerminal('Uploading file...')
			logic.STOR(mypath + '\\' + selectedLocal)
			if logic.reply[:3] == '226':
				printToTerminal('File Upload Successful\n')
			getDirFiles()
	else:
		tkMessageBox.showinfo("Upload Error", "Please connect to server before uploading file.")

# Function to delete remote file
def delServButton():
	global selectedRemote
	if(len(selectedRemote) < 1):
		tkMessageBox.showinfo("Deletion Error", "No file selected!")
	elif selectedRemote[0] == '>':
		dirDelete()
		#																				<---------------------- Delete directory from server
	else:
		logic.DELE(selectedRemote[5:-1])
		printToTerminal(logic.reply)
		getDirFiles()
		#																				<---------------------- Delete file from server

def delDir():
	global top
	top.destroy()
	global selectedRemote
	logic.RMD(selectedRemote[4:-1])
	printToTerminal(logic.reply)
	getDirFiles()

# Function to download remote file
def dnlServButton():
	global mypath
	global selectedRemote
	logic.baseDirectory = mypath
	if(len(selectedRemote) < 1):
		tkMessageBox.showinfo("Download Error", "No file selected!")
	elif selectedRemote[0] == '>':
		tkMessageBox.showinfo("Download Error", "Directories cannot be downloaded. \n Please select a file.")
	else:
		print selectedRemote[5:-1] + ' file will be downloaded'
		logic.PASV()
		logic.TYPE(selectedRemote[5:-1])
		printToTerminal('Downloading file...')
		logic.RETR(selectedRemote[5:-1])
		if logic.reply[:3] == '226':
				printToTerminal('File Download Successful\n')
		contents = os.listdir(mypath)
		populateListBox(contents)


	

# Function to create directory on the server
def mkdrServButton():
	# global newDirName
	global top
	global isConnected
	if isConnected == True:
		print newDirEntry.get()
		directoryName = newDirEntry.get()
		logic.MKD(directoryName)
		getDirFiles()
	else:
		tkMessageBox.showinfo("New Directory Error", "Cannot make directory whilst disconnected.")
	top.destroy()


# Clear entry functions
def userClear(event):
    userEntry.delete(0, END)
def passClear(event):
	passEntry.delete(0, END)
def addrClear(event):
	addressEntry.delete(0, END)
def portClear(event):
	portEntry.delete(0, END)
def termClear(event):
	terminalEntry.delete(0, END)
def newDirClear(event):
	servDir.delete(0, END)	

# Function called to extract files in server directory
def getDirFiles():
	logic.PASV()
	logic.LIST()
	global remoteList
	global remotePath
	remoteList=['..']
	for fileDet in logic.directoryArray:
		index = fileDet.index(':')
		if fileDet[0] == 'd':
			remoteList.append('>   '+fileDet[(index+4):])
		else:
			remoteList.append('     '+fileDet[(index+4):])

	populateListBoxServ(remoteList)

		


# Function called when directory or file is selected
def doubleClick(object):
	global mypath
	# if starts with . remove from mypath list
	global selectedLocal 

	# Change selected button colour
	for index,button in enumerate(newlist):
		if index == object:
			button.config(bg='PaleTurquoise1')
		else:
			button.config(bg='white')

	oldSelect = selectedLocal
	selectedLocal = contents[object]
	if contents[object] == '..':
		getCdup()
		printToTerminal(logic.reply)
		terminalText.insert('1.0', 'Changed directory to ' + mypath + '\n')
		terminalText.pack()
		showDirContents()
	elif "." not in contents[object]:
		if oldSelect == selectedLocal:
			mypath = mypath + '\\' + contents[object]
			terminalText.insert('1.0', 'Changed directory to ' + mypath + '\n')
			terminalText.pack()
			showDirContents()
	else:
		fileToSend = mypath + '\\' + contents[object]
		terminalText.insert('1.0','Send file: ' + fileToSend + '\n')
		terminalText.pack()

# Run terminal function
def run(event):
	customCommand = event.widget.get()
	terminalEntry.delete(0, END)	
	terminalText.insert('1.0','cmd: ' + customCommand + '\n')
	terminalText.pack()

	sentence = customCommand
	try:
		functionName = sentence[:4].strip().upper()

		if functionName == 'USER':
			logic.USER(sentence[5:])

		elif functionName == 'PASS':
			logic.PASS(sentence[5:])

		elif functionName == 'CWD':
			logic.CWD(sentence[4:])

		elif functionName == 'CDUP':
			logic.CDUP()

		elif functionName == 'QUIT':
			logic.QUIT()
			

		elif functionName == 'PORT':
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.bind(('', 0))
			logic.PORT(socket.gethostbyname(socket.gethostname()), sock.getsockname()[1])

		elif functionName == 'PASV':
			logic.PASV()

		elif functionName == 'TYPE':
			logic.TYPE(sentence[5:])

		elif functionName == 'STRU':
			logic.STRU(sentence[5:])

		elif functionName == 'MODE':
			logic.MODE(sentence[5:])

		elif functionName == 'RETR':
			logic.RETR(sentence[5:])

		elif functionName == 'STOR':
			logic.STOR(sentence[5:])

		elif functionName == 'DELE':
			logic.DELE(sentence[5:])

		elif functionName == 'PWD':
			logic.PWD()

		elif functionName == 'LIST':
			logic.LIST()

			print logic.directoryArray

		elif functionName == 'MKD':
			logic.MKD(sentence[4:])

		elif functionName == 'RMD':
			logic.RMD(sentence[4:])

		elif functionName == 'NOOP':
			logic.NOOP()

		else:
			raise Exception('Command not found')
	except Exception, err:
		print 'Error: ', err

# Called on window close
def disconnect():
	global isConnected
	if isConnected == True:
		logic.QUIT()
	window.destroy()
# Called when disconnect button is pushed
def disconnectBtn():
	global isConnected
	global isLoggedIn
	if isConnected == True:
		isConnected = False
		isLoggedIn = False
		logic.QUIT()
		printToTerminal(logic.reply)
		serverAdd = Label(window, text="",bg='black',fg='white',width=60).grid(column=2,row=2,columnspan=3)
		populateListBoxServ([])


# List contents in directory
def showDirContents():
	global mypath

	folderImage = PhotoImage(file='folder.gif')

	localAdd = Label(window, text=mypath,bg='black',fg='white',width=60,anchor=E).grid(column=0,row=2,columnspan=2)
	localFrame.delete("all")
	global newlist
	newlist = []
	newerlist = []
	global contents 
	contents= os.listdir(mypath)
	goUp = ".."
	contents.insert(0,goUp)
	for index,x in enumerate(contents):
		if "." not in x or x == "..":
			newlist.append(Button(window, text='-->' + x, bg='white',relief='flat',compound="left",command=lambda x = index: doubleClick(x)))
			newerlist.append(localFrame.create_window(10, 10+index*20, anchor=NW, window=newlist[index]))
		else:
			newlist.append(Button(window, text='    ' + x, bg='white',relief='flat',command=lambda x = index: doubleClick(x)))
			newerlist.append(localFrame.create_window(10, 10+index*20, anchor=NW, window=newlist[index]))

# START CLIENT
def connectButton():
	global isConnected
	global isLoggedIn

	if userEntry.get() == 'Username' or passEntry.get() == 'Password' or addressEntry.get() == 'ServerAddress':
		tkMessageBox.showinfo("Login Error", "Please enter a username, password and address.")
	else:
		global logic
		if isConnected == False:
			logic = clientLogic(addressEntry.get(), portEntry.get())
			reply = logic.clientSock.recv(256)
			printToTerminal(reply)
			isConnected = True

		logic.USER(userEntry.get())
		printToTerminal(logic.reply)
		logic.PASS(passEntry.get())
		printToTerminal(logic.reply)

		if logic.reply[:3] == '230':  
			isLoggedIn = True
			getDirFiles()
			logic.PWD()
			remotePath = logic.reply
			reply = remotePath.split('"')
			remotePath = reply[1]
			serverAdd = Label(window, text=remotePath,bg='black',fg='white',width=60).grid(column=2,row=2,columnspan=3)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~ TOPLEVEL POP-UPS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def dirDelete():
	global top
	top = Toplevel(width=1000,pady=10,padx=10)
	top.title("Directory Deletion")

	msg = Message(top, text="You are about to permanenly delete a directory and all of its contents. \n Do you wish to proceed?")
	msg.pack()

	cancelButton = Button(top, text="Cancel", command=top.destroy)
	cancelButton.pack(side="right")
	delButton = Button(top, text="Yes, Delete", command=delDir)
	delButton.pack(side="right")

def dirCreate():
	global top
	global newDirEntry
	top = Toplevel(width=1000,pady=10,padx=10)
	top.title("Create Directory")

	msg = Message(top, text="New Directory Name:")
	msg.pack()

	newDirEntry = Entry(top)
	newDirEntry.pack()
	cancelButton = Button(top, text="Cancel", command=top.destroy)
	cancelButton.pack(side="right")
	delButton = Button(top, text="Create Directory", command=mkdrServButton)
	delButton.pack(side="right")
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~ TKINTER WIDGET SETUP ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Username Entry
entryFrame = Frame(window)
userEntry = Entry(entryFrame)
userLabel=Label(entryFrame,text="Username: ")
entryFrame.grid(row=0,column=0,padx=10,pady=10)
userEntry.insert(0,"Username")
userEntry.bind('<Button-1>', userClear)
userLabel.pack(side="left")
userEntry.pack(side="left")
# Password Entry
passFrame = Frame(window)
passEntry = Entry(passFrame,show='*')
passEntry.insert(0,"Password")
passLabel = Label(passFrame,text="Password: ")
passFrame.grid(row=0,column=1,padx=5,pady=10)
passEntry.bind('<Button-1>', passClear)
passLabel.pack(side="left")
passEntry.pack(side="left")
# Address Entry
addressFrame = Frame(window)
addressEntry = Entry(addressFrame)
addressEntry.insert(0,"Address")
addressLabel = Label(addressFrame, text="Address: ")
addressFrame.grid(row=0,column=2,padx=5,pady=10)
addressEntry.bind('<Button-1>', addrClear)
addressLabel.pack(side="left")
addressEntry.pack(side="left")
# Port Entry
portFrame = Frame(window)
portEntry = Entry(portFrame)
portEntry.insert(0,"Port")
portFrame.grid(row = 0, column=3,padx=5,pady=10)
portEntry.bind('<Button-1>', portClear)
portLabel = Label(portFrame, text="Port: ")
portLabel.pack(side="left")
portEntry.pack(side="left")
# Connect Button
connectBtns = Frame(window)
connectBtns.grid(row=0,column=4,padx=5)
connectBtn = Button(connectBtns, text="CONNECT", command=connectButton)
disconnectBtn = Button(connectBtns, text="DISCONNECT",command=disconnectBtn)
connectBtn.pack(side="left")
disconnectBtn.pack(side="left")
# Server Title
serverTitle = Label(window, text="Files Hosted Remotely").grid(column=2,row=1,padx=10)
serverAdd = Label(window, text="",bg='black',fg='white',width=60).grid(column=2,row=2,columnspan=3,pady=3,padx=5 )
serverBtnFrame = Frame(window)
servDel = Button(serverBtnFrame,text="DEL",command=delServButton)
servDnl = Button(serverBtnFrame,text="DWNL",command=dnlServButton)
servMkdr = Button(serverBtnFrame,text="NEW DIR",command=dirCreate)
serverBtnFrame.grid(row=1,column=4,sticky="nsew", padx=10)
servDel.pack(side="right")
servDnl.pack(side="right")
servMkdr.pack(side="right")
# Local Title
localTitle = Label(window, text="Files Hosted Locally").grid(column=0,row=1,sticky=W,padx=5)
localAdd = Label(window, text=mypath,bg='black',fg='white',width=60).grid(column=0,row=2,columnspan=2,padx=5)
localBtnFrame = Frame(window,padx=10)
localDel = Button(localBtnFrame,text="DEL",command=delLocalButton)
localUpl = Button(localBtnFrame,text="UPL",command=uplLocalButton)
localBtnFrame.grid(row=1,column=1,sticky="nsew", padx=0)
localDel.pack(side="right")
localUpl.pack(side="right")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ TERMINAL ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Frame with terminal responses
terminalFrame = Frame(colormap="new",relief = SUNKEN,borderwidth=2,bg='black')
terminalFrame.grid(row=4,column=0,columnspan=5,padx=framePadX,pady=framePadY)
terminalText = Text(terminalFrame,bg='black',fg='white',height=14,width=120)
terminalText.see(END)
terminalText.pack()
# Clearing terminal
printToTerminal('\n')
printToTerminal('\n')
printToTerminal('\n')
printToTerminal('\n')
printToTerminal('\n')
printToTerminal('\n')
printToTerminal('\n')
printToTerminal('\n')
# Terminal Entry
terminalEntry = Entry(window,width=160,bg='black',fg='white')
terminalEntry.insert(0,">Enter custom command>>")
terminalEntry.grid(row=5,column=0,columnspan=5)
terminalEntry.bind('<Button-1>', termClear)
terminalEntry.bind('<Return>',run)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


mypath = str(os.getcwd())
print mypath
contents = os.listdir(mypath)

# Functions to populate displayed local and remote file directories
def populateListBox(contents):
    mylist.delete(0, END)
    mylist.insert(END, '..')
    for line in contents:
        fileName = os.path.join(mypath, './'+line)
        if os.path.isdir(fileName):
            newline = '>   '+line
        else:
            newline = '     '+line
        mylist.insert(END, str(newline))
def populateListBoxServ(contents):
	servlist.delete(0, END)
	for line in contents:
		servlist.insert(END, str(line))
	
# Functions called to select files or directories on click
def cursorSelect(evt):
    global contents
    global selectedLocal
    value = str((mylist.get(mylist.curselection())))
    print value
    mylist.activate(0)
    if value == '..':
        selectedLocal = '..'
    else:
    	selectedLocal = value[5:]
def cursorSelectServ(evt):
	global selectedRemote
	global remotePath
	value=str((servlist.get(servlist.curselection())))
	servlist.activate(0)
	logic.PWD()
	remotePath = logic.reply
	reply = remotePath.split('"')
	remotePath = reply[1]
	if value == '..':
		selectedRemote = value
		#goUpDirServ()
	else:
		selectedRemote = value
		print selectedRemote

# Functions called to go up a file directory in local and remote
def goUpDir():
    global mypath
    var = mypath.split('\\')
    cwdPath = '\\'.join(var[:-1])
    print cwdPath
    mypath = cwdPath
    printToTerminal(mypath)
    contents = os.listdir(mypath)
    populateListBox(contents)
    localAdd = Label(window, text=mypath,bg='black',fg='white',width=60).grid(column=0,row=2,columnspan=2)

def goUpDirServ():
	global remotePath
	var = remotePath.split('\\')
	remotePath = '\\'.join(var[:-1])
	logic.CDUP()
	if not logic.reply[0] == '5':
		serverAdd = Label(window, text=remotePath,bg='black',fg='white',width=60).grid(column=2,row=2,columnspan=3)
		getDirFiles()
	else:
		getDirFiles()

# Function called to change local, working directory
def changeWorkingDir():
	global mypath

	value = str((mylist.get(mylist.curselection())))
	print 'double', value
	if value == '..':
		goUpDir()
		
	elif value[0] == '>':
		dirPath = os.path.join(mypath, value[4:])
		if os.path.isdir(dirPath):
			mypath = dirPath
			contents = os.listdir(mypath)
			populateListBox(contents)
	localAdd = Label(window, text=mypath,bg='black',fg='white',width=60).grid(column=0,row=2,columnspan=2)

# Function called to get remote path
def getRemPath():
	global remotePath
	logic.PWD()
	remotePath = logic.reply
	reply = remotePath.split('"')
	remotePath = reply[1]
	serverAdd = Label(window, text=remotePath,bg='black',fg='white',width=60).grid(column=2,row=2,columnspan=3)
	
# Function called to change remote working directory
def changeWorkingDirServ():
	global remotePath
	value = str((servlist.get(servlist.curselection())))
	if value == '..':
		goUpDirServ()
	elif value[0] == '>':
		print remotePath+'\\' +value[4:-1]
		print 'change dir'
		logic.CWD(value[4:-1])

		printToTerminal(logic.reply)
		if logic.reply[0] == '2':
			getRemPath()
			print 'Directory changed'
			getDirFiles()
		#logic.PWD()
		print 'changedir'

# Frame with server files 
serverFrame = Frame(width=fileSysX*1.5, height=fileSysY,relief = SUNKEN, bg = 'blue')
serverFrame.grid(row=3,column=2,columnspan=4,padx=framePadX,pady=framePadY)

# Frame with local files - Literallly only for stupid scroll bar
localFrame = Frame(width=65, height=20,relief = SUNKEN, bg = 'red')
localFrame.grid(row=3,column=0,columnspan=2,padx=framePadX,pady=0)

yscrollbar = Scrollbar(localFrame, orient = VERTICAL)
yscrollbar.pack( side = RIGHT, fill = Y )

xscrollbar = Scrollbar(localFrame, orient = HORIZONTAL)
xscrollbar.pack( side = BOTTOM, fill = X )

mylist = Listbox(window, width = 70, height=22, yscrollcommand = yscrollbar.set, xscrollcommand = xscrollbar.set)
mylist.grid(row=3,column=0,columnspan=2)

mylist.bind('<<ListboxSelect>>', cursorSelect)
mylist.bind('<Double-1>', lambda x: changeWorkingDir())

yscrollbarserv = Scrollbar(serverFrame, orient = VERTICAL)
yscrollbarserv.pack( side = RIGHT, fill = Y )

xscrollbarserv = Scrollbar(serverFrame, orient = HORIZONTAL)
xscrollbarserv.pack( side = BOTTOM, fill = X )

servlist = Listbox(window, width = 70, height=22, yscrollcommand = yscrollbarserv.set, xscrollcommand = xscrollbarserv.set)
servlist.grid(row=3,column=2,columnspan=3)

servlist.bind('<<ListboxSelect>>', cursorSelectServ)
servlist.bind('<Double-1>', lambda x: changeWorkingDirServ())

populateListBox(contents)

populateListBoxServ(remoteList)

yscrollbar.config( command = mylist.yview )
xscrollbar.config( command = mylist.xview )

window.protocol("WM_DELETE_WINDOW", disconnect)
window.mainloop()
