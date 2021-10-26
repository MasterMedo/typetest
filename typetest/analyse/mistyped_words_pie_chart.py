import pandas as pd
import matplotlib.pyplot as plt

from typetest.utils import (
    validate_input_file_path,
    damerau_levenshtein_distance,
)


@validate_input_file_path
def plot(input_file, filter_func=lambda c: True):
    """Plots a pie chart representing the shares of numbers of mistakes in
    mistyped words.
    """

    def distance(row):
        return damerau_levenshtein_distance(row.word, row["mistype"])

    def wrong_word_typed(row):
        return row["distance"] >= max(len(row["word"]), len(row["mistype"]))

    def word_skip(row):
        return row["distance"] > 2 and row["word"].startswith(row["mistype"])

    data_frame = pd.read_csv(
        input_file, header=None, names=["word", "mistype", "timestamp"]
    )

    data_frame["distance"] = data_frame.apply(distance, axis=1)
    data_frame["flag"] = data_frame.apply(
        lambda row: not word_skip(row) and not wrong_word_typed(row), axis=1
    )
    data_frame = data_frame[data_frame["flag"]]
    mistakes = data_frame["distance"].value_counts()
    mistakes = list(zip(mistakes.index.to_list(), mistakes.to_list()))

    fig, ax = plt.subplots()

    labels, sizes = zip(*sorted(mistakes))
    explode = [0] + [0.2] * (len(mistakes) - 1)
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", explode=explode)
    # ax = sns.histplot(mistakes, stat="probability")
    ax.set_title("number of mistakes made when typing a word")
    plt.show()
