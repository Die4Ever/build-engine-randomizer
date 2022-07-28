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
    def __init__(self, name='', type='', size:int=0, crc:str='', md5:str='', sha1:str='', externalFiles:bool=False, useRandomizerFolder=True, **kargs):
        self.name = name
        self.type = type
        self.size = size
        self.md5 = md5.lower()
        self.crc = 0
        if crc:
            self.crc = int(crc, 16)
        self.sha1 = sha1.lower()
        self.externalFiles = externalFiles
        self.useRandomizerFolder = useRandomizerFolder
        # can't use external files without also using the randomizer folder, otherwise we're reading from the same files we're writing to
        assert not (self.externalFiles and not self.useRandomizerFolder)

    def __repr__(self):
        return repr(self.__dict__)

    def copy(self) -> 'GameInfo':
        return copyobj(self)

def AddGame(*args, **kargs) -> GameInfo:
    global gamesList
    game = GameInfo(*args, **kargs)
    if 'allowOverwrite' not in {**kargs}:
        assert game.crc not in gamesList, repr(game.__dict__)
    gamesList[game.crc] = game
    return game

class GameMapSettings:
    def __init__(self, gameName=None, minMapVersion=7, maxMapVersion=9,
            swappableItems:dict={}, swappableEnemies:dict={}, addableEnemies:list=[], triggers:dict={}, additions:dict={}, reorderMapsBlacklist:list=[], **kargs):
        self.gameName = gameName
        self.minMapVersion = minMapVersion
        self.maxMapVersion = maxMapVersion
        self.swappableItems = swappableItems
        self.swappableEnemies = swappableEnemies
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
    global gamesMapSettings
    gms: GameMapSettings = GameMapSettings(*args, **kargs)
    assert gms.gameName not in gamesMapSettings, repr(gms.__dict__)
    gamesMapSettings[gms.gameName] = gms
    return gms

class GameConSettings:
    def __init__(self, gameName=None, conFiles={}):
        self.gameName = gameName
        self.conFiles = conFiles

    def __repr__(self):
        return repr(self.__dict__)

    def copy(self) -> 'GameConSettings':
        return copyobj(self)

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




##########################################################################################
##############################          GAME HASHES         ##############################
##########################################################################################

# https://wiki.eduke32.com/wiki/Frequently_Asked_Questions
# ^(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)$
# AddGame('$1', '', $2, '$4', '$5', '$6') # $1
# (\d),(\d)
# $1$2
# idk what an SSI file is, but their sizes seem comparable to the GRP files

AddGame('Ion Fury',                           'Ion Fury',               92644120, '960B3686', 'd834055f0c9a60f8f23163b67d086546', '2cec5ab769ae27c6685d517defa766191c5e66c1', useRandomizerFolder=False) # Steam version
AddGame('Shadow Warrior',                     'Shadow Warrior',         47536148, '7545319F', '9d200b5fb4ace8797e7f8638c4f96af2', '4863226c01d0850c65ac0a3e20831e072b285425', useRandomizerFolder=False) # Steam "Classic" version https://store.steampowered.com/app/238070/Shadow_Warrior_Classic_1997/
AddGame('PowerSlave',                         'PowerSlave',             26904012, 'AC80ECB6', '4ae5cbe10396147ae042463b7df8010f', '548751e10f5c25f80d95321565b13f4664434981') # STUFF.DAT
AddGame('PowerSlave',                         'PowerSlave',             27108170, 'E3B172F1', 'b51391e08a17e5c46e25f6cf46f892eb', 'b84fd656be67271910e5eba4caf69bc81192c174') # STUFF.DAT
AddGame('PowerSlave Demo',                    'PowerSlave',             15904838, '1D8C7645', '61f5b2871e57e757932f338adefbc878', '6bb4b2974da3d90e70c6b4dc56b296f907c180f0') # STUFF.DAT shareware
AddGame('Exhumed Demo',                       'PowerSlave',             16481687, '1A6E27FA', 'e368de92d99e4fb85ebe5f188eb175e3', '2062fec5d513850b3c3dc66c7d44c4b0f91296db') # STUFF.DAT shareware
AddGame('Blood',                              'Blood',                   9570681, 'A8FDDA84', '50e921649a91b2f707af8ef89141e468', '7051cd336a924db4948a99ad2ca2889afc5393a6') # BLOOD.RFF
AddGame('Blood DOS',                          'Blood',                   8200353, 'B291418F', '7c77e3ca23960fe7dcad9ff7de054566', '9246062a9573639c69ec369efd56a0e7e7ffc8e0') # blood.rff

#AddGame('DUKE.RTS v0.99',                    'Duke Nukem 3D',            175567, '6148685E', '7ECAF2753AA9CC924F746B3D0F36E7C2', 'A9356036AEA01583C85B71410F066285AFE3AF2B') # DUKE.RTS v0.99
AddGame('Shareware DUKE3D.GRP v0.99',         'Duke Nukem 3D',           9690241, '02F18900', '56B35E575EBA7F16C0E19628BD6BD934', 'A6341C16BC1170B43BE7F28B5A91C080F9CE3409') # Shareware DUKE3D.GRP v0.99
AddGame('Shareware DUKE3D.GRP v1.0',          'Duke Nukem 3D',          10429258, 'A28AA589', '1E57CF6272E8BE0E746666700CC0EE96', '7D2FDF1E9F1BBCE327650B3AECDAF78E6BBD6211') # Shareware DUKE3D.GRP v1.0
AddGame('Shareware DUKE3D.GRP v1.1',          'Duke Nukem 3D',          10442980, '912E1E8D', '9B0683A74C8BF36BF85631616385BEC8', '5166D6E4DBBA2B8ABB2FDA48257F0FCBDBF17626') # Shareware DUKE3D.GRP v1.1
AddGame('Shareware DUKE3D.GRP v1.3D',         'Duke Nukem 3D',          11035779, '983AD923', 'C03558E3A78D1C5356DC69B6134C5B55', 'A58BDBFAF28416528A0D9A4452F896F46774A806') # Shareware DUKE3D.GRP v1.3D
AddGame('Shareware DUKE3D.GRP v1.5 Mac',      'Duke Nukem 3D',          10444391, 'C5F71561', 'B9CAC374477E09459A313CEA457971EA', 'F035E9F0615E3DB23D2DB4C90232D8A95B5B9585') # Shareware DUKE3D.GRP v1.5 Mac

