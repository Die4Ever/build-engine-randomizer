import pathlib
from BuildLibs.grp import *

filepath = 'C:/Program Files (x86)/Steam/steamapps/common/Ion Fury/fury.grp'
seed = random.randint(1, 999999)

with GrpFile(filepath) as g:
    mapname = 'maps/z1a1.map'
    map = g.getmap(mapname)
    map.Randomize(seed)
    gamedir = os.path.dirname(filepath)
    mapout = os.path.join(gamedir, mapname)
    pathlib.Path(os.path.dirname(mapout)).mkdir(parents=True, exist_ok=True)
    with open(mapout, 'wb') as f:
        f.write(map.data)
