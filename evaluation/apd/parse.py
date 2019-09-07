"""
Parse the squad list and print out player names as a list that can be copy-pasted into a Python script.

Requires one argument to function - the name of the source in the 'original' folder.
"""

import os
import re
import sys
import urllib.parse

path = os.path.dirname(__file__)
path = os.path.join(path, "../../libraries")
if path not in sys.path:
	sys.path.insert(1, path)

from logger import logger

if len(sys.argv) > 1:
	"""
	Load the text.
	"""
	filename = sys.argv[1]
	with open(os.path.join(os.path.dirname(__file__), "original", filename), "r") as f:
		text = ''.join(f.readlines())

	"""
	Look for the pattern in the text.
	"""
	page_pattern = re.compile("<span class=\"fn\"><a href=\"\/wiki\/(.+?)\"")
	pages = page_pattern.findall(text)
	pages = [ urllib.parse.unquote(page) for page in pages ]
	pages = [ page.replace("_", " ") for page in pages ]
	print(pages)
else:
	logger.error("File name not specified")
