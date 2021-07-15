#!/usr/bin/env python3
import os
import sys
import random
import hashlib
import platform
import pandas as pd

from time import time, strftime, gmtime
from datetime import datetime
from argparse import ArgumentParser, RawTextHelpFormatter, FileType
from functools import partial

from blessed import Terminal

from typetest import analyse

filename = os.path.basename(sys.argv[0])
doc = f"""example:
  {filename} -i test.txt -s -d 60
  echo 'The typing seems really strong today.' | {filename} -d 3.5
  {filename} < test.txt

shortcuts:
  ^c / ctrl+c           end the test and get results now
  ^[ / ctrl+[ / esc     end the test and get results now
  ^h / ctrl+h / bksp    delete a character
  ^r / ctrl+r / tab     restart the same test
  ^s / ctrl+s           restart the test with words reshuffled
  ^w / ctrl+w           delete a word
  ^u / ctrl+u           delete a word
"""


def run():
    main(**parse_args())


def main(duration, input, rows, shuffle, help,
         output, mistyped, char_speeds, word_speeds, hash):
    """Reads test words from `input` delimited by whitespace characters.
    Listens to standard input forming a typed word every time a
    whitespace is pressed. Compares typed words with test words. Updates the
    screen calling `draw` every time a key is pressed or every 0.1 seconds,
    whichever comes first.

    The test ends when `duration` time has passed or all words have been typed.
    Upon exiting, test results are printed and stored in `output`.
    """
    if input.isatty():  # no test words provided
        sys.exit(help())

    test = input.read()
    if hash is None:
        hash = hashlib.sha1(test.encode("utf-8")).hexdigest()
    words = test.split()

    if shuffle:
        random.shuffle(words)

    if not sys.__stdin__.isatty():  # force stdin from user
        if platform.system() == 'Windows':
            sys.__stdin__ = open('con:', 'r')  # NOT TESTED
        else:
            sys.__stdin__ = open('/dev/tty', 'r')

    term = Terminal()

    color_normal = term.normal
    color_correct = term.color_rgb(0, 230, 0)
    color_wrong = term.color_rgb(230, 0, 0)

    correct_chars = total_chars = -1
    wpm = 0
    time_passed = actual_duration = start = 0
    word_i = 0
    text = ''
    colors = [color_normal]*len(words)

    mistyped_words = []
    char_times = []

    with term.raw(), \
            term.cbreak(), \
            term.fullscreen(), \
            term.hidden_cursor():
        while word_i < len(words) and (not start or time() - start < duration):
            word = words[word_i]

            color = color_correct if word == text else \
                color_normal if word.startswith(text) else \
                color_wrong
            colors[word_i] = color + term.reverse

            draw(term, rows, words, colors, word_i, text, wpm, time_passed)

            char = term.inkey(timeout=0.1, esc_delay=0)
            char_time = time()
            time_passed = char_time - start if start else 0

            if not char:
                continue

            if not start:
                start = time()

            if char == '\x03' or char == '\x1b':  # ctrl-c or ctrl-[ or esc
                break

            elif char == '\x08' or char == '\x7f':  # ctrl-h or bksp
                text = text[:-1]

            elif char in ('\x12', '\x13', '\t'):  # ctrl-r or ctrl-s or tab
                correct_chars = total_chars = -1
                wpm = 0
                time_passed = actual_duration = start = 0
                word_i = 0
                text = ''
                colors = [color_normal]*len(words)
                mistyped_words = []
                char_times = []
                if char == '\x13':
                    random.shuffle(words)

            elif char == '\x15' or char == '\x17':  # ctrl-u or ctrl-w
                text = ''

            elif char.isspace() and text:
                if word_i + 1 < len(words):  # if not last space
                    total_chars += 1
                    correct_chars += 1

                if text == word:
                    correct_chars += len(word)
                    colors[word_i] = color_correct
                else:
                    colors[word_i] = color_wrong
                    mistyped_words.append((word, text))

                actual_duration = time_passed
                wpm = min(int(correct_chars*12/actual_duration), 999)

                text = ''
                word_i += 1
                char_times.append((char, char_time))

            elif not char.isspace():
                total_chars += 1
                text += char
                if word_i + 1 >= len(words) and words[-1] == text:
                    term.ungetch(' ')
                char_times.append((char, char_time))

    total_chars -= len(text)

    if actual_duration <= 0 or total_chars <= 0:
        return

    accuracy = 100 * correct_chars // total_chars
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    print(f'accuracy: {accuracy}%')
    print(f'speed:    {wpm}wpm')
    print(f'duration: {actual_duration:.2f}s')

    chars, times = zip(*char_times)
    durations = [t1-t0 for t0, t1 in zip(times, times[1:])]
    char_durations = list(zip(chars, durations))

    row = [timestamp, wpm, accuracy, actual_duration, duration, hash]
    output.write(','.join(map(str, row)) + '\n')

    df = pd.DataFrame([(w1, w2, timestamp) for w1, w2 in mistyped_words])
    mistyped.write(df.to_csv(index=False, header=False))

    df = pd.DataFrame([(c, t, 12/t, timestamp) for c, t in char_durations])
    char_speeds.write(df.to_csv(index=False, header=False))

    word = ''
    word_i = 0
    word_duration = 0
    word_durations = []
    for char, duration in char_durations:
        if char.isspace():
            if word == words[word_i]:
                word_durations.append((word, word_duration))
            word_i += 1
            word = ''
            word_duration = 0
        else:
            word += char
            word_duration += duration

    df = pd.DataFrame([(word, t, len(word)*12/t, timestamp)
                       for word, t in word_durations])
    word_speeds.write(df.to_csv(header=False, index=False))


