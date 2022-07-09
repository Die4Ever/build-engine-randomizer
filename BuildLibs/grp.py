import os
from zipfile import ZipFile
from BuildLibs import games
from BuildLibs.buildmap import *

class GrpFile:
    # https://moddingwiki.shikadi.net/wiki/GRP_Format
    # or zip format, at least in the case of Ion Fury
    def __init__(self, filepath):
        self.filepath = filepath
        print('__init__', filepath)
        self.files = {}
        self.filesize = os.path.getsize(filepath)
        with open(filepath, 'rb') as f:
            self.sig = f.read(12)

        print(self.sig)
        if self.sig[:4] == b'PK\x03\x04':
            print('is a zip file')
            self.type = 'zip'
            self.GetFilesInfoZip()
        elif self.sig[:12] == b'KenSilverman':
            print('is a GRP file')
            self.type = 'grp'
            self.GetFilesInfoGrp()
        else:
            raise Exception(filepath + ' is an unknown type')

        self.game = games.GetGame(filepath)
        if not self.game:
            print(repr(self.GetAllFilesEndsWith('.con')))
            raise Exception('unidentified game')

    def __enter__(self, *args):
        trace( '__enter__', *args, self.__dict__)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        trace( '__exit__', self.__dict__)
        pass

    def GetFilesInfoZip(self):
        with ZipFile(self.filepath, 'r') as zip:
                for f in zip.infolist():
                    self.files[f.filename] = { 'size': f.file_size }

    def GetFilesInfoGrp(self):
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

    def getfileZip(self, name):
        if name not in self.files:
            raise Exception('file not found in GRP/ZIP', name, len(self.files))

        with ZipFile(self.filepath, 'r') as zip:
            with zip.open(name) as file:
                return file.read()

    def getfileGrp(self, name):
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

    def getfile(self, name):
        if self.type == 'zip':
            return self.getfileZip(name)
        else:
            return self.getfileGrp(name)

    def getmap(self, name):
        return MapFile(self.game, name, bytearray(self.getfile(name)))

    def Randomize(self, seed):
        for mapname in self.GetAllFilesEndsWith('.map'):
            map = self.getmap(mapname)
            map.Randomize(seed)
            gamedir = os.path.dirname(self.filepath)
            mapout = os.path.join(gamedir, mapname)
            pathlib.Path(os.path.dirname(mapout)).mkdir(parents=True, exist_ok=True)
            with open(mapout, 'wb') as f:
                f.write(map.data)

    def ExtractAll(self, outpath):
        pathlib.Path(outpath).mkdir(parents=True, exist_ok=True)
        for name in self.files.keys():
            data = self.getfile(name)
            trace(name, len(data))
            with open(outpath + name, 'wb') as o:
                o.write(data)


def CreateGrpFile(frompath: str, outpath: str, filenames: list):
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
