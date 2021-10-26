import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from io import StringIO
from collections import deque

from typetest.utils import validate_input_file_path


@validate_input_file_path
def plot(input_file, size=10000, filter_func=lambda c: True):
    """Reads last `size` lines of `input_file` and groups them by characters.
    Removes lowest and highest 10% and boxplots the data.

    filter_func: function taking a `char` returning `True` if char should be
    plotted, `False` otherwise. By default plots all characters.
    """
    with open(input_file) as f:
        q = deque(f, maxlen=size)

    data_frame = pd.read_csv(
        StringIO("".join(q)),
        header=None,
        names=["char", "duration", "wpm", "timestamp"],
    )

    grouped_data_frames = filter(
        lambda t: filter_func(t[1]["char"].iloc[0]),
        data_frame.groupby("char"),
    )

    typing_speeds_in_wpm = []
    chars = []
    means = []
    for char, df in grouped_data_frames:
        if filter_func(char):
            q1 = df["wpm"].quantile(0.1)  # noqa
            q3 = df["wpm"].quantile(0.9)  # noqa
            typing_speed_in_wpm = df.query("@q1 <= wpm <= @q3")["wpm"]
            chars.append(char)
            typing_speeds_in_wpm.append(typing_speed_in_wpm)
            mean = typing_speed_in_wpm.mean()
            means.append(mean if mean > 0 else 0)

    fig, ax = plt.subplots()

    ax.boxplot(typing_speeds_in_wpm, labels=chars)
    mean = round(sum(means) / len(means))
    ax.axhline(y=mean, color="r", linestyle="-", label=f"mean {mean} wpm")

    ax.set_title(f"typing speed per character of last {size} characters")
    ax.set_xlabel("characters")
    ax.set_ylabel("typing speed [wpm]")
    ax.legend()

    ticks = plt.yticks()[0]
    plt.yticks(np.arange(0, ticks[-1], 10))

    plt.show()
