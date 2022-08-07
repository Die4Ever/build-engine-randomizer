import binascii
import struct
from typing import OrderedDict, Union
from BuildLibs import crc32, error, games, info, swapobjkey, trace, warning, FancyPacker
from BuildLibs.buildmapbase import CStat, Sector, Wall, Sprite, MapFileBase, MapCrypt

class MapFile(MapFileBase):
    def CreateHeaderPacker(self):
        self.headerPacker = FancyPacker(
            '<',
            OrderedDict(
                version='i',
                startPos='iii',
                startAngle='h',
                startSect='h',
            )
        )

    def CreateSectorPacker(self):
        # keep AddSector up to date with this
        self.sectorPacker = FancyPacker(
            '<',
            OrderedDict(
                wallptr='h',
                wallnum='h',
                ceilingz='i',
                floorz='i',
                ceilingstat='h',
                floorstat='h',
                ceilingpicnum='h',
                ceilingheinum='h',
                ceilingshade='b',
                ceiling_palette='B',
                ceiling_texcoords='BB',
                floorpicnum='h',
                floorheinum='h',
                floorshade='b',
                floor_palette='B',
                floor_texcoords='BB',
                visibility='B',
                filler='B',
                lowtag='h',
                hightag='h',
                extra='h',
            )
        )

    def CreateWallPacker(self):
        # keep AddWall up to date with this
        self.wallPacker = FancyPacker(
            '<',
            OrderedDict(
                pos='ii',
                next_wall='h',
                next_sector_wall='h',
                next_sector='h',
                cstat='h',
                picnum='h',
                overpicnum='h',
                shade='b',
                palette='B',
                texcoords='BBBB',
                lowtag='h',
                hightag='h',
                extra='h',
            )
        )

    def CreateSpritePacker(self):
        # keep AddSprite up to date with this
        self.spritePacker = FancyPacker(
            '<',
            OrderedDict(
                pos='iii',
                cstat='h',
                picnum='h',
                shade='b',
                palette='B',
                clipdist='B',
                filler='B',
                texcoords='BBbb',
                sectnum='h',
                statnum='h',
                angle='h',
                owner='h',
                velocity='hhh',
                lowtag='h',
                hightag='h',
                extra='h',
            )
        )

    def ReadData(self):
        pos: int = self.ReadHeaders()
        if self.version < self.gameSettings.minMapVersion or self.version > self.gameSettings.maxMapVersion:
            warning('unexpected map version', self.version, self.name, self.gameSettings.minMapVersion, self.gameSettings.maxMapVersion)
        pos = self.ReadNumSectors(pos)
        pos = self.ReadSectors(pos)
        pos = self.ReadNumWalls(pos)
        pos = self.ReadWalls(pos)
        pos = self.ReadNumSprites(pos)
        self.ReadSprites(pos)

    def WriteData(self):
        self.data = bytearray()
        pos: int = self.WriteHeaders()
        pos = self.WriteNumSectors(pos)
        pos = self.WriteSectors(pos)
        pos = self.WriteNumWalls(pos)
        pos = self.WriteWalls(pos)
        pos = self.WriteNumSprites(pos)
        self.WriteSprites(pos)

class MapV6(MapFile):

    SECTOR_SIZE = 37
    SPRITE_SIZE = 43

    def CreateSectorPacker(self):
        # keep AddSector up to date with this
        self.sectorPacker = FancyPacker(
            '<',
            OrderedDict(
                wallptr='h',
                wallnum='h',
                ceilingpicnum='h',
                floorpicnum='h',
                ceilingheinum='h',
                floorheinum='h',
                ceilingz='i',
                floorz='i',
                ceilingshade='b',
                floorshade='b',
                ceilingxpanning='B',
                floorxpanning='B',
                ceilingypanning='B',
                floorypanning='B',
                ceilingstat='B',
                floorstat='B',
                ceiling_palette='B',
                floor_palette='B',
                visibility='B',
                lowtag='h',
                hightag='h',
                extra='h',
            )
        )

    def CreateWallPacker(self):
        # keep AddWall up to date with this
        self.wallPacker = FancyPacker(
            '<',
            OrderedDict(
                pos='ii',
                next_wall='h',
                next_sector='h',
                next_sector_wall='h',
                picnum='h',
                overpicnum='h',
                shade='b',
                palette='B',
                cstat='h',
                texcoords='BBBB',
                lowtag='h',
                hightag='h',
                extra='h',
            )
        )

    def CreateSpritePacker(self):
        # keep AddSprite up to date with this
        self.spritePacker = FancyPacker(
            '<',
            OrderedDict(
                pos='iii',
                cstat='h',
                shade='b',
                palette='B',
                clipdist='B',
                texcoords='BBbb',
                picnum='h',
                angle='h',
                velocity='hhh',
                owner='h',
                sectnum='h',
                statnum='h',
                lowtag='h',
                hightag='h',
                extra='h',
            )
        )