AddGame('DUKE3D.GRP v1.3D',                   'Duke Nukem 3D',          26524524, 'BBC9CE44', '981125CB9237C19AA0237109958D2B50', '3D508EAF3360605B0204301C259BD898717CF468') # DUKE3D.GRP v1.3D
#AddGame('DUKE.RTS v1.0/1.1/1.3D/1.4/1.5',    'Duke Nukem 3D',            188954, '504086C1', '9D29F9673BBDB56068ACF7645C13749C', '738C7F5FD0C8B57EE2E87AE7A97BF8E21A821D07') # DUKE.RTS v1.0/1.1/1.3D/1.4/1.5
AddGame('DUKE3D.GRP v1.4 (Plutonium Pak)',    'Duke Nukem 3D',          44348015, 'F514A6AC', 'C904FFB6A4F3C6080DD1DAC31218B25A', '61E70F883DF9552395406BF3D64F887F3C709438') # DUKE3D.GRP v1.4 (Plutonium Pak)
AddGame('DUKE3D.GRP v1.5 (Atomic Edition)',   'Duke Nukem 3D',          44356548, 'FD3DCFF1', '22B6938FE767E5CC57D1FE13080CD522', '4FDEF8559E2D35B1727FE92F021DF9C148CF696C') # DUKE3D.GRP v1.5 (Atomic Edition)

AddGame('Duke Nukem 3D: Atomic Edition (WT)', 'Duke Nukem 3D',          44356548, '982AFE4A', externalFiles=True) # DUKEWT_CRC
AddGame('Duke Nukem 3D: World Tour',          'Duke Nukem 3D',                37, '5BD05463', '756a398d7d684f55785005833b4dd67c', '7a9afeb6bb1ad7dd097487cad3c8775debddc730', externalFiles=True) # DUKE3D.GRP v1.5 (Atomic Edition)

AddGame('Duke Nukem 3D (South Korean Censored)', 'Duke Nukem 3D', 26385383, 'AA4F6A40') # DUKEKR_CRC
AddGame('Duke Nukem 3D MacUser Demo', 'Duke Nukem 3D', 10628573, '73A15EE7') # DUKEMD2_CRC
AddGame('Platoon Leader', 'WWII GI', 37852572, 'D1ED8C0C') # PLATOONL_CRC
AddGame('Duke it out in D.C.', 'Duke it out in D.C.', 8410187, '39A692BF') # { "Duke it out in D.C.", (int32_t) 0x39A692BF,  8410187, GAMEFLAG_DUKE|GAMEFLAG_ADDON, DUKE15_CRC, "DUKEDC.CON", NULL}
AddGame('Duke Caribbean: Life\'s a Beach', 'Duke Caribbean: Life\'s a Beach', 22397273, '65B5F690') # { "Duke Caribbean: Life's a Beach", (int32_t) 0x65B5F690, 22397273, GAMEFLAG_DUKE|GAMEFLAG_ADDON, DUKE15_CRC, "VACATION.CON", NULL}
AddGame('Duke: Nuclear Winter Demo', 'Duke: Nuclear Winter', 10965909, 'C7EFBFA9') # { "Duke: Nuclear Winter Demo", (int32_t) 0xC7EFBFA9,  10965909, GAMEFLAG_DUKE|GAMEFLAG_ADDON, DUKE15_CRC, "NWINTER.CON", NULL}
AddGame('Duke!ZONE II', 'Duke!ZONE II', 3186656, '1E9516F1') # { "Duke!ZONE II", (int32_t) 0x1E9516F1,  3186656, GAMEFLAG_DUKE|GAMEFLAG_ADDON, DUKE15_CRC, "DZ-GAME.CON", NULL}
AddGame('Duke Nukem\'s Penthouse Paradise', 'Duke Nukem\'s Penthouse Paradise', 2112419, '7CD82A3B') # { "Duke Nukem's Penthouse Paradise", (int32_t) 0x7CD82A3B,  2112419, GAMEFLAG_DUKE|GAMEFLAG_ADDON, DUKE15_CRC, "ppakgame.con", NULL}, // original .zip release
AddGame('Duke Nukem\'s Penthouse Paradise', 'Duke Nukem\'s Penthouse Paradise', 4247491, 'CF928A58') # { "Duke Nukem's Penthouse Paradise", (int32_t) 0xCF928A58,  4247491, GAMEFLAG_DUKE|GAMEFLAG_ADDON, DUKE15_CRC, "PPAKGAME.CON", NULL}, // ZOOM Platform repacked .grp

AddGame('DUKE!ZON.GRP v1.3D',                 'Duke!ZONE II',           26135388, '82C1B47F', 'C960FE3CC6920369EB43A8B00AC4E4EE', '169E9E2BEAB2E9FF6E0660FA3CE93C85B4B56884') # DUKE!ZON.GRP v1.3D
#AddGame('DZ-GAME.CON v1.3D',                 'Duke!ZONE II',              99967, 'F3DCF89D', '65C72C2550049D7456D5F983E0051E7B', '8D05E4646DFBD201877036F5379534D06E6A6DDC') # DZ-GAME.CON v1.3D
#AddGame('DZ-DEFS.CON v1.3D',                 'Duke!ZONE II',              28959, 'F2FE1424', '45DDEB920FF7AF450CD6A19CDFF6EE7E', '7BA88D2B12F5F193DA96822E59E5B7EE9DABFD5C') # DZ-DEFS.CON v1.3D
#AddGame('DZ-USER.CON v1.3D',                 'Duke!ZONE II',              36237, '93401EA4', 'A81793173C384F025768ED853A060F3A', '1E37C7EB9EAB03C938B18B3712DAEF97BA9B9B13') # DZ-USER.CON v1.3D
AddGame('DUKE!ZON.GRP v1.4',                  'Duke!ZONE II',           44100411, '7FB6117C', '031C271C689DD76F9E40241B10B8EBA9', '86A58754A2F2D95271B389FA2B8FAC9AA34CCFCE') # DUKE!ZON.GRP v1.4
#AddGame('DZ-GAME.CON v1.4',                  'Duke!ZONE II',             151198, '5C0E6CC7', '8EF020D2F63C0EE1CC391F00FEEE895D', 'D6DC4C24EC5986C7AC8FB3F4DA85D97E06D72F2E') # DZ-GAME.CON v1.4
#AddGame('DZ-DEFS.CON v1.4',                  'Duke!ZONE II',              36038, '85847E24', '8C7A4622A71F580B57954CA129B0474B', 'D23A2E9CC0FF30B02911AC9D7EC49D55CE856EE0') # DZ-DEFS.CON v1.4
#AddGame('DZ-USER.CON v1.4',                  'Duke!ZONE II',              45037, '739BE376', '1862C4CD17B6C95942B75F72CEAC7AEA', '31E39D7BB9E7E77E468CC67684F41AA58238179A') # DZ-USER.CON v1.4

