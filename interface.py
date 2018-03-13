from Tkinter import *
import tkMessageBox
import os

colours = {
	'tBG'		:	'cornsilk3',
	'tFG'		:	'cornsilk4',
	'aBG' 		:	'snow',
	'aFG'		:	'cyan4',
	'mFG'		:	'bisque4',
	'mBG'		:	'snow',
	'mABG'		:	'honeydew4',
	'dBG1'		:	'CadetBlue2',
	'dFG1'		:	'cornsilk4',
	'dBG2'		:	'cornsilk4',
	'dFG2'		:	'CadetBlue2'
}

#************ FOOTPRINT CALCULATIONS ***********************************
#***********************************************************************
# Transport function - loops through each method of transport, its range and its timeframe
def transPYear(x): 
	try:
		a = x[0].lower() + x[1:]
		y = eval(a + 'In')
		z = eval(a + 'Time')
		return float(y.get())*coeff[a]*timeFramesCoeff[z.get()]
	except ValueError:
		return 0

def elecPYear():
	try:
		return float(elecIn.get())*regCoeff[regionIn.get()]*timeFramesCoeff[elecTime.get()]
	except ValueError:
		return 0

def dietPYear():
	try:
		return	dietCoeff[dietIn.get()]*365
	except ValueError:
		return 0

def clothingPYear():
	try:
		return float(spendIn.get())*clothingCoeff[clothingIn.get()]*timeFramesCoeff[clothingTime.get()]*0.005
	except ValueError:
		return 0
#**************************************************************



# OS communication
def play():
	os.system("filename.py")


#*** LIMITING ENTRIES TO INTEGERS ***
#************************************
# Class taken from Tkinter documentation
# http://effbot.org/zone/tkinter-entry-validate.htm
class ValidatingEntry(Entry):

    def __init__(self, master, value="", **kw):
        apply(Entry.__init__, (self, master), kw)
        self.__value = value
        self.__variable = StringVar()
        self.__variable.set(value)
        self.__variable.trace("w", self.__callback)
        self.config(textvariable=self.__variable)

    def __callback(self, *dummy):
        value = self.__variable.get()
        newvalue = self.validate(value)
        if newvalue is None:
            self.__variable.set(self.__value)
        elif newvalue != value:
            self.__value = newvalue
            self.__variable.set(self.newvalue)
        else:
            self.__value = value

    def validate(self, value):
        return value

class FloatEntry(ValidatingEntry):

    def validate(self, value):
        try:
            if value:
                v = float(value)
            return value
        except ValueError:
            return None



#************* GUI STUFF ******************************
#******************************************************
master = Tk()
master.state('zoomed')
master.wm_title("FTP Application")
master.configure(background = colours['tBG'])

#*** TEXT DISPLAYED ***
#**********************
Label(master, text="Username:", bg = colours['tBG'], fg = colours['tFG'], font="-family arial").grid(row=1, sticky=W)
Label(master, text="Password", bg = colours['tBG'], fg = colours['tFG'], font="-family arial").grid(row=2, sticky=W)

#*** TEXT ENTRIES ***
#********************
usernameIn 		= FloatEntry(master, fg = colours['tFG'])
passwordIn 	= FloatEntry(master, fg = colours['tFG'])

usernameIn.grid(row=2, column=1)
passwordIn.grid(row=3, column=1)




#*** BUTTONS **********************************************************************************************************************
#**********************************************************************************************************************************
class Buttons:
	#*** CONSTRUCTOR ***
	def __init__(self, master):

		Button(master, text='Submit', command=master.quit, background = colours['dBG2'], foreground = colours['dFG2'], activebackground = colours['aBG'], activeforeground = colours['aFG']).grid(row=12, column=2, sticky=W, pady=4)

#*************************************************************************


b = Buttons(master)
mainloop( )