import cProfile
import glob
import os
import shutil
import unittest
from hashlib import md5
from mmap import mmap, ACCESS_READ
from pathlib import Path
from typeguard import typechecked, importhook
from unittest import case

profiling = 0
if not profiling:
    importhook.install_import_hook('BuildLibs')
from BuildLibs import buildmap, crc32, games, trace, setVerbose
from BuildLibs.grp import CreateGrpFile, GrpBase, GrpZipFile, LoadGrpFile


unittest.TestLoader.sortTestMethodsUsing = None
temp:Path = Path('temp/')
zippath:Path = Path('duke3d-shareware.grp.zip')
tempgrp:Path = Path('temp/testing.grp')

settings = {
    'MapFile.chanceDupeItem': 0.5,
    'MapFile.chanceDeleteItem': 0.5,
    'MapFile.chanceDupeEnemy': 0.5,
    'MapFile.chanceDeleteEnemy': 0.5,
    'MapFile.itemVariety': 0,
    'MapFile.enemyVariety': 0,
    'conFile.range': 1,
    'conFile.scale': 1,
    'conFile.difficulty': 0.5,
}

different_settings = {
    'MapFile.chanceDupeItem': 0.75,
    'MapFile.chanceDeleteItem': 0.25,
    'MapFile.chanceDupeEnemy': 0.75,
    'MapFile.chanceDeleteEnemy': 0.25,
    'MapFile.itemVariety': 0,
    'MapFile.enemyVariety': 0,
    'conFile.range': 1.5,
    'conFile.scale': 0.8,
    'conFile.difficulty': 0.7,
}

# zipped for tests
games.AddGame('ZIPPED Shareware DUKE3D.GRP v1.3D', 'Duke Nukem 3D', 4570468, 'BFC91225', '9eacbb74e107fa0b136f189217ce41c7', '4bdf21e32ec6a3fc43092a50a51fce3e4ad6600d') # ZIPPED Shareware DUKE3D.GRP v1.3D for tests

