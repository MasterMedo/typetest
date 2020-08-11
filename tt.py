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

normal = term.normal
correct = term.color(46)
wrong = term.color(196)


def on_resize(*_):
    global redraw
    redraw = True


def draw(words, inwords, word_i, text, wpm, timestamp):
    output_lines = []
    print_line = False
    line, line_i, len_line = '', 0, 0
    for i, (word, inword) in enumerate(zip_longest(words, inwords)):
        if len_line + len(word) >= term.width:
            if print_line:
                if len_line < term.width:
                    line += term.clear_eol

                output_lines.append(line)
                if len(output_lines) >= NUMBER_OF_ROWS:
                    break

            line, line_i, len_line = '', line_i+1, 0

        if line:
            line += ' '
            len_line += 1

        if i == word_i:
            color = correct if word == text else \
                    normal if word.startswith(text) else \
                    wrong

            print_line = True
            line += color + term.reverse(word)

        else:
            color = normal if i >= len(inwords) else \
                    correct if word == inword else \
                    wrong

            line += color + word

        len_line += len(word)

    empty_space = ' ' * (term.width - len(text) - 21)
    line = f">>>{text}{empty_space}{wpm:3d} wpm | {timestamp}"
    output_lines.append(line)

    for line_i, line in enumerate(output_lines):
        if line_i >= term.height:
            break

        echo(term.move_yx(line_i, 0) + line)

    echo(term.move_yx(len(output_lines)-1, 3+len(text)))


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
    inwords = []

    with term.cbreak(), term.fullscreen(), suppress(KeyboardInterrupt):
        while word_i < len(words) and not start or time() - start < DURATION:
            word = words[word_i]

            if redraw:
                draw(words, inwords, word_i, text, wpm, timestamp)
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
                    inwords.append(text)

                    if len(text) == len(word):
                        correct_chars += 1  # space
                        if text == word:
                            correct_chars += len(word)

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
