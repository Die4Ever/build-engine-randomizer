from hashlib import md5
from mmap import mmap, ACCESS_READ

gamesList = {
    'd834055f0c9a60f8f23163b67d086546': 'Ion Fury',
    '22b6938fe767e5cc57d1fe13080cd522': 'Duke Nukem 3D', # Atomic Edition
    '9d200b5fb4ace8797e7f8638c4f96af2': 'Shadow Warrior' # Steam "Classic" version https://store.steampowered.com/app/238070/Shadow_Warrior_Classic_1997/
}

gamesMapSettings = {}

class GameMapSettings:
    def __init__(self, gameName, minMapVersion=7, maxMapVersion=9, swappableItems={}, swappableEnemies={}):
        global gamesMapSettings
        self.gameName = gameName
        self.minMapVersion = minMapVersion
        self.maxMapVersion = maxMapVersion
        self.swappableItems = swappableItems
        self.swappableEnemies = swappableEnemies
        gamesMapSettings[gameName] = self

def GetGame(grppath):
    with open(grppath) as file, mmap(file.fileno(), 0, access=ACCESS_READ) as file:
        md5sum = md5(file).hexdigest()
        print(grppath, md5sum, 'detected game: ', gamesList.get(md5sum))
        # TODO support for unknown games with default settings
        return gamesList.get(md5sum)
    raise Exception('error in GetGame '+grppath)

def GetGameMapSettings(gameName) -> GameMapSettings:
    global gamesMapSettings
    return gamesMapSettings[gameName]

# build these GameMapSettings using this regex find/replace
# define ([\w_]+) (\d+)
# $2: '$1',

GameMapSettings('Ion Fury', minMapVersion=7, maxMapVersion=9,
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

GameMapSettings('Duke Nukem 3D', minMapVersion=7, maxMapVersion=7,
    swappableItems = {
        21: 'FIRSTGUNSPRITE',
        22: 'CHAINGUNSPRITE',
        23: 'RPGSPRITE',
        24: 'FREEZESPRITE',
        25: 'SHRINKERSPRITE',
        26: 'HEAVYHBOMB',
        27: 'TRIPBOMBSPRITE',
        28: 'SHOTGUNSPRITE',
        29: 'DEVISTATORSPRITE',
        30: 'HEALTHBOX',
        31: 'AMMOBOX',
        40: 'AMMO',
        41: 'BATTERYAMMO',
        42: 'DEVISTATORAMMO',
        44: 'RPGAMMO',
        45: 'GROWAMMO',
        46: 'CRYSTALAMMO',
        47: 'HBOMBAMMO',
        48: 'AMMOLOTS',
        49: 'SHOTGUNAMMO',
        51: 'COLA',
        52: 'SIXPAK',
        53: 'FIRSTAID',
        54: 'SHIELD',
        55: 'STEROIDS',
        56: 'AIRTANK',
        57: 'JETPACK',
        # 60: 'ACCESSCARD',
        61: 'BOOTS',
        100: 'ATOMICHEALTH',
        #142: 'NUKEBUTTON',
        1348: 'HOLODUKE'
    },
    swappableEnemies = {}
)

# https://forums.duke4.net/topic/11406-shadow-warrior-scriptset-for-mapster32/
# using find and replace regex on duke3d.def from the above link
# voxel "([^"]+)"\s+\{\s+tile\s+(\d+)\s+\}
# $2: '$1',
GameMapSettings('Shadow Warrior', minMapVersion=7, maxMapVersion=7,
swappableItems = {
    1802: 'medpak.kvx',
    1803: 'medkit.kvx',
    1797: 'uzi.kvx',
    1817: 'grenade.kvx',
    764: 'gunbarl.kvx',
    765: 'camera.kvx',
    1831: '40mmbox.kvx',
    1842: 'mines.kvx',
    1794: 'shotgun.kvx',
    1818: 'rocket.kvx',
    1823: 'shtgammo.kvx',
    1800: 'rcktammo.kvx',
    1813: 'tools.KVX',
    1799: 'uziclip.kvx',
    3031: 'nitevis.kvx',
    1811: 'railgun.kvx',
    1812: 'railpak.kvx',
    3030: 'armor.kvx',
    1793: 'star.kvx',
    1819: 'heat.kvx',
    1792: 'coin.kvx',
    1824: 'heart.kvx',
    1825: 'heart2.kvx',
    1807: 'uziside.kvx',
    1809: 'bomb.kvx',
    1808: 'smoke.kvx',
    1805: 'flash.kvx',
    #1814: 'gorohead.kvx',
    1804: 'shadow.kvx',
    1829: 'caltrop.kvx',
    1810: 'cookie.kvx',
    1766: 'techkey.kvx',
    1765: 'oldkey.kvx',
    # 2520: 'flag1.kvx',
    # 2521: 'flag2.kvx',
    # 2522: 'flag3.kvx',
    # 1767: 'keycard.kvx',
    # 1846: 'oldlock.kvx',
    # 1847: 'oldlock2.kvx',
    # 1850: 'kcrdlck1.kvx',
    # 1851: 'kcrdlck2.kvx',
    # 1852: 'tchklck1.kvx',
    # 1853: 'tchklck2.kvx',
    # 1854: 'tchklck3.kvx',
    # 1769: 'oldkey.kvx',
    # 1773: 'oldkey.kvx',
    # 1777: 'oldkey.kvx',
    # 1770: 'techkey.kvx',
    # 1774: 'techkey.kvx',
    # 1778: 'techkey.kvx',
    # 1771: 'keycard.kvx',
    # 1775: 'keycard.kvx',
    # 1779: 'keycard.kvx',
    817: 'mine.kvx',
    818: 'mine2.kvx',
    819: 'mine3.kvx'
})
# Keys (picnums 1765-1779)