import math
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from itertools import cycle
from matplotlib.ticker import MaxNLocator, FuncFormatter

from typetest.utils import validate_input_file_path

known_hashes = {
    "da4846a3c2a8469dd77c921ab0b0bcd506b6e9f3": "300 most common english "
    + "words",
    "275eb003c4fba77d7e61893c3d9fa869822e06c8": "1000 most common english "
    + "words (no double letters)",
}


@validate_input_file_path
def plot(input_file_path):
    """Reads file at `input_file_path` and plots typing speeds for each
    test taken. Adds a trendline (linear approximation of the curve).

    Tests are separated on the x-axis uniformly apart, regardless of the
    time passed between two adjacent tests (it could be a day, or a year).
    """
    data_frame = pd.read_csv(
        input_file_path,
        header=None,
        names=[
            "timestamp",
            "wpm",
            "accuracy",
            "actual_duration",
            "duration",
            "hash",
        ],
    )

    data_frame.timestamp = pd.to_datetime(data_frame.timestamp).dt.date
    # data_frame = data_frame.set_index(data_frame.timestamp)

    fig, ax = plt.subplots()
    colors = cycle(sns.color_palette())

    # accuracy curve outline
    ax.plot(data_frame.accuracy, color="white", lw=4, alpha=0.5)
    # accuracy curve
    ax.plot(
        data_frame.accuracy,
        color=next(colors),
        lw=1.5,
        label="accuracy [%]",
        alpha=0.5,
    )

    for test_hash, grouped_data_frame in data_frame.groupby("hash"):
        x = grouped_data_frame.index.values.tolist()
        y = grouped_data_frame.wpm
        color = next(colors)
        ax.plot(
            x,
            y,
            color=color,
            lw=3,
            label=known_hashes.get(
                test_hash, "unknown test (add hash to config)"
            ),
        )
        if len(grouped_data_frame) > 1:
            trendline = np.poly1d(np.polyfit(x, y, 1))(x)
            # trendline outline
            ax.plot(x, trendline, "-", lw=4, color="white")
            # trendline
            ax.plot(x, trendline, "--", lw=2, color=color, label="trendline")

    ax.set_title("typing speed per typing test")
    ax.set_xlabel("typing test index")
    ax.set_ylabel("typing speed [wpm]")

    ax.xaxis.set_major_locator(MaxNLocator(20))
    ax.xaxis.set_major_formatter(
        FuncFormatter(
            lambda index, _: data_frame.iloc[int(index) - 1].timestamp
            if int(index) < len(data_frame)
            else ""
        )
    )
    plt.xticks(rotation=90)

    ax.legend(loc="upper left")

    plt.show()
