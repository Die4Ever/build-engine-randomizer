from BuildGames import *

AddGame('Platoon Leader', 'WWII GI', 37852572, 'D1ED8C0C') # PLATOONL_CRC

AddGame('NAPALM.GRP',                         'Napalm',                 44365728, '3DE1589A', 'D926E362839949AA6EBA5BDF35A5F2D6', '9C42E7268A45D57E4B7961E6F1D3414D9DE12323') # NAPALM.GRP
#AddGame('NAPALM.RTS',                        'Napalm',                   564926, '12505172', 'D571897B4E3D43B3757A98C856869ED7', 'C90B050192030FFBD0137C03A4181CB1705B95D3') # NAPALM.RTS
#AddGame('NAPALM.CON (GAME.CON)',             'Napalm',                   142803, '75EF92BD', 'CCBBB146C094F490242FD922293DD5F9', '46F3AE2B37983660835F220AECEEA6060C89F2A7') # NAPALM.CON (GAME.CON)
AddGame('NAM.GRP',                            'NAM',                    43448927, '75C1F07B', '6C910A5438E230F85804353AC54D77B9', '2FD12F94246FBD3014223B76301B812EE8341D05') # NAM.GRP
#AddGame('NAM.RTS',                           'NAM',                      564926, '12505172', 'D571897B4E3D43B3757A98C856869ED7', 'C90B050192030FFBD0137C03A4181CB1705B95D3') # NAM.RTS
#AddGame('NAM.CON (GAME.CON)',                'NAM',                      142803, '75EF92BD', 'CCBBB146C094F490242FD922293DD5F9', '46F3AE2B37983660835F220AECEEA6060C89F2A7') # NAM.CON (GAME.CON)
AddGame('WW2GI.GRP',                          'WWII GI',                77939508, '907B82BF', '27E927BEBA43447DB3951EAADEDB4709', 'FD0208A55EAEF3937C126E1FFF474FB4DFBDA6F5') # WW2GI.GRP
#AddGame('WW2GI.RTS',                         'WWII GI',                  259214, '79D16760', '759F66C9F3C70AEDCAE29473AADE9966', 'CE352EF4C22F85869FDCB060A64EBC263ACEA6B0') # WW2GI.RTS

AddGame('A.W.O.L. v0.91',                     'AWOL',                  252384950, '894F0199', '0161F85CEE80E1A60A28F40643BF02B2', 'C797F9D3BED6BADAD62C4C9C14D78F34058D97A8', canUseRandomizerFolder=False) # AWOL.GRP
AddGame('A.W.O.L.',                           'AWOL',                  244458025, 'DA99945F', '11812e4a50f6151c14df64bf0caae33a', '44393A5DC91BFC59533C679575A5ECD977B416C2', canUseRandomizerFolder=False) # AWOL.GRP r9597-bb01a1394


AddMapSettings('AWOL', minMapVersion=7, maxMapVersion=9,
    swappableItems = {
    },
    swappableEnemies = {
    },
    addableEnemies = [],
    triggers={}
)
# ['awol.con', 'data/awol_aibot.con', 'data/awol_astar.con', 'data/awol_choreo.con', 'data/awol_choreo_scripts.con', 'data/awol_common.con', 'data/awol_customize.con', 'data/awol_cutscene_script1.con', 'data/awol_cutscene_script10.con', 'data/awol_cutscene_script11.con', 'data/awol_cutscene_script2.con', 'data/awol_cutscene_script3.con', 'data/awol_cutscene_script4.con', 'data/awol_cutscene_script5.con', 'data/awol_cutscene_script6.con', 'data/awol_cutscene_script7.con', 'data/awol_cutscene_script8.con', 'data/awol_cutscene_script9.con', 'data/awol_cutscenes.con', 'data/awol_env.con', 'data/awol_ghost.con', 'data/awol_interactables.con', 'data/awol_inventory.con', 'data/awol_levels.con', 'data/awol_main.con', 'data/awol_materials.con', 'data/awol_materials_defs.con', 'data/awol_materials_init.con', 'data/awol_names.con', 'data/awol_nodegraph.con', 'data/awol_objective_scripts.con', 'data/awol_pickups.con', 'data/awol_player.con', 'data/awol_scripted.con', 'data/awol_sounds.con', 'data/awol_subtitles.con', 'data/awol_text.con', 'data/awol_tokens.con', 'data/awol_ui.con', 'data/awol_vfx.con', 'data/awol_weapons.con', 'data/awol_weather.con', 'data/enemy_arctic.con', 'data/enemy_arena.con', 'data/enemy_flyers.con', 'data/enemy_guerrilla.con', 'data/enemy_insurgent.con', 'data/enemy_jungle.con', 'data/enemy_legacy.con', 'data/enemy_security.con', 'data/enemy_shared.con', 'data/mikko.con']
AddConSettings('AWOL', conFiles = {
})