class BloodMap(MapFile):

    HEADER_SIZE = 43

    def CreateHeaderPacker(self):
        self.headerPacker = FancyPacker(
            '<',
            OrderedDict(
                sig='4s',
                version='h',
                startPos='iii',
                startAngle='h',
                startSect='h',
                pskybits='h',
                visibility='i',
                songid='i',
                parallaxtype='c',
                mapRevision='i',
                num_sectors='H',
                num_walls='H',
                num_sprites='H',
            )
        )

    def ReadHeaders(self) -> int:
        super().ReadHeaders()

        if self.songid != 0 and self.songid != 0x7474614d and self.songid != 0x4d617474:
            header = self.data[:self.HEADER_SIZE]
            header[6:self.HEADER_SIZE] = MapCrypt(header[6:self.HEADER_SIZE], 0x7474614d)
            self.crypt = 1
            self.__dict__.update(self.headerPacker.unpack(header[:self.HEADER_SIZE]))

        self.exactVersion = self.version
        self.version = self.exactVersion >> 8

        if self.version == 7: # if (byte_1A76C8)
            self.header2Len = 128
            header2Start = self.HEADER_SIZE
            header2data = self.data[header2Start:header2Start + 128]
            self.header2data = header2data
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

        self.hash = self.data[-4:]
        self.sky_start = self.HEADER_SIZE + self.header2Len
        self.sky_length = (1 << self.pskybits) * 2
        self.sky_data = self.data[self.sky_start:self.sky_start + self.sky_length]
        return self.sky_start + self.sky_length

    def WriteHeaders(self):
        version = self.version
        self.version = self.exactVersion
        self.num_sprites = len(self.sprites)
        header = self.headerPacker.pack(self.__dict__)
        if self.crypt:
            header = bytearray(header)
            header[6:self.HEADER_SIZE] = MapCrypt(header[6:self.HEADER_SIZE], 0x7474614d)
        self.data.extend(header)
        if self.header2Len:
            self.data.extend(self.header2data)
        self.data.extend(self.sky_data)
        return len(self.data)

    def ReadData(self):
        pos: int = self.ReadHeaders()
        pos = self.ReadSectors(pos)
        pos = self.ReadWalls(pos)
        self.ReadSprites(pos)

    def WriteData(self):
        self.data = bytearray()
        pos: int = self.WriteHeaders()
        pos = self.WriteSectors(pos)
        pos = self.WriteWalls(pos)
        self.WriteSprites(pos)

    def WriteSprites(self, pos):
        super().WriteSprites(pos)
        crc: int = binascii.crc32(self.data)
        self.hash = struct.pack('<I', crc)
        self.data.extend(self.hash)


def LoadMap(gameName, name, data: bytearray) -> 'MapFile':
    gameSettings = games.GetGameMapSettings(gameName)
    # Blood has a signature at the front of map files
    if data[:4] == b'BLM\x1a':
        return BloodMap(gameSettings, name, data)
    else:
        (version,) = struct.unpack('<i', data[:4])
        if version <= 6:
            # https://moddingwiki.shikadi.net/wiki/MAP_Format_(Build)#Version_6
            return MapV6(gameSettings, name, data)
        return MapFile(gameSettings, name, data)
