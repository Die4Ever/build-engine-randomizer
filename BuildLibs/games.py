import binascii
import os
from hashlib import md5, sha1
from mmap import mmap, ACCESS_READ

from BuildLibs import copyobj, crc32

gamesList = {}
gamesMapSettings = {}
gamesConSettings = {}

class Game():
    def __init__(self, name, type, size:int=0, crc:str='', md5:str='', sha1:str=''):
        global gamesList
        self.name = name
        self.type = type
        self.md5 = md5.lower()
        self.crc = 0
        if crc:
            self.crc = int(crc, 16)
        self.sha1 = sha1.lower()
        gamesList[self.crc] = self

    def __repr__(self):
        return repr(self.__dict__)

class GameMapSettings:
    def __init__(self, gameName=None, minMapVersion=7, maxMapVersion=9, swappableItems={}, swappableEnemies={}):
        global gamesMapSettings
        self.gameName = gameName
        self.minMapVersion = minMapVersion
        self.maxMapVersion = maxMapVersion
        self.swappableItems = swappableItems
        self.swappableEnemies = swappableEnemies
        if gameName:
            gamesMapSettings[gameName] = self

    def __repr__(self):
        return repr(self.__dict__)

    def copy(self) -> 'GameMapSettings':
        return copyobj(self)

class GameConSettings:
    def __init__(self, gameName=None, conFiles={}):
        self.gameName = gameName
        self.conFiles = conFiles
        if gameName:
            gamesConSettings[gameName] = self

    def copy(self) -> 'GameConSettings':
        return copyobj(self)

def GetGame(grppath) -> Game:
    global gamesList
    size = os.path.getsize(grppath)
    with open(grppath) as file, mmap(file.fileno(), 0, access=ACCESS_READ) as file:
        crc:int = binascii.crc32(file)
        g:Game = gamesList.get(crc)
        if g:
            print('matched game:', repr(g))
            return g
        md5sum:str = md5(file).hexdigest()
        sha:str = sha1(file).hexdigest()
        print('ERROR: in GetGame, unknown game', grppath, 'size:', size, 'crc32:', "0x{:X}".format(crc), 'md5:', md5sum, 'sha1:', sha, sep=', ')
        # TODO support for unknown games with default settings
        return None
    raise Exception('error in GetGame', grppath)

def GetGameMapSettings(game: Game) -> GameMapSettings:
    global gamesMapSettings
    g:GameMapSettings = gamesMapSettings[game.type]
    return g.copy()

def GetGameConSettings(game: Game) -> GameConSettings:
    global gamesConSettings
    g:GameConSettings = gamesConSettings.get(game.type, GameConSettings())
    return g.copy()





##########################################################################################
##############################          GAME HASHES         ##############################
##########################################################################################

# https://wiki.eduke32.com/wiki/Frequently_Asked_Questions
# ^(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)$
# Game('$1', '', $2, '$4', '$5', '$6') # $1
# (\d),(\d)
# $1$2
# idk what an SSI file is, but their sizes seem comparable to the GRP files

Game('Ion Fury',                           'Ion Fury',               92644120, '960B3686', 'd834055f0c9a60f8f23163b67d086546', '2cec5ab769ae27c6685d517defa766191c5e66c1') # Steam version
Game('Shadow Warrior',                     'Shadow Warrior',         47536148, '7545319F', '9d200b5fb4ace8797e7f8638c4f96af2', '4863226c01d0850c65ac0a3e20831e072b285425') # Steam "Classic" version https://store.steampowered.com/app/238070/Shadow_Warrior_Classic_1997/

