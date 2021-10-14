#!/usr/bin/env python3
"""
Provide analysis of tests that have been run.
"""

import os
import re
import sys
import math
import warnings

from io import StringIO
from collections import deque, defaultdict
from argparse import ArgumentParser, RawTextHelpFormatter, FileType
from functools import partial
from itertools import cycle
from matplotlib import rcParams
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from typetest.utils import damerau_levenshtein_distance

warnings.simplefilter("ignore", np.RankWarning)
warnings.simplefilter("error", UserWarning)
rcParams.update({"figure.autolayout": True})
sns.set(font_scale=1.5)
filename = os.path.basename(sys.argv[0])
doc = f"""example:
  {filename}
  {filename} wpm
  {filename} char word
"""

known_hashes = {
    "da4846a3c2a8469dd77c921ab0b0bcd506b6e9f3": "300 most common english words",
    "275eb003c4fba77d7e61893c3d9fa869822e06c8": "1000 most common english words (no double letters)",
}


def run():
    """Parse command line arguments and run main"""
    main(**parse_args())


def show_diagram():
    """Do `plt.show()`, confirming a GUI matplotlib backend is available."""
    try:
        plt.show()
    except UserWarning:
        print("No matplotlib backend found that supports drawing charts.")
        print("Solve this by installing tk!")
        print("For example:")
        print("  sudo apt-get install python-tk")
        print("  sudo pacman -S tk")


def main(graphs, output, mistyped, char_speeds, word_speeds):
    """Draw diagrams the user has requested."""
    is_word = partial(re.match, r"^[a-z]+$")
    if "wpm" in graphs:
        plot_wpm(output)
    if "char" in graphs:
        plot_char_speeds(char_speeds, filter_func=str.islower)
    if "word" in graphs:
        plot_n_best_word_speeds(word_speeds, 50, filter_func=is_word)
    if "dist" in graphs:
        plot_word_wpm_distribution(word_speeds, filter_func=is_word)
    if "mistypes" in graphs:
        plot_mistypes_distribution(mistyped)


def plot_wpm(output):
    """Reads `output` and plots typing speeds uniformly apart.
    Adds a trendline.
    """
    csv_data_frame = pd.read_csv(
        output,
        header=None,
        names=["timestamp", "wpm", "accuracy", "actual_duration", "duration", "hash"],
    )

    if len(csv_data_frame) < 2:
        print("More data is needed, before analysing is possible. " +
              "A minimum of 2 tests is required.")
        return

    csv_data_frame.timestamp = pd.to_datetime(csv_data_frame.timestamp)
    # df = df.set_index(df.timestamp)

    min_wpm = None
    grouped_data_frames = defaultdict(lambda: [[], pd.DataFrame()])
    for index, row in csv_data_frame.iterrows():
        indexes, hash_data_frame = grouped_data_frames[row["hash"]]
        indexes.append(index)
        hash_data_frame = hash_data_frame.append(row)
        grouped_data_frames[row["hash"]] = indexes, hash_data_frame
        if min_wpm is None or row["wpm"] < min_wpm:
            min_wpm = row["wpm"]

    # grouped = sorted(gdf.items(), key=lambda x: x[1][1]['wpm'].mean(),
    #                  reverse=True)
    grouped = grouped_data_frames.items()

    _, axes = plt.subplots()
    colors = cycle(sns.color_palette())
    for row_hash, (indexes, hash_data_frame) in grouped:
        if row_hash in known_hashes:
            row_hash = known_hashes[row_hash]
        color = next(colors)
        axes.plot(indexes, hash_data_frame.wpm, color=color, lw=3, label=row_hash)
        # ax.fill_between(x, y, min_wpm, facecolor=color, label=h)
        trendline = np.poly1d(np.polyfit(indexes, hash_data_frame.wpm, 1))(indexes)
        axes.plot(indexes, trendline, "-", lw=4, color="white")
        axes.plot(indexes, trendline, "--", lw=2, color=color, label="trendline")

    axes.plot(csv_data_frame.accuracy, color="white", lw=4, alpha=0.5)
    axes.plot(csv_data_frame.accuracy, color=next(colors), lw=1.5, label="accuracy [%]", alpha=0.5)

    axes.set_title("typing speed per typing test")
    axes.set_xlabel("")
    axes.set_ylabel("typing speed [wpm]")
    axes.legend()

    # ticks = plt.yticks()[0]
    # plt.yticks(np.arange(0, ticks[-1], 10))
    plt.xticks(csv_data_frame.index, csv_data_frame.timestamp.dt.date, rotation=90)
    # label only every 50th tick
    for i, label in enumerate(axes.xaxis.get_ticklabels()):
        if i % math.ceil(len(csv_data_frame) / 50):
            label.set_visible(False)

    show_diagram()


def plot_char_speeds(char_speeds, size=10000, filter_func=lambda c: True):
    """Reads last `size` lines of `char_speeds` and groups them by characters.
    Removes lowest and highest 10% and boxplots the data.

    filter_func: function taking a `char` returning `True` if char should be
    plotted, `False` otherwise. By default plots all characters.
    """
    queue = deque(char_speeds, maxlen=size)
    csv_data_frame = pd.read_csv(
        StringIO("".join(queue)),
        header=None,
        names=["char", "duration", "wpm", "timestamp"],
    )

    gdf = filter(lambda t: filter_func(t[1]["char"].iloc[0]), csv_data_frame.groupby(["char"]))
    wpms = []
    chars = []
    means = []
    for char, csv_data_frame in gdf:
        if filter_func(char):
            q1 = csv_data_frame["wpm"].quantile(0.1)  # noqa
            q3 = csv_data_frame["wpm"].quantile(0.9)  # noqa
            wpm = csv_data_frame.query("@q1 <= wpm <= @q3")["wpm"]
            chars.append(char)
            wpms.append(wpm)
            means.append(wpm.mean())

    assert chars, "Not enough data"
    _, axes = plt.subplots()

    axes.boxplot(wpms, labels=chars)
    mean = round(sum(means) / len(means))
    axes.axhline(y=mean, color="r", linestyle="-", label=f"mean {mean} wpm")

    axes.set_title(f"typing speed per character of last {size} characters")
    axes.set_xlabel("")
    axes.set_ylabel("typing speed [wpm]")
    axes.legend()

    ticks = plt.yticks()[0]
    plt.yticks(np.arange(0, ticks[-1], 10))

    show_diagram()


