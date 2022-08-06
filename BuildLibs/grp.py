import abc
import glob
import locale
import os
import re
import shutil
import traceback
from datetime import datetime
from pathlib import Path
from typing import OrderedDict
from zipfile import ZipFile

from BuildLibs import debug, error, info, trace, warning
from BuildLibs.buildmap import *
from BuildLibs.confile import ConFile
from BuildLibs.SpoilerLog import SpoilerLog


try:
    locale.setlocale(locale.LC_ALL, '')
except Exception as e:
    error('Failed to set locale', e, '\n', traceback.format_exc())


def LoadGrpFile(filepath:Path) -> 'GrpBase':
    info(filepath)
    game:games.GameInfo = games.GetGame(filepath)
    filesize = os.path.getsize(filepath)
    with open(filepath, 'rb') as f:
        sig = f.read(12)

    trace(sig)
    if sig[:4] == b'PK\x03\x04':
        debug('is a zip file')
        return GrpZipFile(filepath, filesize, game)
    elif sig[:12] == b'KenSilverman':
        debug('is a GRP file')
        return GrpFile(filepath, filesize, game)
    elif sig[:4] == b'RFF\x1a':
        debug('is an RFF file')
        return RffFile(filepath, filesize, game)
    else:
        raise Exception(filepath + ' is an unknown type, size: ', filesize, game)

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
        self.game:games.GameInfo = game
        self.filesize = filesize

        self.GetFilesInfo()
        self.GetExternalFiles()
        cons = self.GetAllFilesEndsWith('.con')
        if not self.game.type:
            info(repr(cons))
            raise Exception('unidentified game')

        self.conSettings = games.GetGameConSettings(self.game)
        if not self.conSettings:
            raise Exception('missing GameConSettings', self.game, filepath)
        elif not self.conSettings.conFiles:
            warning("This game is missing CON file randomization", self.game, filepath)
            for con in cons:
                warning(con)
                # self.ExtractFile('temp/', con)
        else:
            for con in self.conSettings.conFiles:
                if con not in cons:
                    warning('file not found', con)

        self.mapSettings = games.GetGameMapSettings(self.game)
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

    def GetOutputPath(self, basepath:Path=Path('')) -> Path:
        gamedir = os.path.dirname(self.filepath)
        if not basepath:
            basepath = gamedir
        if self.game.useRandomizerFolder:
            basepath = Path(basepath, 'Randomizer')
        return Path(basepath)

    def GetDeleteFolders(self, basepath:Path) -> list:
        if self.game.useRandomizerFolder:
            return [basepath]

        mapFiles = self.GetAllFilesEndsWith('.map')
        folders = set(['Randomizer.html'])
        f:str
        for f in self.files:
            if f in self.conSettings.conFiles or f in mapFiles:
                folders.add(Path(f).parts[0])
        ret = list(folders)
        ret.sort(key=str.casefold)
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

    # basepath is only used by tests
    def _Randomize(self, seed:int, settings:dict, basepath:Path, spoilerlog, filehandle) -> None:
        spoilerlog.write(datetime.now().strftime('%c') + ': Randomizing with seed: ' + str(seed) + ', settings:\n    ' + repr(settings) + '\n')
        spoilerlog.write(str(self.filepath))
        spoilerlog.write(repr(self.game) + '\n\n')

        for (conName,conSettings) in self.conSettings.conFiles.items():
            data = self.getfile(conName, filehandle)
            text = data.decode('iso_8859_1')
            con:ConFile = ConFile(self.game, conSettings, conName, text)
            con.Randomize(seed, settings, spoilerlog)
            out = Path(basepath, conName)
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out, 'w') as f:
                text = con.GetText()
                size = locale.format_string('%d bytes', len(text), grouping=True)
                spoilerlog.write(str(out) + ' is ' + size)
                f.write(text)

        maps = self.GetAllFilesEndsWith('.map')
        mapRenames = {}
        if settings.get('grp.reorderMaps'):
            restricted = settings['grp.reorderMaps'] == 'restricted'
            mapRenames = self.ShuffleMaps(seed, restricted, maps)

        for mapname in maps:
            map:MapFile = self.getmap(mapname, filehandle)
            map.Randomize(seed, settings, spoilerlog)
            writename = mapRenames.get(mapname, mapname)
            out = Path(basepath, writename)
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out, 'wb') as f:
                size = locale.format_string('%d bytes', len(map.data), grouping=True)
                spoilerlog.write(str(mapname) + ' writing to ' + str(out) + ', is ' + size)
                f.write(map.data)

        spoilerlog.write('\n')
        spoilerlog.write(repr(self.conSettings))
        spoilerlog.write('\n')
        spoilerlog.write(repr(self.mapSettings))


    def Randomize(self, seed:int, settings:dict={}, basepath:Path='') -> None:
        basepath:Path = self.GetOutputPath(basepath)
        deleteFolders = self.GetDeleteFolders(basepath)
        for f in deleteFolders:
            f = Path(f)
            if f.is_dir():
                shutil.rmtree(f)
            elif f.is_file():
                os.remove(f)

        out = Path(basepath, 'Randomizer.html')
        Path(os.path.dirname(out)).mkdir(parents=True, exist_ok=True)
        with self.getFileHandle() as filehandle, SpoilerLog(out) as spoilerlog:
            try:
                return self._Randomize(seed, settings, basepath, spoilerlog, filehandle)
            except:
                error(str(self.filepath))
                error(self.game, ', seed: ', seed, ', settings: ', settings, ', basepath: ', basepath)
                error('\n  == files: ', self.files, ' == end of files listing ==\n')
                raise

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


