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
    def __init__(self, gameName=None, minMapVersion=7, maxMapVersion=9, swappableItems={}, swappableEnemies={}, addableEnemies={}, triggers={}, additions={}):
        self.gameName = gameName
        self.minMapVersion = minMapVersion
        self.maxMapVersion = maxMapVersion
        self.swappableItems = swappableItems
        self.swappableEnemies = swappableEnemies
        self.addableEnemies = addableEnemies
        self.triggers = triggers
        self.additions = additions

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

def SpriteRange(min, max, value):
    d={}
    for i in range(min,max+1):
        d[i] = value
    return d




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
    },
    addableEnemies = {
        7300: 'A_MECHSECT',
        12096: 'A_CULTIST',
        12288: 'A_GREATER',
        11796: 'A_SHOTGUNNER',
        12925: 'A_BRUTE',
        11600: 'A_DRONE',
        11450: 'A_DEACON',
        13175: 'A_ARCHANGEL',
        13350: 'A_WENTEKO',
        13600: 'A_NUKEMUTANT',
        13685: 'A_NUKEMUTANT_RISE',
        13720: 'A_NUKEMUTANT_GDF',
        13785: 'A_NUKEMUTANT_GDF_RISE',
        11392: 'A_PSEUDO_ENEMY',
        13850: 'A_HESKEL_BOT',
    },
    triggers={}
)

AddMapSettings('Duke Nukem 3D', minMapVersion=7, maxMapVersion=9,
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
        #2219: 'EXPLOSION2BOT',
        2370: 'GREENSLIME',
        2371: 'GREENSLIME2',
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
    },
    addableEnemies = {
        675: 'EGG',
        1680: 'LIZTROOP',
        1820: 'OCTABRAIN',
        1880: 'DRONE',
        1920: 'COMMANDER',
        1960: 'RECON',
        1975: 'TANK',
        2000: 'PIGCOP',
        2120: 'LIZMAN',
        2370: 'GREENSLIME',
        4610: 'NEWBEAST',
    },
    triggers = {
        # 675 EGG doesn't work for spawning?
        9: dict(name='RESPAWN', hightags=[1680, 1820, 1960, 2000, 2120, 2370], lowtags=[]),
    },
    additions = {
        # lower case because python doesn't have case-insensitive dicts
        'e1l3.map': [ # ensure the player gets weapons to start with
                dict(pos=[24160, 52032, 45056], sectnum=296, choices=[21,22,23,24,25,26,27,28,29]), # under the chair
                dict(pos=[28096, 50688, 22528], sectnum=297, choices=[21,22,23,24,25,26,27,28,29]), # in the locker
                dict(pos=[47864, 29653, 20480], sectnum=265, choices=[23,47]), # explosives near the end of the map
                dict(pos=[47270, 25876, 34370], sectnum=272, texcoords=[8, 8, 0, 0], choices=[26]), # single pipe bomb near the end of the map
            ]
    }
)

