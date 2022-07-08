from BuildLibs.grp import *

filepath = 'C:/Program Files (x86)/Steam/steamapps/common/Ion Fury/fury.grp'
seed = random.randint(1, 999999)

with GrpFile(filepath) as g:
    map = g.getmap('maps/z1a1.map')
    map.Randomize(seed)
