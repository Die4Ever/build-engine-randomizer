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
            raise NotImplementedError('MAP Format Version 6 is not yet implemented', name)

        if self.version < self.gameSettings.minMapVersion or self.version > self.gameSettings.maxMapVersion:
            raise AssertionError('unexpected map version '+str(self.version), name)

        self.packer = FancyPacker('<', dict(pos='iii', cstat='h', picnum='h', gfxstuff='bBBB',
            texcoords='BBbb', sectnum='h', statnum='h', angle='h', owner='h',
            velocity='hhh', lowtag='h', hightag='h', extra='h'))

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
        self.triggers = []
        self.other_sprites = []
        for i in range(num_sprites):
            sprite = self.GetSprite(i)
            self.AppendSprite(sprite)

        self.sectors = []
        self.sectorCache = {}
        for i in range(self.numsects):
            # first wall, num walls
            start = self.sectors_start + i*self.sector_size
            # pair of firstwall and numwalls
            sect = unpack('<hh', data[start:start + 4])
            self.sectors.append(sect)


    def Randomize(self, seed:int, settings:dict, spoilerlog):
        try:
            spoilerlog.SetFilename(self.name)
            spoilerlog.SetGameMapSettings(self.gameSettings)
            self.spoilerlog = spoilerlog
            self._Randomize(seed, settings)
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

    def IsEnemy(self, sprite:Sprite, cstat: CStat) -> bool:
        return sprite.picnum in self.gameSettings.swappableEnemies and cstat.invisible==False

    def IsTrigger(self, sprite:Sprite, cstat: CStat) -> bool:
        return sprite.picnum in self.gameSettings.triggers

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
            **add.copy()
        }
        del add['choices']

        sprite = Sprite(add)
        self.AppendSprite(sprite)
        spritetype = self.GetSpriteType(sprite)
        self.spoilerlog.AddSprite(spritetype, sprite)


    def AppendSprite(self, sprite:Sprite) -> None:
        cstat = CStat(sprite.cstat)
        if self.IsItem(sprite, cstat):
            self.items.append(sprite)
        elif self.IsEnemy(sprite, cstat):
            self.enemies.append(sprite)
        elif self.IsTrigger(sprite, cstat):
            self.triggers.append(sprite)
        else:
            self.other_sprites.append(sprite)

    def GetSpriteType(self, sprite:Sprite) -> str:
        cstat = CStat(sprite.cstat)
        if self.IsItem(sprite, cstat):
            return 'item'
        elif self.IsEnemy(sprite, cstat):
            return 'enemy'
        elif self.IsTrigger(sprite, cstat):
            return 'trigger'
        else:
            return 'other'

    def WriteSprites(self):
        sprites = self.items + self.enemies + self.triggers + self.other_sprites
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
        sprite = self.packer.unpack(self.data[start:start+self.sprite_size])
        return Sprite(sprite)

    def WriteSprite(self, sprite:Sprite, num):
        assert num >= 0
        start = self.sprites_start + num*self.sprite_size
        assert start + self.sprite_size <= len(self.data)
        newdata = self.packer.pack(sprite.__dict__)
        i = start
        for b in newdata:
            self.data[i] = b
            i+=1

    def GetSectorInfo(self, sector:int) -> Sector:
        if sector in self.sectorCache:
            return self.sectorCache[sector]

        wall = self.sectors[sector][0]
        numwalls = self.sectors[sector][1]
        walls = {}
        nearbySectors = set()
        shapes = [[]]
        for i in range(numwalls):
            start = self.walls_start + wall*self.wall_size
            (x, y, nextwall, otherwall, nextsect) = unpack('<iihhh', self.data[start:start + 14])
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