# https://forums.duke4.net/topic/11406-shadow-warrior-scriptset-for-mapster32/
# using find and replace regex on duke3d.def from the above link
# voxel "([^"]+)"\s+\{\s+tile\s+(\d+)\s+\}
# $2: '$1',
AddMapSettings('Shadow Warrior', minMapVersion=7, maxMapVersion=7,
    swappableItems = {
        1802: 'medpak',
        1803: 'medkit',
        1797: 'uzi',
        1817: 'grenade',
        764: 'gunbarl',
        765: 'camera',
        1831: '40mmbox',
        1842: 'mines',
        1794: 'shotgun',
        1818: 'rocket',
        1823: 'shtgammo',
        1800: 'rcktammo',
        1813: 'tools',
        1799: 'uziclip',
        3031: 'nitevis',
        1811: 'railgun',
        1812: 'railpak',
        3030: 'armor',
        1793: 'star',
        1819: 'heat',
        1792: 'coin',
        1824: 'heart',
        1825: 'heart2',
        1807: 'uziside',
        1809: 'bomb',
        1808: 'smoke',
        1805: 'flash',
        1814: 'gorohead',
        1804: 'shadow',
        1829: 'caltrop',
        1810: 'cookie',
        #1766: 'techkey',
        1765: 'oldkey',
        # 2520: 'flag1',
        # 2521: 'flag2',
        # 2522: 'flag3',
        # 1767: 'keycard',
        # 1846: 'oldlock',
        # 1847: 'oldlock2',
        # 1850: 'kcrdlck1',
        # 1851: 'kcrdlck2',
        # 1852: 'tchklck1',
        # 1853: 'tchklck2',
        # 1854: 'tchklck3',
        # 1765: 'MASTER_KEY1',# gold
        # 1769: 'oldkey',# silver
        # 1773: 'oldkey',# bronze
        # 1777: 'oldkey',# red
        # 1770: 'techkey',
        # 1774: 'techkey',
        # 1778: 'techkey',
        # 1771: 'keycard',
        # 1775: 'keycard',
        # 1779: 'keycard',
        817: 'mine',
        818: 'mine2',
        819: 'mine3',
        #2470: 'EXIT_SWITCH'
    },
    swappableEnemies = {
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
    },
    addableEnemies = {
        4096: 'EVIL_NINJA',
        4320: 'BIG_RIPPER',
        1210: 'SUMO_BOSS',
        1300: 'SERPENT_BOSS',
        1400: 'COOLIE',
        1441: 'COOLIE_GHOST',
        1469: 'GREEN_GUARDIAN',
        5426: 'ZILLA_BOSS',
        5162: 'FEMALE_WARRIOR',
        1580: 'LITTLE_RIPPER',
        800: 'HORNET',
    },
    triggers={}
)
# Keys (picnums 1765-1779)
# Locks 1846-1854


AddMapSettings('PowerSlave', minMapVersion=6, maxMapVersion=6,
    swappableItems={
        488: 'Pistol',
        490: 'Machine Gun',
        491: 'Fancy Gun',
    },
    swappableEnemies={
        1526: 'Mummy',# to 1531
        1664: 'Mummy',# to 1746
        1949: 'Mummy',# to 1963
        2311: 'Anubis Zombie',# to 2373
        2432: 'Omenwasp',# to 2497 and 2552?
        2498: 'Armadillo',# to 2548
        2559: 'Boss Looking Biped',# to 2642 and 2687
        2643: 'Boss Looking Serpent',# to 2675
        2698: 'Boss Looking Spider',# to 2750
        2751: 'Lion Woman',# to 2816 and 3038 to 3049?
        2817: 'Dude With Gun',# to 3032
        3072: 'Scorpion',# to 3136 and 3151 to 3181?
        3137: 'Mouth',# to 3147
        3200: 'Grasshopper',# to 3250
    },
    triggers={},
    additions={}
)


