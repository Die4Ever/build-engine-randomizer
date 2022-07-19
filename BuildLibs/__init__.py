import sys

if sys.version_info[0] < 3:
    raise ImportError('Python < 3 is unsupported.')
if sys.version_info[0] == 3 and sys.version_info[1] < 6:
    raise ImportError('Python < 3.6 is unsupported.')

from typing import OrderedDict, Union
from struct import unpack, pack
import binascii
from collections import namedtuple
import random
import pathlib
from datetime import datetime
import re

def GetVersion() -> str:
    return 'v0.5.3 Alpha'

packLengthRegex = re.compile('(\d+)(\w+)')
class FancyPacker:
    def __init__(self, endianness: str, mappings: OrderedDict):
        self.format = endianness
        self.keys = {}
        for k, v in mappings.items():
            self.format += v
            m = packLengthRegex.match(v)
            if m:
                self.keys[k] = 1
            else:
                self.keys[k] = len(v)


    def unpack(self, data: bytearray) -> dict:
        t = unpack(self.format, data)
        dict = {}
        i = 0
        for k, L in self.keys.items():
            if L == 1:
                dict[k] = t[i]
                i+=1
                continue
            dict[k] = list(t[i:i+L])
            i+=L

        return dict

    def pack(self, dict: dict) -> bytes:
        values = [None] * (len(self.format)-1)
        i = 0
        for k, L in self.keys.items():
            v = dict[k]
            if L > 1:
                values[i:i+L] = v
            else:
                values[i] = v
            i+=L
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
        if type(d[k]) not in [int, str, bool, type(None)]:
            d[k] = d[k].copy()
    obj = type(obj)()
    obj.__dict__ = d
    return obj

verbose = 1

def error(*args, **kargs):
    print('ERROR:', *args, **kargs)
    with open("errorlog.txt", "a") as file:
        print(datetime.now().strftime('%c') + ': ERROR:', *args, **kargs, file=file)

def warning(*args, **kargs):
    print('WARNING:', *args, **kargs)
    with open("errorlog.txt", "a") as file:
        print(datetime.now().strftime('%c') + ': WARNING:', *args, **kargs, file=file)

def info(*args, **kargs):
    if verbose > -1:
        print('DEBUG:', *args, **kargs)

def debug(*args, **kargs):
    if verbose > 0:
        print('DEBUG:', *args, **kargs)

def trace(*args, **kargs):
    if verbose > 1:
        print('TRACE:', *args, **kargs)


def setVerbose(v: int):
    global verbose
    verbose = v