AddGame('DUKEDC13.SSI v1.3D',                 'Duke it out in D.C.',     7926624, 'A9242158', 'D085D538A6BF40EBB041D964787A5D20', '66A96327EC514710D3526D87259CF5C0ABBBB841') # DUKEDC13.SSI v1.3D
AddGame('DUKEDCPP.SSI v1.4',                  'Duke it out in D.C.',     8225517, 'B79D997F', 'F0BFA5B956C8E3DBCBA1042118C1F456', '30D6AA2A44E936D09D6B423CFAB7C0595E2376F9') # DUKEDCPP.SSI v1.4
AddGame('DUKEDC.GRP (Atomic Edition)',        'Duke it out in D.C.',     8410183, 'A8CF80DA', '8AB2E7328DB4153E4158C850DE82D7C0', '1B66C3AD9A65556044946DD1CA97A839FCFEDC3B') # DUKEDC.GRP (Atomic Edition)
AddGame('NWINTER.GRP',                        'Duke: Nuclear Winter',   16169365, 'F1CAE8E4', '1250F83DCC3588293F0CE5C6FC701B43', 'A6728F621F121F9DB02EE67C39EFDBB5EEA95711') # NWINTER.GRP

AddGame('VACA13.SSI v1.3D',                   'Duke Caribbean: Life\'s a Beach', 23559381, '4A2DBB62', '974616FC968D188C984E4F9A60F3C4BE', '2B7779AB211FB21CD2D7DEF93E2B9BBF948E406F') # VACA13.SSI v1.3D
AddGame('VACAPP.SSI v1.4',                    'Duke Caribbean: Life\'s a Beach', 22551333, '2F4FCCEE', '540AFD010435450D73FA3463437FCFC9', '58FD872BE376957D63D9F5C3BD169D5FCDF28664') # VACAPP.SSI v1.4
AddGame('VACA15.SSI v1.5',                    'Duke Caribbean: Life\'s a Beach', 22521880, 'B62B42FD', '22C8CD6235FC2B7ECEFEFC2442570D68', '84945D64E246E91840A872F332494D8509B66DD9') # VACA15.SSI v1.5
AddGame('VACATION.GRP (Atomic Edition)',      'Duke Caribbean: Life\'s a Beach', 22213819, '18F01C5B', '1C105CED73B776C172593764E9D0D93E', '65B8B787616ED637F86CFCAA90DE24C8E65B3DCC') # VACATION.GRP (Atomic Edition)

AddGame('NAPALM.GRP',                         'Napalm',                 44365728, '3DE1589A', 'D926E362839949AA6EBA5BDF35A5F2D6', '9C42E7268A45D57E4B7961E6F1D3414D9DE12323') # NAPALM.GRP
#AddGame('NAPALM.RTS',                        'Napalm',                   564926, '12505172', 'D571897B4E3D43B3757A98C856869ED7', 'C90B050192030FFBD0137C03A4181CB1705B95D3') # NAPALM.RTS
#AddGame('NAPALM.CON (GAME.CON)',             'Napalm',                   142803, '75EF92BD', 'CCBBB146C094F490242FD922293DD5F9', '46F3AE2B37983660835F220AECEEA6060C89F2A7') # NAPALM.CON (GAME.CON)
AddGame('NAM.GRP',                            'NAM',                    43448927, '75C1F07B', '6C910A5438E230F85804353AC54D77B9', '2FD12F94246FBD3014223B76301B812EE8341D05') # NAM.GRP
#AddGame('NAM.RTS',                           'NAM',                      564926, '12505172', 'D571897B4E3D43B3757A98C856869ED7', 'C90B050192030FFBD0137C03A4181CB1705B95D3') # NAM.RTS
#AddGame('NAM.CON (GAME.CON)',                'NAM',                      142803, '75EF92BD', 'CCBBB146C094F490242FD922293DD5F9', '46F3AE2B37983660835F220AECEEA6060C89F2A7') # NAM.CON (GAME.CON)
AddGame('WW2GI.GRP',                          'WWII GI',                77939508, '907B82BF', '27E927BEBA43447DB3951EAADEDB4709', 'FD0208A55EAEF3937C126E1FFF474FB4DFBDA6F5') # WW2GI.GRP
#AddGame('WW2GI.RTS',                         'WWII GI',                  259214, '79D16760', '759F66C9F3C70AEDCAE29473AADE9966', 'CE352EF4C22F85869FDCB060A64EBC263ACEA6B0') # WW2GI.RTS

# build these GameMapSettings using this regex find/replace
# define ([\w_]+) (\d+)
# $2: '$1',