# https://moddingwiki.shikadi.net/wiki/GRP_Format
class GrpFile(GrpBase):
    def GetFilesInfo(self) -> None:
        with open(self.filepath, 'rb') as f:
            f.seek(12)
            data = f.read(4)
            (numFiles,) = struct.unpack('<I', data)
            trace('numFiles:', numFiles)
            offset = 16 + 16*numFiles
            for i in range(numFiles):
                data = f.read(16)
                name = data[:12].strip(b'\x00').decode('ascii')
                (size,) = struct.unpack('<I', data[12:16])
                trace(name, size)
                self.files[name] = {
                    'size': size,
                    'offset': offset
                }
                offset += size

    def _getfile(self, name, filehandle) -> bytes:
        info = self.files.get(name)
        if not info:
            raise Exception('file not found in GRP', name, len(self.files))

        if filehandle:
            filehandle.seek(info['offset'])
            return filehandle.read(info['size'])

        with open(self.filepath, 'rb') as f:
            f.seek(info['offset'])
            return f.read(info['size'])

    def getFileHandle(self):
        return open(self.filepath, 'rb')


# idk what to call these, but Ion Fury uses one
class GrpZipFile(GrpBase):
    def GetFilesInfo(self) -> None:
        with ZipFile(self.filepath, 'r') as zip:
            for f in zip.infolist():
                self.files[f.filename] = { 'size': f.file_size }

    def _getfile(self, name, filehandle) -> bytes:
        if name not in self.files:
            raise Exception('file not found in GRP/ZIP', name, len(self.files))

        if filehandle:
            with filehandle.open(name) as f:
                return f.read()

        with ZipFile(self.filepath, 'r') as zip:
            with zip.open(name) as file:
                return file.read()

    def getFileHandle(self):
        return ZipFile(self.filepath, 'r')


# used by Blood https://github.com/Die4Ever/build-engine-randomizer/issues/21
class RffFile(GrpBase):
    def GetFilesInfo(self) -> None:
        headerPack = FancyPacker('<', OrderedDict(sign='4s', version='h', pad1='h', offset='I', filenum='I'))
        directoryPack = FancyPacker('<', OrderedDict(unused1='16s', offset='I', size='I', unused2='8s', flags='B', type='3s', name='8s', id='i'))
        itemSize = 48

        with open(self.filepath, 'rb') as file:
            data = file.read(16)
            header = headerPack.unpack(data)
            trace(header)
            self.offset = header['offset']
            self.fileNum = header['filenum']
            file.seek(self.offset, os.SEEK_SET)
            data = bytearray(file.read(itemSize * self.fileNum))

        self.version = header['version']
        self.versionClass = header['version'] & 0xff00
        if self.versionClass == 0x200:
            self.crypt = 0
        elif self.versionClass == 0x300:
            self.crypt = 1
        else:
            raise NotImplementedError(self.filepath + ' ' + repr(header))

        if self.crypt:
            data = RffDecrypt(data, self.offset + (self.version & 0xff) * self.offset)

        for i in range(self.fileNum):
            d = directoryPack.unpack(data[i*itemSize:(i+1)*itemSize])
            d['type'] = d['type'].decode()
            name = d['name'].decode().replace('\x00', '')
            filename = name + '.' + d['type']
            d['name'] = filename
            del d['unused1']
            del d['unused2']
            self.files[filename] = d


    def _getfile(self, name, filehandle) -> bytes:
        info = self.files.get(name)
        if not info:
            raise Exception('file not found in RFF', name, len(self.files))

        if filehandle:
            filehandle.seek(info['offset'], os.SEEK_SET)
            data = filehandle.read(info['size'])
        else:
            with open(self.filepath, 'rb') as f:
                f.seek(info['offset'], os.SEEK_SET)
                data = f.read(info['size'])

        DICT_CRYPT = 16
        if info['flags'] & DICT_CRYPT:
            data = bytearray(data)
            decryptSize = min(info['size'], 0x100)
            data[:decryptSize] = RffDecrypt(data[:decryptSize], 0)
        return data


    def getFileHandle(self):
        return open(self.filepath, 'rb')


def CreateGrpFile(frompath: Path, outpath: Path, filenames: list) -> None:
    outfile = open(outpath, 'wb')
    outfile.write(b'KenSilverman')
    outfile.write(struct.pack('<I', len(filenames)))

    datas = []
    for name in filenames:
        with open(Path(frompath, name), 'rb') as f:
            d = f.read()
            datas.append(d)
            outfile.write(struct.pack('<12sI', str(name).encode('ascii'), len(d)))

    for d in datas:
        outfile.write(d)

    outfile.close()

def RffDecrypt(data:bytearray, key:int) -> bytearray:
    for i in range(len(data)):
        data[i] = data[i] ^ ((key>>1) & 0xff)
        key += 1
    return data
