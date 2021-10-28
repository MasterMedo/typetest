#!/usr/bin/env python3
import os
import csv
import sys
import random
import hashlib
import platform

from pathlib import Path
from datetime import datetime
from functools import partial
from time import time, strftime, gmtime
from argparse import ArgumentParser, RawTextHelpFormatter, FileType

from blessed import Terminal

from typetest.utils import create_least_typed_words_and_worst_words_test_files


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
    """Parse command arguments and run main"""
    main(**parse_args())


def main(
    duration,
    input,
    rows,
    shuffle_flag,
    help,
    output_directory,
    hash,
):
    """Reads test words from `input` delimited by whitespace characters.
    Listens to standard input forming a typed word every time a
    whitespace is pressed. Compares typed words with test words. Updates the
    screen calling `draw` every time a key is pressed or every 0.1 seconds,
    whichever comes first.

    The test ends when `duration` time has passed or all words have been typed.
    Upon exiting, test results are printed and stored in `test_results_file`.
    """
    if input.isatty():  # no test words provided, fallback to a default test
        base_directory = os.path.dirname(__file__)
        input = open(base_directory + "/tests/common_300", "r")
        if duration is None:
            duration = 60
            shuffle_flag = True

    if duration is None:
        duration = float("inf")

    test = input.read()
    words = test.split()

    if hash is None:
        hash = hashlib.sha1(test.encode("utf-8")).hexdigest()

    if shuffle_flag:
        random.shuffle(words)

    if not sys.__stdin__.isatty():  # force stdin from user
        if platform.system() == "Windows":
            sys.__stdin__ = open("con:", "r")  # NOT TESTED
        else:
            sys.__stdin__ = open("/dev/tty", "r")

    terminal = Terminal()

    color_normal = terminal.normal
    color_correct = terminal.color_rgb(0, 230, 0)
    color_wrong = terminal.color_rgb(230, 0, 0)

    correct_chars = total_chars = -1
    typing_speed_in_wpm = 0
    typing_duration = actual_duration = start = 0
    word_index = 0
    user_text = ""
    colors = [color_normal] * len(words)

    char_times = []
    restart_count = 0

    with terminal.raw(), terminal.cbreak(), terminal.fullscreen(), terminal.hidden_cursor():  # noqa E501
        while word_index < len(words) and (
            not start or time() - start < duration
        ):
            word = words[word_index]

            if word == user_text:
                color = color_correct
            elif word.startswith(user_text):
                color = color_normal
            else:
                color = color_wrong

            colors[word_index] = color + terminal.reverse

            draw(
                terminal,
                rows,
                words,
                colors,
                word_index,
                user_text,
                typing_speed_in_wpm,
                typing_duration,
            )

            char = terminal.inkey(timeout=0.1, esc_delay=0)
            char_time = time()
            typing_duration = char_time - start if start else 0

            if not char:
                continue

            if not start:
                start = time()

            if char == "\x03" or char == "\x1b":  # ctrl-c or ctrl-[ or esc
                # stop the test
                break

            elif char == "\x08" or char == "\x7f":  # ctrl-h or bksp
                # delete last character
                user_text = user_text[:-1]

            elif char in ("\x12", "\x13", "\t"):  # ctrl-r or ctrl-s or tab
                # restart test
                restart_count += 1
                correct_chars = total_chars = -1
                typing_speed_in_wpm = 0
                typing_duration = actual_duration = start = 0
                word_index = 0
                user_text = ""
                colors = [color_normal] * len(words)
                char_times = []
                if char == "\x13":  # ctrl-s
                    random.shuffle(words)

            elif char == "\x15" or char == "\x17":  # ctrl-u or ctrl-w
                # clear user input
                user_text = ""

            elif char.isspace() and user_text:  # word is submitted
                if word_index + 1 < len(words):  # if not last space
                    # count the space character as correct
                    total_chars += 1
                    correct_chars += 1

                if user_text == word:
                    correct_chars += len(word)
                    colors[word_index] = color_correct
                else:
                    colors[word_index] = color_wrong

                actual_duration = typing_duration
                typing_speed_in_wpm = min(
                    int(correct_chars * 12 / actual_duration), 999
                )

                user_text = ""
                word_index += 1
                char_times.append((char, char_time))

            elif not char.isspace():
                # append the character to user input
                total_chars += 1
                user_text += char
                if (
                    word_index + 1 >= len(words) and words[-1] == user_text
                ):  # last word
                    # end test without needing to submit a space
                    terminal.ungetch(" ")
                char_times.append((char, char_time))

    # remove excess user input
    total_chars -= len(user_text)

    if actual_duration <= 0 or total_chars <= 0:  # test is invalid
        return

    # calculate results and write them to output files

    accuracy = 100 * correct_chars // total_chars
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    print(f"accuracy: {accuracy}%")
    print(f"speed:    {typing_speed_in_wpm}wpm")
    print(f"duration: {actual_duration:.2f}s")
    print(f"restarts: {restart_count}")
    print(
        f"keystrokes: {correct_chars} correct | {total_chars - correct_chars}"
        + " incorrect"
    )

    test_results_file = open(output_directory + "/results.csv", "a")
    mistyped_words_file = open(output_directory + "/mistyped_words.csv", "a")
    char_speeds_file = open(output_directory + "/char_speeds.csv", "a")
    word_speeds_file = open(output_directory + "/word_speeds.csv", "a")

    test_results_writer = csv.writer(test_results_file, lineterminator="\n")
    row = [
        timestamp,
        typing_speed_in_wpm,
        accuracy,
        actual_duration,
        duration,
        hash,
    ]
    test_results_writer.writerow(row)

    chars, times = zip(*char_times)
    char_durations = [t1 - t0 for t0, t1 in zip(times, times[1:])]
    char_speeds_writer = csv.writer(char_speeds_file, lineterminator="\n")
    for char, duration in zip(chars, char_durations):
        char_speeds_writer.writerow([char, duration, 12 / duration, timestamp])

    word = ""
    word_index = 0
    word_duration = 0
    word_durations = []
    mistyped_writer = csv.writer(mistyped_words_file, lineterminator="\n")
    word_speeds_writer = csv.writer(word_speeds_file, lineterminator="\n")
    for char, duration in zip(chars, char_durations):
        if char.isspace():
            if word == words[word_index]:
                word_durations.append((word, word_duration))
                word_speeds_writer.writerow(
                    [
                        word,
                        word_duration,
                        len(word) * 12 / word_duration,
                        timestamp,
                    ]
                )
            else:
                mistyped_writer.writerow([words[word_index], word, timestamp])

            word_index += 1
            word = ""
            word_duration = 0
        else:
            word += char
            word_duration += duration

    test_results_file.close()
    mistyped_words_file.close()
    char_speeds_file.close()
    word_speeds_file.close()

    create_least_typed_words_and_worst_words_test_files(
        Path(output_directory) / "word_speeds.csv",
        Path(output_directory) / "../tests/least_typed_words",
        Path(output_directory) / "../tests/worst_words",
    )


