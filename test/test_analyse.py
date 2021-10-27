import unittest
from unittest.mock import MagicMock

import pandas as pd
import matplotlib.pyplot as plt

from typetest.analyse import (
    mistyped_words_pie_chart,
    typing_speed_distribution,
    typing_speed_of_n_best_words,
    typing_speed_per_char,
    typing_speed_per_test,
)


class TestAnalyse(unittest.TestCase):
    def test_plot_wpm(self):
        pd.read_csv = MagicMock(
            return_value=pd.DataFrame(
                columns=[
                    "timestamp",
                    "wpm",
                    "accuracy",
                    "actual_duration",
                    "duration",
                    "hash",
                ],
                data=[
                    [
                        "2021-10-21T21:21+13:00",
                        1000,
                        100,
                        5,
                        5,
                        "abcda4846a3c2a8469dd77c921ab0b0bcd506b6e9f3",
                    ],
                    [
                        "2021-10-21T21:21+13:00",
                        1000,
                        100,
                        5,
                        5,
                        "abcda4846a3c2a8469dd77c921ab0b0bcd506b6e9f3",
                    ],
                ],
            )
        )
        plt.show = MagicMock()
        typing_speed_per_test.plot("./test/placeholder")
        pd.read_csv.assert_called_once()
        plt.show.assert_called_once()

    def test_plot_wpm_returns_when_not_enough_data(self):
        pd.read_csv = MagicMock(
            return_value=pd.DataFrame(
                columns=[
                    "timestamp",
                    "wpm",
                    "accuracy",
                    "actual_duration",
                    "duration",
                    "hash",
                ],
                data=[],
            )
        )
        plt.show = MagicMock()
        typing_speed_per_test.plot("./test/placeholder")
        pd.read_csv.assert_called_once()
        plt.show.assert_called_once()

    def test_plot_char_speeds(self):
        pd.read_csv = MagicMock(
            return_value=pd.DataFrame(
                columns=["char", "duration", "wpm", "timestamp"],
                data=[["a", 1, 1000, "2021-10-21T21:21+13:00"]],
            )
        )
        plt.show = MagicMock()
        typing_speed_per_char.plot("./test/placeholder")
        pd.read_csv.assert_called_once()
        plt.show.assert_called_once()

    def test_plot_n_best_word_speeds(self):
        pd.read_csv = MagicMock(
            return_value=pd.DataFrame(
                columns=["word", "duration", "wpm", "timestamp"],
                data=[
                    ["turtle", 4, 1001, "2021-10-21T21:21+13:00"],
                    ["pigeon", 5, 999, "2021-10-21T21:21+13:00"],
                    ["albatross", 6, 1000, "2021-10-21T21:21+13:00"],
                    ["giraffe", 6, 1000, "2021-10-21T21:21+13:00"],
                    ["elephant", 6, 1000, "2021-10-21T21:21+13:00"],
                ],
            )
        )
        plt.show = MagicMock()
        typing_speed_of_n_best_words.plot("./test/placeholder", 2)
        pd.read_csv.assert_called_once()
        plt.show.assert_called_once()

    def test_plot_word_wpm_distribution(self):
        pd.read_csv = MagicMock(
            return_value=pd.DataFrame(
                columns=["word", "duration", "wpm", "timestamp"]
            )
        )
        plt.show = MagicMock()
        typing_speed_distribution.plot("test/placeholder")
        pd.read_csv.assert_called_once()
        plt.show.assert_called_once()

    def test_plot_mistypes_distribution(self):
        pd.read_csv = MagicMock(
            return_value=pd.DataFrame(
                columns=["word", "mistype", "timestamp"],
                data=[
                    ["turtle", "trutle", "2021-10-21T21:21+13:00"],
                    ["pigeon", "pgeone", "2021-10-21T21:21+13:00"],
                    ["albatross", "abbatros", "2021-10-21T21:21+13:00"],
                    ["giraffe", "gragfe", "2021-10-21T21:21+13:00"],
                    ["elephant", "elelgpaglea", "2021-10-21T21:21+13:00"],
                ],
            )
        )
        plt.show = MagicMock()
        mistyped_words_pie_chart.plot("./test/placeholder")
        pd.read_csv.assert_called_once()
        plt.show.assert_called_once()
