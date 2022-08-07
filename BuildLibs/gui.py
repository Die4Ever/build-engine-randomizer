from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
import webbrowser
from idlelib.tooltip import Hovertip
from BuildLibs import GetVersion
from BuildLibs.grp import *


# from https://stackoverflow.com/a/68701602
class ScrollableFrame:
    """
    # How to use class
    from tkinter import *
    obj = ScrollableFrame(master,height=300 # Total required height of canvas,width=400 # Total width of master)
    objframe = obj.frame
    # use objframe as the main window to make widget
    """
    def __init__ (self,master,width,height,mousescroll=0):
        self.mousescroll = mousescroll
        self.master = master
        self.height = height
        self.width = width
        self.main_frame = Frame(self.master)
        self.main_frame.pack(fill=BOTH,expand=1)

        self.scrollbar = Scrollbar(self.main_frame, orient=VERTICAL)
        self.scrollbar.pack(side=RIGHT,fill=Y)

        self.canvas = Canvas(self.main_frame,yscrollcommand=self.scrollbar.set)
        self.canvas.pack(expand=True,fill=BOTH)

        self.scrollbar.config(command=self.canvas.yview)

        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion = self.canvas.bbox("all")))

        self.frame = Frame(self.canvas,width=self.width,height=self.height)
        self.frame.pack(expand=True,fill=BOTH)
        self.canvas.create_window((0,0), window=self.frame, anchor="nw")

        self.frame.bind("<Enter>", self.entered)
        self.frame.bind("<Leave>", self.left)

    def _on_mouse_wheel(self,event):
        self.canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    def entered(self,event):
        if self.mousescroll:
            self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def left(self,event):
        if self.mousescroll:
            self.canvas.unbind_all("<MouseWheel>")

