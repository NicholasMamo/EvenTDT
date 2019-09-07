import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../..'))
# print(sys.path)

from libraries.vector import vector_math
from libraries.vector.vector import Vector

v = Vector({"x": 1, "y": 2})
print(vector_math.normalize(v))
print(vector_math.magnitude(v))
