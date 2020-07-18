"""
Usage:
    cli.py  [-abcehnps] [-r=<directory> | -f=<file>] [-d=<duration>]
            [--bg=<color> --fg=<color> --cc=<color> --wc=<color>]
            [-t=<tag>...] [-q | -v | -vv | -vvv]
            [--cpm --dph]
            [-o=<file>] [--delimiters=<string>]
    cli.py  (--help | --version)


Options:
    -a --all-correct-chars      Consider correct characters from both
                                correct and wrong words. #
    -b --beep                   Alert the user when he makes a mistake. #
    --bg=<color>                Terminal background color.
    -c --char-by-char           Evaluate char by char instead of
                                word by word. #
    --cc=<color>                Correct color.
    --cpm                       Show characters per minute. #
    -d --duration=<duration>    Limit duration of the typing test to
                                <duration>.
    --delimiters=<string>       Delimiters to divide text file by.
                                Decoded with utf-8.
    --dph                       Show depressions per hour. #
    -e --endless                Repeat test endlessly, if -r is
                                specified randomizes every repetition. #
    -f --file=<file>            File to read the test from.
                                Overrides '--root-dir' option.
    --fg=<color>                Foreground basic text color.
    -h --hide                   Hide timer and dynamic wpm counter.
    --help                      Show this screen.
    -n --normalize              Use keystrokes over characters. #
    -o --output=<file>          File to store output result in.
    -p --prevent-wrong          Accept only correct words. #
    -q --quiet                  Print no result.
    -r --root-dir=<directory>   Root directory to randomize the test
                                from.
    -s --shuffle-words          Shuffle words in the test.
    -t --tag=<tag>...           List of tags.
    -v --verbose                Show a more extensive result.
    --version                   Show version.
    --wc=<color>                Wrong color.

Shortcuts:
    C-c / ^C / Ctrl+c           End the test and get results now.
    C-h / ^H / Ctrl+h           Backspace.
    C-r / ^R / Ctrl+r           Restart the same test. #
    C-w / ^W / Ctrl+w           Delete a word. #
"""

from docopt import docopt
from schema import Schema, And, Or, Use, SchemaError
from os import path, walk
from sys import argv
from random import choice
from typetest import VERSION, TESTDIR, CONFIG, DELIMITERS, DURATION
from typetest import COLOR_BLACK, COLOR_WHITE, COLOR_GREEN, COLOR_RED

import yaml
import typetest


def load_cli_args():
    typetest.args = docopt(__doc__, argv=argv[1:], version=VERSION)


def add_config_args():
    with open(CONFIG) as f:
        config_args = yaml.safe_load(f.read())
    if not config_args:
        config_args = {}

    typetest.args = merge_args(typetest.args, config_args)


def merge_args(x, y):
    for key in set(x) | set(y):
        if y.get(key) and not x[key] or x[key] is None and key in y:
            x[key] = y[key]
    return x


def error(key):
    return f"Error in key, value ('{key}', {typetest.args[key]}):\n"


def color_error(key):
    return error(key) + '<color> should be an integer between 0 and 256'


def file_error(key):
    return error(key) + '<file> should be an existing file.'


def path_error(key):
    return error(key) + '<path> should refer to a valid path.'


def directory_error(key):
    return error(key) + '<directory> should be an existing directory.'


def delimiter_error(key):
    return error(key) + '<delimiters> should be a string of delimiters.'


def no_file_error(key):
    return error(key) + '<directory> should contain a file.'


def duration_error(key):
    return error(key) + '<duration> should be an integer larger than 0.'


def gtzero(x):
    return x > 0


def iscolor(x):
    return 0 <= x < 256


def to_unicode(x):
    return bytes(x, 'utf-8').decode('unicode_escape')


def validate_args():
    schema = Schema({
        '--all-correct-chars': bool,
        '--beep': bool,
        '--char-by-char': bool,
        '--cpm': bool,
        '--dph': bool,
        '--endless': bool,
        '--hide': bool,
        '--help': bool,
        '--normalize': bool,
        '--prevent-wrong': bool,
        '--quiet': bool,
        '--shuffle-words': bool,
        '--version': bool,
        '--verbose': int,
        '--tag': list,
        '--bg': Or(None, And(Use(int), iscolor, error=color_error('--bg'))),
        '--fg': Or(None, And(Use(int), iscolor, error=color_error('--fg'))),
        '--cc': Or(None, And(Use(int), iscolor, error=color_error('--cc'))),
        '--wc': Or(None, And(Use(int), iscolor, error=color_error('--wc'))),
        '--duration': Or(None, And(Use(int), gtzero, error=duration_error('--duration'))),
        '--delimiters': Or(None, Use(to_unicode), error=delimiter_error('--delimiters')),
        '--file': Or(None, path.isfile, error=file_error('--file')),
        '--output': Or(None, path.exists, error=path_error('--output')),
        '--root-dir': Or(None, path.isdir, error=directory_error('--root-dir'))
    })

    try:
        typetest.args = schema.validate(typetest.args)
    except SchemaError as e:
        exit(e)


def add_default_args():
    try:
        if not typetest.args['--duration']:
            typetest.args['--duration'] = DURATION

        if not typetest.args['--file']:
            if not typetest.args['--root-dir']:
                typetest.args['--root-dir'] = TESTDIR
            root, _, files = next(walk(typetest.args['--root-dir']))
            typetest.args['--file'] = path.join(root, choice(files))

        if not typetest.args['--bg']:
            typetest.args['--bg'] = COLOR_BLACK

        if not typetest.args['--fg']:
            typetest.args['--fg'] = COLOR_WHITE

        if not typetest.args['--cc']:
            typetest.args['--cc'] = COLOR_GREEN

        if not typetest.args['--wc']:
            typetest.args['--wc'] = COLOR_RED

        if not typetest.args['--delimiters']:
            typetest.args['--delimiters'] = DELIMITERS

    except IndexError:
        exit(no_file_error(typetest.args['--root-dir']))