# we need the correct file order so we can match the md5
original_order = [
'DEFS.CON', 'GAME.CON', 'USER.CON', 'D3DTIMBR.TMB', 'DUKESW.BIN', 'LOOKUP.DAT', 'PALETTE.DAT',
'TABLES.DAT', 'SECRET.VOC', 'BLANK.VOC', 'ROAM06.VOC', 'ROAM58.VOC', 'PREDRG.VOC', 'GBLASR01.VOC',
'PREDPN.VOC', 'PREDDY.VOC', 'CHOKN12.VOC', 'PREDRM.VOC', 'LIZSPIT.VOC', 'PIGRM.VOC', 'ROAM29.VOC',
'ROAM67.VOC', 'PIGRG.VOC', 'PIGPN.VOC', 'PIGDY.VOC', 'PIGWRN.VOC', 'OCTARM.VOC', 'OCTARG.VOC', 'OCTAAT1.VOC',
'OCTAAT2.VOC', 'OCTAPN.VOC', 'OCTADY.VOC', 'BOS1RM.VOC', 'BOS1RG.VOC', 'BOS1PN.VOC', 'BOS1DY.VOC', 'KICKHIT.VOC',
'RICOCHET.VOC', 'BULITHIT.VOC', 'PISTOL.VOC', 'CLIPOUT.VOC', 'CLIPIN.VOC', 'CHAINGUN.VOC', 'SHOTGNCK.VOC',
'RPGFIRE.VOC', 'BOMBEXPL.VOC', 'PBOMBBNC.VOC', 'WPNSEL21.VOC', 'SHRINK.VOC', 'LSRBMBPT.VOC', 'LSRBMBWN.VOC',
'SHRINKER.VOC', 'VENTBUST.VOC', 'GLASS.VOC', 'GLASHEVY.VOC', 'SHORTED.VOC', 'SPLASH.VOC', 'ALERT.VOC', 'REACTOR.VOC',
'SUBWAY.VOC', 'GEARGRND.VOC', 'GASP.VOC', 'GASPS07.VOC', 'PISSING.VOC', 'KNUCKLE.VOC', 'DRINK18.VOC', 'EXERT.VOC',
'HARTBEAT.VOC', 'PAIN13.VOC', 'PAIN28.VOC', 'PAIN39.VOC', 'PAIN87.VOC', 'WETFEET.VOC', 'LAND02.VOC', 'DUCTWLK.VOC',
'PAIN54.VOC', 'PAIN75.VOC', 'PAIN93.VOC', 'PAIN68.VOC', 'DAMN03.VOC', 'DAMNIT04.VOC', 'COMEON02.VOC', 'WAITIN03.VOC',
'COOL01.VOC', 'AHMUCH03.VOC', 'DANCE01.VOC', 'LETSRK03.VOC', 'READY2A.VOC', 'RIPEM08.VOC', 'ROCKIN02.VOC',
'AHH04.VOC', 'GULP01.VOC', 'PAY02.VOC', 'AMESS06.VOC', 'BITCHN04.VOC', 'DOOMED16.VOC', 'HOLYCW01.VOC',
'HOLYSH02.VOC', 'IMGOOD12.VOC', 'ONLYON03.VOC', 'PIECE02.VOC', 'RIDES09.VOC', '2RIDE06.VOC', 'THSUK13A.VOC',
'WANSOM4A.VOC', 'MYSELF3A.VOC', 'NEEDED03.VOC', 'SHAKE2A.VOC', 'DUKNUK14.VOC', 'GETSOM1A.VOC', 'GOTHRT01.VOC',
'GROOVY02.VOC', 'WHRSIT05.VOC', 'BOOBY04.VOC', 'DIESOB03.VOC', 'DSCREM04.VOC', 'LOOKIN01.VOC', 'PISSIN01.VOC',
'GETITM19.VOC', 'SCUBA.VOC', 'JETPAKON.VOC', 'JETPAKI.VOC', 'JETPAKOF.VOC', 'GOGGLE12.VOC', 'THUD.VOC',
'SQUISH.VOC', 'TELEPORT.VOC', 'GBELEV01.VOC', 'GBELEV02.VOC', 'SWITCH.VOC', 'FLUSH.VOC', 'QUAKE.VOC',
'MONITOR.VOC', 'POOLBAL1.VOC', 'ONBOARD.VOC', 'BUBBLAMB.VOC', 'MACHAMB.VOC', 'WIND54.VOC', 'STEAMHIS.VOC',
'BARMUSIC.VOC', 'WARAMB13.VOC', 'WARAMB21.VOC', 'WARAMB23.VOC', 'WARAMB29.VOC', 'COMPAMB.VOC', 'SLIDOOR.VOC',
'OPENDOOR.VOC', 'EDOOR10.VOC', 'EDOOR11.VOC', 'FSCRM10.VOC', 'H2OGRGL2.VOC', 'GRIND.VOC', 'ENGHUM.VOC',
'LAVA06.VOC', 'PHONBUSY.VOC', 'ROAM22.VOC', 'AMB81B.VOC', 'ROAM98B.VOC', 'H2ORUSH2.VOC', 'PROJRUN.VOC',
'FIRE09.VOC', '!PRISON.VOC', '!PIG.VOC', '!BOSS.VOC', 'MICE3.VOC', 'DRIP3.VOC', 'ITEM15.VOC', 'BONUS.VOC',
'CATFIRE.VOC', 'KILLME.VOC', 'SHOTGUN7.VOC', 'DMDEATH.VOC', 'HAPPEN01.VOC', 'DSCREM15.VOC', 'DSCREM16.VOC',
'DSCREM17.VOC', 'DSCREM18.VOC', 'DSCREM38.VOC', 'RIP01.VOC', 'NOBODY01.VOC', 'CHEW05.VOC', 'LETGOD01.VOC',
'HAIL01.VOC', 'BLOWIT01.VOC', 'EATSHT01.VOC', 'FACE01.VOC', 'INHELL01.VOC', 'SUKIT01.VOC', 'PISSES01.VOC',
'GRABBAG.MID', 'STALKER.MID', 'DETHTOLL.MID', 'STREETS.MID', 'WATRWLD1.MID', 'SNAKE1.MID', 'THECALL.MID',
'TILES000.ART', 'TILES001.ART', 'TILES002.ART', 'TILES003.ART', 'TILES004.ART', 'TILES005.ART', 'TILES006.ART',
'TILES007.ART', 'TILES008.ART', 'TILES009.ART', 'TILES010.ART', 'TILES011.ART', 'TILES012.ART', 'E1L1.MAP',
'E1L2.MAP', 'E1L3.MAP', 'E1L4.MAP', 'E1L5.MAP', 'E1L6.MAP'
]

