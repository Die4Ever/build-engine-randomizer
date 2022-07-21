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

class Sector:
    def __init__(self, **kargs):
        self.__dict__ = dict(**kargs)
        self.nearbySectors:set
        self.walls:list
        self.shapes:list


class Sprite:
    def __init__(self, d):
        self.__dict__ = d
        self.pos:tuple
        self.picnum:int
        self.sectnum:int
        self.length:int

    def copy(self) -> 'Sprite':
        d = self.__dict__.copy()
        for k in d.keys():
            if type(d[k]) != int:
                d[k] = d[k].copy()
        return Sprite(d)

    def __repr__(self):
        return repr(self.__dict__)


def LoadMap(gameName, name, data: bytearray) -> 'MapFile':
    # Blood has a signature at the front of map files
    if data[:4] == b'BLM\x1a':
        return BloodMap(gameName, name, data)
    else:
        (version,) = unpack('<i', data[:4])
        if version <= 6:
            # https://moddingwiki.shikadi.net/wiki/MAP_Format_(Build)#Version_6
            raise NotImplementedError('MAP Format Version 6 is not yet implemented', name)
        return MapFile(gameName, name, data)


class MapFile:
    # https://moddingwiki.shikadi.net/wiki/MAP_Format_(Build)
    def __init__(self, gameName, name, data: bytearray):
        info('\n', name, len(data))
        self.name = name
        self.game_name = gameName
        self.gameSettings = games.GetGameMapSettings(gameName)
        self.crypt = 0

        self.version = 0
        self.sector_size = 40
        self.wall_size = 32
        self.sprite_size = 44
        self.header2Len = 0
        self.x_sector_size = 0
        self.x_sprite_size = 0
        self.x_wall_size = 0

        self.ReadHeaders(data)

        if self.version < self.gameSettings.minMapVersion or self.version > self.gameSettings.maxMapVersion:
            warning('unexpected map version', self.version, name, self.gameSettings.minMapVersion, self.gameSettings.maxMapVersion)

        trace(self.__dict__, '\n')
        self.data = data

        self.spritePacker = FancyPacker('<', OrderedDict(pos='iii', cstat='h', picnum='h', gfxstuff='bBBB',
            texcoords='BBbb', sectnum='h', statnum='h', angle='h', owner='h',
            velocity='hhh', lowtag='h', hightag='h', extra='h'))

        self.items = []
        self.enemies = []
        self.triggers = []
        self.other_sprites = []
        self.sectors = []
        self.walls = []
        self.sectorCache = {}
        self.ReadData()

    def ReadHeaders(self, data):
        self.numSects:int
        headerPacker = FancyPacker('<', OrderedDict(version='i', startPos='iii', startAngle='h', startSect='h', numSects='H'))
        self.headerLen = 22
        self.__dict__.update(headerPacker.unpack(data[:self.headerLen]))
        self.sectors_start = self.headerLen

    def ReadData(self):
        pos = self.ReadSectors()
        (self.num_walls,) = unpack('<H', self.data[pos:pos + 2])
        self.walls_start = pos + 2
        pos = self.ReadWalls()
        (self.num_sprites,) = unpack('<H', self.data[pos:pos + 2])
        self.sprites_start = pos + 2
        self.sprites_end = self.ReadSprites()

    def ReadSectors(self) -> int:
        pos = self.sectors_start
        for i in range(self.numSects):
            # pair of firstwall and numwalls
            data = self.data[pos:pos + self.sector_size]
            if self.crypt and self.version == 7:
                data = MapCrypt(data, self.mapRevision*self.sector_size)
            sect = unpack('<hh', data[:4])
            self.sectors.append(sect)
            pos += self.sector_size
            (extra,) = unpack('<h', data[-2:])
            if extra > 0:
                pos += self.x_sector_size
        return pos

    def ReadWalls(self) -> int:
        pos = self.walls_start
        for i in range(self.num_walls):
            data = self.data[pos:pos + self.wall_size]
            if self.crypt and self.version == 7:
                data = MapCrypt(data, (self.mapRevision*self.sector_size)  | 0x7474614d)
            wall = unpack('<iihhh', data[:14])
            self.walls.append(wall)
            pos += self.wall_size
            (extra,) = unpack('<h', data[-2:])
            if extra > 0:
                pos += self.x_wall_size
        return pos

    def ReadSprites(self):
        pos = self.sprites_start
        for i in range(self.num_sprites):
            sprite = self.GetSprite(i, pos)
            self.AppendSprite(sprite)
            pos += sprite.length
        return pos


    def Randomize(self, seed:int, settings:dict, spoilerlog):
        try:
            spoilerlog.SetFilename(self.name)
            spoilerlog.SetGameMapSettings(self.gameSettings)
            self.spoilerlog = spoilerlog
            self._Randomize(seed, settings)
        except:
            error('Randomize', self.name)
            raise
        finally:
            self.spoilerlog = None
            spoilerlog.FinishRandomizingFile()

    def _Randomize(self, seed:int, settings:dict):
        self.spoilerlog.write('before: '
            + 'items: ' + str(len(self.items)) + ', enemies: ' + str(len(self.enemies))
            + ', triggers: ' + str(len(self.triggers)) + ', other_sprites: ' + str(len(self.other_sprites))
        )

        chanceDupeItem:float = settings['MapFile.chanceDupeItem']
        chanceDeleteItem:float = settings['MapFile.chanceDeleteItem']

        chanceDupeEnemy:float = settings['MapFile.chanceDupeEnemy']
        chanceDeleteEnemy:float = settings['MapFile.chanceDeleteEnemy']

        itemVariety:float = settings['MapFile.itemVariety']
        enemyVariety:float = settings['MapFile.enemyVariety']

        rng = random.Random(crc32('map dupe items', self.name, seed))
        self.DupeSprites(rng, self.items, chanceDupeItem, 1, self.gameSettings.swappableItems.keys(), itemVariety, 'item')

        rng = random.Random(crc32('map shuffle items', self.name, seed))
        self.SwapAllSprites(rng, self.items, 'item')

        rng = random.Random(crc32('map reduce items', self.name, seed))
        self.ReduceSprites(rng, self.items, chanceDeleteItem, 'item')
        trace('\n')

        rng = random.Random(crc32('map dupe enemies', self.name, seed))
        self.DupeSprites(rng, self.enemies, chanceDupeEnemy, 2, self.gameSettings.addableEnemies.keys(), enemyVariety, 'enemy')

        rng = random.Random(crc32('map shuffle enemies', self.name, seed))
        self.SwapAllSprites(rng, self.enemies, 'enemy')

        rng = random.Random(crc32('map reduce enemies', self.name, seed))
        self.ReduceSprites(rng, self.enemies, chanceDeleteEnemy, 'enemy')
        trace('\n')

        rng = random.Random(crc32('map rando triggers', self.name, seed))
        self.RandomizeTriggers(rng, self.triggers, self.gameSettings.triggers)

        rng = random.Random(crc32('map additions', self.name, seed))
        for add in self.gameSettings.additions.get(self.name.lower(), []):
            self.AddSprite(rng, add)

        self.WriteSprites()

        self.spoilerlog.ListSprites('item', self.items)
        self.spoilerlog.ListSprites('enemy', self.enemies)

        self.spoilerlog.write('after: '
            + 'items: ' + str(len(self.items)) + ', enemies: ' + str(len(self.enemies))
            + ', triggers: ' + str(len(self.triggers)) + ', other_sprites: ' + str(len(self.other_sprites))
        )

    def IsItem(self, sprite:Sprite, cstat: CStat) -> bool:
        if self.gameSettings.swappableItems and sprite.picnum not in self.gameSettings.swappableItems:
                return False
        elif (not self.gameSettings.swappableItems) and sprite.picnum < 10:
            return False
        #elif (self.game_name == 'Ion Fury' and not cstat.blocking) or cstat.blockingHitscan or cstat.invisible or cstat.onesided or cstat.facing != 0:
        elif cstat.blockingHitscan or cstat.invisible or cstat.onesided or cstat.facing != 0:
            return False
        return True

    def SwapSprites(self, spritetype:str, a:Sprite, b:Sprite):
        self.spoilerlog.SwapSprites(spritetype, a, b)

        swapobjkey(a, b, 'pos')
        swapobjkey(a, b, 'sectnum')
        swapobjkey(a, b, 'angle')
        #swapobjkey(a, b, 'hightag')
        #swapobjkey(a, b, 'lowtag')# this seems to cause problems with shadow warrior enemies changing types?

    def DupeSprite(self, rng: random.Random, sprite:Sprite, spacing: float, possibleReplacements, replacementChance:float, spritetype: str) -> Union[Sprite,None]:
        sprite = sprite.copy()
        if rng.random() < replacementChance:
            sprite.picnum = rng.choice((*possibleReplacements, sprite.picnum))
        for i in range(20):
            x = rng.choice([-350, -250, -150, 0, 150, 250, 350])
            y = rng.choice([-350, -250, -150, 0, 150, 250, 350])
            if x == 0 and y == 0:
                continue
            sprite.pos[0] += x * spacing
            sprite.pos[1] += y * spacing
            newsect = self.GetContainingSectorNearby(sprite.sectnum, sprite.pos)
            if newsect is not None:
                sprite.sectnum = newsect
                self.spoilerlog.AddSprite(spritetype, sprite)
                return sprite
        return None

    def SwapAllSprites(self, rng, toSwap, spritetype:str):
        for a in range(len(toSwap)):
            b = rng.randrange(0, len(toSwap))
            if a == b:
                continue
            a = toSwap[a]
            b = toSwap[b]
            self.SwapSprites(spritetype, a, b)

    def DupeSprites(self, rng: random.Random, items: list, rate: float, spacing: float, possibleReplacements, replacementChance:float, spritetype: str):
        for sprite in items.copy():
            if rng.random() > rate:
                continue
            newsprite = self.DupeSprite(rng, sprite, spacing, possibleReplacements, replacementChance, spritetype)
            if newsprite:
                items.append(newsprite)

    def ReduceSprites(self, rng: random.Random, items: list, rate: float, spritetype: str):
        for i in range(len(items)-1, -1, -1):
            if rng.random() > rate:
                continue
            self.spoilerlog.DelSprite(spritetype, items[i])
            items[i] = items[-1]
            items.pop()

    def RandomizeTriggers(self, rng: random.Random, sprites: list, triggerSettings: dict) -> None:
        if not triggerSettings:
            return
        sprite:Sprite
        for sprite in sprites:
            settings = triggerSettings.get(sprite.picnum)
            if not settings:
                continue
            hightags = settings.get('hightags')
            if hightags:
                sprite.hightag = rng.choice([*hightags, sprite.hightag])
                self.spoilerlog.SpriteChangedTag('hightag', sprite, sprite.hightag)
            lowtags = settings.get('lowtags')
            if lowtags:
                sprite.lowtag = rng.choice([*lowtags, sprite.lowtag])
                self.spoilerlog.SpriteChangedTag('lowtag', sprite, sprite.lowtag)

    def AddSprite(self, rng: random.Random, add: dict) -> None:
        add = {
            'picnum': rng.choice(add['choices']),
            'cstat': 0,
            'gfxstuff': [0,0,32,0],
            'texcoords': [32,32,0,0],
            'statnum': 0,
            'angle': 1536,
            'owner': -1,
            'velocity': [0,0,0],
            'lowtag': 0,
            'hightag': 0,
            'extra': -1,
            'length': self.sprite_size,
            **add.copy()
        }
        del add['choices']

        sprite = Sprite(add)
        self.AppendSprite(sprite)
        spritetype = self.GetSpriteType(sprite)
        self.spoilerlog.AddSprite(spritetype, sprite)


    def AppendSprite(self, sprite:Sprite) -> None:
        cstat = CStat(sprite.cstat)
        if sprite.picnum in self.gameSettings.swappableItems:
            self.items.append(sprite)
        elif not self.gameSettings.swappableItems and self.IsItem(sprite, cstat):
            self.items.append(sprite)
        elif sprite.picnum in self.gameSettings.swappableEnemies and cstat.invisible==False:
            self.enemies.append(sprite)
        elif sprite.picnum in self.gameSettings.triggers:
            self.triggers.append(sprite)
        else:
            self.other_sprites.append(sprite)

    def GetSpriteType(self, sprite:Sprite) -> str:
        cstat = CStat(sprite.cstat)
        if sprite.picnum in self.gameSettings.swappableItems:
            return 'item'
        elif not self.gameSettings.swappableItems and self.IsItem(sprite, cstat):
            return 'item'
        elif sprite.picnum in self.gameSettings.swappableEnemies and cstat.invisible==False:
            return 'enemy'
        elif sprite.picnum in self.gameSettings.triggers:
            return 'trigger'
        else:
            return 'other'

    def WriteNumSprites(self, num):
        (self.data[self.sprites_start - 2], self.data[self.sprites_start - 1]) = pack('<H', num)

    def WriteSprites(self):
        sprites = self.items + self.enemies + self.triggers + self.other_sprites

        self.WriteNumSprites(len(sprites))

        pos = self.sprites_start
        self.data = self.data[:pos]
        for i in range(len(sprites)):
            self.WriteSprite(sprites[i], i, pos)
            pos += sprites[i].length

    def GetSprite(self, id, pos) -> Sprite:
        assert id >= 0
        assert pos + self.sprite_size <= len(self.data)
        if self.crypt and self.version == 7:
            data = MapCrypt(self.data[pos:pos+self.sprite_size], (self.mapRevision*self.sprite_size) | 0x7474614d)
            d = self.spritePacker.unpack(data)
        else:
            d = self.spritePacker.unpack(self.data[pos:pos+self.sprite_size])

        sprite = Sprite(d)
        sprite.length = self.sprite_size
        if sprite.extra > 0:
            pos += self.sprite_size
            sprite.extraData = self.data[pos:pos+self.x_sprite_size]
            sprite.length += self.x_sprite_size
        return sprite

    def WriteSprite(self, sprite:Sprite, id, pos):
        assert id >= 0
        assert pos == len(self.data)
        newdata = self.spritePacker.pack(sprite.__dict__)
        if self.crypt and self.version == 7:
            newdata = bytearray(newdata)
            newdata = MapCrypt(newdata, (self.mapRevision*self.sprite_size) | 0x7474614d)
        self.data.extend(newdata)
        if sprite.extra > 0:
            self.data.extend(sprite.extraData)


    def GetSectorInfo(self, sector:int) -> Sector:
        if sector in self.sectorCache:
            return self.sectorCache[sector]

        wall = self.sectors[sector][0]
        numwalls = self.sectors[sector][1]
        walls = {}
        nearbySectors = set()
        shapes = [[]]
        for i in range(numwalls):
            (x, y, nextwall, otherwall, nextsect) = self.walls[wall]
            nearbySectors.add(nextsect)
            point = (x, y)
            walls[wall] = point
            shapes[-1].append(point)
            if nextwall in walls:
                shapes.append([])
            wall += 1

        shapes.pop(-1)
        nearbySectors.discard(-1)
        nearbySectors.discard(sector)
        sect = Sector(walls=walls, nearbySectors=nearbySectors, shapes=shapes)
        self.sectorCache[sector] = sect
        return sect

    def GetContainingSectorNearby(self, sector:int, point) -> Union[int,None]:
        sectorInfo:Sector = self.GetSectorInfo(sector)
        if PointIsInSector(sectorInfo, point):
            return sector
        for sect2 in sectorInfo.nearbySectors:
            sectorInfo2:Sector = self.GetSectorInfo(sect2)
            if PointIsInSector(sectorInfo2, point):
                return sect2
        return None


    def GetData(self) -> bytearray:
        return self.data


