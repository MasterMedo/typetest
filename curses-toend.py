import time, textwrap, curses
from keytype import TypingTest, generate_test


stdscr = curses.initscr()
curses.start_color()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
curses.curs_set(0)

maxy, maxx = stdscr.getmaxyx()

testscr_rows = 3                                    # number of rows for the test screen
testscr = curses.newwin(testscr_rows, maxx, 0, 0)   # words that need to be typed
wordscr = curses.newwin(1, maxx, 4, 1)              # window to type the current word

curses.init_pair(1, 196, 0) # red on black
curses.init_pair(2, 46, 0)  # green on black
curses.init_pair(3, 0, 196) # white on red
curses.init_pair(4, 0, 46)  # white on green

basic_word_color = curses.color_pair(0)             # white on black
wrong_word_color = curses.color_pair(1)             # red   on black
correct_word_color = curses.color_pair(2)           # green on black
current_word_color = curses.A_REVERSE               # black on white
current_wrong_word_color = curses.color_pair(3)     # red   on white
current_correct_word_color = curses.color_pair(4)   # red   on white

word = ''
test_row_i = 0
test_word_i = 0
start_time = time.time()
test = TypingTest(test=generate_test())

test_rows = []
for row in textwrap.wrap(' '.join(test.test_words), maxx-1):
    words = row.split()
    word_colors = list(map(lambda w: [w, basic_word_color], words))
    test_rows.append(word_colors)

while True:
    testscr.erase()

    test_word = test_rows[test_row_i][test_word_i][0]

    if word == test_word[:len(word)] and len(word) == len(test_word):
        test_rows[test_row_i][test_word_i][1] = current_correct_word_color

    elif word == test_word[:len(word)]:
        test_rows[test_row_i][test_word_i][1] = current_word_color

    else:
        test_rows[test_row_i][test_word_i][1] = current_wrong_word_color

    for i, row in enumerate(test_rows[test_row_i:test_row_i+3]):
        for j, (w, color) in enumerate(row):
            testscr.addstr(w, color)
            if j+1 != len(row):
                testscr.addstr(' ')
        if i != 2:
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
            end_time = time.time()
            duration = end_time-start_time
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

curses.curs_set(1)
curses.nocbreak()
stdscr.keypad(0);
curses.echo()
curses.endwin()

test.submit(duration)
print(test.result_extensive())
