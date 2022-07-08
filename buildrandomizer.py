from grp.grp import *

filepath = 'C:/Program Files (x86)/Steam/steamapps/common/Ion Fury/fury.grp'

with GrpFile(filepath) as g:
    map = g.getmap('maps/z1a1.map')