#Game('DUKE.RTS v0.99',                    'Duke Nukem 3D',            175567, '6148685E', '7ECAF2753AA9CC924F746B3D0F36E7C2', 'A9356036AEA01583C85B71410F066285AFE3AF2B') # DUKE.RTS v0.99
Game('Shareware DUKE3D.GRP v0.99',         'Duke Nukem 3D',           9690241, '02F18900', '56B35E575EBA7F16C0E19628BD6BD934', 'A6341C16BC1170B43BE7F28B5A91C080F9CE3409') # Shareware DUKE3D.GRP v0.99
Game('Shareware DUKE3D.GRP v1.0',          'Duke Nukem 3D',          10429258, 'A28AA589', '1E57CF6272E8BE0E746666700CC0EE96', '7D2FDF1E9F1BBCE327650B3AECDAF78E6BBD6211') # Shareware DUKE3D.GRP v1.0
Game('Shareware DUKE3D.GRP v1.1',          'Duke Nukem 3D',          10442980, '912E1E8D', '9B0683A74C8BF36BF85631616385BEC8', '5166D6E4DBBA2B8ABB2FDA48257F0FCBDBF17626') # Shareware DUKE3D.GRP v1.1
Game('Shareware DUKE3D.GRP v1.3D',         'Duke Nukem 3D',          11035779, '983AD923', 'C03558E3A78D1C5356DC69B6134C5B55', 'A58BDBFAF28416528A0D9A4452F896F46774A806') # Shareware DUKE3D.GRP v1.3D
Game('Shareware DUKE3D.GRP v1.5 Mac',      'Duke Nukem 3D',          10444391, 'C5F71561', 'B9CAC374477E09459A313CEA457971EA', 'F035E9F0615E3DB23D2DB4C90232D8A95B5B9585') # Shareware DUKE3D.GRP v1.5 Mac
Game('DUKE3D.GRP v1.3D',                   'Duke Nukem 3D',          26524524, 'BBC9CE44', '981125CB9237C19AA0237109958D2B50', '3D508EAF3360605B0204301C259BD898717CF468') # DUKE3D.GRP v1.3D
#Game('DUKE.RTS v1.0/1.1/1.3D/1.4/1.5',    'Duke Nukem 3D',            188954, '504086C1', '9D29F9673BBDB56068ACF7645C13749C', '738C7F5FD0C8B57EE2E87AE7A97BF8E21A821D07') # DUKE.RTS v1.0/1.1/1.3D/1.4/1.5
Game('DUKE3D.GRP v1.4 (Plutonium Pak)',    'Duke Nukem 3D',          44348015, 'F514A6AC', 'C904FFB6A4F3C6080DD1DAC31218B25A', '61E70F883DF9552395406BF3D64F887F3C709438') # DUKE3D.GRP v1.4 (Plutonium Pak)
Game('DUKE3D.GRP v1.5 (Atomic Edition)',   'Duke Nukem 3D',          44356548, 'FD3DCFF1', '22B6938FE767E5CC57D1FE13080CD522', '4FDEF8559E2D35B1727FE92F021DF9C148CF696C') # DUKE3D.GRP v1.5 (Atomic Edition)
Game('DUKE!ZON.GRP v1.3D',                 'Duke!ZONE II',           26135388, '82C1B47F', 'C960FE3CC6920369EB43A8B00AC4E4EE', '169E9E2BEAB2E9FF6E0660FA3CE93C85B4B56884') # DUKE!ZON.GRP v1.3D
#Game('DZ-GAME.CON v1.3D',                 'Duke!ZONE II',              99967, 'F3DCF89D', '65C72C2550049D7456D5F983E0051E7B', '8D05E4646DFBD201877036F5379534D06E6A6DDC') # DZ-GAME.CON v1.3D
#Game('DZ-DEFS.CON v1.3D',                 'Duke!ZONE II',              28959, 'F2FE1424', '45DDEB920FF7AF450CD6A19CDFF6EE7E', '7BA88D2B12F5F193DA96822E59E5B7EE9DABFD5C') # DZ-DEFS.CON v1.3D
#Game('DZ-USER.CON v1.3D',                 'Duke!ZONE II',              36237, '93401EA4', 'A81793173C384F025768ED853A060F3A', '1E37C7EB9EAB03C938B18B3712DAEF97BA9B9B13') # DZ-USER.CON v1.3D
Game('DUKE!ZON.GRP v1.4',                  'Duke!ZONE II',           44100411, '7FB6117C', '031C271C689DD76F9E40241B10B8EBA9', '86A58754A2F2D95271B389FA2B8FAC9AA34CCFCE') # DUKE!ZON.GRP v1.4
#Game('DZ-GAME.CON v1.4',                  'Duke!ZONE II',             151198, '5C0E6CC7', '8EF020D2F63C0EE1CC391F00FEEE895D', 'D6DC4C24EC5986C7AC8FB3F4DA85D97E06D72F2E') # DZ-GAME.CON v1.4
#Game('DZ-DEFS.CON v1.4',                  'Duke!ZONE II',              36038, '85847E24', '8C7A4622A71F580B57954CA129B0474B', 'D23A2E9CC0FF30B02911AC9D7EC49D55CE856EE0') # DZ-DEFS.CON v1.4
#Game('DZ-USER.CON v1.4',                  'Duke!ZONE II',              45037, '739BE376', '1862C4CD17B6C95942B75F72CEAC7AEA', '31E39D7BB9E7E77E468CC67684F41AA58238179A') # DZ-USER.CON v1.4
Game('DUKEDC13.SSI v1.3D',                 'Duke it out in D.C.',     7926624, 'A9242158', 'D085D538A6BF40EBB041D964787A5D20', '66A96327EC514710D3526D87259CF5C0ABBBB841') # DUKEDC13.SSI v1.3D
Game('DUKEDCPP.SSI v1.4',                  'Duke it out in D.C.',     8225517, 'B79D997F', 'F0BFA5B956C8E3DBCBA1042118C1F456', '30D6AA2A44E936D09D6B423CFAB7C0595E2376F9') # DUKEDCPP.SSI v1.4
Game('DUKEDC.GRP (Atomic Edition)',        'Duke it out in D.C.',     8410183, 'A8CF80DA', '8AB2E7328DB4153E4158C850DE82D7C0', '1B66C3AD9A65556044946DD1CA97A839FCFEDC3B') # DUKEDC.GRP (Atomic Edition)
Game('NWINTER.GRP',                        'Duke: Nuclear Winter',   16169365, 'F1CAE8E4', '1250F83DCC3588293F0CE5C6FC701B43', 'A6728F621F121F9DB02EE67C39EFDBB5EEA95711') # NWINTER.GRP
Game('NAPALM.GRP',                         'Napalm',                 44365728, '3DE1589A', 'D926E362839949AA6EBA5BDF35A5F2D6', '9C42E7268A45D57E4B7961E6F1D3414D9DE12323') # NAPALM.GRP
#Game('NAPALM.RTS',                        'Napalm',                   564926, '12505172', 'D571897B4E3D43B3757A98C856869ED7', 'C90B050192030FFBD0137C03A4181CB1705B95D3') # NAPALM.RTS
#Game('NAPALM.CON (GAME.CON)',             'Napalm',                   142803, '75EF92BD', 'CCBBB146C094F490242FD922293DD5F9', '46F3AE2B37983660835F220AECEEA6060C89F2A7') # NAPALM.CON (GAME.CON)
Game('NAM.GRP',                            'NAM',                    43448927, '75C1F07B', '6C910A5438E230F85804353AC54D77B9', '2FD12F94246FBD3014223B76301B812EE8341D05') # NAM.GRP
#Game('NAM.RTS',                           'NAM',                      564926, '12505172', 'D571897B4E3D43B3757A98C856869ED7', 'C90B050192030FFBD0137C03A4181CB1705B95D3') # NAM.RTS
#Game('NAM.CON (GAME.CON)',                'NAM',                      142803, '75EF92BD', 'CCBBB146C094F490242FD922293DD5F9', '46F3AE2B37983660835F220AECEEA6060C89F2A7') # NAM.CON (GAME.CON)
Game('WW2GI.GRP',                          'WWII GI',                77939508, '907B82BF', '27E927BEBA43447DB3951EAADEDB4709', 'FD0208A55EAEF3937C126E1FFF474FB4DFBDA6F5') # WW2GI.GRP
#Game('WW2GI.RTS',                         'WWII GI',                  259214, '79D16760', '759F66C9F3C70AEDCAE29473AADE9966', 'CE352EF4C22F85869FDCB060A64EBC263ACEA6B0') # WW2GI.RTS

