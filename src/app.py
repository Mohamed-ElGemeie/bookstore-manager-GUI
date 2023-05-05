import tkinter as tk
from pages.PrintPage import *

class App(tk.Tk):
  
  # inherate everything from tkinter
  def __init__(self,*args,**kwargs):
    # create tkinter window
    tk.Tk.__init__(self,*args,**kwargs)
    # resolution of the window
    self.geometry('1280x700+20+20')

    window = tk.Frame(self)
    window.pack(side="top",fill='both',expand=True)
    window.grid_rowconfigure(0,weight=1)
    window.grid_columnconfigure(0,weight=1)

    # stacker of pages
    buttons = tk.Frame(window)
    stacker = tk.Frame(window)

    #change stacker row and column sizes
    stacker.grid_rowconfigure(0,weight=1)
    stacker.grid_columnconfigure(0,weight=1)


    pages = (PrintPage,PrintPage)
    page_names = ("كتب Books","كتب Books")
    self.frames = {}
    

    for i,g in zip(pages,page_names):
        
        page_name=i.__name__

        frame= i(stacker,self,bg='#48788a')
        self.frames[page_name]= frame
        frame.grid(row=0,column=0,sticky='nsew')

        tk.Button(buttons,font=30,width=20,height=2,text=(g),command=lambda: self.show_frame(page_name)).pack(side="left")

    buttons.pack(side="top",fill="x")
    stacker.pack(side="bottom",fill='both',expand=True)

    # self.frames: holds all the tkinter frames
    # {tkinter page-name string : tkinter page object}
    # holds all the classes the inherante the tkiner frame

    # opens the startpage on start up

  def show_frame(self,page_name):
    """
    Takes a tkinter frame object (page) and displays it on top, front to the user
    parameters:
      page_name: name of the page's tkinter frame class
    """
    frame=self.frames[page_name]
    frame.tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()