from BuildGames import *

AddGame('PowerSlave',                         'PowerSlave',             26904012, 'AC80ECB6', '4ae5cbe10396147ae042463b7df8010f', '548751e10f5c25f80d95321565b13f4664434981', canUseGrpFile=True) # STUFF.DAT
AddGame('PowerSlave',                         'PowerSlave',             27108170, 'E3B172F1', 'b51391e08a17e5c46e25f6cf46f892eb', 'b84fd656be67271910e5eba4caf69bc81192c174', canUseGrpFile=True) # STUFF.DAT
AddGame('PowerSlave Demo',                    'PowerSlave',             15904838, '1D8C7645', '61f5b2871e57e757932f338adefbc878', '6bb4b2974da3d90e70c6b4dc56b296f907c180f0', canUseGrpFile=True) # STUFF.DAT shareware
AddGame('Exhumed Demo',                       'PowerSlave',             16481687, '1A6E27FA', 'e368de92d99e4fb85ebe5f188eb175e3', '2062fec5d513850b3c3dc66c7d44c4b0f91296db', canUseGrpFile=True) # STUFF.DAT shareware

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

AddGameSettings('PowerSlave',
    commands= dict(
        grp={'pcexhumed': '-nosetup -g'},
        folder={'pcexhumed': '-nosetup -j '}
    )
)
