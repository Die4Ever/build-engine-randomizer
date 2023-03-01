from BuildGames import *

AddGame('Shadow Warrior',                     'Shadow Warrior',         47536148, '7545319F', '9d200b5fb4ace8797e7f8638c4f96af2', '4863226c01d0850c65ac0a3e20831e072b285425', canUseRandomizerFolder=False) # Steam "Classic" version https://store.steampowered.com/app/238070/Shadow_Warrior_Classic_1997/

# https://forums.duke4.net/topic/11406-shadow-warrior-scriptset-for-mapster32/
# using find and replace regex on duke3d.def from the above link
# voxel "([^"]+)"\s+\{\s+tile\s+(\d+)\s+\}
# $2: '$1',
AddMapSettings('Shadow Warrior', minMapVersion=7, maxMapVersion=7,
    swappableItems = {
        1802: SpriteInfo('medpak'),
        1803: SpriteInfo('medkit'),
        1797: SpriteInfo('uzi'),
        1817: SpriteInfo('grenade'),
        764: SpriteInfo('gunbarl'),
        765: SpriteInfo('camera'),
        1831: SpriteInfo('40mmbox'),
        1842: SpriteInfo('mines'),
        1794: SpriteInfo('shotgun'),
        1818: SpriteInfo('rocket'),
        1823: SpriteInfo('shtgammo'),
        1800: SpriteInfo('rcktammo'),
        1813: SpriteInfo('tools'),
        1799: SpriteInfo('uziclip'),
        3031: SpriteInfo('nitevis'),
        1811: SpriteInfo('railgun'),
        1812: SpriteInfo('railpak'),
        3030: SpriteInfo('armor'),
        1793: SpriteInfo('star'),
        1819: SpriteInfo('heat'),
        1792: SpriteInfo('coin'),
        1824: SpriteInfo('heart'),
        1825: SpriteInfo('heart2'),
        1807: SpriteInfo('uziside'),
        1809: SpriteInfo('bomb'),
        1808: SpriteInfo('smoke'),
        1805: SpriteInfo('flash'),
        1814: SpriteInfo('gorohead'),
        1804: SpriteInfo('shadow'),
        1829: SpriteInfo('caltrop'),
        1810: SpriteInfo('cookie'),
        #1766: SpriteInfo('techkey'),
        #1765: SpriteInfo('oldkey'),
        # 2520: SpriteInfo('flag1'),
        # 2521: SpriteInfo('flag2'),
        # 2522: SpriteInfo('flag3'),
        # 1767: SpriteInfo('keycard'),
        # 1846: SpriteInfo('oldlock'),
        # 1847: SpriteInfo('oldlock2'),
        # 1850: SpriteInfo('kcrdlck1'),
        # 1851: SpriteInfo('kcrdlck2'),
        # 1852: SpriteInfo('tchklck1'),
        # 1853: SpriteInfo('tchklck2'),
        # 1854: SpriteInfo('tchklck3'),
        # 1765: SpriteInfo('MASTER_KEY1'),# gold
        # 1769: SpriteInfo('oldkey'),# silver
        # 1773: SpriteInfo('oldkey'),# bronze
        # 1777: SpriteInfo('oldkey'),# red
        # 1770: SpriteInfo('techkey'),
        # 1774: SpriteInfo('techkey'),
        # 1778: SpriteInfo('techkey'),
        # 1771: SpriteInfo('keycard'),
        # 1775: SpriteInfo('keycard'),
        # 1779: SpriteInfo('keycard'),
        817: SpriteInfo('mine'),
        818: SpriteInfo('mine2'),
        819: SpriteInfo('mine3'),
        #2470: 'EXIT_SWITCH'
    },
    swappableEnemies = {
        4096: SpriteInfo('EVIL_NINJA'),
        4162: SpriteInfo('EVIL_NINJA_CROUCHING'),
        4320: SpriteInfo('BIG_RIPPER'),
        1400: SpriteInfo('COOLIE'),
        1441: SpriteInfo('COOLIE_GHOST'),
        1469: SpriteInfo('GREEN_GUARDIAN'),
        5162: SpriteInfo('FEMALE_WARRIOR'),
        1580: SpriteInfo('LITTLE_RIPPER'),
        #3780: SpriteInfo('FISH'),
        800: SpriteInfo('HORNET'),
    },
    addableEnemies = [4096, 4320, 1400, 1441, 1469, 5162, 1580, 800,],
    triggers={},
    bosses={
        1210: SpriteInfo('SUMO_BOSS'),
        1300: SpriteInfo('SERPENT_BOSS'),
        5426: SpriteInfo('ZILLA_BOSS')
    }
)
# Keys (picnums 1765-1779)
# Locks 1846-1854

AddGameSettings('Shadow Warrior',
commands = dict( # https://voidpoint.io/terminx/eduke32/-/blob/master/source/duke3d/src/cmdline.cpp#L39
    grp={'voidsw.exe': '-nosetup -g'},
    folder={'voidsw.exe': '-nosetup -j '},
    simple={}
))
