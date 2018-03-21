from Tkinter import *
import os


len_max = 0
list_items = ["item2", "item2", "item3+a few characters for the size"]
for m in list_items:
    if len(m) > len_max:
        len_max = len(m)


master = Tk()

my_listbox1 = Listbox(master, width = len_max)
my_listbox1.grid(row = 0, column = 0)

my_listbox2 = Listbox(master, width = len_max)
my_listbox2.grid(row = 0, column = 1)

my_listbox1.insert(END, list_items[0])
my_listbox2.insert(END, list_items[1])
my_listbox2.insert(END, list_items[2])

master.mainloop()