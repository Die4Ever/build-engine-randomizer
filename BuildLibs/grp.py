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
        self.filesize = os.path.getsize(filepath)
        with open(filepath, 'rb') as f:
            self.sig = f.read(12)
        
        print(self.sig)
        if self.sig[:4] == b'PK\x03\x04':
            print('is a zip file')
            self.type = 'zip'
        elif self.sig[:12] == b'KenSilverman':
            print('is a GRP file')
            self.type = 'grp'
        else:
            raise Exception(filepath + ' is an unknown type')
        
        self.game = games.GetGame(filepath)

    def __enter__(self, *args):
        trace( '__enter__', *args, self.__dict__)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        trace( '__exit__', self.__dict__)
        pass

    def getfileZip(self, name):
        with ZipFile(self.filepath, 'r') as zip:
            with zip.open(name) as file:
                return file.read()
        raise Exception('file not found in GRP/ZIP', requestedName)

    def getfileGrp(self, requestedName):
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
                if name == requestedName:
                    f.seek(offset, 0)
                    return f.read(size)
                offset += size
        raise Exception('file not found in GRP', requestedName, numFiles)



    def getfile(self, name):
        if self.type == 'zip':
            return self.getfileZip(name)
        else:
            return self.getfileGrp(name)

    def getmap(self, name):
        return MapFile(self.game, name, bytearray(self.getfile(name)))

def randomize(grppath, maps, seed):
    with GrpFile(grppath) as g:
        for mapname in maps:
            map = g.getmap(mapname)
            map.Randomize(seed)
            gamedir = os.path.dirname(grppath)
            mapout = os.path.join(gamedir, mapname)
            pathlib.Path(os.path.dirname(mapout)).mkdir(parents=True, exist_ok=True)
            with open(mapout, 'wb') as f:
                f.write(map.data)
