from BuildLibs.grp import *

grppath = 'C:/Program Files (x86)/Steam/steamapps/common/Ion Fury/fury.grp'
mapname = 'maps/z1a1.map'
seed = random.randint(1, 999999)
randomize(grppath, [mapname], seed)

grppath = 'C:/Games/Build Engine/Duke Nukem 3D/DUKE3D.GRP'
mapname = 'E1L1.MAP'
seed = random.randint(1, 999999)
randomize(grppath, [mapname], seed)