AddMapSettings('Blood', minMapVersion=7, maxMapVersion=7,
    swappableItems={
        519: 'Doctor\'s Bag',
        524: 'Flare Gun',
        525: 'Voodoo Doll',
        526: 'Napalm Launcher',
        527: 'Random Weapon',
        589: 'Dynamite',
        619: 'Shells',
        760: 'Crystal Ball',
        800: 'Life Leech',
        802: 'Gasoline',
        809: 'TNT',
        810: 'Remote Mine',
        811: 'Proximity Mine',
        812: 'Shells',
        813: 'Bullets',
        814: 'Bullets',
        815: 'Ammo',
        816: 'Flares',
        817: 'Shield', # ?
        818: 'Flares',
        819: 'Flares',
        820: 'Soulsphere', # ?
        822: 'Medicine Pouch',
        827: 'Jumping Boots',
        829: 'Akimbo',
        830: 'Diving Suit',
        831: 'Something?',
        837: 'Suit',
        839: 'Beastvision',
        **SpriteRange(2169, 2172, 'Life Essence'),
        **SpriteRange(2428, 2432, 'Reflective Shots'),
        **SpriteRange(2433, 2437, 'Life Seed'),
        # GUI elements?
        # 2560: 'Jumping Boots',
        # 2561: 'Skulls',
        # 2562: 'Something?',
        # 2563: 'Shadow Cloak',
        # 2564: 'Diving Helmet',
        # 2565: 'Diving Suit',
        # 2566: 'Crystal Ball',
        # 2567: 'Akimbo',
        # 2568: 'Beast Vision',
        # 2569: 'Health',
        2578: 'Fire Armor',
        2586: 'Body Armor',
        2594: 'Super Armor',
        2602: 'Spirit Armor',
        2628: 'Basic Armor',
        #**SpriteRange(2552, 2558, 'Key'),
    },
    swappableEnemies={
        **SpriteRange(1170, 1258, 'Zombie'),
        **SpriteRange(1270, 1324, 'Hellhound'),
        **SpriteRange(3724, 3728, 'Hellhound Skeleton'),
        **SpriteRange(1370, 1442, 'Fat Zombie'),
        **SpriteRange(3604, 3623, 'Fat Zombie'),
        **SpriteRange(1470, 1536, 'Gargoyle'),
        **SpriteRange(3719, 3723, 'Stone Gargoyle'),
        **SpriteRange(1570, 1662, 'Gill Beast'),
        **SpriteRange(3734, 3738, 'Gill Beast Skeleton'),
        **SpriteRange(1745, 1764, 'Rat'),
        **SpriteRange(1792, 1820, 'Acid Pod'),
        #**SpriteRange(1024, 1028, 'Tchernobog'),
        #**SpriteRange(1835, 1854, 'Tchernobog'),
        #**SpriteRange(3140, 3144, 'Tchernobog'),
        **SpriteRange(1870, 1889, 'Bone Eel'),
        **SpriteRange(3729, 3733, 'Bone Eel'),
        **SpriteRange(1908, 1947, 'Spider'),
        **SpriteRange(1948, 1974, 'Bat'),
        **SpriteRange(1980, 2011, 'Hand from Hell'),
        **SpriteRange(2659, 2806, 'Cerberus'),
        **SpriteRange(2820, 2909, 'Cultist'),
        **SpriteRange(2955, 3040, 'Beast'),
        **SpriteRange(3584, 2603, 'Beast Swimming'),
        **SpriteRange(3694, 3718, 'Beast'),
        **SpriteRange(3060, 3114, 'Phantasm'),
        **SpriteRange(3739, 3743, 'Phantasm Skeleton'),
        **SpriteRange(3663, 3677, 'Skeleton'), # ?
    },
    addableEnemies={
    })


# difficulty > 0 means higher number makes the game harder
AddConSettings('Ion Fury', conFiles = {
    'scripts/customize.con': {
        '.*\wHEALTH': {'difficulty': -1},
        '.*MAXAMMO': {'difficulty': -1},
        '.*AMOUNT': {'difficulty': -1},

        '.*_DMG': {'difficulty': 0}, # not sure if this affects enemies too or just the player?

        '.*_HEALTH': {'difficulty': 1},
    }
})

AddConSettings('Duke Nukem 3D', conFiles = {
    'USER.CON': {
        'SWEARFREQUENCY': {'difficulty': 0},
        '.*HEALTH': {'difficulty': -1},
        'MAX.*AMMO': {'difficulty': -1},
        '.*AMMOAMOUNT': {'difficulty': -1},
        '.*_AMOUNT': {'difficulty': -1},
        'HANDBOMBBOX': {'difficulty': -1},
        '.*_WEAPON_STRENGTH': {'difficulty': -1},

        '.*\wSTRENGTH': {'difficulty': 1},
        'PIG_SHIELD_AMOUNT\d': {'difficulty': 1},

        # idk what these do
        'OCTASCRATCHINGPLAYER': {'difficulty': 0},
        'LIZGETTINGDAZEDAT': {'difficulty': 0},
        'LIZEATINGPLAYER': {'difficulty': 0},
        'NEWBEASTSCRATCHAMOUNT': {'difficulty': 0},
    }
})
