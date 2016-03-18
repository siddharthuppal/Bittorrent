import sys
import Tkinter
from tkFileDialog import askopenfilename
#import tkMessageBox

def quit_handler():
    print "program is quitting!"
    sys.exit(0)

def open_file_handler():
    file= askopenfilename()
    print file
    return file


main_window = Tkinter.Tk()


open_file = Tkinter.Button(main_window, command=open_file_handler, padx=100, text="OPEN FILE")
open_file.pack()


quit_button = Tkinter.Button(main_window, command=quit_handler, padx=100, text="QUIT")
quit_button.pack()


main_window.mainloop()
