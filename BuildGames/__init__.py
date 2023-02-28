import binascii
import os
from hashlib import md5, sha1
from mmap import mmap, ACCESS_READ
from BuildLibs import *
from pathlib import Path

gamesList = {}
gamesMapSettings = {}
gamesConSettings = {}

class GameInfo():
    def __init__(self, name='', type='', size:int=0, crc:str='', md5:str='', sha1:str='', externalFiles:bool=False, canUseRandomizerFolder=True, canUseGrpFile=False, **kargs):
        self.name = name
        self.type = type
        self.size = size
        self.md5 = md5.lower()
        self.crc = 0
        if crc:
            self.crc = int(crc, 16)
        self.sha1 = sha1.lower()
        self.externalFiles = externalFiles
        self.canUseRandomizerFolder = canUseRandomizerFolder
        self.canUseGrpFile = canUseGrpFile
        # can't use external files without also using the randomizer folder, otherwise we're reading from the same files we're writing to
        assert not (self.externalFiles and not self.canUseRandomizerFolder)

    def __repr__(self):
        return repr(self.__dict__)

    def copy(self) -> 'GameInfo':
        return copyobj(self)


def AddGame(*args, **kargs) -> GameInfo:
    """
        https://wiki.eduke32.com/wiki/Frequently_Asked_Questions
        ^(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)$
        AddGame('$1', '', $2, '$4', '$5', '$6') # $1
        (\d),(\d)
        $1$2
        idk what an SSI file is, but their sizes seem comparable to the GRP files
    """

    global gamesList
    game = GameInfo(*args, **kargs)
    if 'allowOverwrite' not in {**kargs}:
        assert game.crc not in gamesList, repr(game.__dict__)
    gamesList[game.crc] = game
    return game

class GameMapSettings:
    def __init__(self, gameName=None, minMapVersion=7, maxMapVersion=9, idType:str='picnum',
            swappableItems:dict={}, swappableEnemies:dict={}, addableEnemies:list=[],
            triggers:dict={}, additions:dict={}, reorderMapsBlacklist:list=[], **kargs):
        self.gameName = gameName
        self.minMapVersion = minMapVersion
        self.maxMapVersion = maxMapVersion
        self.idType = idType

        if idType == 'lowtag':
            self.swappableItems = {v[idType]: {'picnum':k, **v} for(k,v) in swappableItems.items()}
            self.swappableEnemies = {v[idType]: {'picnum':k, **v} for(k,v) in swappableEnemies.items()}
        elif idType == 'picnum':
            self.swappableItems = swappableItems
            self.swappableEnemies = swappableEnemies
        else:
            raise Exception('unknown idType: '+repr(idType))

        assert len(self.swappableItems) == len(swappableItems)
        assert len(self.swappableEnemies) == len(swappableEnemies)

        self.addableEnemies = addableEnemies
        self.triggers = triggers
        self.additions = additions
        self.reorderMapsBlacklist = reorderMapsBlacklist
        self.__dict__.update(kargs)

    def __repr__(self):
        return repr(self.__dict__)

    def copy(self) -> 'GameMapSettings':
        return copyobj(self)

def AddMapSettings(*args, **kargs) -> GameMapSettings:
    """
        build GameMapSettings using this regex find/replace
        define ([\w_]+) (\d+)
        $2: '$1',
    """
    global gamesMapSettings
    gms: GameMapSettings = GameMapSettings(*args, **kargs)
    assert gms.gameName not in gamesMapSettings, repr(gms.__dict__)
    gamesMapSettings[gms.gameName] = gms
    return gms

class GameConSettings:
    def __init__(self, gameName: Union[None,str]=None, mainScript: Union[None,str]=None, flags: int=0, defName: Union[None,str]=None, conFiles: dict={}):
        self.gameName = gameName
        self.mainScript = mainScript
        self.flags = flags
        self.defName = defName
        self.conFiles = conFiles

    def __repr__(self):
        return repr(self.__dict__)

    def copy(self) -> 'GameConSettings':
        return copyobj(self)

# difficulty > 0 means higher number makes the game harder
def AddConSettings(*args, **kargs) -> GameConSettings:
    global gamesConSettings
    gcs: GameConSettings = GameConSettings(*args, **kargs)
    assert gcs.gameName not in gamesConSettings, repr(gcs.__dict__)
    gamesConSettings[gcs.gameName] = gcs
    return gcs

def GetGame(grppath:Path) -> GameInfo:
    global gamesList
    size = os.path.getsize(grppath)
    with open(grppath) as file, mmap(file.fileno(), 0, access=ACCESS_READ) as file:
        crc:int = binascii.crc32(file)
        g:GameInfo = gamesList.get(crc)
        if g:
            if not g.size:
                g.size = size
            if not g.md5:
                g.md5 = md5(file).hexdigest()
            if not g.sha1:
                g.sha1 = sha1(file).hexdigest()
            info('matched game:', repr(g))
            return g.copy()
        md5sum:str = md5(file).hexdigest()
        sha:str = sha1(file).hexdigest()
        error('ERROR: in GetGame, unknown game', grppath, 'size:', size, 'crc32:', "0x{:X}".format(crc), 'md5:', md5sum, 'sha1:', sha, sep=', ')
        # TODO support for unknown games with default settings, for now return dummy game
        return GameInfo('Unknown Game')
    raise Exception('error in GetGame', grppath)

def GetGameMapSettings(game: GameInfo) -> GameMapSettings:
    global gamesMapSettings
    g:GameMapSettings = gamesMapSettings[game.type]
    return g.copy()

def GetGameConSettings(game: GameInfo) -> GameConSettings:
    global gamesConSettings
    g:GameConSettings = gamesConSettings.get(game.type, GameConSettings())
    return g.copy()

def SpriteInfo(name:str, category:str='', lowtag:int=0, xrepeat:int=0, yrepeat:int=0, palettes=None) -> dict:
    d = dict(name=name, category=category)
    if lowtag:
        d['lowtag'] = lowtag
    if xrepeat:
        d['xrepeat'] = xrepeat
        d['yrepeat'] = yrepeat
    if palettes:
        d['palettes'] = palettes
    return d

def SpriteRange(min:int, max:int, value:dict):
    d={}
    for i in range(min,max+1):
        d[i] = value
    return d

def ConVar(regex:str, difficulty:float=0, range:float=1, balance:float=1) -> dict:
    return { 'regexstr': regex, 'difficulty': difficulty, 'range': range, 'balance': balance }

from BuildGames import Blood, Duke3d, IonFury, OtherGames, PowerSlave, ShadowWarrior
