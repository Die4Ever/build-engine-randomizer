import webbrowser
from BuildLibs import GetVersion
from BuildLibs.grp import *
from GUI import *

unavail = 'Unavailable for this game'
enabledOptions = {'Disabled': False, 'Enabled': True, unavail: False}
chanceDupeItem = {'Few': 0.4, 'Some': 0.55, 'Many': 0.7, 'Extreme': 0.9}
chanceDeleteItem = {'Few': 0.4, 'Some': 0.25, 'Many': 0.15, 'Extreme': 0.1}
chanceDupeEnemy = {'Few': 0.4, 'Some': 0.55, 'Many': 0.6, 'Impossible': 0.75}
chanceDeleteEnemy = {'Few': 0.4, 'Some': 0.25, 'Many': 0.2, 'Impossible': 0.15}
spriteVariety = {'Normal': 0, 'Increased': 0.2, 'Extreme': 0.5, unavail: 0}
rangeOptions = {'Low': 0.5, 'Medium': 1, 'High': 1.3, 'Extreme': 1.6, unavail: 1}
difficultyOptions = {'Easy': 0.2, 'Medium': 0.4, 'Difficult': 0.6, 'Impossible': 0.75, unavail: 0.4}
reorderMapsOptions = {**enabledOptions, 'Restricted': 'restricted'}
outputMethodOptions = {'GRP File': 'grp', 'Randomizer Folder': 'folder', 'Simple': 'simple'}

def OptionsList(ops:dict):
    ops = ops.copy()
    ops.pop(unavail, None)
    return ops.keys()

