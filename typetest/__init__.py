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

ROOTDIR = path.dirname(__file__)
VERSION = f'typetest {__version__}'

args = None
test = None
