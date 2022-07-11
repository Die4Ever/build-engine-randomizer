from BuildLibs import *
from BuildLibs import games
import re

defineregex = re.compile('^define\s+([^\s]+)\s+(\d+)(.*)$')

class ConFile:
    def __init__(self, game, conSettings, name, text):
        info('\n', name, len(text))
        self.game = game
        self.conSettings = conSettings
        self.name:str = name
        self.text:str = text
        self.regexes = []
        self.difficulties = []
        for r in self.conSettings:
            self.regexes.append(re.compile('^'+r+'$'))
            self.difficulties.append(self.conSettings[r]['difficulty'])

    def ShouldRandomizeVar(self, name) -> float:
        for i in range(len(self.regexes)):
            if self.regexes[i].match(name):
                return self.difficulties[i]
        return None

    def RandomizeLine(self, l:str, seed:int, range:float, scale:float, difficulty:float) -> str:
        m = defineregex.match(l)
        if not m:
            return l
        name = m.group(1)
        oldval = int(m.group(2))
        theRest = m.group(3)

        var_difficulty = self.ShouldRandomizeVar(name)
        if var_difficulty is None:
            return l

        rng = random.Random(crc32('define', name, seed))
        r = rng.random() * range + 1

        if var_difficulty < 0:
            recip_chance = difficulty
        elif var_difficulty > 0:
            recip_chance = 1 - difficulty
        else:
            recip_chance = 0.5

        if rng.random() < recip_chance:
            r = 1/r
        r *= scale
        newval = round(oldval * r)
        info(name, oldval, newval, end=', ')
        return 'define '+name+' '+str(newval)+theRest

    def Randomize(self, seed:int, settings:dict):
        # split lines
        range:float = settings['conFile.range']
        scale:float = settings['conFile.scale']
        difficulty:float = settings['conFile.difficulty']
        out = ''
        for l in self.text.splitlines():
            l = l.strip()
            if l.startswith('define '):
                l = self.RandomizeLine(l, seed, range, scale, difficulty)
            out += l + '\n'
        self.text = out
        info('\n')

    def GetText(self) -> str:
        return self.text