AddMapSettings('Ion Fury', minMapVersion=7, maxMapVersion=9,
    swappableItems = {
        209: SpriteInfo('I_BATON'),
        210: SpriteInfo('I_LOVERBOY'),
        211: SpriteInfo('I_LOVERBOY_AMMO'),
        212: SpriteInfo('I_MEDPACK'),
        213: SpriteInfo('I_MEDICOMP'),
        214: SpriteInfo('I_MEDKIT'),
        215: SpriteInfo('I_BULLETVEST'),
        216: SpriteInfo('I_ARMORVEST'),
        #217: SpriteInfo('I_ACCESSCARD'),
        218: SpriteInfo('I_MINIGUN_AMMO'),
        219: SpriteInfo('I_PLASMACROSSBOW_AMMO'),
        220: SpriteInfo('I_PLASMACROSSBOW'),
        221: SpriteInfo('I_MINIGUN'),
        222: SpriteInfo('I_CLUSTERPUCK'),
        223: SpriteInfo('I_TECHVEST'),
        224: SpriteInfo('I_SHOTGUN'),
        225: SpriteInfo('I_SHOTGUN_AMMO'),
        226: SpriteInfo('I_GRENADELAUNCHER_AMMO'),
        227: SpriteInfo('I_SMG_AMMO'),
        228: SpriteInfo('I_ARMOR_SHARD'),
        229: SpriteInfo('I_LOVERBOY_AMMO2'),
        230: SpriteInfo('I_SMG'),
        231: SpriteInfo('I_GRENADELAUNCHER'),
        232: SpriteInfo('I_BOWLINGBOMB_PICKUP'),
        233: SpriteInfo('I_SYRINGE'),
        240: SpriteInfo('I_HAZARDSUIT'),
        241: SpriteInfo('I_BOMBRUSH'),
        242: SpriteInfo('I_RADAR'),
        243: SpriteInfo('I_DKSHOES'),
        244: SpriteInfo('I_DAMAGEBOOSTER'),
        6800: SpriteInfo('I_BOWLINGBOMB'),
        9930: SpriteInfo('I_PIZZA_6'),
        9931: SpriteInfo('I_PIZZA_5'),
        9932: SpriteInfo('I_PIZZA_4'),
        9933: SpriteInfo('I_PIZZA_3'),
        9934: SpriteInfo('I_PIZZA_2'),
        9935: SpriteInfo('I_PIZZA_1'),
        9003: SpriteInfo('I_SODA'),
        9002: SpriteInfo('I_SODA_STAND'),
        320: SpriteInfo('I_AMMOCRATE'),
    },
    swappableEnemies = {
        # 7259: SpriteInfo('A_TURRET_BOTTOM'),
        # 7260: SpriteInfo('A_TURRET'),
        # 7281: SpriteInfo('A_TURRETDEAD'),
        7300: SpriteInfo('A_MECHSECT'),
        # 7301: SpriteInfo('A_MECHSECT_HANG'),
        # 7349: SpriteInfo('A_MECHSECT_DEAD1'),
        # 7356: SpriteInfo('A_MECHSECT_DEAD2'),
        12096: SpriteInfo('A_CULTIST'),
        12097: SpriteInfo('A_CULTIST_STAYPUT'),
        12192: SpriteInfo('A_CULTIST_CROUCH'),
        # 12227: SpriteInfo('A_CULTIST_DEAD'),
        # 12255: SpriteInfo('A_CULTIST_DEADHEAD'),
        # 12249: SpriteInfo('A_CULTIST_GIBBED'),
        12288: SpriteInfo('A_GREATER'),
        12289: SpriteInfo('A_GREATER_STAYPUT'),
        12384: SpriteInfo('A_GREATER_CROUCH'),
        # 12426: SpriteInfo('A_GREATER_DEAD1'),
        # 12437: SpriteInfo('A_GREATER_DEAD2'),
        # 12459: SpriteInfo('A_GREATER_GIBBED'),
        11796: SpriteInfo('A_SHOTGUNNER'),
        11797: SpriteInfo('A_SHOTGUNNER_STAYPUT'),
        11892: SpriteInfo('A_SHOTGUNNER_CROUCH'),
        # 11927: SpriteInfo('A_SHOTGUNNER_DEAD'),
        # 11949: SpriteInfo('A_SHOTGUNNER_GIBBED'),
        # 11913: SpriteInfo('A_SHOTGUNNER_DEADHEAD'),
        12925: SpriteInfo('A_BRUTE'),
        12930: SpriteInfo('A_BRUTE_BOTTOM'),
        # 12923: SpriteInfo('A_BRUTE_BOTTOM_DEAD'),
        12960: SpriteInfo('A_BRUTE_TOP'),
        # 13094: SpriteInfo('A_BRUTE_TOP_DEAD'),
        11600: SpriteInfo('A_DRONE'),
        11540: SpriteInfo('A_DIOPEDE_HEAD'),
        11570: SpriteInfo('A_DIOPEDE_BUTT'),
        11450: SpriteInfo('A_DEACON'),
        # 11512: SpriteInfo('A_DEACON_DEAD'),
        13175: SpriteInfo('A_ARCHANGEL'),
        # 13301: SpriteInfo('A_ARCHANGEL_DEAD'),
        13350: SpriteInfo('A_WENTEKO'),
        # 13498: SpriteInfo('A_WENTEKO_DEAD1'),
        # 13486: SpriteInfo('A_WENTEKO_DEAD2'),
        13600: SpriteInfo('A_NUKEMUTANT'),
        13685: SpriteInfo('A_NUKEMUTANT_RISE'),
        # 13707: SpriteInfo('A_NUKEMUTANT_DEAD'),
        # 13698: SpriteInfo('A_NUKEMUTANT_DEADHEAD'),
        # 13717: SpriteInfo('A_NUKEMUTANT_GIBBED'),
        13720: SpriteInfo('A_NUKEMUTANT_GDF'),
        13785: SpriteInfo('A_NUKEMUTANT_GDF_RISE'),
        # 13807: SpriteInfo('A_NUKEMUTANT_GDF_DEAD'),
        # 13830: SpriteInfo('A_NUKEMUTANT_GDF_GIBBED'),
        # 13837: SpriteInfo('A_NUKEMUTANT_GDF_DEADHEAD'),
        11392: SpriteInfo('A_PSEUDO_ENEMY'),
        13850: SpriteInfo('A_HESKEL_BOT'),
        12496: SpriteInfo('A_MECHBOSS_BOTTOM'),
        12488: SpriteInfo('A_MECHBOSS_TOP'),
    },
    addableEnemies = [7300, 12096, 12288, 11796, 12925, 11600, 11450, 13175, 13350, 13600, 13685, 13720, 13785, 11392, 13850],
    triggers={}
)

