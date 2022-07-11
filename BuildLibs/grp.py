import os
from zipfile import ZipFile
from BuildLibs import games
from BuildLibs.buildmap import *
from BuildLibs.confile import ConFile

class GrpFile:
    # https://moddingwiki.shikadi.net/wiki/GRP_Format
    # or zip format, at least in the case of Ion Fury
    def __init__(self, filepath):
        self.filepath = filepath
        info(filepath)
        self.files = {}
        self.filesize = os.path.getsize(filepath)
        with open(filepath, 'rb') as f:
            self.sig = f.read(12)

        trace(self.sig)
        if self.sig[:4] == b'PK\x03\x04':
            debug('is a zip file')
            self.type = 'zip'
            self.GetFilesInfoZip()
        elif self.sig[:12] == b'KenSilverman':
            debug('is a GRP file')
            self.type = 'grp'
            self.GetFilesInfoGrp()
        else:
            raise Exception(filepath + ' is an unknown type')

        cons = self.GetAllFilesEndsWith('.con')
        self.game = games.GetGame(filepath)
        if not self.game:
            info(repr(cons))
            raise Exception('unidentified game')

        self.conSettings = games.GetGameConSettings(self.game)
        if not self.conSettings:
            raise Exception('missing GameConSettings', filepath)
        if not self.conSettings.conFiles:
            warning("This game is missing CON file randomization")
            for con in cons:
                self.ExtractFile('temp/', con)

        mapSettings = games.GetGameMapSettings(self.game)
        if not mapSettings.swappableItems:
            warning("This game doesn't have any swappableItems")
        if not mapSettings.swappableEnemies:
            warning("This game doesn't have any swappableEnemies")


    def GetFilesInfoZip(self) -> None:
        with ZipFile(self.filepath, 'r') as zip:
            for f in zip.infolist():
                self.files[f.filename] = { 'size': f.file_size }

    def GetFilesInfoGrp(self) -> None:
        with open(self.filepath, 'rb') as f:
            f.seek(12)
            data = f.read(4)
            (numFiles,) = unpack('<I', data)
            trace('numFiles:', numFiles)
            offset = 16 + 16*numFiles
            for i in range(numFiles):
                data = f.read(16)
                name = data[:12].strip(b'\x00').decode('ascii')
                (size,) = unpack('<I', data[12:16])
                trace(name, size)
                self.files[name] = {
                    'size': size,
                    'offset': offset
                }
                offset += size

    def getfileZip(self, name) -> bytes:
        if name not in self.files:
            raise Exception('file not found in GRP/ZIP', name, len(self.files))

        with ZipFile(self.filepath, 'r') as zip:
            with zip.open(name) as file:
                return file.read()

    def getfileGrp(self, name) -> bytes:
        if name not in self.files:
            raise Exception('file not found in GRP', name, len(self.files))

        with open(self.filepath, 'rb') as f:
            f.seek(self.files[name]['offset'])
            return f.read(self.files[name]['size'])

    def GetAllFilesEndsWith(self, postfix) -> list:
        matches = []
        postfix = postfix.lower()
        for f in self.files.keys():
            if f.lower().endswith(postfix):
                matches.append(f)
        return matches

    def getfile(self, name) -> bytes:
        if self.type == 'zip':
            return self.getfileZip(name)
        else:
            return self.getfileGrp(name)

    def getmap(self, name) -> MapFile:
        return MapFile(self.game, name, bytearray(self.getfile(name)))

    # basepath is only used by tests
    def Randomize(self, seed:int, settings:dict={}, basepath:str='') -> None:
        info('Randomizing with seed:', seed, ', settings:', settings)
        gamedir = os.path.dirname(self.filepath)
        if not basepath:
            basepath = gamedir
        for mapname in self.GetAllFilesEndsWith('.map'):
            map:MapFile = self.getmap(mapname)
            map.Randomize(seed, settings)
            out = os.path.join(basepath, mapname)
            pathlib.Path(os.path.dirname(out)).mkdir(parents=True, exist_ok=True)
            with open(out, 'wb') as f:
                f.write(map.GetData())

        for (conName,conSettings) in self.conSettings.conFiles.items():
            data = self.getfile(conName)
            text = data.decode('iso_8859_1')
            con:ConFile = ConFile(self.game, conSettings, conName, text)
            con.Randomize(seed, settings)
            out = os.path.join(basepath, conName)
            pathlib.Path(os.path.dirname(out)).mkdir(parents=True, exist_ok=True)
            with open(out, 'w') as f:
                f.write(con.GetText())


    def ExtractFile(self, outpath, name) -> None:
        pathlib.Path(outpath).mkdir(parents=True, exist_ok=True)
        data = self.getfile(name)
        trace(name, len(data))
        with open(outpath + name, 'wb') as o:
            o.write(data)

    def ExtractAll(self, outpath) -> None:
        for name in self.files.keys():
            self.ExtractFile(outpath, name)


def CreateGrpFile(frompath: str, outpath: str, filenames: list) -> None:
    outfile = open(outpath, 'wb')
    outfile.write(b'KenSilverman')
    outfile.write(pack('<I', len(filenames)))

    datas = []
    for name in filenames:
        with open(frompath + name, 'rb') as f:
            d = f.read()
            datas.append(d)
            outfile.write(pack('<12sI', name.encode('ascii'), len(d)))

    for d in datas:
        outfile.write(d)

    outfile.close()
