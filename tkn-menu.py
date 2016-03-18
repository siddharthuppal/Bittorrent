from Tkinter import *
from tkFileDialog import askopenfilename
import sys
import unittest
import bencode

def donothing():
   filewin = Toplevel(root)
   button = Button(filewin, text="Do nothing button")
   button.pack()

def quit_handler():
    print "program is quitting!"
    sys.exit(0)

def open_file_handler():
    file= askopenfilename()
    abc = bencode.bdecode(open(file, 'rb').read())
    print abc
    return file   


root = Tk()
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=donothing)
filemenu.add_command(label="Add Torrent File", command=open_file_handler)
filemenu.add_command(label="Save", command=donothing)
filemenu.add_command(label="Save as...", command=donothing)
filemenu.add_command(label="Close", command=quit_handler)

filemenu.add_separator()

filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Undo", command=donothing)

editmenu.add_separator()

editmenu.add_command(label="Cut", command=donothing)
editmenu.add_command(label="Copy", command=donothing)
editmenu.add_command(label="Paste", command=donothing)
editmenu.add_command(label="Delete", command=donothing)
editmenu.add_command(label="Select All", command=donothing)

menubar.add_cascade(label="Edit", menu=editmenu)
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=donothing)
helpmenu.add_command(label="About...", command=donothing)
menubar.add_cascade(label="Help", menu=helpmenu)

open_file = Button(root, command=open_file_handler, padx=100, text="OPEN FILE")
open_file.pack()

quit_button = Button(root, command=quit_handler, padx=100, text="QUIT")
quit_button.pack()


root.config(menu=menubar)
root.mainloop()
