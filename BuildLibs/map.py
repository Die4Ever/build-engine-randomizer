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
