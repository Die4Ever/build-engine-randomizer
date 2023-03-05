import abc
import glob
import locale
import os
import random
import re
import shutil
import traceback
import ctypes
from datetime import datetime
from pathlib import Path
from typing import List, OrderedDict

from BuildLibs import debug, error, info, trace, warning
from BuildLibs.buildmap import *
from BuildLibs.confile import ConFile
from BuildLibs.SpoilerLog import SpoilerLog
import BuildGames


try:
    locale.setlocale(locale.LC_ALL, '')
except Exception as e:
    error('Failed to set locale', e, '\n', traceback.format_exc())


# game's main resource file, either GRP, ZIP, or RFF
class GrpBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def GetFilesInfo(self) -> None:
        return

    @abc.abstractmethod
    def getFileHandle(self):
        return

    @abc.abstractmethod
    def _getfile(self, name, filehandle) -> bytes:
        return

    def __init__(self, filepath:Path, filesize, game):
        self.filepath = filepath
        info(filepath)
        self.files = {}
        self.game:BuildGames.GameInfo = game
        self.filesize = filesize
        self.deletes = None
        self.spoilerlogpath = None
        self.batpath = None

        self.GetFilesInfo()
        self.GetExternalFiles()
        cons = self.GetAllFilesEndsWith('.con')
        if not self.game.type:
            info(repr(cons))
            raise Exception('unidentified game')

        self.gameSettings = BuildGames.GetGameSettings(self.game)
        if not self.gameSettings:
            raise Exception('missing GameSettings', self.game, filepath)
        elif not self.gameSettings.conFiles:
            warning("This game is missing CON file randomization", self.game, filepath)
            for con in cons:
                warning(con)
                # self.ExtractFile('temp/', con)
        else:
            for con in self.gameSettings.conFiles:
                if con not in cons:
                    warning('file not found', con)

        self.mapSettings = BuildGames.GetGameMapSettings(self.game)
        if not self.mapSettings.swappableItems:
            warning("This game doesn't have any swappableItems", self.game, filepath)
        if not self.mapSettings.swappableEnemies:
            warning("This game doesn't have any swappableEnemies", self.game, filepath)

    def GetExternalFiles(self):
        if not self.game.externalFiles:
            return
        gamedir = os.path.dirname(self.filepath)
        searchdir = Path(gamedir, '**')
        trace(searchdir)
        files = glob.glob(str(searchdir), recursive=True)
        trace(files)
        for f in files:
            p = Path(f)
            rel = p.relative_to(gamedir)
            if 'backup' in f.lower(): # TODO: maybe move old files to backup instead of deleting? but then have to delete the previous files in backup?
                continue
            if 'addons' in f.lower(): # TODO: support addons
                continue
            if 'Randomizer' in rel.parts:
                continue
            if not p.is_file():
                continue

            f = str(rel)
            self.files[f] = {
                'location': p,
                #'parts': p.parts
            }

    def GetAllFilesEndsWith(self, postfix) -> list:
        matches = []
        postfix = postfix.lower()
        for f in self.files.keys():
            if f.lower().endswith(postfix):
                matches.append(f)
        matches.sort()
        return matches

    def getfile(self, name, filehandle=None) -> bytes:
        overridepath = self.files[name].get('location')
        if overridepath:
            with open(overridepath, 'rb') as file:
                return file.read()
        return self._getfile(name, filehandle)

    def getmap(self, name, file) -> MapFile:
        data = bytearray(self.getfile(name, file))
        return LoadMap(self.game, name, data)

    def GetOutputPath(self, basepath:Path, outputMethod) -> Path:
        gamedir = os.path.dirname(self.filepath)
        if not basepath:
            basepath = gamedir
        if outputMethod=='folder':
            basepath = Path(basepath, 'Randomizer')
        return Path(basepath)

    def GetDeletes(self, basepath:Path, outputMethod) -> List[Path]:
        if self.deletes:
            return self.deletes

        outpath:Path = self.GetOutputPath(basepath, outputMethod)
        maybedeletes = self._GetDeletes(outpath, outputMethod)
        self.deletes = []
        for f in maybedeletes:
            if f.exists():
                self.deletes.append(f)
        return self.deletes


    def _GetDeletes(self, outpath:Path, outputMethod) -> List[Path]:
        ret = []
        if outputMethod=='folder':
            ret += [outpath]
            # let's clean up the plain files in the parent folder too
            outpath = outpath.parent
        else:
            ret += [Path(outpath, 'Randomizer')]

        #if outputMethod=='grp': # we check if these exist anyways, might as well always add them to the list and have safer cleanups
        ret += [
            Path(outpath, self.game.type + ' Randomizer.html'),
            Path(outpath, self.game.type + ' Randomizer.grp'),
            Path(outpath, self.game.type + ' Randomizer.grpinfo'),
        ]

        cons = self.gameSettings.conFiles
        maps = self.GetAllFilesEndsWith('.map')
        paths = set([self.game.type + ' Randomizer.html', 'Randomizer.html', self.game.type + ' Randomizer.bat'])
        f:str
        for f in self.files:
            if f in cons or f in maps:
                part:str = Path(f).parts[0]
                paths.add(part)
        paths = list(paths)
        paths.sort(key=str.casefold)
        for f in paths:
            p:Path = Path(outpath, f)
            if p not in ret:
                ret.append(p)
        return ret

    def ShuffleMaps(self, seed, restricted, maps) -> dict:
        maps = maps.copy()
        for m in self.mapSettings.reorderMapsBlacklist:
            if m in maps:
                maps.remove(m)
        if len(maps) == 0:
            return {}

        if not restricted:
            rng = random.Random(crc32('grp reorder maps', seed))
            return dict(zip(maps, rng.sample(maps, k=len(maps))))

        episodes = {}
        mapRenames = {}
        # categorize the maps
        for map in maps:
            match = re.match('\w(\d+)\w(\d+)\.MAP$', map, flags=re.IGNORECASE)
            episode = 'other'
            if match:
                episode = match.group(1)
            if episode not in episodes:
                episodes[episode] = [map]
            else:
                episodes[episode].append(map)
        # shuffle each episode
        for k,v in episodes.items():
            rng = random.Random(crc32('grp reorder maps', k, seed))
            d = dict(zip(v, rng.sample(v, k=len(v))))
            mapRenames.update(d)
        return mapRenames

    @abc.abstractmethod
    def GetGrpOutput(self, basepath: Path, num_files: int, full: bool):
        raise NotImplementedError()

    # basepath is only used by tests
    def _Randomize(self, seed:int, settings:dict, basepath:Path, spoilerlog, filehandle) -> None:
        spoilerlog.write(datetime.now().strftime('%c') + ': Randomizing with seed: ' + str(seed) + ', settings:\n    ' + repr(settings) + '\n')
        spoilerlog.write(str(self.filepath))
        spoilerlog.write(repr(self.game) + '\n\n')

        maps = self.GetAllFilesEndsWith('.map')
        cons = self.gameSettings.conFiles

        outputMethod = settings['outputMethod']
        grpOut = None
        full = False
        if outputMethod in ('grp', 'grpfull'):
            num_files = len(maps) + len(cons)
            if outputMethod == 'grpfull':
                num_files = len(self.files)
                full = True
            grpOut = self.GetGrpOutput(basepath, num_files, seed, full)
            grpOut.open()

        # randomize CON files
        for (conName,conSettings) in cons.items():
            data = self.getfile(conName, filehandle)
            text = data.decode('iso_8859_1')
            con:ConFile = ConFile(self.game, conSettings, conName, text)
            con.Randomize(seed, settings, spoilerlog)

            out = Path(basepath, conName)
            text = con.GetText()
            size = locale.format_string('%d bytes', len(text), grouping=True)
            spoilerlog.write(str(out) + ' is ' + size)

            if grpOut:
                grpOut.write(conName, text.encode('iso_8859_1'))
            else:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.touch(exist_ok=False)
                with open(out, 'wb') as f:
                    f.write(text.encode('iso_8859_1'))

        # MAP shuffling
        mapRenames = {}
        if settings.get('grp.reorderMaps'):
            restricted = settings['grp.reorderMaps'] == 'restricted'
            mapRenames = self.ShuffleMaps(seed, restricted, maps)

        # randomize MAP files
        for mapname in maps:
            map:MapFile = self.getmap(mapname, filehandle)
            map.Randomize(seed, settings, spoilerlog)

            writename = mapRenames.get(mapname, mapname)
            out = Path(basepath, writename)
            size = locale.format_string('%d bytes', len(map.data), grouping=True)
            spoilerlog.write(str(mapname) + ' writing to ' + str(out) + ', is ' + size)

            if grpOut:
                grpOut.write(writename, map.data)
            else:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.touch(exist_ok=False)
                with open(out, 'wb') as f:
                    f.write(map.data)

        # write the remaining files to the GRP
        if grpOut and full:
            for f in self.files.keys():
                if f in cons or f in maps:
                    continue
                grpOut.write(f, self.getfile(f, filehandle))
        if grpOut:
            grpOut.close()

        spoilerlog.write('\n')
        spoilerlog.write(repr(self.gameSettings))
        spoilerlog.write('\n')
        spoilerlog.write(repr(self.mapSettings))


    def Randomize(self, seed:int, settings:dict={}, basepath:Path='') -> None:
        outputMethod = settings['outputMethod']
        outpath:Path = self.GetOutputPath(basepath, outputMethod)
        deletes:List[Path] = self.GetDeletes(basepath, outputMethod)
        for f in deletes:
            info('Deleting: ', f)
            if f.is_dir():
                shutil.rmtree(f)
            elif f.is_file():
                os.remove(f)

        out = Path(outpath, self.game.type + ' Randomizer.html')
        out.parent.mkdir(parents=True, exist_ok=True)
        self.spoilerlogpath = out
        assert not out.exists()
        with self.getFileHandle() as filehandle, SpoilerLog(out) as spoilerlog:
            try:
                self._Randomize(seed, settings, outpath, spoilerlog, filehandle)
                self.WriteBat(outpath, outputMethod)
            except:
                error(str(self.filepath))
                error(self.game, ', seed: ', seed, ', settings: ', settings, ', outpath: ', outpath)
                error('\n  == files: ', self.files, ' == end of files listing ==\n')
                raise


    def WriteBat(self, outpath:Path, outputMethod:str):
        if os.name != 'nt':
            return None
        basepath = outpath
        if outputMethod=='folder':
            basepath = outpath.parent

        commands = self.gameSettings.commands.get(outputMethod)
        if not commands:
            return
        for (k,v) in commands.items():
            exe = Path(basepath, k+'.exe')
            if not exe.exists():
                continue
            bat = Path(basepath, self.game.type + ' Randomizer.bat')
            cmd = k+' '+v
            if outputMethod in ['grp', 'grpfull']:
                cmd += '"' + self.game.type + ' Randomizer.grp"'
            elif outputMethod == 'folder':
                cmd += 'Randomizer'
            bat.touch(exist_ok=False)
            with open(bat, 'w') as file:
                file.write(cmd)
            self.batpath = bat
            return cmd
        self.batpath = None
        warning('Unable to create bat file, unrecognized source port')

    def ExtractFile(self, outpath:Path, name, filehandle=None) -> None:
        outfile = Path(outpath, name)
        outfile.parent.mkdir(parents=True, exist_ok=True)
        data = self.getfile(name, filehandle)
        print(name, len(data), outfile)
        if not data:
            return
        with open(outfile, 'wb') as o:
            o.write(data)

    def ExtractAll(self, outpath:Path) -> None:
        with self.getFileHandle() as filehandle:
            for name in self.files.keys():
                self.ExtractFile(outpath, name, filehandle)


