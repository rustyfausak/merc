import numpy
from pprint import pprint
from merc.box import Box

b = Box(10, 5, 2)
#b.translate([1,1,1])
b.rotate([0.3,0,0])
p = b.pointClosestToPoint([10, 10, 10])
pprint(vars(b))
pprint(p)