Game('VACA13.SSI v1.3D',                   'Duke Caribbean: Life\'s a Beach', 23559381, '4A2DBB62', '974616FC968D188C984E4F9A60F3C4BE', '2B7779AB211FB21CD2D7DEF93E2B9BBF948E406F') # VACA13.SSI v1.3D
Game('VACAPP.SSI v1.4',                    'Duke Caribbean: Life\'s a Beach', 22551333, '2F4FCCEE', '540AFD010435450D73FA3463437FCFC9', '58FD872BE376957D63D9F5C3BD169D5FCDF28664') # VACAPP.SSI v1.4
Game('VACA15.SSI v1.5',                    'Duke Caribbean: Life\'s a Beach', 22521880, 'B62B42FD', '22C8CD6235FC2B7ECEFEFC2442570D68', '84945D64E246E91840A872F332494D8509B66DD9') # VACA15.SSI v1.5
Game('VACATION.GRP (Atomic Edition)',      'Duke Caribbean: Life\'s a Beach', 22213819, '18F01C5B', '1C105CED73B776C172593764E9D0D93E', '65B8B787616ED637F86CFCAA90DE24C8E65B3DCC') # VACATION.GRP (Atomic Edition)

Game('Duke Nukem 3D (South Korean Censored)', 'Duke Nukem 3D', 26385383, 'AA4F6A40') # DUKEKR_CRC
Game('Duke Nukem 3D: Atomic Edition (WT)', 'Duke Nukem 3D', 44356548, '982AFE4A') # DUKEWT_CRC
Game('Duke Nukem 3D MacUser Demo', 'Duke Nukem 3D', 10628573, '73A15EE7') # DUKEMD2_CRC
Game('Platoon Leader', 'WWII GI', 37852572, 'D1ED8C0C') # PLATOONL_CRC
Game('Duke it out in D.C.', 'Duke it out in D.C.', 8410187, '39A692BF') # { "Duke it out in D.C.", (int32_t) 0x39A692BF,  8410187, GAMEFLAG_DUKE|GAMEFLAG_ADDON, DUKE15_CRC, "DUKEDC.CON", NULL}
Game('Duke Caribbean: Life\'s a Beach', 'Duke Caribbean: Life\'s a Beach', 22397273, '65B5F690') # { "Duke Caribbean: Life's a Beach", (int32_t) 0x65B5F690, 22397273, GAMEFLAG_DUKE|GAMEFLAG_ADDON, DUKE15_CRC, "VACATION.CON", NULL}
Game('Duke: Nuclear Winter Demo', 'Duke: Nuclear Winter', 10965909, 'C7EFBFA9') # { "Duke: Nuclear Winter Demo", (int32_t) 0xC7EFBFA9,  10965909, GAMEFLAG_DUKE|GAMEFLAG_ADDON, DUKE15_CRC, "NWINTER.CON", NULL}
Game('Duke!ZONE II', 'Duke!ZONE II', 3186656, '1E9516F1') # { "Duke!ZONE II", (int32_t) 0x1E9516F1,  3186656, GAMEFLAG_DUKE|GAMEFLAG_ADDON, DUKE15_CRC, "DZ-GAME.CON", NULL}
Game('Duke Nukem\'s Penthouse Paradise', 'Duke Nukem\'s Penthouse Paradise', 2112419, '7CD82A3B') # { "Duke Nukem's Penthouse Paradise", (int32_t) 0x7CD82A3B,  2112419, GAMEFLAG_DUKE|GAMEFLAG_ADDON, DUKE15_CRC, "ppakgame.con", NULL}, // original .zip release
Game('Duke Nukem\'s Penthouse Paradise', 'Duke Nukem\'s Penthouse Paradise', 4247491, 'CF928A58') # { "Duke Nukem's Penthouse Paradise", (int32_t) 0xCF928A58,  4247491, GAMEFLAG_DUKE|GAMEFLAG_ADDON, DUKE15_CRC, "PPAKGAME.CON", NULL}, // ZOOM Platform repacked .grp

