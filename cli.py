"""
Usage:
    cli.py  [-abcehpsw] [-v | -q] [-d=<duration>] [-l=<layout>]
            [-r=<directory> | -f=<file>] [-o=<file>]
            [--output-format=<format>]
            [--bg=<color> --fg=<color> --cc=<color> --wc=<color>]
    cli.py  (--help | --version)


Options:
    -a --all-correct-chars      Consider correct characters from both
                                correct and wrong words.
    -b --beep                   Alert the user when he makes a mistake.
    --bg=<color>                Terminal background color. [default: 0]
    -c --chars-over-keystrokes  Use characters instead of keystrokes
                                for calculations.
    --cc=<color>                Correct color. [default: 46]
    -d --duration=<duration>    Limit duration of the typing test to
                                <duration>.
    -e --endless                Repeat test endlessly, if -r is
                                specified randomizes every repetition.
    -f --file=<file>            File to read the test from.
    --fg=<color>                Foreground main color. [default: 7]
    -h --hide                   Hide timer and dynamic wpm counter.
    --help                      Show this screen.
    -l --layout=<layout>        Keyboard layout for calculating
                                keystrokes. [default: en-us]
    -o --output=<file>          File to store output result in.
    --output-format=<format>    File format to store output as; json,
                                csv. [default: json]
    -p --prevent-wrong          Accept up to 4 correct chars in a row,
                                then block incorrect input. If -w is
                                set accept only correct words.
    -q --quiet                  Print no results.
    -r --root=<directory>       Root directory to randomize the test
                                from. [default: tests/english]
    -s --shuffle-words          Shuffle words.
    -v --verbose                Show a more extensive result.
    --version                   Show version.
    -w --word-by-word           Evaluate word by word instead of
                                character by character.
    --wc=<color>                Wrong color. [default: 196]

Shortcuts:
    ^C / Ctrl+c                 End the test and get results now.
    ^R / Ctrl+r                 Restart the same test.

"""

from docopt import docopt
from schema import Schema, And, Or, Use, SchemaError
from os     import path

layouts = ['en-us']
formats = ['csv', 'json']
if __name__ == '__main__':
    args = docopt(__doc__, version='typetest 0.1')
    schema = Schema({
        '--all-correct-chars': bool,
        '--beep': bool,
        '--bg': And(Use(int), lambda n: 0 <= n < 256,
                error='<color> should be an integer between 0 and 256'),
        '--chars-over-keystrokes': bool,
        '--cc': And(Use(int), lambda n: 0 <= n < 256,
                error='<color> should be an integer between 0 and 256'),
        '--duration': Or(None, Use(int), error='<duration> should be int'),
        '--endless': bool,
        '--file': Or(None, Use(open, error='<file> should be readable')),
        '--fg': And(Use(int), lambda n: 0 <= n < 256,
                error='<color> should be an integer between 0 and 256'),
        '--hide': bool,
        '--help': bool,
        '--layout': And(lambda l: l in layouts,
                    error=f'<layout> must be in {layouts}'),
        '--output': Or(None, Use(open, error='<file> should be readable')),
        '--output-format': Or(None, lambda f: f in formats,
                            error=f'<format> should be in {formats}'),
        '--prevent-wrong': bool,
        '--quiet': bool,
        '--root': And(path.exists, error='<directory> should exist'),
        '--shuffle-words': bool,
        '--verbose': bool,
        '--version': bool,
        '--word-by-word': bool,
        '--wc': And(Use(int), lambda n: 0 <= n < 256,
                error='<color> should be an integer between 0 and 256')})
    try:
        args = schema.validate(args)
    except SchemaError as e:
        exit(e)
