from time import time, strftime, gmtime
from datetime import datetime
from itertools import zip_longest
from functools import partial
from contextlib import suppress

from blessed import Terminal

import os
import re
import signal
import random


DURATION = 60  # in seconds
SHUFFLE = True  # shuffle words of a test file?
DIR = os.path.dirname(os.path.realpath(__file__))
TEST_FILE = DIR + '/typetest/tests/english/basic'
NUMBER_OF_ROWS = 2

term = Terminal()

color_normal = term.normal
color_correct = term.color(46)
color_wrong = term.color(196)


def on_resize(*_):
    global redraw
    redraw = True


def draw(words, colors, word_i, text, wpm, timestamp):
    color = color_correct if words[word_i] == text else \
            color_normal if words[word_i].startswith(text) else \
            color_wrong

    colors = colors + [color + term.reverse]
    print_line = -1
    line_i = 0
    len_line = 0
    line_words = []
    for i, (word, color) in enumerate(zip_longest(words, colors, fillvalue=color_normal)):
        if len_line + len(word) + len(line_words) > term.width:
            if print_line >= min(term.height, NUMBER_OF_ROWS):
                break

            elif print_line >= 0:
                line = ' '.join(line_words)
                if len_line + len(line_words) - 1 < term.width:
                    line += term.clear_eol
                echo(term.move_yx(print_line, 0) + line)
                print_line += 1

            line_i += 1
            len_line = 0
            line_words = []

        if i == word_i:
            print_line += 1

        line_words.append(color + word + term.normal)
        len_line += len(word)

    echo(term.move_yx(print_line, 0))
    echo(f">>>{text}{' '*(term.width-len(text)-21)}{wpm:3d} wpm | {timestamp}")
    echo(term.move_x(3 + len(text)))


redraw = True
echo = partial(print, end='', flush=True)
signal.signal(signal.SIGWINCH, on_resize)

if __name__ == '__main__':
    with open(TEST_FILE) as f:
        words = re.findall(r"[\w']+", f.read())

    if SHUFFLE:
        random.shuffle(words)

    timestamp = '00:00:00'
    correct_chars = total_chars = wpm = 0
    duration = start = end = 0
    word_i = 0
    text = ''
    colors = []

    with term.cbreak(), term.fullscreen(), suppress(KeyboardInterrupt):
        while word_i < len(words) and not start or time() - start < DURATION:
            word = words[word_i]

            if redraw:
                draw(words, colors, word_i, text, wpm, timestamp)
                redraw = False

            char = term.inkey(timeout=0.1)
            if not char:
                continue

            if not start:
                start = time()

            end = time()
            duration = end - start
            timestamp = strftime('%H:%M:%S', gmtime(duration))

            if char.name == 'KEY_BACKSPACE':
                text = text[:-1]

            elif char == ' ':
                if text:
                    total_chars += len(word) + 1
                    color = color_correct if text == word else color_wrong
                    colors.append(color)

                    if text == word:
                        correct_chars += len(word) + 1

                    wpm = min(int(correct_chars*12/duration), 999)

                    text = ''
                    word_i += 1
            else:
                text += char

            redraw = True

    accuracy = 100 * correct_chars // total_chars
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f'accuracy: {accuracy}%')
    print(f'speed:    {wpm}wpm')
    print(f'duration: {duration:.0f}s')
