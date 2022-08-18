import abc
import binascii
import copy
import random
import struct
from pathlib import Path
from typing import OrderedDict, Union

from BuildLibs import crc32, error, games, info, swapobjkey, trace, warning, FancyPacker


class CStat:

    def __init__(self, cstat):
        self.blocking = bool(cstat & 1)
        self.facing = bool(cstat & 0x30)       # 48
        self.onesided = bool(cstat & 0x40)
        self.blockingHitscan = bool(cstat & 0x800)
        self.invisible = bool(cstat & 0x8000)


class Sector:

    def __init__(self, data):
        self.wallptr: int = data.get('wallptr', 0)
        self.wallnum: int = data.get('wallnum', 0)
        self.ceilingz: int = data.get('ceilingz', 0)
        self.floorz: int = data.get('floorz', 0)
        self.ceilingstat: int = data.get('ceilingstat', 0)
        self.floorstat: int = data.get('floorstat', 0)
        self.ceilingpicnum: int = data.get('ceilingpicnum', 0)
        self.ceilingheinum: int = data.get('ceilingheinum', 0)
        self.ceilingshade: int = data.get('ceilingshade', 0)
        self.ceiling_palette: int = data.get('ceiling_palette', 0)
        self.ceiling_texcoords: list = data.get('ceiling_texcoords', [0, 0])
        self.floorpicnum: int = data.get('floorpicnum', 0)
        self.floorheinum: int = data.get('floorheinum', 0)
        self.floorshade: int = data.get('floorshade', 0)
        self.floor_palette: int = data.get('floor_palette', 0)
        self.floor_texcoords: list = data.get('floor_texcoords', [0, 0])
        self.visibility: int = data.get('visibility', 0)
        self.filler: int = data.get('filler', 0)
        self.lowtag: int = data.get('lowtag', 0)
        self.hightag: int = data.get('hightag', 0)
        self.extra: int = data.get('extra', -1)
        self.length: int = data.get('length', 0)
        self.ceilingxpanning: int = data.get('ceilingxpanning', 0)
        self.floorxpanning: int = data.get('floorxpanning', 0)
        self.ceilingypanning: int = data.get('ceilingypanning', 0)
        self.floorypanning: int = data.get('floorypanning', 0)

        self.walls: Union[list, None] = data.get('walls', None)
        self.nearbySectors: Union[set, None] = data.get('nearbySectors', None)
        self.shapes: Union[list, None] = data.get('shapes', None)


class Wall:

    def __init__(self, data):
        self.pos: list = data.get('pos', [0, 0])
        self.next_wall: int = data.get('next_wall', 0)
        self.next_sector_wall: int = data.get('next_sector_wall', -1)
        self.next_sector: int = data.get('next_sector', -1)
        self.cstat: int = data.get('cstat', 0)
        # self.picnum: int = data.get('picnum', 142)
        self.picnum: int = data.get('picnum', -1)
        self.overpicnum : int = data.get('overpicnum', 0)
        self.shade: int = data.get('shade', 0)
        self.palette: int = data.get('palette', 0)
        self.texcoords: list = data.get('texcoords', [1, 1, 0, 0])
        self.lowtag: int = data.get('lowtag', 0)
        self.hightag: int = data.get('hightag', 0)
        self.extra: int = data.get('extra', -1)
        self.length: int = data.get('length', 0)


class Sprite:

    def __init__(self, data):
        self.pos: list = data.get('pos', [0, 0, 0])
        self.cstat: int = data.get('cstat', 0)
        self.picnum: int = data.get('picnum', 0)
        self.shade: int = data.get('shade', 0)
        self.palette: int = data.get('palette', 0)
        self.clipdist: int = data.get('clipdist', 0)
        self.filler: int = data.get('filler', 0)
        self.texcoords: list = data.get('texcoords', [0, 0, 0, 0])
        self.sectnum: int = data.get('sectnum', -1)
        self.statnum: int = data.get('statnum', 0)
        self.angle: int = data.get('angle', 0)
        self.owner: int = data.get('owner', -1)
        self.velocity: list = data.get('velocity', [0, 0, 0])
        self.lowtag: int = data.get('lowtag', 0)
        self.hightag: int = data.get('hightag', 0)
        self.extra: int = data.get('extra', -1)
        self.length: int = data.get('length', 0)

    def __copy__(self) -> 'Sprite':
        cls = self.__class__
        copied = cls.__new__(cls)
        copied.__dict__.update(self.__dict__)
        copied.pos = copied.pos[:]
        copied.texcoords = copied.texcoords[:]
        copied.velocity = copied.velocity[:]
        return copied