AddMapSettings('Duke Nukem 3D', minMapVersion=7, maxMapVersion=9,
    swappableItems = {
        21: SpriteInfo('FIRSTGUNSPRITE'),
        22: SpriteInfo('CHAINGUNSPRITE'),
        23: SpriteInfo('RPGSPRITE'),
        24: SpriteInfo('FREEZESPRITE'),
        25: SpriteInfo('SHRINKERSPRITE'),
        26: SpriteInfo('HEAVYHBOMB'),
        27: SpriteInfo('TRIPBOMBSPRITE'),
        28: SpriteInfo('SHOTGUNSPRITE'),
        29: SpriteInfo('DEVISTATORSPRITE'),
        #30: SpriteInfo('HEALTHBOX'),
        #31: SpriteInfo('AMMOBOX'),
        37: SpriteInfo('FREEZEAMMO'),
        40: SpriteInfo('AMMO'),
        41: SpriteInfo('BATTERYAMMO'),
        42: SpriteInfo('DEVISTATORAMMO'),
        44: SpriteInfo('RPGAMMO'),
        45: SpriteInfo('GROWAMMO'),
        46: SpriteInfo('CRYSTALAMMO'),
        47: SpriteInfo('HBOMBAMMO'),
        #48: SpriteInfo('AMMOLOTS'),
        49: SpriteInfo('SHOTGUNAMMO'),
        51: SpriteInfo('COLA'),
        52: SpriteInfo('SIXPAK'),
        53: SpriteInfo('FIRSTAID'),
        54: SpriteInfo('SHIELD'),
        55: SpriteInfo('STEROIDS'),
        56: SpriteInfo('AIRTANK'),
        57: SpriteInfo('JETPACK'),
        59: SpriteInfo('HEATSENSOR'),
        # 60: SpriteInfo('ACCESSCARD'),
        61: SpriteInfo('BOOTS'),
        100: SpriteInfo('ATOMICHEALTH'),
        #142: SpriteInfo('NUKEBUTTON'),
        1348: SpriteInfo('HOLODUKE'),
    },
    swappableEnemies = {
        675: SpriteInfo('EGG'),
        #1550: SpriteInfo('SHARK'),
        1680: SpriteInfo('LIZTROOP'),
        1681: SpriteInfo('LIZTROOPRUNNING'),
        1682: SpriteInfo('LIZTROOPSTAYPUT'),
        1705: SpriteInfo('LIZTOP'),
        1715: SpriteInfo('LIZTROOPSHOOT'),
        1725: SpriteInfo('LIZTROOPJETPACK'),
        #1734: SpriteInfo('LIZTROOPDSPRITE'),
        1741: SpriteInfo('LIZTROOPONTOILET'),
        1742: SpriteInfo('LIZTROOPJUSTSIT'),
        1744: SpriteInfo('LIZTROOPDUCKING'),
        1820: SpriteInfo('OCTABRAIN'),
        1821: SpriteInfo('OCTABRAINSTAYPUT'),
        1845: SpriteInfo('OCTATOP'),
        1880: SpriteInfo('DRONE'),
        1920: SpriteInfo('COMMANDER'),
        1921: SpriteInfo('COMMANDERSTAYPUT'),
        1960: SpriteInfo('RECON'),
        1975: SpriteInfo('TANK'),
        2000: SpriteInfo('PIGCOP'),
        2001: SpriteInfo('PIGCOPSTAYPUT'),
        2045: SpriteInfo('PIGCOPDIVE'),
        #2060: SpriteInfo('PIGCOPDEADSPRITE'),
        2061: SpriteInfo('PIGTOP'),
        2120: SpriteInfo('LIZMAN'),
        2121: SpriteInfo('LIZMANSTAYPUT'),
        2150: SpriteInfo('LIZMANSPITTING'),
        2160: SpriteInfo('LIZMANFEEDING'),
        2165: SpriteInfo('LIZMANJUMP'),
        #2219: SpriteInfo('EXPLOSION2BOT'),
        2370: SpriteInfo('GREENSLIME'),
        2371: SpriteInfo('GREENSLIME2'),
        # 2630: SpriteInfo('BOSS1'),
        # 2631: SpriteInfo('BOSS1STAYPUT'),
        # 2660: SpriteInfo('BOSS1SHOOT'),
        # 2670: SpriteInfo('BOSS1LOB'),
        # 2696: SpriteInfo('BOSSTOP'),
        # 2710: SpriteInfo('BOSS2'),
        # 2760: SpriteInfo('BOSS3'),
        4610: SpriteInfo('NEWBEAST'),
        4611: SpriteInfo('NEWBEASTSTAYPUT'),
        4690: SpriteInfo('NEWBEASTJUMP'),
        4670: SpriteInfo('NEWBEASTHANG'),
        4671: SpriteInfo('NEWBEASTHANGDEAD'),
        # 4740: SpriteInfo('BOSS4'),
        # 4741: SpriteInfo('BOSS4STAYPUT'),
    },
    addableEnemies = [675, 1680, 1820, 1880, 1920, 1960, 1975, 2000, 2120, 2370, 4610,],
    triggers = {
        # 675 EGG doesn't work for spawning?
        9: dict(name='RESPAWN', hightags=[1680, 1820, 1960, 2000, 2120, 2370], lowtags=[], not_hightags=[2630, 2631, 2660, 2670, 2696, 2710, 2760, 4740, 4741]),
    },
    additions = {
        # lower case because python doesn't have case-insensitive dicts, maybe I should create these with a function
        'e1l3.map': [ # ensure the player gets weapons to start with
                dict(pos=[24160, 52032, 45056], sectnum=296, choices=[21,22,23,24,25,26,27,28,29]), # under the chair
                dict(pos=[28096, 50688, 22528], sectnum=297, choices=[21,22,23,24,25,26,27,28,29]), # in the locker
                dict(pos=[47864, 29653, 20480], sectnum=265, choices=[23,47]), # explosives near the end of the map
                dict(pos=[47270, 25876, 34370], sectnum=272, texcoords=[8, 8, 0, 0], choices=[26]), # single pipe bomb near the end of the map
            ]
    },
    reorderMapsBlacklist = [ 'E1L7.MAP', 'E1L8.MAP', 'E3L10.MAP' ]
)

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
        1765: SpriteInfo('oldkey'),
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
        1210: SpriteInfo('SUMO_BOSS'),
        1300: SpriteInfo('SERPENT_BOSS'),
        1400: SpriteInfo('COOLIE'),
        1441: SpriteInfo('COOLIE_GHOST'),
        1469: SpriteInfo('GREEN_GUARDIAN'),
        5426: SpriteInfo('ZILLA_BOSS'),
        5162: SpriteInfo('FEMALE_WARRIOR'),
        1580: SpriteInfo('LITTLE_RIPPER'),
        #3780: SpriteInfo('FISH'),
        800: SpriteInfo('HORNET'),
    },
    addableEnemies = [4096, 4320, 1210, 1300, 1400, 1441, 1469, 5426, 5162, 1580, 800,],
    triggers={}
)
# Keys (picnums 1765-1779)
# Locks 1846-1854