@typechecked
class BERandoTestCase(unittest.TestCase):
    def subTest(self, msg=case._subtest_msg_sentinel, **params):
        print('\n----------------------------------\nstarting subTest', msg, '\n----------------------------------')
        return super().subTest(msg, **params)

    @classmethod
    def tearDownClass(cls):
        # GitHub Actions doesn't show STDERR
        print('Finished '+ str(cls.__name__))
        super().tearDownClass()

    def test_1_extract_zipgrp(self):
        # I zipped the GRP file to save space in the repo
        # but also Ion Fury uses ZIP format anyways so we do need to test it
        grp: GrpBase = None
        with self.subTest('ExtractAll'):
            grp = LoadGrpFile(zippath)
            self.assertEqual(len(grp.files), len(original_order))
            grp.ExtractAll(temp)

        with self.subTest('CreateGrpFile'):
            CreateGrpFile(temp, tempgrp, original_order)

        grp = None
        with self.subTest('Verify new GRP File'):
            grp = LoadGrpFile(tempgrp)
            self.assertEqual(grp.game.type, 'Duke Nukem 3D')

    def test_rando(self):
        # first get vanilla MD5s
        with self.subTest('Open GRP File'):
            grp: GrpFile = LoadGrpFile(tempgrp)
        vanilla = self.Md5GameFiles('Vanilla', grp, temp)
        self.assertIsNotNone(vanilla, 'Vanilla MD5s')
        self.assertGreater(len(vanilla), 0, 'Vanilla MD5s')

        # now test randomizing with different seeds and settings, comparing MD5s each time
        grp0451 = self.TestRandomize(tempgrp, 451, vanilla, False)
        self.assertDictEqual(grp0451, {'E1L1.MAP': '92d3555d92495f1d158844def24d3653', 'E1L2.MAP': 'a1ff6de8e3ff85e7de201bf6f93d59a7', 'E1L3.MAP': '9fb5450bd3781d70fa3e95d70aa50b1a', 'E1L4.MAP': 'f3fd61103fe07e90afbf19f2b99a83fb', 'E1L5.MAP': '8affa9fe8ddb2ecc5951a87788629417', 'E1L6.MAP': 'c8d921798945faa9a9321ad018fc80d2', 'USER.CON': '9b1c55539cf34de3076cc7510b4eff50'})
        self.TestRandomize(zippath, 2052, grp0451, False)
        self.TestRandomize(tempgrp, 451, grp0451, True)
        self.TestRandomize(tempgrp, 451, grp0451, False, settings=different_settings)


    def test_external_files(self):
        try:
            with self.subTest('Create External File'):
                testdata = 'Damn, I\'m lookin good!'
                extname = 'external_file.txt'
                gamedir = Path(tempgrp).parent
                extpath = Path(gamedir, extname)
                with open(extpath, 'w') as file:
                    file.write(testdata)

            with self.subTest('Open GRP File'):
                games.AddGame('Shareware DUKE3D.GRP v1.3D',         'Duke Nukem 3D',          11035779, '983AD923', 'C03558E3A78D1C5356DC69B6134C5B55', 'A58BDBFAF28416528A0D9A4452F896F46774A806', externalFiles=True, allowOverwrite=True) # Shareware DUKE3D.GRP v1.3D
                grp: GrpZipFile = LoadGrpFile(tempgrp)

            with self.subTest('Read External File'):
               t = grp.getfile(extname).decode()
               self.assertEqual(t, testdata, 'Got external file path override')
        finally:
            games.AddGame('Shareware DUKE3D.GRP v1.3D',         'Duke Nukem 3D',          11035779, '983AD923', 'C03558E3A78D1C5356DC69B6134C5B55', 'A58BDBFAF28416528A0D9A4452F896F46774A806', externalFiles=False, allowOverwrite=True) # Shareware DUKE3D.GRP v1.3D

    @unittest.skip
    def test_other_grps(self):
        # optionally use the othertests folder for testing your own collection of games that aren't freeware
        files = glob.glob('othertests/*', recursive=True)
        for f in files:
            if 'skip' in f:
                continue
            with self.subTest(f):
                f = Path(f)
                self.TestRandomize(f, 451, {}, False)
                #grp = LoadGrpFile(f)
                #grp.ExtractAll(Path(temp,str(f)+'-extracted'))

    def test_combine(self):
        # optionally make a new grp file
        globfiles = glob.glob('combine/*', recursive=True)
        files = []
        for f in globfiles:
            f = Path(f)
            if f.is_file():
                files.append(f)
        if files:
            CreateGrpFile(Path(''), Path('temp/combined.grp'), files)


    def TestRandomize(self, grppath:Path, seed:int, oldMd5s:dict, shouldMatch:bool, settings:dict=settings) -> dict:
        self.maxDiff = None
        testname = str(grppath) + ' Seed ' + ('0451' if seed==451 else str(seed))
        foldername = grppath.name + '-' + str(crc32(testname+repr(settings)))
        basepath = Path(temp, foldername)
        newMd5s = None
        with self.subTest('Randomize '+testname):
            grp:GrpBase = LoadGrpFile(grppath)
            grp.Randomize(seed, settings=settings, basepath=basepath)

            if grp.game.useRandomizerFolder:
                basepath = Path(basepath, 'Randomizer')
            newMd5s = self.Md5GameFiles(testname, grp, basepath)
            self.assertIsNotNone(newMd5s, 'New MD5s')
            self.assertGreater(len(newMd5s), 0, 'New MD5s')

            if oldMd5s:
                self.assertIsNotNone(oldMd5s, 'Old MD5s')
                self.assertGreater(len(oldMd5s), 0, 'Old MD5s')
                if shouldMatch:
                    self.assertDictEqual(oldMd5s, newMd5s)
                else:
                    self.assertEqual(len(oldMd5s), len(newMd5s), 'Same number of files')
                    for k in oldMd5s.keys():
                        self.assertNotEqual(oldMd5s[k], newMd5s[k], k)

            with open(Path(basepath, 'Randomizer.html')) as spoilerlog:
                logs = spoilerlog.read()
                self.assertGreater(len(logs), 10, 'found spoiler logs')
                self.assertInLogs('Randomizing with seed: '+str(seed), logs)
                for con in grp.conSettings.conFiles.keys():
                    con = str(Path(con))
                    self.assertInLogs('Finished randomizing file: '+con, logs)
                for map in grp.GetAllFilesEndsWith('.map'):
                    map = str(Path(map))
                    self.assertInLogs('Finished randomizing file: '+map, logs)
                self.assertInLogs('<div class="ListSprites">', logs)
                if grp.mapSettings.triggers:
                    self.assertInLogs('set hightag to ', logs)
                self.assertInLogs('<div class="FileSection">', logs)
        return newMd5s

    def assertInLogs(self, text, logs):
        if text.lower() not in logs.lower():
            self.fail(text + ' not found in logs')

    def Md5GameFiles(self, testname:str, grp:GrpBase, basepath:Path) -> dict:
        with self.subTest('MD5 '+testname):
            maps = grp.GetAllFilesEndsWith('.map')
            cons = list(grp.conSettings.conFiles.keys())
            return self.Md5Files(basepath, (maps+cons))

    def Md5Files(self, basepath: Path, filenames: list) -> dict:
        md5s = {}
        for f in filenames:
            t = self.Md5File(Path(basepath, f))
            md5s[f] = t
        trace('Md5Files ', basepath, ': ', md5s)
        return md5s

    def Md5File(self, filename:Path):
        with open(filename) as file, mmap(file.fileno(), 0, access=ACCESS_READ) as file:
            md5sum = md5(file).hexdigest()
            return md5sum

    def test_walls(self):
        with self.subTest('test PointIsInShape'):
            walls = [(0,0), (10,0), (10,10), (0,10)]
            self.assertEqual(buildmap.PointIsInShape(walls, (5,5), 0) % 2, 1)
            self.assertEqual(buildmap.PointIsInShape(walls, (15,15), 0) % 2, 0)

    def test_encrypt_decrypt(self):
        # ensure it's reversible
        data = bytearray(b'123456')
        d2 = buildmap.MapCrypt(data, 451)
        d2 = buildmap.MapCrypt(d2, 451)
        self.assertEqual(data, d2)

        data = bytearray(b'dfgdfghcvbngertguhyrtujityr3456436fdghsdfgxcvb')
        d2 = buildmap.MapCrypt(data, 0x7474614d)
        d2 = buildmap.MapCrypt(d2, 0x7474614d)
        self.assertEqual(data, d2)



def runtests():
    unittest.main(verbosity=9, warnings="error", failfast=True)


if __name__ == "__main__":
    try:
        if os.path.isdir(temp):
            shutil.rmtree(temp)
        if profiling:
            setVerbose(-10)
            cProfile.run("runtests()", sort="cumtime")
        else:
            runtests()
    finally:
    #     if os.path.isdir(temp):
    #         shutil.rmtree(temp)
        pass
