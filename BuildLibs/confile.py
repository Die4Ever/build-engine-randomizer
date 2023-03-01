from BuildLibs import *
import BuildGames
from pathlib import Path
import re

defineregex = re.compile('^define\s+([^\s]+)\s+(\d+)(.*)$')

class ConFile:
    def __init__(self, game, conSettings, name, text):
        info('\n', name, len(text))
        self.game = game
        self.conSettings:dict = conSettings
        self.name:str = name
        self.text:str = text
        for v in self.conSettings:
            r = re.compile('^'+v['regexstr']+'$')
            v['regex'] = r

    def GetVarSettings(self, name) -> Union[None,dict]:
        for v in self.conSettings:
            if v['regex'].match(name):
                return v
        return None

    def RandomizeLine(self, l:str, seed:int, range:float, balance_scale:float, difficulty:float) -> str:
        m = defineregex.match(l)
        if not m:
            return l
        name = m.group(1)
        oldval = int(m.group(2))
        theRest = m.group(3)

        var_settings:dict = self.GetVarSettings(name)
        if var_settings is None:
            return l
        var_difficulty = var_settings.get('difficulty', 0)

        rng = random.Random(crc32('define', name, seed))
        range *= var_settings.get('range', 1)
        r = rng.random() * range + 1

        if var_difficulty < 0:
            recip_chance = difficulty
        elif var_difficulty > 0:
            recip_chance = 1 - difficulty
        else:
            recip_chance = 0.5

        if rng.random() < recip_chance:
            r = 1/r
        r *= balance_scale * var_settings.get('balance', 1)
        newval = round(oldval * r)
        self.spoilerlog.Change(name, oldval, newval)
        return 'define '+name+' '+str(newval)+theRest

    def Randomize(self, seed:int, settings:dict, spoilerlog):
        try:
            spoilerlog.SetFilename(Path(self.name))
            self.spoilerlog = spoilerlog
            self._Randomize(seed, settings)
        finally:
            self.spoilerlog = None
            spoilerlog.FinishRandomizingFile()

    def _Randomize(self, seed:int, settings:dict):
        # split lines
        range:float = settings['conFile.range']
        scale:float = settings['conFile.scale']
        difficulty:float = settings['conFile.difficulty']
        out = ''
        for l in self.text.splitlines():
            l = l.strip()
            if l.startswith('define '):
                l = self.RandomizeLine(l, seed, range, scale, difficulty)
            out += l + '\r\n'
        self.text = out
        info('\n')

    def GetText(self) -> str:
        return self.text
