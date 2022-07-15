from random import Random
from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
from idlelib.tooltip import Hovertip
import traceback
from BuildLibs.grp import *

class RandoSettings:
    def __init__(self):
        self.width=468
        self.height=375
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
            try:
                self.width = event.width
                self.height = event.height
            except Exception as e:
                print('ERROR: in resize:', e)

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

            self.grppath = grppath
            self.win.title('Loading '+grppath+'...')
            self.update()
            self.grp: GrpFile = GrpFile(grppath)

            self.win.title(self.grp.game.type + ' ' + GetVersion() + ' Randomizer - ' + self.grp.game.name)
            self.randoButton["state"]='normal'
            self.update()
        except Exception as e:
            error('Error Opening File', grppath, e)
            self.closeWindow()
            raise
        return True

    def ChooseFile(self):
        self._ChooseFile()
        if not self.isWindowOpen():
            return
        if not self.grp.conSettings.conFiles:
            self.rangeVar.set('Unavailable for this game')
            self.range['state'] = 'disabled'
            self.difficultyVar.set('Unavailable for this game')
            self.difficulty['state'] = 'disabled'


    def _Randomize(self):
        seed = self.seedEntry.get()
        if seed == '':
            seed = random.randint(1, 999999)

        settings = {}

        settings['MapFile.chanceDupeItem'] = {'Few': 0.3, 'Some': 0.5, 'Many': 0.7, 'Extreme': 0.9}[self.enemiesVar.get()]
        settings['MapFile.chanceDeleteItem'] = {'Few': 0.4, 'Some': 0.3, 'Many': 0.1, 'Extreme': 0.1}[self.enemiesVar.get()]

        settings['MapFile.chanceDupeEnemy'] = {'Few': 0.2, 'Some': 0.5, 'Many': 0.6, 'Extreme': 0.9}[self.enemiesVar.get()]
        settings['MapFile.chanceDeleteEnemy'] = {'Few': 0.5, 'Some': 0.3, 'Many': 0.2, 'Extreme': 0.1}[self.enemiesVar.get()]

        unavail = 'Unavailable for this game'
        settings['conFile.range'] = {'Low': 0.5, 'Medium': 1, 'High': 1.5, 'Extreme': 2.0, unavail: 1}[self.rangeVar.get()]
        settings['conFile.scale'] = 1.0
        settings['conFile.difficulty'] = {'Easy': 0.3, 'Medium': 0.5, 'Difficult': 0.7, 'Extreme': 0.9, unavail: 0.5}[self.difficultyVar.get()]

        self.grp.Randomize(seed, settings=settings)
        messagebox.showinfo('Randomization Complete!', 'All done! Seed: ' + str(seed))
        self.closeWindow()

    def Randomize(self):
        try:
            self.randoButton["state"]='disabled'
            self.update()
            self._Randomize()
        except Exception as e:
            error('Error Randomizing', self.grppath, e)
            if self.isWindowOpen():
                self.randoButton["state"]='normal'
            raise


    def newInput(self, cls, label:str, tooltip:str, row:int, *args):
        label = Label(self.win,text=label,width=20,height=2,font=self.font, anchor='e', justify='left')
        label.grid(column=0,row=row, sticky='E')
        if cls == OptionMenu:
            entry = cls(self.win, *args)
        else:
            entry = cls(self.win, *args, width=20,font=self.font)
        entry.grid(column=1,row=row, sticky='W')

        myTip = Hovertip(label, tooltip)
        myTip = Hovertip(entry, tooltip)
        return entry

    def initWindow(self):
        self.win = Tk()
        self.win.protocol("WM_DELETE_WINDOW",self.closeWindow)
        self.win.bind("<Configure>",self.resize)
        self.win.title('Build Engine Randomizer '+GetVersion()+' Settings')
        self.win.geometry(str(self.width)+"x"+str(self.height))
        #self.win.config()
        self.font = font.Font(size=14)

        row=0
        infoLabel = Label(self.win,text='Make sure you have a backup of your game files!',width=40,height=2,font=self.font)
        infoLabel.grid(column=0,row=row,columnspan=2)
        row+=1

        self.seedEntry = self.newInput(Entry, 'Seed: ', 'RNG Seed', row)
        row+=1

        # items add/reduce? maybe combine them into presets so it's simpler to understand
        self.itemsVar = StringVar(self.win, 'Some')
        self.items = self.newInput(OptionMenu, 'Items: ', 'How many items.\n"Some" is a similar amount to vanilla.', row, self.itemsVar, 'Few', 'Some', 'Many', 'Extreme')
        row+=1

        # enemies add/reduce?
        self.enemiesVar = StringVar(self.win, 'Some')
        self.enemies = self.newInput(OptionMenu, 'Enemies: ', 'How many enemies.\n"Some" is a similar amount to vanilla.', row, self.enemiesVar, 'Few', 'Some', 'Many', 'Extreme')
        row+=1

        # values range
        self.rangeVar = StringVar(self.win, 'Medium')
        self.range = self.newInput(OptionMenu, 'Randomization Range: ', 'How wide the range of values can be randomized.\nThis affects the values in CON files.', row, self.rangeVar, 'Low', 'Medium', 'High', 'Extreme')
        row+=1

        # difficulty? values difficulty?
        self.difficultyVar = StringVar(self.win, 'Medium')
        self.difficulty = self.newInput(OptionMenu, 'Difficulty: ', 'Increase the difficulty for more challenge.\nThis affects the values in CON files.', row, self.difficultyVar, 'Easy', 'Medium', 'Difficult', 'Extreme')
        row+=1

        #self.progressbar = Progressbar(self.win, maximum=1)
        #self.progressbar.grid(column=0,row=row,columnspan=2)
        #row+=1

        self.randoButton = Button(self.win,text='Randomize!',width=20,height=2,font=self.font, command=self.Randomize)
        self.randoButton.grid(column=1,row=100, sticky='SE')
        Hovertip(self.randoButton, 'Dew it!')

    def update(self):
        self.win.update()

def main():
    settings = RandoSettings()

def chooseFile(root):
    filetype = (("All Supported Files",("*.grp","STUFF.DAT")), ("GRP File","*.grp"), ("all files","*.*"))
    target = filedialog.askopenfilename(title="Choose a GRP file",filetypes=filetype)
    return target

def error(title, msg, e=None):
    if e:
        msg += '\n' + str(e) + '\n\n' + traceback.format_exc()
    print(title, '\n', msg)
    messagebox.showerror('Error Opening File', msg)