def plot_n_best_word_speeds(word_speeds, n, filter_func=lambda w: True):
    """Loads all words from `word_speeds` and groups them by word."""
    half = n // 2
    df = pd.read_csv(
        word_speeds, header=None, names=["word", "duration", "wpm", "timestamp"]
    )

    gdf = list(filter(lambda t: filter_func(t[0]), df.groupby(["word"])))

    with open("least_typed_words", "w") as f:
        words_by_freq = list(zip(*sorted(gdf, key=lambda t: len(t[1]))))[0]
        f.write(" ".join(words_by_freq))

    gdf = sorted(gdf, key=lambda x: x[1]["wpm"].median())

    with open("worst_words", "w") as f:
        words_by_median = list(zip(*gdf))[0]
        f.write(" ".join(words_by_median))

    first_half = deque(maxlen=half)
    second_half = deque(maxlen=half)
    for word, df in gdf:
        if len(first_half) < first_half.maxlen:
            first_half.append((word, df["wpm"], df["wpm"].mean()))
        else:
            second_half.append((word, df["wpm"], df["wpm"].mean()))

    words, wpms, means = zip(*list(first_half) + list(second_half))
    mean = round(sum(means) / len(means))

    assert words, "Not enough data"

    _, ax = plt.subplots()

    ax.boxplot(wpms, labels=words)
    ax.axhline(y=mean, color="r", linestyle="-", label=f"mean {mean} wpm")

    ax.set_title(f"worst and best {half} words")
    ax.set_xlabel("")
    ax.set_yscale("linear")
    ax.set_ylabel("typing speed [wpm]")
    ax.legend()

    ticks = plt.yticks()[0]
    plt.yticks(np.arange(ticks[0], ticks[-1], 10))
    plt.xticks(rotation=90)

    show_diagram()


def plot_word_wpm_distribution(word_speeds, filter_func=lambda c: True):
    """Plots a distribution over average speeds of unique words."""
    df = pd.read_csv(
        word_speeds, header=None, names=["word", "duration", "wpm", "timestamp"]
    )

    gdf = list(filter(lambda t: filter_func(t[0]), df.groupby(["word"])))
    wpms = [df["wpm"].median() for word, df in gdf]

    ax = sns.histplot(wpms, kde=True, stat="probability")
    ax.set_title("percentage of words typed at a certain speed")
    ax.set_xlabel("typing speed in wpm")
    ax.set_ylabel("percentage of words")
    show_diagram()


def plot_mistypes_distribution(mistyped):
    """Plots a pie chart representing the shares of numbers of mistakes in
    mistyped words.
    """
    df = pd.read_csv(mistyped, header=None, names=["word", "mistype", "timestamp"])

    mistakes = defaultdict(int)
    words, mistypes = df["word"], df["mistype"]
    for word, mistype in zip(words, mistypes):
        if abs(len(word) - len(mistype)) < 10:
            distance = damerau_levenshtein_distance(word, mistype)
            if distance >= max(len(word), len(mistype)):
                # wrong word has been typed
                continue
            if distance > 3 and word.startswith(mistype):
                # word might be formed of multiple words
                # if mistype in dictionary:
                continue

            mistakes[distance] += 1

    _, ax = plt.subplots()
    labels, sizes = zip(*sorted(mistakes.items()))
    explode = [0] + [0.2] * (len(mistakes) - 1)
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", explode=explode)
    # ax = sns.histplot(mistakes, stat='probability')
    ax.set_title("number of mistakes made when typing a word")
    show_diagram()


def parse_args():
    """Parses `sys.argv` and returns a dictionary suitable for `main`."""
    parser = ArgumentParser(epilog=doc, formatter_class=RawTextHelpFormatter)

    default = "(default: %(default)s)"
    basedir = os.path.dirname(__file__)
    resultsdir = "results"
    parser.add_argument(
        "graphs",
        type=str,
        nargs="*",
        default=["wpm"],
        help="graphs to plot: wpm char word dist mistypes\n" + default,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=FileType("r"),
        default=f"{basedir}/{resultsdir}/results.csv",
        help="file to store results in\n" + default,
    )
    parser.add_argument(
        "-m",
        "--mistyped",
        type=FileType("r"),
        default=f"{basedir}/{resultsdir}/mistyped_words.csv",
        help="file to store mistyped words in\n" + default,
    )
    parser.add_argument(
        "-c",
        "--char_speeds",
        type=FileType("r"),
        default=f"{basedir}/{resultsdir}/char_speeds.csv",
        help="file to store character speeds in\n" + default,
    )
    parser.add_argument(
        "-w",
        "--word_speeds",
        type=FileType("r"),
        default=f"{basedir}/{resultsdir}/word_speeds.csv",
        help="file to store word speeds in\n" + default,
    )

    return dict(parser.parse_args()._get_kwargs())


if __name__ == "__main__":
    run()