AddMapSettings('PowerSlave', minMapVersion=6, maxMapVersion=6,
    swappableItems={
        **SpriteRange(326, 331, SpriteInfo('Life Blood')),
        **SpriteRange(332, 337, SpriteInfo('Cobra Venom Bowl')),
        782: SpriteInfo('Still Beating Heart'),
        488: SpriteInfo('Pistol'),
        490: SpriteInfo('Machine Gun'),
        491: SpriteInfo('Fancy Gun'),
        877: SpriteInfo('Quick Loader'),
        878: SpriteInfo('Grenade'),
        879: SpriteInfo('Fuel Canister'),
        881: SpriteInfo('Machine Gun Ammo'),
        882: SpriteInfo('Machine Gun Ammo'),
        **SpriteRange(899, 901, SpriteInfo('Cobra Staff')),
        983: SpriteInfo('Extra Life'),
        3457: SpriteInfo('Golden Cobra'),
        **SpriteRange(3502, 3507, SpriteInfo('Magical Essence')),
        **SpriteRange(3516, 3520, SpriteInfo('Raw Energy')),
        3602: SpriteInfo('Grenade'),
    },
    swappableEnemies={
        **SpriteRange(861, 875, SpriteInfo('Spider')),
        **SpriteRange(1526, 1531, SpriteInfo('Mummy')),
        **SpriteRange(1664, 1746, SpriteInfo('Mummy')),
        **SpriteRange(1949, 1963, SpriteInfo('Mummy')),
        **SpriteRange(2311, 2373, SpriteInfo('Anubis Zombie')),
        **SpriteRange(2432, 2497, SpriteInfo('Omenwasp')),
        2552: SpriteInfo('Omenwasp'),
        **SpriteRange(2498, 2548, SpriteInfo('Am-mit')),
        **SpriteRange(2751, 2816, SpriteInfo('Bastet')),
        **SpriteRange(3038, 3049, SpriteInfo('Bastet')),
        **SpriteRange(3137, 3147, SpriteInfo('Mouth')),
        **SpriteRange(3200, 3250, SpriteInfo('Grasshopper')),
    },
    triggers={},
    additions={},
    keyItems={
        **SpriteRange(3320, 3347, SpriteInfo('Key')),
    },
    bosses={
        **SpriteRange(2559, 2642, SpriteInfo('Set')),
        2687: SpriteInfo('Set'),
        **SpriteRange(2643, 2675, SpriteInfo('Magmantis')),
        **SpriteRange(2698, 2750, SpriteInfo('Selkis')),
        **SpriteRange(3072, 3136, SpriteInfo('Kilmaatikahn')),
        **SpriteRange(3151, 3181, SpriteInfo('Kilmaatikahn')),
    }
)