# zipped for tests
Game('ZIPPED Shareware DUKE3D.GRP v1.3D', 'Duke Nukem 3D', 4570468, 'BFC91225', '9eacbb74e107fa0b136f189217ce41c7', '4bdf21e32ec6a3fc43092a50a51fce3e4ad6600d') # ZIPPED Shareware DUKE3D.GRP v1.3D for tests


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
        320: 'I_AMMOCRATE',
    },
    swappableEnemies = {
        # 7259: 'A_TURRET_BOTTOM',
        # 7260: 'A_TURRET',
        # 7281: 'A_TURRETDEAD',
        7300: 'A_MECHSECT',
        # 7301: 'A_MECHSECT_HANG',
        # 7349: 'A_MECHSECT_DEAD1',
        # 7356: 'A_MECHSECT_DEAD2',
        12096: 'A_CULTIST',
        12097: 'A_CULTIST_STAYPUT',
        12192: 'A_CULTIST_CROUCH',
        # 12227: 'A_CULTIST_DEAD',
        # 12255: 'A_CULTIST_DEADHEAD',
        # 12249: 'A_CULTIST_GIBBED',
        12288: 'A_GREATER',
        12289: 'A_GREATER_STAYPUT',
        12384: 'A_GREATER_CROUCH',
        # 12426: 'A_GREATER_DEAD1',
        # 12437: 'A_GREATER_DEAD2',
        # 12459: 'A_GREATER_GIBBED',
        11796: 'A_SHOTGUNNER',
        11797: 'A_SHOTGUNNER_STAYPUT',
        11892: 'A_SHOTGUNNER_CROUCH',
        # 11927: 'A_SHOTGUNNER_DEAD',
        # 11949: 'A_SHOTGUNNER_GIBBED',
        # 11913: 'A_SHOTGUNNER_DEADHEAD',
        12925: 'A_BRUTE',
        12930: 'A_BRUTE_BOTTOM',
        # 12923: 'A_BRUTE_BOTTOM_DEAD',
        12960: 'A_BRUTE_TOP',
        # 13094: 'A_BRUTE_TOP_DEAD',
        11600: 'A_DRONE',
        11540: 'A_DIOPEDE_HEAD',
        11570: 'A_DIOPEDE_BUTT',
        11450: 'A_DEACON',
        # 11512: 'A_DEACON_DEAD',
        13175: 'A_ARCHANGEL',
        # 13301: 'A_ARCHANGEL_DEAD',
        13350: 'A_WENTEKO',
        # 13498: 'A_WENTEKO_DEAD1',
        # 13486: 'A_WENTEKO_DEAD2',
        13600: 'A_NUKEMUTANT',
        13685: 'A_NUKEMUTANT_RISE',
        # 13707: 'A_NUKEMUTANT_DEAD',
        # 13698: 'A_NUKEMUTANT_DEADHEAD',
        # 13717: 'A_NUKEMUTANT_GIBBED',
        13720: 'A_NUKEMUTANT_GDF',
        13785: 'A_NUKEMUTANT_GDF_RISE',
        # 13807: 'A_NUKEMUTANT_GDF_DEAD',
        # 13830: 'A_NUKEMUTANT_GDF_GIBBED',
        # 13837: 'A_NUKEMUTANT_GDF_DEADHEAD',
        11392: 'A_PSEUDO_ENEMY',
        13850: 'A_HESKEL_BOT',
        12496: 'A_MECHBOSS_BOTTOM',
        12488: 'A_MECHBOSS_TOP',
    }
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
        #30: 'HEALTHBOX',
        #31: 'AMMOBOX',
        37: 'FREEZEAMMO',
        40: 'AMMO',
        41: 'BATTERYAMMO',
        42: 'DEVISTATORAMMO',
        44: 'RPGAMMO',
        45: 'GROWAMMO',
        46: 'CRYSTALAMMO',
        47: 'HBOMBAMMO',
        #48: 'AMMOLOTS',
        49: 'SHOTGUNAMMO',
        51: 'COLA',
        52: 'SIXPAK',
        53: 'FIRSTAID',
        54: 'SHIELD',
        55: 'STEROIDS',
        56: 'AIRTANK',
        57: 'JETPACK',
        59: 'HEATSENSOR',
        # 60: 'ACCESSCARD',
        61: 'BOOTS',
        100: 'ATOMICHEALTH',
        #142: 'NUKEBUTTON',
        1348: 'HOLODUKE',
    },
    swappableEnemies = {
        675: 'EGG',
        #1550: 'SHARK',
        1680: 'LIZTROOP',
        1681: 'LIZTROOPRUNNING',
        1682: 'LIZTROOPSTAYPUT',
        1705: 'LIZTOP',
        1715: 'LIZTROOPSHOOT',
        1725: 'LIZTROOPJETPACK',
        #1734: 'LIZTROOPDSPRITE',
        1741: 'LIZTROOPONTOILET',
        1742: 'LIZTROOPJUSTSIT',
        1744: 'LIZTROOPDUCKING',
        1820: 'OCTABRAIN',
        1821: 'OCTABRAINSTAYPUT',
        1845: 'OCTATOP',
        1880: 'DRONE',
        1920: 'COMMANDER',
        1921: 'COMMANDERSTAYPUT',
        1960: 'RECON',
        1975: 'TANK',
        2000: 'PIGCOP',
        2001: 'PIGCOPSTAYPUT',
        2045: 'PIGCOPDIVE',
        #2060: 'PIGCOPDEADSPRITE',
        2061: 'PIGTOP',
        2120: 'LIZMAN',
        2121: 'LIZMANSTAYPUT',
        2150: 'LIZMANSPITTING',
        2160: 'LIZMANFEEDING',
        2165: 'LIZMANJUMP',
        2219: 'EXPLOSION2BOT',
        2370: 'GREENSLIME',
        2370: 'GREENSLIME2',
        # 2630: 'BOSS1',
        # 2631: 'BOSS1STAYPUT',
        # 2660: 'BOSS1SHOOT',
        # 2670: 'BOSS1LOB',
        # 2696: 'BOSSTOP',
        # 2710: 'BOSS2',
        # 2760: 'BOSS3',
        4610: 'NEWBEAST',
        4611: 'NEWBEASTSTAYPUT',
        4690: 'NEWBEASTJUMP',
        4670: 'NEWBEASTHANG',
        4671: 'NEWBEASTHANGDEAD',
        # 4740: 'BOSS4',
        # 4741: 'BOSS4STAYPUT',
    }
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
        1814: 'gorohead.kvx',
        1804: 'shadow.kvx',
        1829: 'caltrop.kvx',
        1810: 'cookie.kvx',
        #1766: 'techkey.kvx',
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
        # 1765: 'MASTER_KEY1',# gold
        # 1769: 'oldkey.kvx',# silver
        # 1773: 'oldkey.kvx',# bronze
        # 1777: 'oldkey.kvx',# red
        # 1770: 'techkey.kvx',
        # 1774: 'techkey.kvx',
        # 1778: 'techkey.kvx',
        # 1771: 'keycard.kvx',
        # 1775: 'keycard.kvx',
        # 1779: 'keycard.kvx',
        817: 'mine.kvx',
        818: 'mine2.kvx',
        819: 'mine3.kvx',
        #2470: 'EXIT_SWITCH'
    }, swappableEnemies = {
        4096: 'EVIL_NINJA',
        4162: 'EVIL_NINJA_CROUCHING',
        4320: 'BIG_RIPPER',
        1210: 'SUMO_BOSS',
        1300: 'SERPENT_BOSS',
        1400: 'COOLIE',
        1441: 'COOLIE_GHOST',
        1469: 'GREEN_GUARDIAN',
        5426: 'ZILLA_BOSS',
        5162: 'FEMALE_WARRIOR',
        1580: 'LITTLE_RIPPER',
        #3780: 'FISH',
        800: 'HORNET',
    }
)
# Keys (picnums 1765-1779)
# Locks 1846-1854

GameConSettings('Ion Fury', conFiles = {
    'scripts/customize.con': [
        '.*HEALTH', '.*MAXAMMO', '.*_DMG', '.*AMOUNT'
    ]
})

GameConSettings('Duke Nukem 3D', conFiles = {
    'USER.CON': [
        'SWEARFREQUENCY', '.*HEALTH', '.*AMMO', '.*STRENGTH', '.*AMMOAMOUNT', '.*_AMOUNT'
    ]
})
