import shutil
from BuildLibs.grp import *
import BuildLibs.gui
import cProfile, pstats
import unittest
from unittest import case
from hashlib import md5, sha1
from mmap import mmap, ACCESS_READ

#unittest.TestLoader.sortTestMethodsUsing = None
temp = 'temp/'
grppath: str = 'duke3d-shareware.grp.zip'
testing_grp = 'temp/testing.grp'

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

class BaseTestCase(unittest.TestCase):
    def subTest(self, msg=case._subtest_msg_sentinel, **params):
        print('\nstarting subTest', msg)
        return super().subTest(msg, **params)

    def test_extract_zipgrp(self):
        grp: GrpFile = None
        with self.subTest('ExtractAll'):
            grp = GrpFile(grppath)
            self.assertEqual(len(grp.files), len(original_order))
            grp.ExtractAll(temp)

        with self.subTest('CreateGrpFile'):
            CreateGrpFile(temp, testing_grp, original_order)

        grp = None
        with self.subTest('Verify new GRP File'):
            grp = GrpFile(testing_grp)
            self.assertEqual(grp.game.type, 'Duke Nukem 3D')

        oldmd5s = {}
        with self.subTest('MD5 Original Maps'):
            maps = grp.GetAllFilesEndsWith('.map')
            oldmd5s = self.Md5Maps(temp, maps)

        with self.subTest('Randomize Maps'):
            grp.Randomize(int('0451'))

        newmd5s = {}
        with self.subTest('MD5 Randomized Maps'):
            maps = grp.GetAllFilesEndsWith('.map')
            newmd5s = self.Md5Maps(temp, maps)

        with self.subTest('Compare MD5s After Randomizing'):
            for k in oldmd5s.keys():
                self.assertNotEqual(oldmd5s[k], newmd5s[k], k)


    def Md5Maps(self, basepath: str, filenames: list) -> dict:
        md5s = {}
        for f in filenames:
            t = self.Md5File(basepath + f)
            md5s[f] = t
        print(repr(md5s))
        return md5s

    def Md5File(self, filename):
        with open(filename) as file, mmap(file.fileno(), 0, access=ACCESS_READ) as file:
            md5sum = md5(file).hexdigest()
            return md5sum


def runtests():
    unittest.main(verbosity=9, warnings="error")#, failfast=True)

try:
    if os.path.isdir(temp):
        shutil.rmtree(temp)
    #cProfile.run("runtests()", sort="cumtime")
    runtests()
finally:
    if os.path.isdir(temp):
        shutil.rmtree(temp)
