import sys

if sys.version_info[0] < 3:
    raise ImportError('Python < 3 is unsupported.')
if sys.version_info[0] == 3 and sys.version_info[1] < 6:
    raise ImportError('Python < 3.6 is unsupported.')

import os
from typing import OrderedDict, Union
import struct
import binascii
from collections import namedtuple
import random
import pathlib
from datetime import datetime
import re

def GetVersion() -> str:
    return 'v0.6 Beta'

packLengthRegex = re.compile('^(.*?)(\d+)(\w)(.*?)$')
class FancyPacker:

    def __init__(self, endianness: str, mappings: OrderedDict):
        self.format = endianness
        self.keys = {}
        self.total_len = 0
        for k, v in mappings.items():
            self.format += v
            m = packLengthRegex.match(v)
            if m:
                self.keys[k] = len(m.group(1)) + 1 + len(m.group(4))
            else:
                self.keys[k] = len(v)
            self.total_len += self.keys[k]

    def unpack(self, data: bytes) -> dict:
        t = struct.unpack(self.format, data)
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
        values = [None] * self.total_len
        i = 0
        for k, L in self.keys.items():
            v = dict[k]
            if L > 1:
                values[i:i+L] = v
            else:
                values[i] = v
            i+=L
        return struct.pack(self.format, *values)

    def calcsize(self) -> int:
        return struct.calcsize(self.format)


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

def checkCleanupErrorLog():
    if getattr(checkCleanupErrorLog, "checked", False):
        return
    checkCleanupErrorLog.checked = True
    doCleanup = True

    try:
        if os.path.isfile("errorlog.txt"):
            with open("errorlog.txt") as file:
                doCleanup = False
                firstLine = file.readline()
                if firstLine.strip() != GetVersion():
                    doCleanup = True

        if doCleanup:
            with open("errorlog.txt", 'w') as file:
                print(GetVersion() +'\n', file=file)
        else:
            with open("errorlog.txt", "a") as file:
                print('\n\n', file=file)
    except Exception as e:
        # the checked property means this function won't be called recursively
        error('checkCleanupErrorLog:', e)


def error(*args, **kargs):
    print('ERROR:', *args, **kargs)
    checkCleanupErrorLog()
    with open("errorlog.txt", "a") as file:
        print(datetime.now().strftime('%c') + ': ERROR:', *args, **kargs, file=file)

def warning(*args, **kargs):
    print('WARNING:', *args, **kargs)
    checkCleanupErrorLog()
    with open("errorlog.txt", "a") as file:
        print(datetime.now().strftime('%c') + ': WARNING:', *args, **kargs, file=file)

def info(*args, **kargs):
    if verbose > -1:
        print('INFO:', *args, **kargs)

def debug(*args, **kargs):
    if verbose > 0:
        print('DEBUG:', *args, **kargs)

def trace(*args, **kargs):
    if verbose > 1:
        print('TRACE:', *args, **kargs)


def setVerbose(v: int):
    global verbose
    verbose = v
