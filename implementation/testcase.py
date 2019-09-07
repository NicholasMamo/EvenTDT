import os
import sys

print(sys.path[0])
sys.path.insert(1, os.path.join(sys.path[0], '../libraries'))
print(sys.path[1])

from vector import vector_math
from vector.vector import Vector
from vector.nlp.document import Document

v = Vector({"x": 1, "y": 2})
print(vector_math.normalize(v))
print(vector_math.magnitude(v))

d = Document("", {"x": 2})
print(d.get_attributes())

from wikinterface.linkcollector import LinkCollector

seed = ["Romania"]
lc = LinkCollector()
print(lc.get_links(seed))
