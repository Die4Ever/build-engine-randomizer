from BuildLibs.grpbase import *
from zipfile import ZipFile
import binascii
from mmap import mmap, ACCESS_READ

def LoadGrpFile(filepath:Path) -> 'GrpBase':
    info(filepath)
    game:BuildGames.GameInfo = BuildGames.GetGame(filepath)
    filesize = os.path.getsize(filepath)
    with open(filepath, mode='rb') as f:
        sig = f.read(12)

    trace(sig)
    if sig[:4] == b'PK\x03\x04':
        debug('is a zip file')
        return GrpZipFile(filepath, filesize, game)
    elif sig[:12] == b'KenSilverman':
        debug('is a GRP file')
        return GrpFile(filepath, filesize, game)
    elif sig[:4] == b'RFF\x1a':
        debug('is an RFF file')
        return RffFile(filepath, filesize, game)
    else:
        raise Exception(filepath + ' is an unknown type, size: ', filesize, game)


# https://moddingwiki.shikadi.net/wiki/GRP_Format
class GrpFile(GrpBase):
    def GetFilesInfo(self) -> None:
        with open(self.filepath, 'rb') as f:
            f.seek(12)
            data = f.read(4)
            (numFiles,) = struct.unpack('<I', data)
            trace('numFiles:', numFiles)
            offset = 16 + 16*numFiles
            for i in range(numFiles):
                data = f.read(16)
                name = data[:12].strip(b'\x00').decode('ascii')
                (size,) = struct.unpack('<I', data[12:16])
                trace(name, size)
                self.files[name] = {
                    'size': size,
                    'offset': offset
                }
                offset += size

    def _getfile(self, name, filehandle) -> bytes:
        info = self.files.get(name)
        if not info:
            raise Exception('file not found in GRP', name, len(self.files))

        if filehandle:
            filehandle.seek(info['offset'])
            return filehandle.read(info['size'])

        with open(self.filepath, 'rb') as f:
            f.seek(info['offset'])
            return f.read(info['size'])

    def getFileHandle(self):
        return open(self.filepath, 'rb')

    def GetGrpOutput(self, basepath: Path, num_files: int, seed: int, full: bool):
        p = Path(basepath, self.game.type + ' Randomizer.grp')
        extraname = str(seed)
        scriptname = None
        defName = None
        flags = 0
        if self.gameSettings:
            scriptname = self.gameSettings.mainScript
            defName = self.gameSettings.defName
            flags = self.gameSettings.flags
        depend = 0 if full else self.game.crc
        return GrpOutput(p, self.game.type, num_files, extraname, scriptname, defName, flags, depend)


# idk what to call these, but Ion Fury uses one
class GrpZipFile(GrpBase):
    def GetFilesInfo(self) -> None:
        with ZipFile(self.filepath, 'r') as zip:
            for f in zip.infolist():
                self.files[f.filename] = { 'size': f.file_size }

    def _getfile(self, name, filehandle) -> bytes:
        if name not in self.files:
            raise Exception('file not found in GRP/ZIP', name, len(self.files))

        if filehandle:
            with filehandle.open(name) as f:
                return f.read()

        with ZipFile(self.filepath, 'r') as zip:
            with zip.open(name) as file:
                return file.read()

    def getFileHandle(self):
        return ZipFile(self.filepath, 'r')

    def GetGrpOutput(self, basepath: Path, num_files: int, seed: int, full: bool):
        p = Path(basepath, self.game.type + ' Randomizer.grp')
        extraname = str(seed)
        scriptname = None
        defName = None
        flags = 0
        if self.gameSettings:
            scriptname = self.gameSettings.mainScript
            defName = self.gameSettings.defName
            flags = self.gameSettings.flags
        depend = 0 if full else self.game.crc
        return GrpZipOutput(p, self.game.type, num_files, extraname, scriptname, defName, flags, depend)


