#!/usr/bin/env python3
import os
import csv
import sys
import random
import hashlib
import platform
from time import time, strftime, gmtime
from datetime import datetime
from argparse import ArgumentParser, RawTextHelpFormatter, FileType
from functools import partial

from blessed import Terminal


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
    typing_duration,
    typed_word_input,
    rows,
    shuffle_flag,
    help,
    output_directory,
    hash,
):
    """Reads test words from `typed_word_input` delimited by whitespace characters.
    Listens to standard input forming a typed word every time a
    whitespace is pressed. Compares typed words with test words. Updates the
    screen calling `draw` every time a key is pressed or every 0.1 seconds,
    whichever comes first.

    The test ends when `duration` time has passed or all words have been typed.
    Upon exiting, test results are printed and stored in `test_results_file`.
    """
    if typed_word_input.isatty():  # no test words provided, fallback to a default test
        base_directory = os.path.dirname(__file__)
        typed_word_input = open(base_directory + "/tests/common_300", "r")
        if typing_duration is None:
            typing_duration = 60
            shuffle_flag = True

    if typing_duration is None:
        typing_duration = float("inf")

    test = typed_word_input.read()
    words_list = test.split()

    if hash is None:
        hash = hashlib.sha1(test.encode("utf-8")).hexdigest()

    if shuffle_flag:
        random.shuffle(words_list)

    if not sys.__stdin__.isatty():  # force stdin from user
        if platform.system() == "Windows":
            sys.__stdin__ = open("con:", "r")  # NOT TESTED
        else:
            sys.__stdin__ = open("/dev/tty", "r")

    terminal = Terminal()

    normal_word_colour = terminal.normal
    correct_word_colour = terminal.color_rgb(0, 230, 0)
    wrong_word_colour = terminal.color_rgb(230, 0, 0)

    characters_correct = total_chars = -1
    words_per_minute = 0
    passed_duration = actual_duration = start = 0
    test_word_index = 0
    user_text = ""
    colors = [normal_word_colour] * len(words_list)

    character_times = []

    with terminal.raw(), terminal.cbreak(), terminal.fullscreen(), terminal.hidden_cursor():
        while test_word_index < len(words_list) and (not start or time() - start < typing_duration):
            test_word = words_list[test_word_index]

            if test_word == user_text:
                color = correct_word_colour
            elif test_word.startswith(user_text):
                color = normal_word_colour
            else:
                color = wrong_word_colour

            colors[test_word_index] = color + terminal.reverse

            draw(terminal, rows, words_list, colors, test_word_index, user_text, words_per_minute, passed_duration)

            character = terminal.inkey(timeout=0.1, esc_delay=0)
            char_time = time()
            passed_duration = char_time - start if start else 0

            if not character:
                continue

            if not start:
                start = time()

            if character == "\x03" or character == "\x1b":  # ctrl-c or ctrl-[ or esc
                # stop the test
                break

            elif character == "\x08" or character == "\x7f":  # ctrl-h or bksp
                # delete last character
                user_text = user_text[:-1]

            elif character in ("\x12", "\x13", "\t"):  # ctrl-r or ctrl-s or tab
                # restart test
                characters_correct = total_chars = -1
                words_per_minute = 0
                passed_duration = actual_duration = start = 0
                test_word_index = 0
                user_text = ""
                colors = [normal_word_colour] * len(words_list)
                character_times = []
                if character == "\x13":  # ctrl-s
                    random.shuffle(words_list)

            elif character == "\x15" or character == "\x17":  # ctrl-u or ctrl-w
                # clear user input
                user_text = ""

            elif character.isspace() and user_text:  # word is submitted
                if test_word_index + 1 < len(words_list):  # if not last space
                    # count the space character as correct
                    total_chars += 1
                    characters_correct += 1

                if user_text == test_word:
                    characters_correct += len(test_word)
                    colors[test_word_index] = correct_word_colour
                else:
                    colors[test_word_index] = wrong_word_colour

                actual_duration = passed_duration
                words_per_minute = min(int(characters_correct * 12 / actual_duration), 999)

                user_text = ""
                test_word_index += 1
                character_times.append((character, char_time))

            elif not character.isspace():
                # append the character to user input
                total_chars += 1
                user_text += character
                if test_word_index + 1 >= len(words_list) and words_list[-1] == user_text:  # last word
                    # end test without needing to submit a space
                    terminal.ungetch(" ")
                character_times.append((character, char_time))

    # remove excess user input
    total_chars -= len(user_text)

    if actual_duration <= 0 or total_chars <= 0:  # test is invalid
        return

    # calculate results and write them to output files

    accuracy = 100 * characters_correct // total_chars
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    print(f"accuracy: {accuracy}%")
    print(f"speed:    {words_per_minute}wpm")
    print(f"duration: {actual_duration:.2f}s")

    test_results_file = open(output_directory + "/results.csv", "a")
    mistyped_words_file = open(output_directory + "/mistyped_words.csv", "a")
    character_speeds_file = open(output_directory + "/char_speeds.csv", "a")
    word_speeds_file = open(output_directory + "/word_speeds.csv", "a")

    test_results_writer = csv.writer(test_results_file, lineterminator="\n")
    row = [timestamp, words_per_minute, accuracy, actual_duration, typing_duration, hash]
    test_results_writer.writerow(row)

    characters, character_times = zip(*character_times)
    character_durations = [t1 - t0 for t0, t1 in zip(character_times, character_times[1:])]
    character_speeds_writer = csv.writer(character_speeds_file, lineterminator="\n")
    for character, typing_duration in zip(characters, character_durations):
        character_speeds_writer.writerow([character, typing_duration, 12 / typing_duration, timestamp])

    test_word = ""
    test_word_index = 0
    word_duration = 0
    word_durations = []
    mistyped_writer = csv.writer(mistyped_words_file, lineterminator="\n")
    word_speeds_writer = csv.writer(word_speeds_file, lineterminator="\n")
    for character, typing_duration in zip(characters, character_durations):
        if character.isspace():
            if test_word == words_list[test_word_index]:
                word_durations.append((test_word, word_duration))
                word_speeds_writer.writerow(
                    [
                        test_word,
                        word_duration,
                        len(test_word) * 12 / word_duration,
                        timestamp,
                    ]
                )
            else:
                mistyped_writer.writerow([words_list[test_word_index], test_word, timestamp])

            test_word_index += 1
            test_word = ""
            word_duration = 0
        else:
            test_word += character
            word_duration += typing_duration


