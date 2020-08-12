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
CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
TEST_FILE_PATH = CURRENT_DIRECTORY + '/typetest/tests/english/basic'
NUMBER_OF_ROWS = 2

term = Terminal()

color_normal = term.normal
color_correct = term.color(46)
color_wrong = term.color(196)


def on_resize(*_):
    """Called every time a resize signal (`signal.SIGWINCH`) is sent.

    Sets the global `redraw` flag to true.
    """
    global redraw
    redraw = True


def draw(words, colors, word_i, text, wpm, timestamp):
    """Text wraps the `words` list to the terminal width, and prints
    `NUMBER_OF_ROWS` lines of wrapped words starting with the line
    containing the current word that is being typed.
    As a consequence this can become slow if the text is really long,
    and the duration of the test is infinite.
    A better approach would be to text wrap only `on_resize`, but that
    would mean there would need to be at least 2 structures holding the
    same data for `words` and `colors` (one text wrapped, one not).

    Already typed words appear in either `color_correct` or `color_wrong`,
    whereas the currently typed word can additionally be `color_normal` when
    the word starts with the typed text but isn't (yet) correct.
    """
    current_word_color = color_correct if words[word_i] == text else \
        color_normal if words[word_i].startswith(text) else \
        color_wrong

    colors = colors + [current_word_color + term.reverse]

    line_i = 0
    len_line = 0
    line_words = []
    line_height = None
    for i, (word, color) in enumerate(zip_longest(words, colors,
                                                  fillvalue=color_normal)):
        if line_height and line_height >= min(term.height, NUMBER_OF_ROWS):
            break

        if len_line + len(word) + len(line_words) > term.width:
            if line_height is not None:
                line = ' '.join(line_words)
                if len_line + len(line_words) - 1 < term.width:
                    line += term.clear_eol

                echo(term.move_yx(line_height, 0) + line)
                line_height += 1

            line_i += 1
            len_line = 0
            line_words = []

        if i == word_i:
            line_height = 0

        line_words.append(color + word + color_normal)
        len_line += len(word)

    echo(term.move_yx(line_height, 0))
    echo(f">>>{text}{' '*(term.width-len(text)-21)}{wpm:3d} wpm | {timestamp}")
    echo(term.move_x(3 + len(text)))


redraw = True
echo = partial(print, end='', flush=True)
signal.signal(signal.SIGWINCH, on_resize)

if __name__ == '__main__':
    with open(TEST_FILE_PATH) as f:
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

                    if text == word:
                        correct_chars += len(word) + 1
                        colors.append(color_correct)
                    else:
                        colors.append(color_wrong)

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
