from textwrap import wrap

import curses
import typetest

color_basic = None
color_basic_reverse = None
color_wrong = None
color_wrong_reverse = None
color_correct = None
color_correct_reverse = None

stdscr = None

rows_maxy = 0
test_row_i = 0
test_word_i = 0
test_char_i = 0

prompt = '>>>'
prompt_size = 4  # ">>>"
speed_size = 7  # "213 wpm"
time_size = 8  # "00:00:00"
word_size = 0


def init():
    global word_size
    global stdscr, rows_maxy, rows
    global color_basic, color_basic_reverse, color_wrong, color_wrong_reverse, color_correct, color_correct_reverse

    stdscr = curses.initscr()
    curses.start_color()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    curses.curs_set(0)

    curses.init_pair(1, typetest.args['--fg'], typetest.args['--bg'])  # white on black
    curses.init_pair(2, typetest.args['--bg'], typetest.args['--fg'])  # black on white
    curses.init_pair(3, typetest.args['--wc'], typetest.args['--bg'])  # red   on black
    curses.init_pair(4, typetest.args['--bg'], typetest.args['--wc'])  # black on red
    curses.init_pair(5, typetest.args['--cc'], typetest.args['--bg'])  # green on black
    curses.init_pair(6, typetest.args['--bg'], typetest.args['--cc'])  # black on green

    color_basic = curses.color_pair(1)
    color_basic_reverse = curses.color_pair(2)
    color_wrong = curses.color_pair(3)
    color_wrong_reverse = curses.color_pair(4)
    color_correct = curses.color_pair(5)
    color_correct_reverse = curses.color_pair(6)

    maxy, maxx = stdscr.getmaxyx()

    rows_maxy = 3 if not typetest.args['--char-by-char'] else maxy - int(not typetest.args['--hide'])

    word_size = maxx - speed_size - time_size - prompt_size - 3

    test_text = ' '.join(typetest.test.test_words)
    text_rows = wrap(test_text, maxx-1, break_long_words=False, break_on_hyphens=False)
    rows = [[list(map(lambda char: [char, color_basic], word)) for word in row]
            for row in map(str.split, text_rows)]

    if not typetest.args['--char-by-char']:
        for i in range(len(rows[0][0])):
            rows[0][0][i][1] = color_basic_reverse
    else:
        rows[0][0][0][1] = color_basic_reverse


def draw_stdscr():
    global stdscr, rows, rows_maxy, test_row_i

    stdscr.erase()

    start_row_i = min(test_row_i, len(rows) - rows_maxy)
    for row_i, row in enumerate(rows[start_row_i:start_row_i + rows_maxy]):
        for word_i, word in enumerate(row):
            for char_i, (char, color) in enumerate(word):
                stdscr.addstr(char, color)
            if word_i + 1 != len(row):
                stdscr.addstr(' ')
        if row_i != rows_maxy - 1:
            stdscr.addstr('\n')


def draw_stats():
    word = typetest.test.text_word

    m, s = divmod(int(typetest.test.duration), 60)
    h, m = divmod(m, 60)
    if h > 23:
        h = 0
    time = f'{h:02d}:{m:02d}:{s:02d}'

    speed = min(int(typetest.test.tmp_speed_wpm), 999)
    speed = f'{speed:3d} wpm'

    stdscr.addstr('\n')
    stdscr.addstr(f'{prompt} {word[-word_size:]:{word_size}s} {time} {speed}')
    stdscr.refresh()
    # exit(f'{prompt} {word[-word_size:]:{word_size}s} {time} {speed}')


def change_char_colors():
    global rows, test_row_i, test_word_i, test_char_i

    if typetest.test.triggered_new_char:
        if typetest.test.text_raw[-1] == typetest.test.test[typetest.test.text_char_i]:
            rows[test_row_i][test_word_i][test_char_i][1] = color_correct
        else:
            rows[test_row_i][test_word_i][test_char_i][1] = color_wrong
        test_char_i += 1
        if test_char_i == len(rows[test_row_i][test_word_i]):
            test_char_i = 0
            test_word_i += 1
            if test_word_i == len(rows[test_row_i]):
                test_word_i = 0
                test_row_i += 1
        rows[test_row_i][test_word_i][test_char_i][1] = color_basic_reverse

    elif typetest.test.triggered_deletion:
        rows[test_row_i][test_word_i][test_char_i][1] = color_basic
        test_char_i -= 1
        if test_char_i < 0:
            test_word_i -= 1
            test_char_i = len(rows[test_row_i][test_word_i]) - 1
            if test_word_i < 0:
                # test_rows_i -= 1
                test_word_i = len(rows[test_row_i]) - 1
        rows[test_row_i][test_word_i][test_char_i][1] = color_basic_reverse


def change_word_colors():
    global rows, test_row_i, test_word_i

    if typetest.test.triggered_new_word:
        if typetest.test.last_text_word == typetest.test.last_test_word:
            for i in range(len(rows[test_row_i][test_word_i])):
                rows[test_row_i][test_word_i][i][1] = color_correct

        else:
            for i in range(len(rows[test_row_i][test_word_i])):
                rows[test_row_i][test_word_i][i][1] = color_wrong
            if typetest.args['--beep']:
                print('\a', end='')

        test_word_i += 1
        if test_word_i == len(rows[test_row_i]):
            test_word_i = 0
            test_row_i += 1

        for i in range(len(rows[test_row_i][test_word_i])):
            rows[test_row_i][test_word_i][i][1] = color_basic_reverse

    elif typetest.test.text_word != typetest.test.test_word[:len(typetest.test.text_word)]:
        for i in range(len(rows[test_row_i][test_word_i])):
            rows[test_row_i][test_word_i][i][1] = color_wrong_reverse

    elif typetest.test.text_word == typetest.test.test_word:
        for i in range(len(rows[test_row_i][test_word_i])):
            rows[test_row_i][test_word_i][i][1] = color_correct_reverse

    elif typetest.test.text_word == typetest.test.test_word[:len(typetest.test.text_word)]:
        for i in range(len(rows[test_row_i][test_word_i])):
            rows[test_row_i][test_word_i][i][1] = color_basic_reverse


def shutdown():
    curses.curs_set(1)
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