class RandoSettings:
    def __init__(self):
        self.width=480
        self.height=500
        self.initWindow()
        self.ChooseFile()
        if self.root:
            self.root.mainloop()

    def closeWindow(self):
        self.root.destroy()
        self.root=None

    def isWindowOpen(self) -> bool:
        return self.root!=None

    def resize(self,event):
        if event.widget == self.root:
            try:
                trace('resize', event.width, event.height)
                self.width = event.width
                self.height = event.height
            except Exception as e:
                error('ERROR: in resize:', e)

    def _ChooseFile(self):
        grppath = ''
        try:
            self.randoButton["state"]='disabled'
            self.update()
            grppath = chooseFile(self.root)
            if grppath == '':
                warning('no file selected!')
                self.closeWindow()
                return True

            self.grppath = grppath
            self.root.title('Loading '+grppath+'...')
            self.update()
            self.grp: GrpBase = LoadGrpFile(grppath)

            self.root.title(self.grp.game.type + ' ' + GetVersion() + ' Randomizer - ' + self.grp.game.name)
            self.randoButton["state"]='normal'
            self.update()
        except Exception as e:
            errordialog('Error Opening File', grppath, e)
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
        if not self.grp.mapSettings.addableEnemies:
            self.enemyVarietyVar.set('Unavailable for this game')
            self.enemyVariety['state'] = 'disabled'
        if self.grp.game.useRandomizerFolder:
            self.randomizerFolderVar.set('Enabled')
        else:
            self.randomizerFolderVar.set('Disabled')
        if self.grp.game.externalFiles:
            self.randomizerFolder['state'] = 'disabled'
        else:
            self.randomizerFolder['state'] = 'normal'

    def ReadSettings(self):
        settings = {}
        seed = self.seedEntry.get()
        if seed == '':
            seed = random.randint(1, 999999)
        settings['seed'] = seed

        unavail = 'Unavailable for this game'
        enabled = {'Disabled': False, 'Enabled': True, 'Unavailable for this game': False}

        settings['MapFile.chanceDupeItem'] = {'Few': 0.4, 'Some': 0.55, 'Many': 0.7, 'Extreme': 0.9}[self.itemsVar.get()]
        settings['MapFile.chanceDeleteItem'] = {'Few': 0.4, 'Some': 0.25, 'Many': 0.15, 'Extreme': 0.1}[self.itemsVar.get()]

        settings['MapFile.chanceDupeEnemy'] = {'Few': 0.4, 'Some': 0.55, 'Many': 0.6, 'Impossible': 0.75}[self.enemiesVar.get()]
        settings['MapFile.chanceDeleteEnemy'] = {'Few': 0.4, 'Some': 0.25, 'Many': 0.2, 'Impossible': 0.15}[self.enemiesVar.get()]

        settings['MapFile.itemVariety'] = {'Normal': 0, 'Increased': 0.2, 'Extreme': 0.5, unavail: 0}[self.itemVarietyVar.get()]
        settings['MapFile.enemyVariety'] = {'Normal': 0, 'Increased': 0.2, 'Extreme': 0.5, unavail: 0}[self.enemyVarietyVar.get()]

        settings['conFile.range'] = {'Low': 0.5, 'Medium': 1, 'High': 1.3, 'Extreme': 1.6, unavail: 1}[self.rangeVar.get()]
        settings['conFile.scale'] = 1.0
        settings['conFile.difficulty'] = {'Easy': 0.2, 'Medium': 0.4, 'Difficult': 0.6, 'Impossible': 0.75, unavail: 0.4}[self.difficultyVar.get()]

        settings['grp.reorderMaps'] = {**enabled, 'Restricted': 'restricted'}[self.reorderMapsVar.get()]
        settings['useRandomizerFolder'] = enabled[self.randomizerFolderVar.get()]
        self.grp.game.useRandomizerFolder = settings['useRandomizerFolder']
        return settings

    def _Randomize(self, settings):
        seed = settings['seed']
        self.grp.Randomize(seed, settings=settings)
        messagebox.showinfo('Randomization Complete!', 'All done! Seed: ' + str(seed))
        self.closeWindow()

    def WarnOverwrites(self) -> bool:
        deleting = self.grp.GetDeleteFolders(self.grp.GetOutputPath())
        deletingstrs = []
        for d in deleting:
            deletingstrs.append(str(d))
        return messagebox.askokcancel(
            title='Will DELETE files!',
            message='This may take a minute.\nWILL DELETE/OVERWRITE THE FOLLOWING:\n'
            + '\n'.join(deletingstrs)
        )

    def Randomize(self):
        try:
            self.randoButton["state"]='disabled'
            self.update()
            settings = self.ReadSettings()

            if not self.WarnOverwrites():
                info('Declined overwrite warning, not randomizing')
                if self.isWindowOpen():
                    self.randoButton["state"]='normal'
                return

            self._Randomize(settings)
        except Exception as e:
            errordialog('Error Randomizing', self.grppath, e)
            if self.isWindowOpen():
                self.randoButton["state"]='normal'
            raise


    def newInput(self, cls, label:str, tooltip:str, row:int, *args, **kargs):
        label = Label(self.win,text=label,width=22,height=2,font=self.font, anchor='e', justify='left')
        label.grid(column=0,row=row, sticky='E')
        if cls == OptionMenu:
            entry = cls(self.win, *args, **kargs)
        else:
            entry = cls(self.win, *args, width=18,font=self.font, **kargs)
        entry.grid(column=1,row=row, sticky='W')

        myTip = Hovertip(label, tooltip)
        myTip = Hovertip(entry, tooltip)
        return entry

    def initWindow(self):
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW",self.closeWindow)
        self.root.bind("<Configure>",self.resize)
        self.root.title('Build Engine Randomizer ' + GetVersion()+' Settings')
        self.root.geometry(str(self.width)+"x"+str(self.height))

        scroll = ScrollableFrame(self.root, width=self.width, height=self.height, mousescroll=1)
        self.win = scroll.frame
        #self.win.config()
        self.font = font.Font(size=14)
        self.linkfont = font.Font(size=12, underline=True)

        row=0
        infoLabel = Label(self.win,text='Make sure you have a backup of your game files!\nRandomizer might overwrite files\ninside the game directory.',width=40,height=4,font=self.font)
        infoLabel.grid(column=0,row=row,columnspan=2,rowspan=1)
        row+=1

        self.seedVar = StringVar(self.win, random.randint(1, 999999))
        self.seedEntry:Entry = self.newInput(Entry, 'Seed: ', 'RNG Seed. Each seed is a different game!\nLeave blank for a random seed.', row, textvariable=self.seedVar)
        row+=1

        # items add/reduce? maybe combine them into presets so it's simpler to understand
        self.itemsVar = StringVar(self.win, 'Some')
        items:OptionMenu = self.newInput(OptionMenu, 'Items: ', 'How many items.\n"Some" is a similar amount to vanilla.', row, self.itemsVar, 'Few', 'Some', 'Many', 'Extreme')
        row+=1

        # enemies add/reduce?
        self.enemiesVar = StringVar(self.win, 'Some')
        enemies:OptionMenu = self.newInput(OptionMenu, 'Enemies: ', 'How many enemies.\n"Some" is a similar amount to vanilla.', row, self.enemiesVar, 'Few', 'Some', 'Many', 'Impossible')
        row+=1

        # values range
        self.rangeVar = StringVar(self.win, 'Medium')
        self.range:OptionMenu = self.newInput(OptionMenu, 'Randomization Range: ', 'How wide the range of values can be randomized.\nThis affects the values in CON files.', row, self.rangeVar, 'Low', 'Medium', 'High', 'Extreme')
        row+=1

        # difficulty? values difficulty?
        self.difficultyVar = StringVar(self.win, 'Medium')
        self.difficulty:OptionMenu = self.newInput(OptionMenu, 'Difficulty: ', 'Increase the difficulty for more challenge.\nThis affects the values in CON files.', row, self.difficultyVar, 'Easy', 'Medium', 'Difficult', 'Impossible')
        row+=1

        self.itemVarietyVar = StringVar(self.win, 'Normal')
        self.itemVariety:OptionMenu = self.newInput(OptionMenu, 'Item Variety: ', 'Chance to add items that shouldn\'t be on the map.', row, self.itemVarietyVar, 'Normal', 'Increased', 'Extreme')
        row+=1

        self.enemyVarietyVar = StringVar(self.win, 'Normal')
        self.enemyVariety:OptionMenu = self.newInput(OptionMenu, 'Enemy Variety: ', 'Chance to add enemies that shouldn\'t be on the map.\nThis can create difficult situations.', row, self.enemyVarietyVar, 'Normal', 'Increased', 'Extreme')
        row+=1

        self.reorderMapsVar = StringVar(self.win, 'Disabled')
        reorderMaps:OptionMenu = self.newInput(OptionMenu, 'Reorder Maps: ', 'Shuffle the order of the maps.', row, self.reorderMapsVar, 'Disabled', 'Restricted', 'Enabled')
        row+=1

        # TODO: option to enable/disable loading external files?

        self.randomizerFolderVar = StringVar(self.win, '')
        self.randomizerFolder:OptionMenu = self.newInput(OptionMenu, 'Use Randomizer Folder: ', 'Put randomized files inside Randomizer folder.\nWorks great with EDuke32, doesn\'t work with voidsw or Ion Fury.\nJust use the default setting.', row, self.randomizerFolderVar, 'Disabled', 'Enabled')
        row+=1

        #self.progressbar = Progressbar(self.win, maximum=1)
        #self.progressbar.grid(column=0,row=row,columnspan=2)
        #row+=1

        discordLink = Label(self.win,text='discord.gg/QwjnYWhKsY',width=22,height=2,font=self.linkfont, fg="Blue", cursor="hand2")
        discordLink.bind('<Button-1>', lambda *args: webbrowser.open_new('https://discord.gg/QwjnYWhKsY'))
        discordLink.grid(column=0,row=100)
        myTip = Hovertip(discordLink, 'Join our Discord!')

        self.randoButton = Button(self.win,text='Randomize!',width=18,height=2,font=self.font, command=self.Randomize)
        self.randoButton.grid(column=1,row=100, sticky='SE')
        Hovertip(self.randoButton, 'Dew it!')

    def update(self):
        self.root.update()

def main():
    settings = RandoSettings()

def chooseFile(root):
    filetype = (("All Supported Files",("*.grp","STUFF.DAT",'*.rff')), ("GRP Files","*.grp"), ('RFF Files','*.rff'), ('DAT Files', '*.DAT'), ("All Files","*.*"))
    target = filedialog.askopenfilename(title="Choose a GRP file",filetypes=filetype)
    return target

def errordialog(title, msg, e=None):
    if e:
        msg += '\n' + str(e) + '\n\n' + traceback.format_exc()
    error(title, '\n', msg)
    messagebox.showerror(title, msg)