class RandoSettings(GUIBase):
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
        if not self.grp.gameSettings.conFiles:
            self.rangeVar.set(unavail)
            self.range['state'] = 'disabled'
            self.difficultyVar.set(unavail)
            self.difficulty['state'] = 'disabled'
        if not self.grp.mapSettings.addableEnemies:
            self.enemyVarietyVar.set(unavail)
            self.enemyVariety['state'] = 'disabled'

        if self.grp.game.canUseGrpFile:
            self.outputMethodVar.set('GRP File')
        elif self.grp.game.canUseRandomizerFolder:
            self.outputMethodVar.set('Randomizer Folder')
        else:
            self.outputMethodVar.set('Simple')

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

        settings['MapFile.chanceDupeItem'] = chanceDupeItem[self.itemsVar.get()]
        settings['MapFile.chanceDeleteItem'] = chanceDeleteItem[self.itemsVar.get()]

        settings['MapFile.chanceDupeEnemy'] = chanceDupeEnemy[self.enemiesVar.get()]
        settings['MapFile.chanceDeleteEnemy'] = chanceDeleteEnemy[self.enemiesVar.get()]

        settings['MapFile.itemVariety'] = spriteVariety[self.itemVarietyVar.get()]
        settings['MapFile.enemyVariety'] = spriteVariety[self.enemyVarietyVar.get()]

        settings['conFile.range'] = rangeOptions[self.rangeVar.get()]
        settings['conFile.scale'] = 1.0
        settings['conFile.difficulty'] = difficultyOptions[self.difficultyVar.get()]

        settings['grp.reorderMaps'] = reorderMapsOptions[self.reorderMapsVar.get()]
        settings['outputMethod'] = outputMethodOptions[self.outputMethodVar.get()]
        return settings

    def _Randomize(self, settings):
        seed = settings['seed']
        self.grp.Randomize(seed, settings=settings, progressCallback=self.ProgressCallback)
        spoilerpath = self.grp.spoilerlogpath.absolute()
        batpath = self.grp.batpath
        dialogtext = 'All done! Seed: ' + str(seed)
        dialogtext += '\n\nTo see all the changes made, check out:\n\n'+str(spoilerpath)
        if batpath:
            batpath = batpath.absolute()
            dialogtext += '\n\nTo play, run:\n\n'+str(batpath)
        elif os.name == 'nt':
            dialogtext += '\n\nUnable to automatically create bat file. You may be using an untested source port or output method combination. Please report this on GitHub, Discord, or message me.'

        messagebox.showinfo('Randomization Complete!', dialogtext)
        self.closeWindow()

    def ProgressCallback(self, mapname, maps, status):
        num = len(maps)
        i = maps.index(mapname)
        i += status
        percent = int(i/num * 100)
        text = 'Randomizing '+str(percent)+'%'
        self.root.title(text + ': '+mapname)
        self.randoButton['text'] = text
        self.update()

    def WarnOverwrites(self, settings) -> bool:
        outputMethod = settings['outputMethod']
        deleting = self.grp.GetDeletes(None, outputMethod)
        deletingstrs = []
        d : Path
        maps = {}
        for d in deleting:
            s = str(d.absolute())
            if s.lower().endswith('.map'):
                key = str(Path(d.absolute().parent, '*.map'))
                maps[key] = maps.get(key, 0) + 1
            else:
                deletingstrs.append(s)
        for (k,v) in maps.items():
                deletingstrs.append(k + ' (' + str(v) + ' map files)')

        return messagebox.askokcancel(
            title='Will DELETE files!',
            message='This may take a minute.\nWILL DELETE/OVERWRITE THE FOLLOWING:\n\n'
            + '\n\n'.join(deletingstrs)
        )

    def Randomize(self):
        try:
            self.randoButton["state"]='disabled'
            self.update()
            settings = self.ReadSettings()

            if not self.WarnOverwrites(settings):
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
        infoLabel = Label(self.win,
            text='Make sure you have a backup of your game files!\nRandomizer might overwrite files\ninside the game directory.',
            width=40,height=4,font=self.font
        )
        infoLabel.grid(column=0,row=row,columnspan=2,rowspan=1)
        row+=1

        self.seedVar = StringVar(self.win, random.randint(1, 999999))
        self.seedEntry:Entry = self.newInput(Entry, 'Seed: ',
            'RNG Seed. Each seed is a different game!\nLeave blank for a random seed.',
            row, textvariable=self.seedVar
        )
        row+=1

        # items add/reduce? maybe combine them into presets so it's simpler to understand
        self.itemsVar = StringVar(self.win, 'Some')
        items:OptionMenu = self.newInput(OptionMenu, 'Items: ', 'How many items.\n"Some" is a similar amount to vanilla.',
            row, self.itemsVar, *OptionsList(chanceDupeItem)
        )
        row+=1

        # enemies add/reduce?
        self.enemiesVar = StringVar(self.win, 'Some')
        enemies:OptionMenu = self.newInput(OptionMenu, 'Enemies: ', 'How many enemies.\n"Some" is a similar amount to vanilla.',
            row, self.enemiesVar, *OptionsList(chanceDupeEnemy)
        )
        row+=1

        # values range
        self.rangeVar = StringVar(self.win, 'Medium')
        self.range:OptionMenu = self.newInput(OptionMenu, 'Randomization Range: ',
            'How wide the range of values can be randomized.\nThis affects the values in CON files.',
            row, self.rangeVar, *OptionsList(rangeOptions)
        )
        row+=1

        # difficulty? values difficulty?
        self.difficultyVar = StringVar(self.win, 'Medium')
        self.difficulty:OptionMenu = self.newInput(OptionMenu, 'Difficulty: ',
            'Increase the difficulty for more challenge.\nThis affects the values in CON files.',
            row, self.difficultyVar, *OptionsList(difficultyOptions)
        )
        row+=1

        self.itemVarietyVar = StringVar(self.win, 'Increased')
        self.itemVariety:OptionMenu = self.newInput(OptionMenu, 'Item Variety: ',
            'Chance to add items that shouldn\'t be on the map.',
            row, self.itemVarietyVar, *OptionsList(spriteVariety)
        )
        row+=1

        self.enemyVarietyVar = StringVar(self.win, 'Increased')
        self.enemyVariety:OptionMenu = self.newInput(OptionMenu, 'Enemy Variety: ',
            'Chance to add enemies that shouldn\'t be on the map.\nThis can create difficult situations.',
            row, self.enemyVarietyVar, *OptionsList(spriteVariety)
        )
        row+=1

        self.reorderMapsVar = StringVar(self.win, 'Disabled')
        reorderMaps:OptionMenu = self.newInput(OptionMenu, 'Reorder Maps: ',
            'Shuffle the order of the maps.',
            row, self.reorderMapsVar, *OptionsList(reorderMapsOptions)
        )
        row+=1

        # TODO: option to enable/disable loading external files?

        self.outputMethodVar = StringVar(self.win, 'GRP File')
        self.randomizerFolder:OptionMenu = self.newInput(OptionMenu, 'Output Method: ',
            'GRP File: Usually the preferred method.\nRandomizer Folder: Works great with EDuke32, doesn\'t work with voidsw or Ion Fury.\nSimple: Just put the files in the game folder.\nUsually just use the default setting.',
            row, self.outputMethodVar, *OptionsList(outputMethodOptions)
        )
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

        self.ChooseFile()

    def update(self):
        self.root.update()

def main():
    settings = RandoSettings()

def chooseFile(root):
    filetype = (("All Supported Files",("*.grp","STUFF.DAT",'*.rff')), ("GRP Files","*.grp"), ('RFF Files','*.rff'), ('DAT Files', '*.DAT'), ("All Files","*.*"))
    target = filedialog.askopenfilename(title="Choose a GRP file",filetypes=filetype)
    return target
