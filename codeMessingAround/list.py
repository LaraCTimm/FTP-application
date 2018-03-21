from Tkinter import *
import os

root = Tk()
scrollbar = Scrollbar(root)
scrollbar.pack( side = RIGHT, fill = Y )


mypath = str(os.getcwd())

print mypath
#mypath = os.path.join(mypath, '.\clientDirectory')
contents = os.listdir(mypath)
#print contents

def populateListBox(contents):
    mylist.delete(0, END)
    mylist.insert(END, '...')
    for line in contents:
        fileName = os.path.join(mypath, './'+line)
        if os.path.isdir(fileName):
            newline = '>   '+line
        else:
            newline = '     '+line
        mylist.insert(END, str(newline))


def cursorSelect(evt):
    global value
    global contents
    value = str((mylist.get(mylist.curselection())))
    print value

    mylist.activate(0)

    if value == '...':
        goUpDir()
    elif value[0] == '>':
        changeWorkingDir(value[4:])


def goUpDir():
    global mypath
    var = mypath.split('\\')
    cwdPath = '\\'.join(var[:-1])
    print cwdPath
    mypath = cwdPath
    contents = os.listdir(mypath)
    populateListBox(contents)

def changeWorkingDir(dirName):
    global mypath
    dirPath = os.path.join(mypath, dirName)
    if os.path.isdir(dirPath):
        mypath = dirPath
        contents = os.listdir(mypath)
        populateListBox(contents)



mylist = Listbox(root, yscrollcommand = scrollbar.set )
mylist.bind('<<ListboxSelect>>', cursorSelect)
populateListBox(contents)

mylist.pack( side = LEFT, fill = BOTH )
scrollbar.config( command = mylist.yview )


mainloop()