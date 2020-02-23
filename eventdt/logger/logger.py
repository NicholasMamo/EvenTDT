"""
A logging interface.
"""

from datetime import datetime

import os
import sys

paths = [
	os.path.join(os.path.dirname(__file__), '..'),
	os.path.join(os.path.dirname(__file__), '..', '..')
]

for path in paths:
	if path not in sys.path:
		sys.path.insert(1, path)

from objects.ordered_enum import OrderedEnum
from config import conf

class LogLevel(OrderedEnum):
	"""
	The logger's logging level.
	It is based on a :class:`objects.ordered_enum.OrderedEnum`.

	Valid logging levels:

		#. `INFO` - Information and higher-level logging only
		#. `WARNING` - Warnings and higher-level logging only
		#. `ERROR` - Errors and higher-level logging only
	"""

	INFO = 1
	WARNING = 2
	ERROR = 3

def log_time():
	"""
	Get the time string.

	:return: The time string.
	:rtype: str
	"""

	return datetime.now().strftime("%H:%M:%S")

def set_logging_level(level):
	"""
	Set the logging level.

	:param level: The logging level.
	:type level: :class:`logger.logger.LogLevel`
	"""

	conf.LOG_LEVEL = level

def info(message):
	"""
	Log an information message.

	:param message: The message to show.
	:type message: str
	"""

	if conf.LOG_LEVEL <= LogLevel.INFO:
		print("%s: INFO: %s" % (log_time(), message.encode("ascii", "ignore").decode("utf-8")))

def warning(message):
	"""
	Log a warning.

	:param message: The message to show.
	:type message: str
	"""

	if conf.LOG_LEVEL <= LogLevel.WARNING:
		print("%s: WARNING: %s" % (log_time(), message.encode("ascii", "ignore").decode("utf-8")))

def error(message):
	"""
	Log an error.

	:param message: The message to show.
	:type message: str
	"""

	if conf.LOG_LEVEL <= LogLevel.ERROR:
		print("%s: ERROR: %s" % (log_time(), message.encode("ascii", "ignore").decode("utf-8")))
