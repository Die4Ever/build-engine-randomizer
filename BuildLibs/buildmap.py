from struct import *
from BuildLibs import *
from BuildLibs import games

class CStat:
    def __init__(self, cstat):
        self.blocking = bool(cstat & 1)
        self.facing = cstat & 0x30
        self.onesided = cstat & 0x40
        self.blockingHitscan = bool(cstat & 0x800)
        self.invisible = bool(cstat & 0x8000)


class Sprite:
    def __init__(self, d):
        self.__dict__ = d

    def copy(self) -> 'Sprite':
        d = self.__dict__.copy()
        for k in d.keys():
            if type(d[k]) != int:
                d[k] = d[k].copy()
        return Sprite(d)

    def __repr__(self):
        return repr(self.__dict__)

class MapFile:
    # https://moddingwiki.shikadi.net/wiki/MAP_Format_(Build)
    def __init__(self, gameName, name, data: bytearray):
        info('\n', name, len(data))
        self.name = name
        self.game_name = gameName
        self.gameSettings = games.GetGameMapSettings(gameName)
        (self.version, self.startx, self.starty, self.startz, self.startangle, self.startsect, self.numsects) = unpack('<iiiihhH', data[:22])
        self.sector_size = 40
        self.wall_size = 32
        self.sprite_size = 44

        if self.version == 6:
            # https://moddingwiki.shikadi.net/wiki/MAP_Format_(Build)#Version_6
            raise NotImplemented('MAP Format Version 6 is not yet implemented', name)

        if self.version < self.gameSettings.minMapVersion or self.version > self.gameSettings.maxMapVersion:
            raise AssertionError('unexpected map version '+str(self.version), name)

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
        (num_sprites,) = unpack('<H', data[num_sprites_start:self.sprites_start])
        self.sprites_length = num_sprites * self.sprite_size

        trace(self.__dict__, '\n')
        self.data = data

        self.items = []
        self.enemies = []
        self.other_sprites = []
        for i in range(num_sprites):
            sprite = self.GetSprite(i)
            cstat = CStat(sprite.cstat)
            if self.IsItem(sprite, cstat):
                self.items.append(sprite)
            elif self.IsEnemy(sprite, cstat):
                self.enemies.append(sprite)
            else:
                self.other_sprites.append(sprite)

    def Randomize(self, seed):
        debug('items', len(self.items), 'enemies', len(self.enemies), 'other_sprites', len(self.other_sprites), sep=', ')

        rng = random.Random(crc32('map dupe items', self.name, seed))
        self.DupeSprites(rng, self.items, 0.65, 1)

        rng = random.Random(crc32('map shuffle items', self.name, seed))
        self.SwapAllSprites(rng, self.items)

        rng = random.Random(crc32('map reduce items', self.name, seed))
        self.ReduceSprites(rng, self.items, 0.45)
        trace('\n')

        rng = random.Random(crc32('map dupe enemies', self.name, seed))
        self.DupeSprites(rng, self.enemies, 0.85, 3)

        rng = random.Random(crc32('map shuffle enemies', self.name, seed))
        self.SwapAllSprites(rng, self.enemies)

        rng = random.Random(crc32('map reduce enemies', self.name, seed))
        self.ReduceSprites(rng, self.enemies, 0.25)
        trace('\n')

        self.WriteSprites()
        debug('items', len(self.items), 'enemies', len(self.enemies), 'other_sprites', len(self.other_sprites), sep=', ')

    def IsItem(self, sprite:Sprite, cstat: CStat) -> bool:
        if self.gameSettings.swappableItems and sprite.picnum not in self.gameSettings.swappableItems:
                return False
        elif (not self.gameSettings.swappableItems) and sprite.picnum < 10:
            return False
        #elif (self.game_name == 'Ion Fury' and not cstat.blocking) or cstat.blockingHitscan or cstat.invisible or cstat.onesided or cstat.facing != 0:
        elif cstat.blockingHitscan or cstat.invisible or cstat.onesided or cstat.facing != 0:
            return False
        return True

    def IsEnemy(self, sprite:Sprite, cstat: CStat) -> bool:
        return sprite.picnum in self.gameSettings.swappableEnemies and cstat.invisible==False

    def SwapSprites(self, a:Sprite, b:Sprite):
        trace(a, b, '\n')

        swapobjkey(a, b, 'pos')
        swapobjkey(a, b, 'sectnum')
        swapobjkey(a, b, 'angle')

    def DupeSprite(self, rng: random.Random, sprite:Sprite, spacing: float) -> Sprite:
        sprite = sprite.copy()
        x = rng.choice([-300, -200, 200, 300])
        y = rng.choice([-300, -200, 200, 300])
        sprite.pos[0] += x * spacing
        sprite.pos[1] += y * spacing
        # TODO: check walls? and floors?
        return sprite

    def SwapAllSprites(self, rng, toSwap):
        for a in range(len(toSwap)):
            b = rng.randrange(0, len(toSwap))
            if a == b:
                continue
            a = toSwap[a]
            b = toSwap[b]
            self.SwapSprites(a, b)

    def DupeSprites(self, rng: random.Random, items: list, rate: float, spacing: float):
        for sprite in items.copy():
            if rng.random() > rate:
                continue
            newsprite = self.DupeSprite(rng, sprite, spacing)
            items.append(newsprite)

    def ReduceSprites(self, rng: random.Random, items: list, rate: float):
        for i in range(len(items)-1, -1, -1):
            if rng.random() > rate:
                continue
            items[i] = items[-1]
            items.pop()

    def WriteSprites(self):
        sprites = self.items + self.enemies + self.other_sprites
        new_len = self.sprites_start + len(sprites) * self.sprite_size
        if len(self.data) < new_len:
            diff = new_len - len(self.data)
            self.data = bytearray().join((self.data, b'\x00' * diff))
        elif len(self.data) > new_len:
            self.data = self.data[:new_len]

        newdata = pack('<H', len(sprites))
        i = self.walls_start + self.walls_length
        for b in newdata:
            self.data[i] = b
            i+=1

        for i in range(len(sprites)):
            self.WriteSprite(sprites[i], i)

    def GetSprite(self, num) -> Sprite:
        assert num >= 0
        start = self.sprites_start + num*self.sprite_size
        assert start + self.sprite_size <= len(self.data)
        sprite = fancy_unpack(
            '<', self.sprite_format,
            self.data[start:start+self.sprite_size]
        )
        return Sprite(sprite)

    def WriteSprite(self, sprite:Sprite, num):
        assert num >= 0
        start = self.sprites_start + num*self.sprite_size
        assert start + self.sprite_size <= len(self.data)
        newdata = fancy_pack('<', self.sprite_format, sprite.__dict__)
        i = start
        for b in newdata:
            self.data[i] = b
            i+=1

    def GetData(self) -> bytearray:
        return self.data
