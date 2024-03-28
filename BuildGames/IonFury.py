from BuildGames import *

AddGame('Ion Fury',                           'Ion Fury',               92644120, '960B3686', 'd834055f0c9a60f8f23163b67d086546', '2cec5ab769ae27c6685d517defa766191c5e66c1', canUseRandomizerFolder=False, canUseGrpFile=True) # Steam version
AddGame('Ion Fury',                           'Ion Fury',               92644105, 'F3A52423', '2f2a861001ab446bd32a78667f91db40', '9b763ff2caf112d9aa9e4f5ed7a9a26c98af6eaa', canUseRandomizerFolder=False, canUseGrpFile=True) # Steam version version v2.0.01.10459

AddGame('Ion Fury Aftershock',                'Ion Fury Aftershock',    163939122, '2D7CAC72', 'a326052d456a9c9a80ca13cb90270d5b', '720b17e4110448e33129504918feea3dc23fe900', canUseRandomizerFolder=False, canUseGrpFile=True) # Steam Aftershock version
AddGame('Ion Fury Aftershock',                'Ion Fury Aftershock',    163948283, 'AE68B9E7', '7bfcea0b46d3afb206cbc5f4a2e3282c', '8177341cd8691b6a8667fd51d0ed9837ce74d523', canUseRandomizerFolder=False, canUseGrpFile=True) # Steam Aftershock version v3.0.03.104182
AddGame('Ion Fury Aftershock',                'Ion Fury Aftershock',    160826590, 'E175FB41', 'cbd077bb55dd4f776a937a104807797f', '78c142276411ebfef7ece2133ed5c4f0b428dc65', canUseRandomizerFolder=False, canUseGrpFile=True) # Steam Aftershock version v3.0.0.9.10514

ion_fury_map_settings = dict(minMapVersion=7, maxMapVersion=9,
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

        # Aftershock
        # define I_BANSHEE                        16083
        # define I_COLLECTIBLE                    17200
        17201: SpriteInfo('I_WRECKER'),
        17202: SpriteInfo('I_GRENADELAUNCHER_GAS'),
        17203: SpriteInfo('I_SHOTGUN_CLUSTER'),
        17204: SpriteInfo('I_GASGRENADE_AMMO'),
        17205: SpriteInfo('I_CLUSTER_AMMO'),
        17211: SpriteInfo('I_WRECKER_AMMO'),
        17212: SpriteInfo('I_WRECKER_AMMO_SIXPACK'),
        17206: SpriteInfo('I_BOOM_BAG'),
        17207: SpriteInfo('I_INVULNERABILITY'),
        17208: SpriteInfo('I_POCKET_PARASITE'),
        17209: SpriteInfo('I_AGILITY_SURGE'),
        17210: SpriteInfo('I_GOLDEN_GUN'),
        17213: SpriteInfo('I_FLAMETRAP'),
        17214: SpriteInfo('I_INFLATABLE_CHAIR'),
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

AddMapSettings('Ion Fury', **ion_fury_map_settings)
AddMapSettings('Ion Fury Aftershock', **ion_fury_map_settings)

ion_fury_game_settings = dict(
    mainScript='scripts/main.con', defName='fury.def', flags=128,
    commands = dict(# https://voidpoint.io/terminx/eduke32/-/blob/master/source/duke3d/src/cmdline.cpp#L39
        grp=OrderedDict(eduke32='-nosetup -g', fury='-nosetup -g'),
        folder=OrderedDict(eduke32='-nosetup -j '),
        simple={}
    ),
    conFiles = {
        'scripts/customize.con': [
            ConVar('.*\wHEALTH', -1, range=0.5),
            ConVar('MEDKIT_HEALTHAMOUNT', -1, range=0.5),
            ConVar('.*MAXAMMO', -1),
            ConVar('.*AMOUNT', -1),

            ConVar('.*_DMG', 0), # not sure if this affects enemies too or just the player?

            ConVar('.*_HEALTH', 1),
        ]
    }
)

aftershock_game_settings = {**ion_fury_game_settings, 'defName':'ashock.def'}

AddGameSettings('Ion Fury', **ion_fury_game_settings)
AddGameSettings('Ion Fury Aftershock', **aftershock_game_settings)
