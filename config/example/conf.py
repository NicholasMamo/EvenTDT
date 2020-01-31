"""
EvenTDT configuration.
"""

ACCOUNTS = [
	{
		'ACCESS_TOKEN': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
		'ACCESS_TOKEN_SECRET': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
		'CONSUMER_KEY': 'XXXXXXXXXXXXXXXXXXXXXXXXX',
		'CONSUMER_SECRET': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
	}
]
"""
:var ACCOUNTS: The sets of Twitter API credential.
:vartype ACCOUNTS: list of dict
"""

LOG_LEVEL = 1
"""
:var LOG_LEVEL: The logging level.
				The different logging levels are listed in :class:`eventdt.logger.logger.LogLevel`.
:vartype LOG_LEVEL: int
"""
