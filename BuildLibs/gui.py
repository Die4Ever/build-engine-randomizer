from random import Random
from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
import traceback
from BuildLibs.grp import *

class RandoSettings:
    def __init__(self):
        self.width=500
        self.height=500
        self.initWindow()
        self.ChooseFile()
        if self.win:
            self.win.mainloop()

    def closeWindow(self):
        self.win.destroy()
        self.win=None

    def isWindowOpen(self) -> bool:
        return self.win!=None

    def resize(self,event):
        if event.widget == self.win:
            pass

    def _ChooseFile(self):
        grppath = ''
        try:
            self.randoButton["state"]='disabled'
            self.update()
            grppath = chooseFile(self.win)
            if grppath == '':
                warning('no file selected!')
                self.closeWindow()
                return True
            self.grp: GrpFile = GrpFile(grppath)
            self.win.title(self.grp.game.type + ' ' + GetVersion() + ' Randomizer - ' + self.grp.game.name)
            self.randoButton["state"]='normal'
        except Exception as e:
            messagebox.showerror('Error Opening File', str(e) +'\n\n' + traceback.format_exc())
            print('Error Opening File', grppath, '\n', str(e),'\n\n', traceback.format_exc())
            self.closeWindow()
            raise
        return True

    def ChooseFile(self):
        self._ChooseFile()

    def _Randomize(self):
        seed = self.seedEntry.get()
        if seed == '':
            seed = random.randint(1, 999999)
        self.grp.Randomize(seed)
        messagebox.showinfo('Randomization Complete!', 'All done! Seed: ' + str(seed))
        self.closeWindow()

    def Randomize(self):
        try:
            self.randoButton["state"]='disabled'
            self.update()
            self._Randomize()
        except Exception as e:
            messagebox.showerror('Error Randomizing', str(e) +'\n\n' + traceback.format_exc())
            if self.isWindowOpen():
                self.randoButton["state"]='normal'
            raise


    def initWindow(self):
        self.win = Tk()
        self.win.protocol("WM_DELETE_WINDOW",self.closeWindow)
        self.win.bind("<Configure>",self.resize)
        self.win.title('Build Engine Randomizer '+GetVersion()+' Settings')
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