# used by Blood https://github.com/Die4Ever/build-engine-randomizer/issues/21
class RffFile(GrpBase):
    def GetFilesInfo(self) -> None:
        headerPack = FancyPacker('<', OrderedDict(sign='4s', version='h', pad1='h', offset='I', filenum='I'))
        directoryPack = FancyPacker('<', OrderedDict(unused1='16s', offset='I', size='I', unused2='8s', flags='B', type='3s', name='8s', id='i'))
        itemSize = 48

        with open(self.filepath, 'rb') as file:
            data = file.read(16)
            header = headerPack.unpack(data)
            trace(header)
            self.offset = header['offset']
            self.fileNum = header['filenum']
            file.seek(self.offset, os.SEEK_SET)
            data = bytearray(file.read(itemSize * self.fileNum))

        self.version = header['version']
        self.versionClass = header['version'] & 0xff00
        if self.versionClass == 0x200:
            self.crypt = 0
        elif self.versionClass == 0x300:
            self.crypt = 1
        else:
            raise NotImplementedError(self.filepath + ' ' + repr(header))

        if self.crypt:
            data = RffCrypt(data, self.offset + (self.version & 0xff) * self.offset)

        for i in range(self.fileNum):
            d = directoryPack.unpack(data[i*itemSize:(i+1)*itemSize])
            d['type'] = d['type'].decode()
            name = d['name'].decode().replace('\x00', '')
            filename = name + '.' + d['type']
            d['name'] = filename
            del d['unused1']
            del d['unused2']
            self.files[filename] = d


    def _getfile(self, name, filehandle) -> bytes:
        info = self.files.get(name)
        if not info:
            raise Exception('file not found in RFF', name, len(self.files))

        if filehandle:
            filehandle.seek(info['offset'], os.SEEK_SET)
            data = filehandle.read(info['size'])
        else:
            with open(self.filepath, 'rb') as f:
                f.seek(info['offset'], os.SEEK_SET)
                data = f.read(info['size'])

        DICT_CRYPT = 16
        if info['flags'] & DICT_CRYPT:
            data = bytearray(data)
            decryptSize = min(info['size'], 0x100)
            data[:decryptSize] = RffCrypt(data[:decryptSize], 0)
        return data


    def getFileHandle(self):
        return open(self.filepath, 'rb')

    def GetGrpOutput(self, basepath: Path, num_files: int, seed: int, full: bool):
        p = Path(basepath, self.game.type + ' Randomizer.rff')
        extraname = str(seed)
        scriptname = None
        defName = None
        flags = 0
        if self.gameSettings:
            scriptname = self.gameSettings.mainScript
            defName = self.gameSettings.defName
            flags = self.gameSettings.flags
        depend = 0 if full else self.game.crc
        return RffOutput(p, self.game.type, num_files, extraname, scriptname, defName, flags, depend)


class GrpOutput(GrpOutputBase):
    def open(self):
        filepath = self.outpath
        filepath.parent.mkdir(parents=True, exist_ok=True)
        assert not filepath.exists()
        self.outfile = open(filepath, 'w+b')
        self.outfile.write(b'KenSilverman')
        self.outfile.write(struct.pack('<I', self.num_files))
        for i in range(self.num_files):
            self.outfile.write(struct.pack('<12sI', "".encode('ascii'), 0))
        return self

    def write(self, name: str, data: bytes):
        self.num_saved_files += 1
        # seek to write header
        # KenSilverman is 12 bytes and number of files is 4 bytes for a 16 byte block, filename and filesize are the same
        headerpos = self.outfile.seek(16 * self.num_saved_files)
        self.outfile.write(struct.pack('<12sI', name.encode('ascii'), len(data)))

        # seek to the end to write data
        pos = self.outfile.seek(0, 2)
        self.outfile.write(data)
        self.files[name] = dict(headerpos=headerpos, pos=pos, len=len(data))

    def close(self):
        # get size, calculate crc, and close the grp file
        crc = None
        end = self.outfile.seek(0, 2)
        self.outfile.seek(0)
        self.outfile.flush()
        with mmap(self.outfile.fileno(), 0, access=ACCESS_READ) as file:
            crc = binascii.crc32(file)
        self.outfile.close()

        self.write_info(end, crc)


class RffOutput(GrpOutput):
    def open(self):
        raise NotImplementedError("RffOutput")


class GrpZipOutput(GrpOutputBase):
    def open(self):
        filepath = self.outpath
        filepath.parent.mkdir(parents=True, exist_ok=True)
        assert not filepath.exists()
        self.outfile = ZipFile(filepath, mode='x')

    def write(self, name: str, data: bytes):
        self.outfile.writestr(name, data)

    def close(self):
        # get size, calculate crc, and close the zip file
        self.outfile.close()
        filepath = self.outpath
        size = os.path.getsize(filepath)
        crc = None
        with open(filepath) as file, mmap(file.fileno(), 0, access=ACCESS_READ) as file:
            crc:int = binascii.crc32(file)

        self.write_info(size, crc)


def RffCrypt(data:bytearray, key:int) -> bytearray:
    for i in range(len(data)):
        data[i] = data[i] ^ ((key>>1) & 0xff)
        key += 1
    return data