def draw(
    terminal,
    rows,
    words,
    colors,
    word_index,
    user_text,
    typing_speed_in_wpm,
    typing_duration,
):
    """Text wraps the `words` list to the terminal width, and prints `rows`
    lines of wrapped words coloured with `colors` starting with the line
    containing the current word that is being typed.
    Then, if there is space, prints `prompt` + `text` + `stats`.
    """

    def join(words, length):
        eol = (
            terminal.clear_eol
            if length + len(words) - 1 < terminal.width
            else ""
        )
        return " ".join(line_words) + eol

    echo = partial(print, end="", flush=True, file=terminal.stream)
    allowed_height = min(terminal.height, rows)

    line_length = 0
    line_words = []
    line_height = None
    for i, (word, color) in enumerate(zip(words, colors)):
        if line_length + len(word) + len(line_words) > terminal.width:
            if line_height is not None:
                echo(
                    terminal.move_yx(line_height, 0)
                    + join(line_words, line_length)
                )
                line_height += 1
                if line_height >= allowed_height:
                    break

            line_length = 0
            line_words = []

        if i == word_index:
            line_height = 0

        line_length += len(word)
        line_words.append(color + word + terminal.normal)

    else:
        echo(terminal.move_yx(line_height, 0) + join(line_words, line_length))
        line_height += 1

    if allowed_height > 1:
        prompt = ">>>"
        timestamp = strftime("%H:%M:%S", gmtime(typing_duration))
        stats = f"{typing_speed_in_wpm:3d} wpm | {timestamp}"
        n = terminal.width - len(prompt) - len(stats)
        echo(
            terminal.move_yx(line_height, 0)
            + f"{prompt}{user_text[:n]: <{n}}{stats}"
        )

    for i in range(1, allowed_height - line_height + 1):
        echo(terminal.move_yx(line_height + i, 0) + terminal.clear_eol)


def parse_args():
    """Parses `sys.argv` and returns a dictionary suitable for `main`."""

    def directory_path(string):
        if os.path.isdir(string):
            return string
        else:
            raise NotADirectoryError(string)

    parser = ArgumentParser(epilog=doc, formatter_class=RawTextHelpFormatter)

    default = "(default: %(default)s)"
    base_directory = os.path.dirname(__file__)
    parser.add_argument(
        "-d",
        "--duration",
        type=float,
        default=None,
        help="duration in seconds "
        + "(default: <infinity> when a custom test is given, 60 seconds "
        + "otherwise)",
    )
    parser.add_argument(
        "--hash",
        type=str,
        default=None,
        help="custom hash (generated from input by default)",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=FileType("r"),
        default=sys.stdin,
        help="file to read words from (default: sys.stdin)",
    )
    parser.add_argument(
        "-o",
        "--output-directory",
        type=directory_path,
        default=base_directory + "/results",
        help="file to store results in\n" + default,
    )
    parser.add_argument(
        "-s",
        "-shuffle",
        "--shuffle_flag",
        action="store_true",
        help="shuffle words " + default,
    )
    parser.add_argument(
        "-r",
        "--rows",
        type=int,
        default=2,
        help="number of test rows to show " + default,
    )

    return dict(parser.parse_args()._get_kwargs(), help=parser.print_help)


if __name__ == "__main__":
    run()
