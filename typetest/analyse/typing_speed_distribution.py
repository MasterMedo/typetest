import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from typetest.utils import validate_input_file_path


@validate_input_file_path
def plot(input_file, filter_func=lambda c: True):
    """Plots a distribution over average speeds of unique words."""
    data_frame = pd.read_csv(
        input_file,
        header=None,
        names=["word", "duration", "wpm", "timestamp"],
    )

    grouped_data_frames = list(
        filter(lambda t: filter_func(t[0]), data_frame.groupby(["word"]))
    )
    typing_speeds_in_wpm = [
        data_frame["wpm"].median() for word, data_frame in grouped_data_frames
    ]

    ax = sns.histplot(typing_speeds_in_wpm, kde=True, stat="probability")
    ax.set_title("percentage of words typed at a certain speed")
    ax.set_xlabel("typing speed [words per minute]")
    ax.set_ylabel("percentage of words")
    plt.show()
