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
    return 'v0.451 Alpha'

def fancy_unpack(endianness: str, mappings: tuple, data: bytearray) -> Dict:
    format = endianness
    layout = []
    for k in range(len(mappings) // 2):
        format += mappings[k*2+1]
        layout.append(len(mappings[k*2+1]))

    t = unpack(format, data)
    dict = {}
    i = 0
    for k in range(len(mappings)>>1):
        a = []
        for f in range(len(mappings[k*2+1])):
            a.append(t[i])
            i+=1
        if len(a)==1:
            dict[mappings[k*2]] = a[0]
        else:
            dict[mappings[k*2]] = a

    return dict

def fancy_pack(endianness: str, mappings: tuple, dict: Dict) -> bytearray:
    format = endianness
    values = []
    for k in range(len(mappings) // 2):
        format += mappings[k*2+1]
        v = dict[mappings[k*2]]
        if type(v) == list:
            values += v
        else:
            values.append(v)
    return pack(format, *values)

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
