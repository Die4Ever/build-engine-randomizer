import sys
from typing import Dict

if sys.version_info[0] < 3:
    raise ImportError('Python < 3 is unsupported.')
if sys.version_info[0] == 3 and sys.version_info[1] < 6:
    raise ImportError('Python < 3.6 is unsupported.')

from struct import unpack, pack
import binascii
from collections import namedtuple

def fancy_unpack(endianness: str, mappings: tuple, data: bytearray) -> Dict:
    format = endianness
    layout = []
    for k in range(len(mappings)>>1):
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
    for k in range(len(mappings)>>1):
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