class GrpOutputBase(metaclass=abc.ABCMeta):
    def __init__(self, outpath: Path, gamename: str, num_files: int, extraname: str, scriptname: Union[None,str], defName: Union[None,str], flags: int, depend: int):
        self.num_files = num_files
        self.outpath = outpath
        self.gamename = gamename
        self.num_saved_files = 0
        self.files = dict()
        self.extraname = extraname
        self.scriptname = scriptname
        self.defName = defName
        self.flags = flags
        self.depend = depend

    def __enter__(self):
        return self.open()

    def __exit__(self, *args):
        self.close()

    @abc.abstractmethod
    def open(self):
        return self

    @abc.abstractmethod
    def write(self, name: str, data: bytes):
        return

    @abc.abstractmethod
    def close(self):
        return

    def write_info(self, size: int, crc: int):
        # grpinfo file so eDuke32 knows what to do with it
        crc = ctypes.c_int32(crc).value
        depend = ctypes.c_int32(self.depend).value
        if self.extraname:
            self.extraname = ' ' + self.extraname
        grpinfo_path = Path(self.outpath.parent, self.outpath.name + 'info')
        info = "grpinfo\n{\n"
        info += '    name "' + self.gamename + ' Randomizer' + self.extraname + '"\n'
        if self.scriptname:
            info += '    scriptname "' + self.scriptname + '"\n'
        if self.defName:
            info += '    defname "' + self.defName + '"\n'
        info += '    size ' + str(size) + '\n'
        info += "    crc  " + str(crc) + "\n"
        info += '    flags ' + str(self.flags) + '\n'
        info += '    dependency ' + str(depend) + '\n'
        info += "}\n"
        grpinfo_path.parent.mkdir(parents=True, exist_ok=True)
        grpinfo_path.touch(exist_ok=False)
        with open(grpinfo_path, 'wb') as i:
            i.write(info.encode('ascii'))
