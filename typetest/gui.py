from textwrap       import wrap
from curses         import *

from typetest.core  import output_results
from typetest.util  import TypeTestDone

import typetest

COLOR_BASIC           = None
COLOR_BASIC_REVERSE   = None
COLOR_WRONG           = None
COLOR_WRONG_REVERSE   = None
COLOR_CORRECT         = None
COLOR_CORRECT_REVERSE = None

stdscr   = None
testscr  = None
wordscr  = None
timescr  = None
speedscr = None

test_height = 0
test_row_i  = 0
test_word_i = 0

def init():
    global stdscr, testscr, wordscr, timescr, speedscr
    global testscr_height, testscr_rows
    global COLOR_BASIC, COLOR_BASIC_REVERSE, COLOR_WRONG, COLOR_WRONG_REVERSE, COLOR_CORRECT, COLOR_CORRECT_REVERSE

    stdscr = initscr()
    start_color()
    noecho()
    cbreak()
    stdscr.keypad(1)
    curs_set(0)

    init_pair(1, typetest.args['--fg'], typetest.args['--bg'])  # white on black
    init_pair(2, typetest.args['--bg'], typetest.args['--fg'])  # black on white
    init_pair(3, typetest.args['--wc'], typetest.args['--bg'])  # red   on black
    init_pair(4, typetest.args['--bg'], typetest.args['--wc'])  # black on red
    init_pair(5, typetest.args['--cc'], typetest.args['--bg'])  # green on black
    init_pair(6, typetest.args['--bg'], typetest.args['--cc'])  # black on green

    COLOR_BASIC           = color_pair(1)
    COLOR_BASIC_REVERSE   = color_pair(2)
    COLOR_WRONG           = color_pair(3)
    COLOR_WRONG_REVERSE   = color_pair(4)
    COLOR_CORRECT         = color_pair(5)
    COLOR_CORRECT_REVERSE = color_pair(6)
                                                                # defaults
    maxy, maxx = stdscr.getmaxyx()

    testscr_max_height = 3 if typetest.args['--word-by-word'] else maxy

    stats_height = int(not typetest.args['--hide'])
    testscr_height = min(maxy - stats_height, testscr_max_height)

    prompt_size   = 4+1 # ">>> "
    speedscr_size = 7+1 # "213 wpm"
    timescr_size  = 8+1 # "00:00:00"
    wordscr_size  = maxx - speedscr_size - timescr_size - prompt_size

    testscr  = newwin(testscr_height,          maxx,              0,           0)
    prompt   = newwin(  stats_height,   prompt_size, testscr_height,           0)
    wordscr  = newwin(  stats_height,  wordscr_size, testscr_height, prompt_size)
    timescr  = newwin(  stats_height,  timescr_size, testscr_height,
            maxx - speedscr_size - timescr_size)
    speedscr = newwin(  stats_height, speedscr_size, testscr_height,
            maxx - speedscr_size)

    if typetest.args['--word-by-word']:
        prompt.addstr('>>> ')
        prompt.refresh()

    test_text = ' '.join(typetest.test.test_words)
    add_color = lambda word: [word, COLOR_BASIC]
    testscr_rows = [list(map(add_color, row)) for row in map(str.split, wrap(test_text, maxx-1, break_long_words=False, break_on_hyphens=False))]
    testscr_rows[0][0][1] = COLOR_BASIC_REVERSE

def play():
    while True:
        draw_testscr()
        c = testscr.getch()

        c = chr(c) if c != 127 else '\b'

        typetest.test.addch(c)

        if not typetest.args['--hide']:
            if typetest.args['--word-by-word']:
                draw_wordscr()
            draw_timescr()
            draw_speedscr()

def draw_testscr():
    global testscr, testscr_rows, testscr_height
    global test_row_i, test_word_i

    testscr.erase()

    start_row_i = min(test_row_i, len(testscr_rows) - testscr_height)
    for row_i, row in enumerate(testscr_rows[start_row_i:start_row_i + testscr_height]):
        for word_i, (word, color) in enumerate(row):
            testscr.addstr(word, color)
            if word_i + 1 != len(row):
                testscr.addstr(' ')
        if row_i != testscr_height - 1:
            testscr.addstr('\n')

def draw_wordscr():
    global testscr_rows, test_row_i, test_word_i

    wordscr.erase()

    if typetest.test.triggered_new_word:
        test_word = testscr_rows[test_row_i][test_word_i][0]

        if typetest.test.is_last_word_correct():
            testscr_rows[test_row_i][test_word_i][1] = COLOR_CORRECT

        else:
            testscr_rows[test_row_i][test_word_i][1] = COLOR_WRONG

        test_word_i += 1

        if test_word_i == len(testscr_rows[test_row_i]):
            test_word_i = 0
            test_row_i += 1

        testscr_rows[test_row_i][test_word_i][1] = COLOR_BASIC_REVERSE

    elif not typetest.test.are_current_words_equal():
            testscr_rows[test_row_i][test_word_i][1] = COLOR_WRONG_REVERSE

    elif typetest.test.is_current_word_correct():
            testscr_rows[test_row_i][test_word_i][1] = COLOR_CORRECT_REVERSE

    elif typetest.test.are_current_words_equal():
            testscr_rows[test_row_i][test_word_i][1] = COLOR_BASIC_REVERSE

    wordscr.addstr(typetest.test.get_current_text_word())
    wordscr.refresh()

def draw_timescr():
    global timescr
    timescr.erase()
    m, s = divmod(int(typetest.test.duration), 60)
    h, m  = divmod(m, 60)
    if h > 23:
        h = 0
    timescr.addstr(f'{h:02d}:{m:02d}:{s:02d}')
    timescr.refresh()

def draw_speedscr():
    global speedscr
    speedscr.erase()
    speed = min(int(typetest.test.tmp_speed_wpm), 999)
    speedscr.addstr(f'{speed} wpm')
    speedscr.refresh()

def shutdown():
    curs_set(1)
    nocbreak()
    stdscr.keypad(0);
    echo()
    endwin()