class MapFileBase(metaclass=abc.ABCMeta):

    """
    https://moddingwiki.shikadi.net/wiki/MAP_Format_(Build)

    """

    HEADER_SIZE = 20
    SECTOR_SIZE = 40
    WALL_SIZE = 32
    SPRITE_SIZE = 44

    def __init__(self, gameSettings, name, data: bytearray = None):
        self.gameSettings = gameSettings
        self.name = name
        self.data = data

        self.version = 0
        self.startPos = [0, 0, 0]
        self.startAngle = 0
        self.startSect = 0
        self.num_sectors = 0
        self.num_sprites = 0
        self.num_walls = 0

        self.crypt = 0

        self.header2Len = 0
        self.x_sector_size = 0
        self.x_wall_size = 0
        self.x_sprite_size = 0

        self.CreateHeaderPacker()
        self.CreateSectorPacker()
        self.CreateWallPacker()
        self.CreateSpritePacker()

        assert self.HEADER_SIZE == self.headerPacker.calcsize()
        assert self.SECTOR_SIZE == self.sectorPacker.calcsize()
        assert self.WALL_SIZE == self.wallPacker.calcsize()
        assert self.SPRITE_SIZE == self.spritePacker.calcsize()

        self.sectors = []
        self.walls = []
        #self.sprites = []
        self.items = []
        self.enemies = []
        self.triggers = []
        self.other_sprites = []
        self.sectorCache = {}

        if data is not None:
            self.ReadData()
            assert len(self.sectors) > 0
            assert len(self.walls) > 0
            # assert len(self.sprites) > 0

    def __str__(self):
        lines = []
        lines.append(f'MapFile: {self.name}')

        lines.append(f'    version: {self.version}')
        lines.append(f'    startPos: {self.startPos}')
        lines.append(f'    startAngle: {self.startAngle}')
        lines.append(f'    startSect: {self.startSect}')

        lines.append(f'    num sectors: {self.num_sectors}')
        lines.append(f'    num walls: {self.num_walls}')
        lines.append(f'    num sprites: {self.num_sprites}')
        lines.append(f'    len sectors: {len(self.sectors)}')
        lines.append(f'    len walls: {len(self.walls)}')
        lines.append(f'    len sprites: {len(self.sprites)}')
        lines.append(f'    len data: {len(self.data) if self.data is not None else None}')

        return '\n'.join(lines)

    @property
    def sprites(self):
        return self.items + self.enemies + self.triggers + self.other_sprites

    def Randomize(self, seed:int, settings:dict, spoilerlog):
        try:
            spoilerlog.SetFilename(Path(self.name))
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
        self.DupeSprites(rng, self.items, chanceDupeItem, 1, self.gameSettings.swappableItems, itemVariety, 'item')

        rng = random.Random(crc32('map shuffle items', self.name, seed))
        self.SwapAllSprites(rng, self.items, 'item')

        rng = random.Random(crc32('map reduce items', self.name, seed))
        self.ReduceSprites(rng, self.items, chanceDeleteItem, 'item')
        trace('\n')

        rng = random.Random(crc32('map dupe enemies', self.name, seed))
        enemiesReplacements = {}
        for i in self.gameSettings.addableEnemies:
            enemiesReplacements[i] = self.gameSettings.swappableEnemies[i]
        self.DupeSprites(rng, self.enemies, chanceDupeEnemy, 2, enemiesReplacements, enemyVariety, 'enemy')

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

        self.WriteData()

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

    def DupeSprite(self, rng: random.Random, sprite:Sprite, spacing: float, possibleReplacements:dict, replacementChance:float, spritetype: str) -> Union[Sprite,None]:
        sprite = copy.copy(sprite)
        if rng.random() < replacementChance:
            replace = rng.choice((*possibleReplacements.keys(), sprite.picnum))
            if replace != sprite.picnum:
                r = possibleReplacements[replace]
                sprite.lowtag = r.get('lowtag', sprite.lowtag)
                xrepeat = r.get('xrepeat', sprite.texcoords[0])
                yrepeat = r.get('yrepeat', sprite.texcoords[1])
                palettes = r.get('palettes', [0])
                sprite.palette = rng.choice(palettes)
                sprite.texcoords = [xrepeat, yrepeat, 0, 0]
            sprite.picnum = replace
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

    def DupeSprites(self, rng: random.Random, items: list, rate: float, spacing: float, possibleReplacements:dict, replacementChance:float, spritetype: str):
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
            if sprite.hightag in settings.get('not_hightags', []):
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
        # keep up to date with CreateSpritePacker
        add = {
            'picnum': rng.choice(add['choices']),
            'cstat': 0,
            'shade': 0,
            'palette': 0,
            'clipdist': 32,
            'filler': 0,
            'texcoords': [32,32,0,0],
            'statnum': 0,
            'angle': 1536,
            'owner': -1,
            'velocity': [0,0,0],
            'lowtag': 0,
            'hightag': 0,
            'extra': -1,
            'length': self.SPRITE_SIZE,
            **add.copy()
        }
        del add['choices']

        sprite = Sprite(add)
        self.AppendSprite(sprite)
        spritetype = self.GetSpriteType(sprite)
        self.spoilerlog.AddSprite(spritetype, sprite)

    def AppendSector(self, sector: Sector) -> None:
        self.sectors.append(sector)

    def AppendWall(self, wall: Wall) -> None:
        self.walls.append(wall)

    def AppendSprite(self, sprite: Sprite) -> None:
        cstat = CStat(sprite.cstat)
        if sprite.picnum in self.gameSettings.swappableItems:
            self.items.append(sprite)
        elif not self.gameSettings.swappableItems and self.IsItem(sprite, cstat):
            self.items.append(sprite)
        elif sprite.picnum in self.gameSettings.swappableEnemies and not cstat.invisible:
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
        elif sprite.picnum in self.gameSettings.swappableEnemies and not cstat.invisible:
            return 'enemy'
        elif sprite.picnum in self.gameSettings.triggers:
            return 'trigger'
        else:
            return 'other'

    def GetSector(self, pos) -> Sector:
        data = self.data[pos:pos + self.SECTOR_SIZE]

        if self.crypt and self.version == 7:
            data = MapCrypt(data, self.mapRevision * self.SECTOR_SIZE)

        sector = Sector(self.sectorPacker.unpack(data))
        sector.length = self.SECTOR_SIZE
        if sector.extra > 0:
            pos += self.SECTOR_SIZE
            sector.extraData = self.data[pos:pos + self.x_sector_size]
            sector.length += self.x_sector_size
        return sector

    def GetWall(self, pos) -> Wall:
        data = self.data[pos:pos + self.WALL_SIZE]

        if self.crypt and self.version == 7:
            data = MapCrypt(data, (self.mapRevision * self.SECTOR_SIZE) | 0x7474614d)

        wall = Wall(self.wallPacker.unpack(data))
        wall.length = self.WALL_SIZE
        if wall.extra > 0:
            pos += self.WALL_SIZE
            wall.extraData = self.data[pos:pos + self.x_wall_size]
            wall.length += self.x_wall_size
        return wall

    def GetSprite(self, pos) -> Sprite:
        data = self.data[pos:pos + self.SPRITE_SIZE]

        if self.crypt and self.version == 7:
            data = MapCrypt(self.data[pos:pos + self.SPRITE_SIZE], (self.mapRevision * self.SPRITE_SIZE) | 0x7474614d)

        sprite = Sprite(self.spritePacker.unpack(data))
        sprite.length = self.SPRITE_SIZE
        if sprite.extra > 0:
            pos += self.SPRITE_SIZE
            sprite.extraData = self.data[pos:pos + self.x_sprite_size]
            sprite.length += self.x_sprite_size
        return sprite

    @abc.abstractmethod
    def CreateHeaderPacker(self):
        return

    @abc.abstractmethod
    def CreateSectorPacker(self):
        # keep AddSector up to date with this
        return

    @abc.abstractmethod
    def CreateWallPacker(self):
        # keep AddWall up to date with this
        return

    @abc.abstractmethod
    def CreateSpritePacker(self):
        # keep AddSprite up to date with this
        return

    def ReadHeaders(self) -> int:
        self.__dict__.update(self.headerPacker.unpack(self.data[:self.HEADER_SIZE]))
        return self.HEADER_SIZE

    def WriteHeaders(self) -> int:
        # TODO: Create header object
        newdata = self.headerPacker.pack(self.__dict__)
        self.data.extend(newdata)
        return len(newdata)

    def ReadNumSectors(self, start) -> int:
        stop = start + 2
        (self.num_sectors,) = struct.unpack('<H', self.data[start:stop])
        return stop

    def WriteNumSectors(self, start) -> int:
        new_data = struct.pack('<H', len(self.sectors))
        self.data.extend(new_data)
        return start + len(new_data)

    def ReadNumWalls(self, start) -> int:
        stop = start + 2
        (self.num_walls, ) = struct.unpack('<H', self.data[start:stop])
        return stop

    def WriteNumWalls(self, start) -> int:
        new_data = struct.pack('<H', len(self.walls))
        self.data.extend(new_data)
        return start + len(new_data)

    def ReadNumSprites(self, start) -> int:
        stop = start + 2
        (self.num_sprites, ) = struct.unpack('<H', self.data[start:stop])
        return stop

    def WriteNumSprites(self, pos) -> int:
        new_data = struct.pack('<H', len(self.sprites))
        self.data.extend(new_data)
        return pos + len(new_data)

    def ReadSectors(self, pos) -> int:
        for i in range(self.num_sectors):
            sector = self.GetSector(pos)
            self.AppendSector(sector)
            pos += sector.length
        return pos

    def WriteSector(self, sector: Sector):
        newdata = self.sectorPacker.pack(sector.__dict__)
        if sector.extra > 0:
            newdata += sector.extraData
        self.data.extend(newdata)

    def WriteSectors(self, pos) -> int:
        for sector in self.sectors:
            self.WriteSector(sector)
            pos += sector.length
        return pos

    def ReadWalls(self, pos) -> int:
        for i in range(self.num_walls):
            wall = self.GetWall(pos)
            self.AppendWall(wall)
            pos += wall.length
        return pos

    def WriteWall(self, wall: Wall):
        newdata = self.wallPacker.pack(wall.__dict__)
        if wall.extra > 0:
            newdata += wall.extraData
        self.data.extend(newdata)

    def WriteWalls(self, pos) -> int:
        for wall in self.walls:
            self.WriteWall(wall)
            pos += wall.length
        return pos

    def ReadSprites(self, pos) -> int:
        for i in range(self.num_sprites):
            sprite = self.GetSprite(pos)
            self.AppendSprite(sprite)
            pos += sprite.length
        return pos

    def WriteSprite(self, sprite: Sprite):
        try:
            newdata = self.spritePacker.pack(sprite.__dict__)
        except:
            print('FAILD:', sprite.__dict__)
            raise

        newdata = bytearray(newdata)
        if self.crypt and self.version == 7:
            newdata = MapCrypt(newdata, (self.mapRevision * self.SPRITE_SIZE) | 0x7474614d)

        if sprite.extra > 0:
            newdata.extend(sprite.extraData)
        self.data.extend(newdata)

    def WriteSprites(self, pos) -> int:
        for sprite in self.sprites:
            self.WriteSprite(sprite)
            pos += sprite.length
        return pos

    @abc.abstractmethod
    def ReadData(self):
        return

    @abc.abstractmethod
    def WriteData(self):
        return

    def GetSectorInfo(self, sector:int) -> Sector:
        if sector in self.sectorCache:
            return self.sectorCache[sector]

        assert sector >= 0
        assert sector < len(self.sectors)

        wallptr = self.sectors[sector].wallptr
        numwalls = self.sectors[sector].wallnum

        walls = {}
        nearbySectors = set()
        shapes = [[]]
        for i in range(numwalls):
            w = self.walls[wallptr]
            nearbySectors.add(w.next_sector)
            walls[wallptr] = w.pos
            shapes[-1].append(w.pos)
            if w.next_wall in walls:
                shapes.append([])
            wallptr += 1

        shapes.pop(-1)
        nearbySectors.discard(-1)
        nearbySectors.discard(sector)
        sect = Sector({'walls': walls, 'nearbySectors': nearbySectors, 'shapes': shapes})
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
