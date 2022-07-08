from hashlib import md5
from mmap import mmap, ACCESS_READ

gamesList = {
    'd834055f0c9a60f8f23163b67d086546': 'Ion Fury'
}

gamesMapSettings = {}

class GameMapSettings:
    def __init__(self, gameName, mapVersion, swappableItems, swappableEnemies):
        self.gameName = gameName
        self.mapVersion = mapVersion
        self.swappableItems = swappableItems
        self.swappableEnemies = swappableEnemies

gamesMapSettings['Ion Fury'] = GameMapSettings('Ion Fury', mapVersion=9,
    swappableItems = {
        209: 'I_BATON',
        210: 'I_LOVERBOY',
        211: 'I_LOVERBOY_AMMO',
        212: 'I_MEDPACK',
        213: 'I_MEDICOMP',
        214: 'I_MEDKIT',
        215: 'I_BULLETVEST',
        216: 'I_ARMORVEST',
        #217: 'I_ACCESSCARD',
        218: 'I_MINIGUN_AMMO',
        219: 'I_PLASMACROSSBOW_AMMO',
        220: 'I_PLASMACROSSBOW',
        221: 'I_MINIGUN',
        222: 'I_CLUSTERPUCK',
        223: 'I_TECHVEST',
        224: 'I_SHOTGUN',
        225: 'I_SHOTGUN_AMMO',
        226: 'I_GRENADELAUNCHER_AMMO',
        227: 'I_SMG_AMMO',
        228: 'I_ARMOR_SHARD',
        229: 'I_LOVERBOY_AMMO2',
        230: 'I_SMG',
        231: 'I_GRENADELAUNCHER',
        232: 'I_BOWLINGBOMB_PICKUP',
        233: 'I_SYRINGE',
        240: 'I_HAZARDSUIT',
        241: 'I_BOMBRUSH',
        242: 'I_RADAR',
        243: 'I_DKSHOES',
        244: 'I_DAMAGEBOOSTER',
        6800: 'I_BOWLINGBOMB',
        9930: 'I_PIZZA_6',
        9931: 'I_PIZZA_5',
        9932: 'I_PIZZA_4',
        9933: 'I_PIZZA_3',
        9934: 'I_PIZZA_2',
        9935: 'I_PIZZA_1',
        9003: 'I_SODA',
        9002: 'I_SODA_STAND',
        320: 'I_AMMOCRATE'
    },
    swappableEnemies = {}
)

def GetGame(grppath):
    with open(grppath) as file, mmap(file.fileno(), 0, access=ACCESS_READ) as file:
        md5sum = md5(file).hexdigest()
        print(grppath, md5sum, 'detected game: ', gamesList.get(md5sum))
        # TODO support for unknown games with default settings
        return gamesList[md5sum]
    return None

def GetGameMapSettings(gameName) -> GameMapSettings:
    return gamesMapSettings[gameName]
