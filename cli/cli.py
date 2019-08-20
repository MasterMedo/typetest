"""
Usage:
    cli.py  [-abehpsw] [-v | -q] [-d=<duration>] [-l=<layout>]
            [-r=<directory> | -f=<file>]
            [-o=<file>] [--output-format=<format>]
            [--bg=<color> --fg=<color> --cc=<color> --wc=<color>]
    cli.py  (--help | --version)


Options:
    -a --all-correct-chars      Consider correct characters from both
                                correct and wrong words.
    -b --beep                   Alert the user when he makes a mistake.
    --bg=<color>                Terminal background color. [default: 0]
    --cc=<color>                Correct color. [default: 46]
    --cpm                       Show characters per minute.
    -d --duration=<duration>    Limit duration of the typing test to
                                <duration>.
    --dph                       Show depressions per hour.
    -e --endless                Repeat test endlessly, if -r is
                                specified randomizes every repetition.
    -f --file=<file>            File to read the test from.
    --fg=<color>                Foreground main color. [default: 7]
    -h --hide                   Hide timer and dynamic wpm counter.
    --help                      Show this screen.
    -l --layout=<layout>        Keyboard layout for calculating
                                keystrokes. [default: qwerty]
    -n --normalize              Use keystrokes over characters.
    -o --output=<file>          File to store output result in.
    --output-format=<format>    File format to store output as; json,
                                csv. [default: json]
    -p --prevent-wrong          Accept up to 4 correct chars in a row,
                                then block incorrect input. If -w is
                                set accept only correct words.
    -q --quiet                  Print no results.
    -r --root-dir=<directory>   Root directory to randomize the test
                                from. [default: tests/english/]
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

from docopt     import docopt
from schema     import Schema, And, Or, Use, SchemaError
from os         import path, walk
from re         import split
from cli.keytype import TypingTest
from random     import choice, shuffle
from textwrap   import wrap
from time       import time

import curses

layouts  = ['colemak',  'dvorak', 'qwerty']
formats  = ['csv', 'json']


def start():
    args = docopt(__doc__, version='typetest 0.1')
    schema = Schema({
        '--all-correct-chars':      bool,#
        '--beep':                   bool,#
        '--endless':                bool,#
        '--hide':                   bool,
        '--help':                   bool,
        '--prevent-wrong':          bool,#
        '--quiet':                  bool,
        '--shuffle-words':          bool,
        '--verbose':                bool,
        '--version':                bool,
        '--word-by-word':           bool,#

        '--bg': And(Use(int), lambda n: 0 <= n < 256,
                error='<color> should be an integer between 0 and 256.'),
        '--fg': And(Use(int), lambda n: 0 <= n < 256,
                error='<color> should be an integer between 0 and 256.'),
        '--cc': And(Use(int), lambda n: 0 <= n < 256,
                error='<color> should be an integer between 0 and 256.'),
        '--wc': And(Use(int), lambda n: 0 <= n < 256,
                error='<color> should be an integer between 0 and 256.'),

        '--duration':   Or(None, And(Use(int), lambda n: 0 < n,#
                        error='<duration> should be an int larger than 0.')),

        '--file':       Or(None, And(path.isfile,
                        error='<file> should be an existing file.')),
        '--output':     Or(None, And(path.exists,#
                        error='<file> should refer to an existing path.')),
        '--root-dir':   And(path.isdir,
                        error='<directory> should be an existing directory.'),

        '--output-format':  And(lambda f: f in formats,#
                            error=f'<format> should be in {formats}.'),
        '--layout':         And(lambda l: l in layouts,#
                            error=f'<layout> must be in {layouts}.'),
        })
    try:
        args = schema.validate(args)
    except SchemaError as e:
        exit(e)

    if args['--file']:
        with open(args['--file'], 'r') as f:
            test_raw = f.read()
    else:
        try:
            root, _, files = next(walk(args['--root-dir']))
            test_path = choice(files)
            with open(root+test_path, 'r') as f:
                test_raw = f.read()
        except IndexError as e:
            exit(f"No files in {args['--root-dir']}.")

    test_words = list(filter(None, split('[ \n]+', test_raw)))
    if args['--shuffle-words']:
        shuffle(test_words)

    test_text = ' '.join(test_words)
    test = TypingTest(test_text)

    stdscr = curses.initscr()
    curses.start_color()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    curses.curs_set(0)
                                                        # defaults
    curses.init_pair(1, args['--fg'], args['--bg'])     # white on black
    curses.init_pair(2, args['--bg'], args['--fg'])     # black on white
    curses.init_pair(3, args['--wc'], args['--bg'])     # red   on black
    curses.init_pair(4, args['--cc'], args['--bg'])     # green on black
    curses.init_pair(5, args['--bg'], args['--wc'])     # black on red
    curses.init_pair(6, args['--bg'], args['--cc'])     # black on green

    basic_word_color           = curses.color_pair(1)
    current_word_color         = curses.color_pair(2)
    wrong_word_color           = curses.color_pair(3)
    correct_word_color         = curses.color_pair(4)
    current_wrong_word_color   = curses.color_pair(5)
    current_correct_word_color = curses.color_pair(6)

    maxy, maxx = stdscr.getmaxyx()

    wordscr_height = 0 if args['--hide'] or maxx < 3 else 1

    add_color = lambda word: [word, basic_word_color]
    test_rows = [list(map(add_color, row)) for row in map(str.split, wrap(test_text, maxx-1))]

    if args['--word-by-word']:
        testscr_rows = min(maxy-wrdscr_height, 3)
    else:
        testscr_rows = min(maxy-wordscr_height, len(test_rows))

    testscr = curses.newwin(testscr_rows,   maxx, 0, 0)
    prompt  = curses.newwin(1,              5, testscr_rows, 0)
    prompt.addstr('>>> ')
    prompt.refresh()
    wordscr = curses.newwin(1,              maxx, testscr_rows, 4)

    word = ''
    test_row_i = 0
    test_word_i = 0
    start_time = time()

    try:
        while True:
            testscr.erase()

            test_word = test_rows[test_row_i][test_word_i][0]

            if word == test_word[:len(word)] and len(word) == len(test_word):
                test_rows[test_row_i][test_word_i][1] = current_correct_word_color

            elif word == test_word[:len(word)]:
                test_rows[test_row_i][test_word_i][1] = current_word_color

            else:
                test_rows[test_row_i][test_word_i][1] = current_wrong_word_color

            start_row_i = min(test_row_i, len(test_rows) - testscr_rows)
            for i, row in enumerate(test_rows[start_row_i:start_row_i+testscr_rows]):
                for j, (w, color) in enumerate(row):
                    testscr.addstr(w, color)
                    if j+1 != len(row):
                        testscr.addstr(' ')
                if i != testscr_rows-1:
                    testscr.addstr('\n')
            testscr.refresh()

            c = wordscr.getch()

            if c == 127:
                test.addch(chr(c))
                word = word[:-1]
                wordscr.addstr("\b \b")

            elif chr(c) in ' \n':
                wordscr.erase()

                if not word:
                    continue

                test.addword(word)

                if len(test.test_words) == len(test.text_words):
                    break

                test_word = test_rows[test_row_i][test_word_i][0]

                if test_word == word:
                    test_rows[test_row_i][test_word_i][1] = correct_word_color

                else:
                    test_rows[test_row_i][test_word_i][1] = wrong_word_color

                word = ''

                test_word_i += 1
                if test_word_i == len(test_rows[test_row_i]):
                    test_word_i = 0
                    test_row_i += 1

            else:
                word += chr(c)
                wordscr.addch(c)
    except KeyboardInterrupt as e:
        pass
    except Exception as e:
        curses.curs_set(1)
        exit(e)

    curses.curs_set(1)
    curses.nocbreak()
    stdscr.keypad(0);
    curses.echo()
    curses.endwin()

    end_time = time()
    duration = end_time - start_time

    try:
        test.submit(duration)
    except TypeError as e:
        exit()

    if args['--verbose']:
        print(f'accuracy:       {test.accuracy:.{0}f}%')
        print(f'duration:       {test.duration:.{2}f} sec\n')
        print(f'correct words:  {len(test.correct_words)}')
        print(f'correct chars:  {len(test.correct_chars)}\n')
        print(f'true speed:     {test.true_speed_wpm:.{0}f} wpm')
        print(f'normalized:     {test.speed_wpm:.{0}f} wpm\n')
        print(f'true speed:     {test.true_speed_cpm:.{0}f} cpm')
        print(f'normalized:     {test.speed_cpm:.{0}f} cpm\n')
        print(f'true speed:     {test.true_speed_dph:.{0}f} dph')
        print(f'normalized:     {test.speed_dph:.{0}f} dph')

    elif not args['--quiet']:
        print(f'accuracy:       {test.accuracy:.{0}f}%')
        print(f'duration:       {test.duration:.{2}f} sec')
        print(f'true speed:     {test.true_speed_wpm:.{0}f} wpm')