class BloodMap(MapFile):
    def ReadHeaders(self, data):
        self.headerPacker = FancyPacker('<', OrderedDict(
            sig='4s', version='h', startPos='iii', startAngle='h', startSect='h', pskybits='h', visibility='i',
            songid='i', parallaxtype='c', mapRevision='i', numSects='H', num_walls='H', num_sprites='H')
        )
        self.headerLen = 43
        self.__dict__.update(self.headerPacker.unpack(data[:self.headerLen]))

        if self.songid != 0 and self.songid != 0x7474614d and self.songid != 0x4d617474:
            header = data[:self.headerLen]
            header[6:self.headerLen] = MapCrypt(header[6:self.headerLen], 0x7474614d)
            self.crypt = 1
            self.__dict__.update(self.headerPacker.unpack(header[:self.headerLen]))

        self.exactVersion = self.version
        self.version = self.exactVersion >> 8

        if self.version == 7: # if (byte_1A76C8)
            self.header2Len = 128
            header2Start = self.headerLen
            header2data = data[header2Start:header2Start + 128]
            if self.crypt:
                header2data = MapCrypt(header2data, self.num_walls)

            header2Packer = FancyPacker('<', OrderedDict(x_sprite_size='i', x_wall_size='i', x_sector_size='i'))
            header2 = header2Packer.unpack(header2data[64:76]) # skip the 64 bytes starting padding
            self.__dict__.update(header2)
        else:
            self.header2Len = 0
            self.x_sector_size = 60
            self.x_sprite_size = 56
            self.x_wall_size = 24

        self.hash = data[-4:]
        self.sky_start = self.headerLen + self.header2Len
        self.sky_length = (1<<self.pskybits) * 2
        self.sectors_start = self.sky_start + self.sky_length

    def WriteNumSprites(self, num):
        self.num_sprites = num
        header = self.headerPacker.pack(self.__dict__)
        if self.crypt:
            header = bytearray(header)
            header[6:self.headerLen] = MapCrypt(header[6:self.headerLen], 0x7474614d)
        self.data[6:self.headerLen] = header[6:self.headerLen]

    def ReadData(self):
        self.walls_start = self.ReadSectors()
        self.sprites_start = self.ReadWalls()
        self.sprites_end = self.ReadSprites()

    def WriteSprites(self):
        super().WriteSprites()
        # TODO: write md4 hash?
        crc:int = binascii.crc32(self.data)
        self.hash = pack('<I', crc)
        self.data.extend(self.hash)


def PointIsInSector(sect:Sector, testpos:list) -> bool:
    intersects = 0
    for shape in sect.shapes:
        intersects = PointIsInShape(shape, testpos, intersects)
    return (intersects%2)==1


def PointIsInShape(walls, p, intersects) -> int:
    # https://stackoverflow.com/a/2922778
    i=0
    n=len(walls)
    j=n-1
    while i < n:
        # ensure the wall straddles the point on the Y axis
        if ((walls[i][1] > p[1]) != (walls[j][1] > p[1])):
            # check slope?
            wallXSize = walls[j][0]-walls[i][0]
            wallYSize = walls[j][1]-walls[i][1]
            pointYDist = p[1]-walls[i][1]
            if p[0] < wallXSize * pointYDist / wallYSize + walls[i][0]:
                intersects += 1
        j=i
        i+=1
    return intersects

def MapCrypt(data:bytearray, key:int) -> bytearray:
    # reversible/symmetrical
    for i in range(len(data)):
        data[i] = data[i] ^ (key & 0xff)
        key += 1
    return data
