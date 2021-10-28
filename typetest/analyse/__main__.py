#!/usr/bin/env python3

import os
import re
import sys
import warnings
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path
from argparse import ArgumentParser, RawTextHelpFormatter, FileType
from functools import partial
from matplotlib import rcParams

from typetest.analyse import (
    typing_speed_per_test,
    typing_speed_per_test_duration,
    typing_speed_distribution,
    typing_speed_of_n_best_words,
    typing_speed_per_char,
    mistyped_words_pie_chart,
)

warnings.simplefilter("ignore", np.RankWarning)
warnings.simplefilter("error", UserWarning)
rcParams.update({"figure.autolayout": True})
sns.set(font_scale=1)
filename = os.path.basename(sys.argv[0])
doc = f"""example:
  {filename}
  {filename} wpm
  {filename} char word
"""


def run():
    """Parse command line arguments and run main"""
    try:
        main(**parse_args())
    except UserWarning:
        print(
            "No matplotlib backend found that supports drawing charts."
            + "\nSolve this by installing `tk`!\nFor example:"
            + "\n\nsudo apt-get install python-tk\nor\nsudo pacman -S tk"
        )


def main(graphs, output, mistyped, char_speeds, word_speeds, help):
    """Draw diagrams the user has requested."""
    is_word = partial(re.match, r"^[a-z]+$")
    if "wpm" in graphs:
        typing_speed_per_test.plot(output)
    if "duration" in graphs:
        typing_speed_per_test_duration.plot(output)
    if "char" in graphs:
        typing_speed_per_char.plot(char_speeds, filter_func=str.islower)
    if "word" in graphs:
        typing_speed_of_n_best_words.plot(word_speeds, 50, filter_func=is_word)
    if "dist" in graphs:
        typing_speed_distribution.plot(word_speeds, filter_func=is_word)
    if "mistypes" in graphs:
        mistyped_words_pie_chart.plot(mistyped, filter_func=is_word)


def parse_args():
    """Parses `sys.argv` and returns a dictionary suitable for `main`."""
    parser = ArgumentParser(epilog=doc, formatter_class=RawTextHelpFormatter)

    default = "(default: %(default)s)"
    base_directory = Path(__file__).parent.parent
    results_directory = "results"
    parser.add_argument(
        "graphs",
        type=str,
        nargs="*",
        default=["wpm", "dist", "word", "char", "mistypes", "duration"],
        help="graphs to plot: wpm char word dist mistypes duration\n"
        + default,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=f"{base_directory}/{results_directory}/results.csv",
        help="file to store results in\n" + default,
    )
    parser.add_argument(
        "-m",
        "--mistyped",
        type=str,
        default=f"{base_directory}/{results_directory}/mistyped_words.csv",
        help="file to store mistyped words in\n" + default,
    )
    parser.add_argument(
        "-c",
        "--char_speeds",
        type=str,
        default=f"{base_directory}/{results_directory}/char_speeds.csv",
        help="file to store character speeds in\n" + default,
    )
    parser.add_argument(
        "-w",
        "--word_speeds",
        type=str,
        default=f"{base_directory}/{results_directory}/word_speeds.csv",
        help="file to store word speeds in\n" + default,
    )

    return dict(parser.parse_args()._get_kwargs(), help=parser.print_help)


if __name__ == "__main__":
    run()
