import math
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from itertools import cycle
from collections import defaultdict
from matplotlib.ticker import MaxNLocator, FuncFormatter

from typetest.utils import validate_input_file_path


@validate_input_file_path
def plot(input_file_path):
    """Reads `input_file_path` and plots typing speeds (wpm)
    categorized by buckets of test duration.

    Bucket labels and their time intervals:
    short: below 20 seconds
    medium: 20 to 60 seconds
    long: 60 seconds to 10 minutes
    extra long: >10 minutes
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

    grouped_data_frames = data_frame.groupby(
        pd.cut(data_frame["actual_duration"], [0, 20, 60, 600])
    )

    fig, ax = plt.subplots()
    colors = cycle(sns.color_palette())
    ax.plot(data_frame.accuracy, color="white", lw=4, alpha=0.5)
    ax.plot(
        data_frame.accuracy,
        color=next(colors),
        lw=1.5,
        label="accuracy [%]",
        alpha=0.5,
    )

    for duration, grouped_data_frame in grouped_data_frames:
        x = grouped_data_frame.index.values.tolist()
        y = grouped_data_frame.wpm
        color = next(colors)
        ax.plot(x, y, color=color, lw=3, label=duration)
        if len(x) > 1:
            trendline = np.poly1d(np.polyfit(x, y, 1))(x)
            ax.plot(x, trendline, "-", lw=4, color="white")
            ax.plot(x, trendline, "--", lw=2, label="trendline", color=color)

    ax.set_title("typing speed categorized by test duration")
    ax.set_xlabel("date of taking the particular test")
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

    ax.legend()
    plt.show()