def draw(term, rows, words, colors, word_i, text, wpm, time_passed):
    """Text wraps the `words` list to the terminal width, and prints `rows`
    lines of wrapped words coloured with `colors` starting with the line
    containing the current word that is being typed.
    Then, if there is space, prints `prompt` + `text` + `stats`.
    """
    def join(words, length):
        eol = term.clear_eol if length + len(words) - 1 < term.width else ''
        return ' '.join(line_words) + eol

    echo = partial(print, end='', flush=True, file=term.stream)
    allowed_height = min(term.height, rows)

    len_line = 0
    line_words = []
    line_height = None
    for i, (word, color) in enumerate(zip(words, colors)):
        if len_line + len(word) + len(line_words) > term.width:
            if line_height is not None:
                echo(term.move_yx(line_height, 0) + join(line_words, len_line))
                line_height += 1
                if line_height >= allowed_height:
                    break

            len_line = 0
            line_words = []

        if i == word_i:
            line_height = 0

        len_line += len(word)
        line_words.append(color + word + term.normal)

    else:
        echo(term.move_yx(line_height, 0) + join(line_words, len_line))
        line_height += 1

    if allowed_height > 1:
        prompt = '>>>'
        timestamp = strftime('%H:%M:%S', gmtime(time_passed))
        stats = f'{wpm:3d} wpm | {timestamp}'
        n = term.width - len(prompt) - len(stats)
        echo(term.move_yx(line_height, 0) + f'{prompt}{text[:n]: <{n}}{stats}')

    for i in range(1, allowed_height - line_height + 1):
        echo(term.move_yx(line_height + i, 0) + term.clear_eol)


def parse_args():
    """Parses `sys.argv` and returns a dictionary suitable for `main`."""
    parser = ArgumentParser(epilog=doc, formatter_class=RawTextHelpFormatter)

    default = '(default: %(default)s)'
    basedir = os.path.dirname(__file__)
    parser.add_argument('-d', '--duration', type=float, default=float('inf'),
                        help='duration in seconds ' + default)
    parser.add_argument('--hash', type=str, default=None,
                        help='custom hash (generated from input by default)')
    parser.add_argument('-i', '--input', type=FileType('r'),
                        default=sys.stdin,
                        help='file to read words from (default: sys.stdin)')
    parser.add_argument('-o', '--output', type=FileType('a'),
                        default=basedir + '/results/results.csv',
                        help='file to store results in\n' + default)
    parser.add_argument('-m', '--mistyped', type=FileType('a'),
                        default=basedir + '/results/mistyped_words.csv',
                        help='file to store mistyped words in\n' + default)
    parser.add_argument('-c', '--char_speeds', type=FileType('a'),
                        default=basedir + '/results/char_speeds.csv',
                        help='file to store character speeds in\n' + default)
    parser.add_argument('-w', '--word_speeds', type=FileType('a'),
                        default=basedir + '/results/word_speeds.csv',
                        help='file to store word speeds in\n' + default)
    parser.add_argument('-s', '--shuffle', action='store_true',
                        help='shuffle words ' + default)
    parser.add_argument('-r', '--rows', type=int, default=2,
                        help='number of test rows to show ' + default)

    return dict(parser.parse_args()._get_kwargs(), help=parser.print_help)


if __name__ == '__main__':
    main(**parse_args())
