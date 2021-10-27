"""Various utility functions."""
import pandas as pd

from functools import wraps
from random import sample
from collections import Counter
from os.path import dirname, isfile


def damerau_levenshtein_distance(word_1: str, word_2: str) -> int:
    """Calculates the distance between two words."""
    inf = len(word_1) + len(word_2)
    table = [
        [inf for _ in range(len(word_1) + 2)] for _ in range(len(word_2) + 2)
    ]

    for i in range(1, len(word_1) + 2):
        table[1][i] = i - 1
    for i in range(1, len(word_2) + 2):
        table[i][1] = i - 1

    last_encountered_cols = {}
    for col, char_1 in enumerate(word_1, 2):
        last_row = 0
        for row, char_2 in enumerate(word_2, 2):
            last_encountered_col = last_encountered_cols.get(char_2, 0)

            addition = table[row - 1][col] + 1
            deletion = table[row][col - 1] + 1
            substitution = table[row - 1][col - 1] + (
                0 if char_1 == char_2 else 1
            )

            transposition = (
                table[last_row - 1][last_encountered_col - 1]
                + (col - last_encountered_col - 1)
                + (row - last_row - 1)
                + 1
            )

            table[row][col] = min(
                addition, deletion, substitution, transposition
            )

            if char_1 == char_2:
                last_row = row
        last_encountered_cols[char_1] = col

    return table[len(word_2) + 1][len(word_1) + 1]


def validate_input_file_path(func):
    """Wrapper function that checks if the first argument of the
    decorated function is a filename of a file that exists.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        file_to_open = args[0]

        if not isfile(file_to_open):
            exit(
                f"The file {file_to_open} does not exist. Please run"
                + "`typetest` to generate more test results, or provide"
                + "a custom path to results file/directory"
            )

        func(*args, **kwargs)

    return wrapper


@validate_input_file_path
def create_least_typed_words_and_worst_words_test_files(
    input_file, least_typed_words_output_file, worst_words_output_file
):
    data_frame = pd.read_csv(
        input_file,
        header=None,
        names=["word", "duration", "wpm", "timestamp"],
    )

    counter = Counter(sample(list(data_frame["word"]), k=len(data_frame)))
    with open(least_typed_words_output_file, "w") as f:
        f.write(" ".join(reversed(list(zip(*counter.most_common()))[0])))

    grouped_data_frames = sorted(
        data_frame.groupby("word"), key=lambda x: x[1]["wpm"].median()
    )

    with open(worst_words_output_file, "w") as f:
        words_by_median = list(zip(*grouped_data_frames))[0]
        f.write(" ".join(words_by_median))
