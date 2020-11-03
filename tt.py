#!/usr/bin/env python3
from time import time, strftime, gmtime
from datetime import datetime
from functools import partial
from contextlib import suppress

import os
import sys
import signal
import argparse

from blessed import Terminal

parser = argparse.ArgumentParser(description=f"""example:
  {__file__} -d 3.5 The typing seems really strong today.
  echo 'I love typing' | {__file__}
  {__file__} < test.txt
""", formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-d', '--duration', type=float, default=float('inf'),
                    help='duration in seconds')
parser.add_argument('-r', '--rows', type=int, default=2,
                    help='number of test rows to show')
parser.add_argument('words', nargs='*',
                    help='provide words via args in lieu of stdin')

args = parser.parse_args()
DURATION = args.duration
NUMBER_OF_ROWS = args.rows
words = args.words
if not words:
    words = sys.stdin.read().split()
    sys.argv.extend(words)

sys.__stdin__ = os.fdopen(1)
term = Terminal()

color_normal = term.normal
color_correct = term.color_rgb(0, 230, 0)
color_wrong = term.color_rgb(230, 0, 0)


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
    def echo_line():
        line = ' '.join(line_words)
        if len_line + len(line_words) - 1 < term.width:
            line += term.clear_eol

        echo(term.move_yx(line_height, 0) + line)

    current_word_color = color_correct if words[word_i] == text else \
        color_normal if words[word_i].startswith(text) else \
        color_wrong

    colors = colors + [current_word_color + term.reverse]

    line_i = 0
    len_line = 0
    line_words = []
    line_height = None
    for i, word in enumerate(words):
        color = colors[i] if i < len(colors) else color_normal

        if line_height is not None and line_height >= min(term.height-1, NUMBER_OF_ROWS):
            break

        if len_line + len(word) + len(line_words) > term.width:
            if line_height is not None:
                echo_line()
                line_height += 1

            line_i += 1
            len_line = 0
            line_words = []

        if i == word_i:
            line_height = 0

        len_line += len(word)
        line_words.append(color + word + color_normal)

    if i + 1 >= len(words) and line_height < min(term.height, NUMBER_OF_ROWS):
        echo_line()
        line_height += 1

    n = term.width - 21
    echo(term.move_yx(line_height, 0) + f'>>>{text[:n]: <{n}}')
    echo(term.move_yx(line_height, n + 3) + f"{wpm:3d} wpm | {timestamp}")
    for i in range(1, min(term.height, NUMBER_OF_ROWS) - line_height + 1):
        echo(term.move_yx(line_height + i, 0) + term.clear_eol)


redraw = True
echo = partial(print, end='', flush=True)
signal.signal(signal.SIGWINCH, on_resize)
if __name__ == '__main__':
    timestamp = '00:00:00'
    correct_chars = total_chars = wpm = 0
    duration = start = end = 0
    word_i = 0
    text = ''
    colors = []

    with term.cbreak(), \
            term.fullscreen(), \
            term.hidden_cursor(), \
            suppress(KeyboardInterrupt):
        while word_i < len(words) and (not start or time() - start < DURATION):
            word = words[word_i]

            if redraw:
                draw(words, colors, word_i, text, wpm, timestamp)
                redraw = False

            char = term.inkey(timeout=0.1)
            if not char:
                continue

            if not start:
                start = time()

            if char.name == 'KEY_BACKSPACE':
                text = text[:-1]

            elif (char == ' ' or char == '\n') and text:
                if text == word:
                    correct_chars += len(word) + 1
                    colors.append(color_correct)
                else:
                    colors.append(color_wrong)

                total_chars += len(word) + 1
                duration = time() - start
                wpm = min(int(correct_chars*12/duration), 999)
                timestamp = strftime('%H:%M:%S', gmtime(duration))

                text = ''
                word_i += 1

            elif char == '\x12':  # ctrl-r
                os.execv(sys.executable, ['python'] + sys.argv)

            elif char == '\x15' or char == '\x17':  # ctrl-u or ctrl-w
                text = ''

            else:
                text += char
                if word_i + 1 >= len(words) and words[-1] == text:
                    term.ungetch(' ')

            redraw = True

    accuracy = 100 * correct_chars // total_chars
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f'accuracy: {accuracy}%')
    print(f'speed:    {wpm}wpm')
    print(f'duration: {duration:.0f}s')
