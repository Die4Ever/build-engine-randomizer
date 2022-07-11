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
        for r in self.conSettings:
            self.regexes.append(re.compile('^'+r+'$'))

    def ShouldRandomizeVar(self, name) -> bool:
        for r in self.regexes:
            if r.match(name):
                return True
        return False

    def RandomizeLine(self, l:str, seed:int, range:float, scale:float) -> str:
        m = defineregex.match(l)
        if not m:
            return l
        name = m.group(1)
        oldval = int(m.group(2))
        theRest = m.group(3)

        if not self.ShouldRandomizeVar(name):
            return l

        rng = random.Random(crc32('define', name, seed))
        r = rng.random() * range + 1
        if rng.random() < 0.5:
            r = 1/r
        r *= scale
        newval = round(oldval * r)
        info(name, oldval, newval, end=', ')
        return 'define '+name+' '+str(newval)+theRest

    def Randomize(self, seed:int, settings:dict):
        # split lines
        range:float = settings['conFile.range']
        scale:float = settings['conFile.scale']
        out = ''
        for l in self.text.splitlines():
            l = l.strip()
            if l.startswith('define '):
                l = self.RandomizeLine(l, seed, range, scale)
            out += l + '\n'
        self.text = out
        info('\n')

    def GetText(self) -> str:
        return self.text
