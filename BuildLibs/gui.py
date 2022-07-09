from random import Random
from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
from BuildLibs.grp import *

class RandoSettings:
    def __init__(self):
        self.width=500
        self.height=500
        self.initWindow()
        self.randoButton["state"]='disabled'
        self.update()
        grppath = chooseFile(self.win)
        if grppath == '':
            warning('no file selected!')
            return
        self.grp: GrpFile = GrpFile(grppath)
        self.win.title(self.grp.game.type + ' Randomizer - ' + self.grp.game.name)
        self.randoButton["state"]='normal'
        self.win.mainloop()

    def closeWindow(self):
        self.win.destroy()
        self.win=None

    def isWindowOpen(self):
        return self.win!=None

    def resize(self,event):
        if event.widget == self.win:
            pass

    def Randomize(self):
        self.randoButton["state"]='disabled'
        self.update()
        seed = self.seedEntry.get()
        if seed == '':
            seed = random.randint(1, 999999)
        self.grp.Randomize(seed)
        messagebox.showinfo('Randomization Complete!', 'All done! Seed: ' + str(seed))
        self.randoButton["state"]='normal'
        self.closeWindow()

    def initWindow(self):
        self.win = Tk()
        self.win.protocol("WM_DELETE_WINDOW",self.closeWindow)
        self.win.bind("<Configure>",self.resize)
        self.win.title("Build Engine Randomizer Settings")
        self.win.geometry(str(self.width)+"x"+str(self.height))
        #self.win.config()
        self.font = font.Font(size=14)

        seedLabel = Label(self.win,text='Seed: ',width=20,height=2,font=self.font)
        seedLabel.grid(column=0,row=0)
        seedEntry = Entry(self.win,width=20,font=self.font)
        seedEntry.grid(column=1,row=0)
        self.seedEntry = seedEntry

        self.randoButton = Button(self.win,text='Randomize!',width=20,height=2,font=self.font,command=self.Randomize)
        self.randoButton.grid(column=1,row=100)

    def update(self):
        self.win.update()

def main():
    settings = RandoSettings()

def chooseFile(root):
    filetype = (("GRP File","*.grp"),("all files","*.*"))
    target = filedialog.askopenfilename(title="Choose a GRP file",filetypes=filetype)
    return target