def draw(terminal, rows, words_list, colors, test_word_index, user_text, words_per_minute, passed_duration):
    """Text wraps the `words` list to the terminal width, and prints `rows`
    lines of wrapped words coloured with `colors` starting with the line
    containing the current word that is being typed.
    Then, if there is space, prints `prompt` + `text` + `stats`.
    """

    def join(words_list, length):
        eol = terminal.clear_eol if length + len(words_list) - 1 < terminal.width else ""
        return " ".join(line_words) + eol

    echo = partial(print, end="", flush=True, file=terminal.stream)
    allowed_height = min(terminal.height, rows)

    line_length = 0
    line_words = []
    line_height = None
    for i, (word, color) in enumerate(zip(words_list, colors)):
        if line_length + len(word) + len(line_words) > terminal.width:
            if line_height is not None:
                echo(terminal.move_yx(line_height, 0) + join(line_words, line_length))
                line_height += 1
                if line_height >= allowed_height:
                    break

            line_length = 0
            line_words = []

        if i == test_word_index:
            line_height = 0

        line_length += len(word)
        line_words.append(color + word + terminal.normal)

    else:
        echo(terminal.move_yx(line_height, 0) + join(line_words, line_length))
        line_height += 1

    if allowed_height > 1:
        prompt = ">>>"
        timestamp = strftime("%H:%M:%S", gmtime(passed_duration))
        stats = f"{words_per_minute:3d} wpm | {timestamp}"
        n = terminal.width - len(prompt) - len(stats)
        echo(terminal.move_yx(line_height, 0) + f"{prompt}{user_text[:n]: <{n}}{stats}")

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
        "-duration",
        "--typing_duration",
        type=float,
        default=None,
        help="duration in seconds "
        + "(default: <infinity> when a custom test is given, 60 seconds otherwise)",
    )
    parser.add_argument(
        "--hash",
        type=str,
        default=None,
        help="custom hash (generated from input by default)",
    )
    parser.add_argument(
        "-i",
        "-input",
        "--typed_word_input",
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
        "-s", "-shuffle", "--shuffle_flag", action="store_true", help="shuffle words " + default
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
