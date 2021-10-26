import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from collections import deque

from typetest.utils import validate_input_file_path


@validate_input_file_path
def plot(input_file, n, filter_func=lambda w: True):
    """Loads all words from `input_file` and groups them by word."""

    data_frame = pd.read_csv(
        input_file,
        header=None,
        names=["word", "duration", "wpm", "timestamp"],
    )

    grouped_data_frames = list(
        filter(lambda t: filter_func(t[0]), data_frame.groupby("word"))
    )
    grouped_data_frames = sorted(
        grouped_data_frames, key=lambda x: x[1]["wpm"].median()
    )

    first_half = deque(maxlen=n // 2)
    second_half = deque(maxlen=n // 2)
    for word, df in grouped_data_frames:
        if len(first_half) < first_half.maxlen:
            first_half.append((word, df["wpm"], df["wpm"].mean()))
        else:
            second_half.append((word, df["wpm"], df["wpm"].mean()))

    words, typing_speeds_in_wpm, means = zip(
        *list(first_half) + list(second_half)
    )
    mean = round(sum(means) / len(means))

    fig, ax = plt.subplots()

    ax.boxplot(typing_speeds_in_wpm, labels=words)
    ax.axhline(y=mean, color="r", linestyle="-", label=f"mean {mean} wpm")

    ax.set_title(f"worst and best {n // 2} words")
    ax.set_xlabel("")
    ax.set_yscale("linear")
    ax.set_ylabel("typing speed [wpm]")
    ax.legend()

    ticks = plt.yticks()[0]
    plt.yticks(np.arange(ticks[0], ticks[-1], 10))
    plt.xticks(rotation=90)

    plt.show()
