from struct import *
import random
from BuildLibs import *

class MapFile:
    # https://moddingwiki.shikadi.net/wiki/MAP_Format_(Build)
    def __init__(self, name, data: bytes):
        print(name, len(data))
        self.name = name
        (self.version, self.startx, self.starty, self.startz, self.startangle, self.startsect, self.numsects) = unpack('<iiiihhH', data[:22])
        self.sector_size = 40
        self.wall_size = 32
        self.sprite_size = 44

        if self.version == 6:
            # https://moddingwiki.shikadi.net/wiki/MAP_Format_(Build)#Version_6
            raise NotImplemented('MAP Format Version 6 is not yet implemented')

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
        #for i in range(self.num_sprites):
        #    print(self.GetSprite(i))
        
    def Randomize(self, seed):
        rng = random.Random(crc32('map randomize', self.name, seed))
        for a in range(self.num_sprites):
            b = rng.randrange(0, self.num_sprites)
            if a == b:
                continue
            self.SwapSprites(a, b)
            break # TODO: remove this
        pass
    
    def GetSprite(self, num):
        assert num >= 0
        assert num < self.num_sprites
        start = self.sprites_start + num*self.sprite_size
        sprite = fancy_unpack(
            '<',
            ('pos', 'iii', 'cstat', 'h', 'gfxstuff', 'hbBBB', 'texcoords', 'BBbb',
            'sectnum', 'h', 'statnum', 'h', 'angle', 'h', 'owner', 'h',
            'velocity', 'hhh', 'lowtag', 'h', 'hightag', 'h', 'extra', 'h'),
            self.data[start:start+self.sprite_size]
        )
        return sprite

    def WriteSprite(self, sprite, num):
        pass
    
    def SwapSprites(self, idxa, idxb):
        print('SwapSprites', idxa, idxb)
        a = self.GetSprite(idxa)
        b = self.GetSprite(idxb)
        print(a)
        print(b)

        swapdictkey(a, b, 'pos')
        swapdictkey(a, b, 'sectnum')
        swapdictkey(a, b, 'angle')

        self.WriteSprite(a, idxa)
        self.WriteSprite(b, idxb)

        #a = self.GetSprite(idxa)
        #b = self.GetSprite(idxb)
        print(a)
        print(b)

