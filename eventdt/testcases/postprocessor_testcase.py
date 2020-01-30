import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../'))

from apd.postprocessors.external.wikipedia_postprocessor import WikipediaPostprocessor

pp = WikipediaPostprocessor()
pp.postprocess(["Striker (association football)", "Inside forward"], [])
