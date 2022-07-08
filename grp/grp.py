import os
from zipfile import ZipFile
from struct import *

class MapFile:
    # https://moddingwiki.shikadi.net/wiki/MAP_Format_(Build)
    def __init__(self, name, data: bytes):
        print(name, len(data))
        self.name = name
        (self.version, self.startx, self.starty, self.startz, self.startangle, self.startsect, self.numsects) = unpack('<iiiihhH', data[:22])
        self.sector_size = 40
        self.wall_size = 32
        self.sprite_size = 44

        self.sectors_start = 22
        self.sectors_length = self.numsects * self.sector_size
        num_walls_start = self.sectors_start + self.sectors_length
        self.walls_start = num_walls_start + 2
        (self.num_walls,) = unpack('<H', data[num_walls_start:self.walls_start])
        self.walls_length = self.num_walls * self.wall_size
        num_sprites_start = self.walls_start + self.walls_length
        self.sprites_start = num_sprites_start + 2
        (self.num_sprites,) = unpack('<H', data[num_sprites_start:self.sprites_start])
        self.sprites_length = self.num_sprites * self.sprite_size

        print(self.__dict__)
        self.data = data


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

    def __enter__(self, *args):
        print('__enter__', *args)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def getfile(self, name):
        with ZipFile(self.filepath, 'r') as zip:
            with zip.open(name) as file:
                return file.read()

    def getmap(self, name):
        return MapFile(name, self.getfile(name))

