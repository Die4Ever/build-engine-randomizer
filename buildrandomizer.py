from BuildLibs.grp import *
#import cProfile, pstats

grppath = 'C:/Program Files (x86)/Steam/steamapps/common/Ion Fury/fury.grp'
#grppath = 'C:/Games/Build Engine/Duke Nukem 3D/DUKE3D.GRP'
grppath = 'C:/Program Files (x86)/Steam/steamapps/common/Shadow Warrior Original/gameroot/Sw.grp'
seed = random.randint(1, 999999)
randomize(grppath, seed)

#cProfile.run("randomize(grppath, seed)", sort="cumtime")