# https://github.com/thomasrogers03/bloom/blob/master/bloom/resources/sprite_types.yaml
AddMapSettings('Blood', minMapVersion=7, maxMapVersion=7,
    swappableItems={
        518: SpriteInfo('Tome', 'items', lowtag=136, xrepeat=40, yrepeat=40),
        519: SpriteInfo('Doctor\'s Bag', 'items', lowtag=107, xrepeat=48, yrepeat=48),
        #522: SpriteInfo('Black Chest', 'items', lowtag=137, xrepeat=12, yrepeat=12),
        #523: SpriteInfo('Wooden Chest', 'items', lowtag=138, xrepeat=12, yrepeat=12),
        524: SpriteInfo('Flare Pistol', 'weapons', lowtag=43, xrepeat=48, yrepeat=48),
        525: SpriteInfo('Voodoo Doll', 'weapons', lowtag=44, xrepeat=48, yrepeat=48),
        #525: SpriteInfo('Voodoo Doll', 'weapons', lowtag=70, xrepeat=48, yrepeat=48),
        526: SpriteInfo('Napalm Launcher', 'weapons', lowtag=46, xrepeat=48, yrepeat=48),
        539: SpriteInfo('Tesla Cannon', 'weapons', lowtag=45, xrepeat=48, yrepeat=48),
        548: SpriteInfo('Tesla Charge', 'ammo', lowtag=73, xrepeat=24, yrepeat=24),
        558: SpriteInfo('Tommy Gun', 'weapons', lowtag=42, xrepeat=48, yrepeat=48),
        559: SpriteInfo('Sawed Off', 'weapons', lowtag=41, xrepeat=48, yrepeat=48),
        589: SpriteInfo('Bundle of TNT', 'weapons', lowtag=62, xrepeat=48, yrepeat=48),
        618: SpriteInfo('Spray Can', 'weapons', lowtag=60, xrepeat=40, yrepeat=40),
        619: SpriteInfo('4 Shotgun Shells', 'ammo', lowtag=67, xrepeat=48, yrepeat=48),
        760: SpriteInfo('Crystal Ball', 'items', lowtag=121, xrepeat=40, yrepeat=40),
        #768: SpriteInfo('Shadow Cloak', 'items', lowtag=126, xrepeat=12, yrepeat=12),
        800: SpriteInfo('Life Leech', 'weapons', lowtag=50, xrepeat=48, yrepeat=48),
        801: SpriteInfo('Gasoline Can', 'ammo', lowtag=79, xrepeat=48, yrepeat=48),
        809: SpriteInfo('Case of TNT', 'weapons', lowtag=63, xrepeat=48, yrepeat=48),
        810: SpriteInfo('Remote Detonator', 'weapons', lowtag=65, xrepeat=40, yrepeat=40),
        811: SpriteInfo('Proximity Detonator', 'weapons', lowtag=64, xrepeat=40, yrepeat=40),
        812: SpriteInfo('Box of Shotgun Shells', 'ammo', lowtag=68, xrepeat=48, yrepeat=48),
        813: SpriteInfo('A Few Bullets', 'ammo', lowtag=69, xrepeat=48, yrepeat=48),
        816: SpriteInfo('Flares', 'ammo', lowtag=76, xrepeat=48, yrepeat=48),
        817: SpriteInfo('Full Drum of Bullets', 'ammo', lowtag=72, xrepeat=48, yrepeat=48),
        820: SpriteInfo('Trapped Soul', 'ammo', lowtag=66, xrepeat=24, yrepeat=24),
        #822: SpriteInfo('Medicine Pouch', 'items', lowtag=108, xrepeat=10, yrepeat=10),
        825: SpriteInfo('Invulnerability', 'items', lowtag=114, xrepeat=40, yrepeat=40),
        827: SpriteInfo('Boots of Jumping', 'items', lowtag=115, xrepeat=40, yrepeat=40),
        #828: SpriteInfo('Raven Flight', 'items', lowtag=116, xrepeat=12, yrepeat=12),
        829: SpriteInfo('Guns Akimbo', 'items', lowtag=117, xrepeat=40, yrepeat=40),
        830: SpriteInfo('Diving Suit', 'items', lowtag=118, xrepeat=80, yrepeat=64),
        #831: SpriteInfo('Gas Mask', 'items', lowtag=119, xrepeat=10, yrepeat=10),
        #832: SpriteInfo('Random Ammo', 'ammo', lowtag=80, xrepeat=12, yrepeat=12),
        839: SpriteInfo('Beast Vision', 'items', lowtag=125, xrepeat=40, yrepeat=40),
        #840: SpriteInfo('Rage Shroom', 'items', lowtag=127, xrepeat=12, yrepeat=12),
        841: SpriteInfo('Delirium Shroom', 'items', lowtag=128, xrepeat=48, yrepeat=48),
        #842: SpriteInfo('Grow Shroom', 'items', lowtag=129, xrepeat=12, yrepeat=12),
        #843: SpriteInfo('Shrink Shroom', 'items', lowtag=130, xrepeat=12, yrepeat=12),
        896: SpriteInfo('Limited Invisibility', 'items', lowtag=113, xrepeat=40, yrepeat=40),
        2169: SpriteInfo('Life Essence', 'items', lowtag=109, xrepeat=40, yrepeat=40),
        2428: SpriteInfo('Reflective Shots', 'items', lowtag=124, xrepeat=40, yrepeat=40),
        2433: SpriteInfo('Life Seed', 'items', lowtag=110, xrepeat=40, yrepeat=40),
        2578: SpriteInfo('Fire Armor', 'items', lowtag=142, xrepeat=64, yrepeat=64),
        2586: SpriteInfo('Body Armor', 'items', lowtag=141, xrepeat=64, yrepeat=64),
        2594: SpriteInfo('Super Armor', 'items', lowtag=144, xrepeat=64, yrepeat=64),
        2602: SpriteInfo('Spirit Armor', 'items', lowtag=143, xrepeat=64, yrepeat=64),
        2628: SpriteInfo('Basic Armor', 'items', lowtag=140, xrepeat=64, yrepeat=64),
    },
    swappableEnemies={
        #832: SpriteInfo('Random Creature', 'monsters', lowtag=200, xrepeat=0, yrepeat=0),
        1170: SpriteInfo('Axe Zombie', 'monsters', lowtag=203, xrepeat=40, yrepeat=40),
        1209: SpriteInfo('Sleep Zombie', 'monsters', lowtag=244, xrepeat=40, yrepeat=40),
        #1209: SpriteInfo('Sleep Zombie', 'monsters', lowtag=416, xrepeat=40, yrepeat=40),
        1270: SpriteInfo('Hound', 'monsters', lowtag=211, xrepeat=40, yrepeat=40),
        1370: SpriteInfo('Fat Zombie', 'monsters', lowtag=204, xrepeat=48, yrepeat=48),
        #1470: SpriteInfo('Stone Gargoyle', 'monsters', lowtag=206, xrepeat=40, yrepeat=40),
        1470: SpriteInfo('Stone Gargoyle', 'monsters', lowtag=207, xrepeat=40, yrepeat=40),
        #1530: SpriteInfo('Stone Statue', 'monsters', lowtag=208, xrepeat=40, yrepeat=40),
        1530: SpriteInfo('Stone Statue', 'monsters', lowtag=209, xrepeat=40, yrepeat=40),
        1570: SpriteInfo('Gill Beast', 'monsters', lowtag=217, xrepeat=48, yrepeat=48),
        1745: SpriteInfo('Rat', 'monsters', lowtag=220, xrepeat=24, yrepeat=24),
        #1792: SpriteInfo('Mother Pod', 'monsters', lowtag=221, xrepeat=32, yrepeat=32),
        #1792: SpriteInfo('Mother Pod', 'monsters', lowtag=223, xrepeat=48, yrepeat=48),
        1792: SpriteInfo('Mother Pod', 'monsters', lowtag=225, xrepeat=32, yrepeat=32),
        #1797: SpriteInfo('Mother Tentacle', 'monsters', lowtag=222, xrepeat=32, yrepeat=32),
        #1797: SpriteInfo('Mother Tentacle', 'monsters', lowtag=224, xrepeat=48, yrepeat=48),
        1797: SpriteInfo('Mother Tentacle', 'monsters', lowtag=225, xrepeat=48, yrepeat=48),
        1870: SpriteInfo('Eel', 'monsters', lowtag=218, xrepeat=32, yrepeat=32),
        1920: SpriteInfo('Spider', 'monsters', lowtag=213, xrepeat=16, yrepeat=16),
        #1920: SpriteInfo('Spider', 'monsters', lowtag=216, xrepeat=16, yrepeat=16),
        1980: SpriteInfo('Hand', 'monsters', lowtag=212, xrepeat=32, yrepeat=32),
        2680: SpriteInfo('Cerberus', 'monsters', lowtag=227, xrepeat=64, yrepeat=64),
        #2820: SpriteInfo('Beast Cultist', 'monsters', lowtag=201, xrepeat=40, yrepeat=40),
        #2820: SpriteInfo('Beast Cultist', 'monsters', lowtag=247, xrepeat=40, yrepeat=40),
        #2820: SpriteInfo('Beast Cultist', 'monsters', lowtag=248, xrepeat=40, yrepeat=40),
        2820: SpriteInfo('Beast Cultist', 'monsters', lowtag=249, xrepeat=40, yrepeat=40),
        3054: SpriteInfo('Earth Zombie', 'monsters', lowtag=205, xrepeat=40, yrepeat=40),
        3060: SpriteInfo('Phantasm', 'monsters', lowtag=210, xrepeat=40, yrepeat=40),
        #3385: SpriteInfo('Shotgun Cultist Prone', 'monsters', lowtag=230, xrepeat=40, yrepeat=40),
        3385: SpriteInfo('Shotgun Cultist Prone', 'monsters', lowtag=246, xrepeat=40, yrepeat=40),
        3798: SpriteInfo('Innocent', 'monsters', lowtag=245, xrepeat=40, yrepeat=40),
        3870: SpriteInfo('Tiny Caleb', 'monsters', lowtag=250, xrepeat=4, yrepeat=4),
    },
    addableEnemies=[1170, 1209, 1270, 1370, 1470, 1530, 1570, 1745, 1792, 1797, 1870, 1920, 1980, 2680, 3054, 3060, 3385, 3870],
    keyItems={
        2552: SpriteInfo('Skull Key', 'keys', lowtag=100, xrepeat=8, yrepeat=8),
        2553: SpriteInfo('Eye Key', 'keys', lowtag=101, xrepeat=8, yrepeat=8),
        2554: SpriteInfo('Fire Key', 'keys', lowtag=102, xrepeat=8, yrepeat=8),
        2555: SpriteInfo('Dagger Key', 'keys', lowtag=103, xrepeat=8, yrepeat=8),
        2556: SpriteInfo('Spider Key', 'keys', lowtag=104, xrepeat=8, yrepeat=8),
        2557: SpriteInfo('Moon Key', 'keys', lowtag=105, xrepeat=8, yrepeat=8),
        2558: SpriteInfo('Key 7', 'keys', lowtag=106, xrepeat=8, yrepeat=8),
    },
    traps={
        655: SpriteInfo('Saw Blade', 'traps', lowtag=454),
        835: SpriteInfo('Guillotine', 'traps', lowtag=458),
        908: SpriteInfo('Hidden Exploder', 'traps', lowtag=459, xrepeat=1, yrepeat=16),
        1080: SpriteInfo('Pendulum', 'traps', lowtag=457),
        1156: SpriteInfo('Switched Zap', 'traps', lowtag=456),
        2183: SpriteInfo('Flame Trap', 'traps', lowtag=452),
    },
    switches={
        318: SpriteInfo('1-Way Switch', 'switches', lowtag=21, xrepeat=12, yrepeat=12),
        912: SpriteInfo('Padlock (1-Shot)', 'switches', lowtag=23, xrepeat=12, yrepeat=12),
        982: SpriteInfo('1-Way Switch', 'switches', lowtag=21, xrepeat=12, yrepeat=12),
        1012: SpriteInfo('1-Way Switch', 'switches', lowtag=21, xrepeat=12, yrepeat=12),
        1046: SpriteInfo('1-Way Switch', 'switches', lowtag=21, xrepeat=12, yrepeat=12),
        1070: SpriteInfo('1-Way Switch', 'switches', lowtag=21, xrepeat=12, yrepeat=12),
        1072: SpriteInfo('1-Way Switch', 'switches', lowtag=21, xrepeat=12, yrepeat=12),
        1074: SpriteInfo('1-Way Switch', 'switches', lowtag=21, xrepeat=12, yrepeat=12),
        1076: SpriteInfo('1-Way Switch', 'switches', lowtag=21, xrepeat=12, yrepeat=12),
        1078: SpriteInfo('1-Way Switch', 'switches', lowtag=21, xrepeat=12, yrepeat=12),
        1161: SpriteInfo('Combination Switch', 'switches', lowtag=22, xrepeat=12, yrepeat=12),
        2532: SpriteInfo('Combination Switch', 'switches', lowtag=22, xrepeat=12, yrepeat=12),
    },
    bosses={
        3140: SpriteInfo('Tchernobog', 'monsters', lowtag=229, xrepeat=64, yrepeat=64),
    }
)


