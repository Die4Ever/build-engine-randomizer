from struct import *
from BuildLibs import *
from BuildLibs import games

class MapFile:
    # https://moddingwiki.shikadi.net/wiki/MAP_Format_(Build)
    def __init__(self, gameName, name, data: bytearray):
        print('\n', name, len(data))
        self.name = name
        self.game_name = gameName
        self.gameSettings = games.GetGameMapSettings(gameName)
        (self.version, self.startx, self.starty, self.startz, self.startangle, self.startsect, self.numsects) = unpack('<iiiihhH', data[:22])
        self.sector_size = 40
        self.wall_size = 32
        self.sprite_size = 44

        if self.version == 6:
            # https://moddingwiki.shikadi.net/wiki/MAP_Format_(Build)#Version_6
            raise NotImplemented('MAP Format Version 6 is not yet implemented')

        if self.version != self.gameSettings.mapVersion:
            raise AssertionError('expected map version '+str(self.gameSettings.mapVersion)+', but got '+str(self.version))

        self.sprite_format = ('pos', 'iii', 'cstat', 'h', 'picnum', 'h', 'gfxstuff', 'bBBB', 'texcoords', 'BBbb',
            'sectnum', 'h', 'statnum', 'h', 'angle', 'h', 'owner', 'h',
            'velocity', 'hhh', 'lowtag', 'h', 'hightag', 'h', 'extra', 'h')

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

        debug(self.__dict__, '\n')
        self.data = data
        
    def Randomize(self, seed):
        rng = random.Random(crc32('map randomize', self.name, seed))
        toSwap = []
        counters = {}
        for i in range(self.num_sprites):
            sprite = self.GetSprite(i)
            if sprite['picnum'] not in counters:
                counters[sprite['picnum']] = 1
            else:
                counters[sprite['picnum']] += 1
        debug(counters, '\n')
        
        for i in range(self.num_sprites):
            sprite = self.GetSprite(i)
            cstat = DecodeCstat(sprite['cstat'])
            if self.gameSettings.swappableItems and sprite['picnum'] not in self.gameSettings.swappableItems:
                continue
            if (self.game_name != 'Duke Nukem 3D' and not cstat.blocking) or cstat.blockingHitscan or cstat.invisible or cstat.onesided or cstat.facing != 0:
                trace('skipping sprite with cstat:',cstat, sprite)
                continue
            if sprite['cstat'] != 1:
                warning('unexpected cstat?', sprite['cstat'], sprite)
                #continue
            toSwap.append(i)
        self.SwapAllSprites(rng, toSwap)
        
    def SwapAllSprites(self, rng, toSwap):
        for a in range(len(toSwap)):
            a = toSwap[a]
            b = rng.randrange(0, len(toSwap))
            b = toSwap[b]
            if a == b:
                continue
            self.SwapSprites(a, b)
    
    def GetSprite(self, num):
        assert num >= 0
        assert num < self.num_sprites
        start = self.sprites_start + num*self.sprite_size
        sprite = fancy_unpack(
            '<', self.sprite_format,
            self.data[start:start+self.sprite_size]
        )
        return sprite

    def WriteSprite(self, sprite, num):
        assert num >= 0
        assert num < self.num_sprites
        start = self.sprites_start + num*self.sprite_size
        newdata = fancy_pack('<', self.sprite_format, sprite)
        i = start
        for b in newdata:
            self.data[i] = b
            i+=1
    
    def SwapSprites(self, idxa, idxb):
        debug('SwapSprites', idxa, idxb)
        a = self.GetSprite(idxa)
        b = self.GetSprite(idxb)
        trace(a, b, '\n')

        swapdictkey(a, b, 'pos')
        swapdictkey(a, b, 'sectnum')
        swapdictkey(a, b, 'angle')

        self.WriteSprite(a, idxa)
        self.WriteSprite(b, idxb)


def DecodeCstat(cstat):
    dict = {
        'blocking': bool(cstat & 1),
        'facing': cstat & 0x30,
        'onesided': cstat & 0x40,
        'blockingHitscan': bool(cstat & 0x800),
        'invisible': bool(cstat & 0x8000)
    }
    return namedtuple("Cstat", dict.keys())(*dict.values())
