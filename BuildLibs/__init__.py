import sys
from typing import Dict

if sys.version_info[0] < 3:
    raise ImportError('Python < 3 is unsupported.')
if sys.version_info[0] == 3 and sys.version_info[1] < 6:
    raise ImportError('Python < 3.6 is unsupported.')

from struct import unpack, pack
import binascii
from collections import namedtuple
import random
import pathlib

def GetVersion() -> str:
    return 'v0.452 Alpha'

class FancyPacker:
    def __init__(self, endianness: str, mappings: tuple):
        format = endianness
        lens = []
        keys = []
        for k in range(len(mappings) // 2):
            format += mappings[k*2+1]
            lens.append(len(mappings[k*2+1]))
            keys.append(mappings[k*2])

        self.format = format
        #self.mappings = mappings
        self.keys = keys
        self.lens = lens

    def unpack(self, data: bytearray) -> dict:
        t = unpack(self.format, data)
        dict = {}
        i = 0
        for k in range(len(self.keys)):
            if self.lens[k] == 1:
                dict[self.keys[k]] = t[i]
                i+=1
                continue
            a = []
            for f in range(self.lens[k]):
                a.append(t[i])
                i+=1
            dict[self.keys[k]] = a

        return dict

    def pack(self, dict: dict) -> bytearray:
        values = []
        for k in range(len(self.keys)):
            v = dict[self.keys[k]]
            if self.lens[k] > 1:
                values += v
            else:
                values.append(v)
        return pack(self.format, *values)


def crc32(*args):
    s = ' '.join(map(str, args))
    return binascii.crc32(s.encode('utf8'))

def swapdictkey(a, b, key):
    a[key], b[key] = b[key], a[key]

def swapobjkey(a, b, key):
    a.__dict__[key], b.__dict__[key] = b.__dict__[key], a.__dict__[key]

# 1-level deep copy, usually enough
def copyobj(obj):
    d = obj.__dict__.copy()
    for k in d.keys():
        if type(d[k]) not in [int, str, type(None)]:
            d[k] = d[k].copy()
    obj = type(obj)()
    obj.__dict__ = d
    return obj

verbose = 1

def _warning(*args, **kargs):
    print('WARNING:', *args, **kargs)

def _debug(*args, **kargs):
    print('DEBUG:', *args, **kargs)

def _trace(*args, **kargs):
    print('TRACE:', *args, **kargs)

warning = _warning
debug = _debug
trace = _trace
info = print

def setVerbose(v: int):
    global debug, trace
    verbose = v
    if verbose:
        debug = _debug
    else:
        debug = lambda *a, **b: None # do-nothing function

    if verbose >= 2:
        trace = _trace
    else:
        trace = lambda *a, **b: None # do-nothing function

setVerbose(verbose)