# difficulty > 0 means higher number makes the game harder
AddConSettings('Ion Fury', conFiles = {
    'scripts/customize.con': [
        ConVar('.*\wHEALTH', -1, range=0.5),
        ConVar('MEDKIT_HEALTHAMOUNT', -1, range=0.5),
        ConVar('.*MAXAMMO', -1),
        ConVar('.*AMOUNT', -1),

        ConVar('.*_DMG', 0), # not sure if this affects enemies too or just the player?

        ConVar('.*_HEALTH', 1),
    ]
})

AddConSettings('Duke Nukem 3D', conFiles = {
    'USER.CON': [
        ConVar('TRIPBOMB_STRENGTH', -1, balance=1.5),
        ConVar('HANDBOMB_WEAPON_STRENGTH', -1, balance=1.5),
        ConVar('YELLHURTSOUNDSTRENGTH', 0, range=0),
        ConVar('SWEARFREQUENCY', 0),
        ConVar('.*HEALTH', -1, range=0.5),
        ConVar('MAX.*AMMO', -1),
        ConVar('.*AMMOAMOUNT', -1),
        ConVar('.*_AMOUNT', -1),
        ConVar('HANDBOMBBOX', -1),
        ConVar('.*_WEAPON_STRENGTH', -1),

        ConVar('.*\wSTRENGTH', 1),
        ConVar('PIG_SHIELD_AMOUNT\d', 1),

        # idk what these do
        ConVar('OCTASCRATCHINGPLAYER', 0),
        ConVar('LIZGETTINGDAZEDAT', 0),
        ConVar('LIZEATINGPLAYER', 0),
        ConVar('NEWBEASTSCRATCHAMOUNT', 0),
    ]
})
