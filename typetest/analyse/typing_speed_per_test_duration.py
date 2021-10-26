import math
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from itertools import cycle
from collections import defaultdict

from typetest.utils import validate_input_file_path


@validate_input_file_path
def plot(output):
    """Reads `output` and plots typing speeds (wpm)
    categorized by buckets of test duration.

    Bucket labels and their time intervals:
    short: below 20 seconds
    medium: 20 to 60 seconds
    long: 60 seconds to 10 minutes
    extra long: >10 minutes
    """
    data_frame = pd.read_csv(
        output,
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

    data_frame.timestamp = pd.to_datetime(data_frame.timestamp)

    gdf = defaultdict(lambda: [[], pd.DataFrame()])
    for index, row in data_frame.iterrows():
        actual_duration = row["actual_duration"]
        key = None
        if actual_duration < 20:
            key = "short (< 20s)"
        elif actual_duration >= 20 and actual_duration < 60:
            key = "medium (> 20s and < 60s)"
        elif actual_duration >= 60 and actual_duration < 600:
            key = "long (> 60s and < 600s)"
        else:
            key = "extra long (> 600s)"
        indexes, hdf = gdf[key]
        indexes.append(index)
        hdf = hdf.append(row)
        gdf[key] = indexes, hdf

    grouped = gdf.items()
    fig, ax = plt.subplots()
    colors = cycle(sns.color_palette())
    for key, (indexes, hdf) in grouped:
        x = indexes
        y = hdf.wpm
        color = next(colors)
        ax.plot(x, y, color=color, lw=3, label=key)
        if len(x) > 1:
            trendline = np.poly1d(np.polyfit(x, y, 1))(x)
            ax.plot(x, trendline, "-", lw=4, color="white")
            ax.plot(x, trendline, "--", lw=2, label="trendline", color=color)

    # plot accuracy
    ax.plot(data_frame.accuracy, color="white", lw=4, alpha=0.5)
    ax.plot(
        data_frame.accuracy,
        color=next(colors),
        lw=1.5,
        label="accuracy [%]",
        alpha=0.5,
    )

    ax.set_title("typing speed categorized by test duration")
    ax.set_xlabel("")
    ax.set_ylabel("typing speed [wpm]")
    ax.legend()

    # add ticks
    plt.xticks(data_frame.index, data_frame.timestamp.dt.date, rotation=90)
    for i, label in enumerate(ax.xaxis.get_ticklabels()):
        if i % math.ceil(len(data_frame) / 50):
            label.set_visible(False)

    plt.show()
