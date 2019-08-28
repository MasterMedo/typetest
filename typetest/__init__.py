"""TypeTest: typing test in the terminal.

It provides the ability to test your typing speed directly in the
terminal and save results for later analysis.
"""

from os import path

__license__ = ''
__version__ = '0.1.0'
__release__ = False
__author__  = 'Mislav Vuletić'
__email__   = 'mislav.vuletic@gmail.com'

VERSION = f'typetest {__version__}'
ROOTDIR = path.dirname(__file__)
USER_HOME   = path.expanduser('~')

# config files
CONFIG = path.join(USER_HOME, '.typetest.yaml')
OUTPUT = path.join(USER_HOME, '.typetest.csv')

# default args
COLOR_BLACK = 0
COLOR_WHITE = 7
COLOR_GREEN = 46
COLOR_RED   = 196
DELIMITERS = '\n '
TESTDIR = path.join(ROOTDIR, 'tests/english')

args = None
test = None
