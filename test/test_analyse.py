import unittest
from unittest.mock import MagicMock

import pandas as pd
import matplotlib.pyplot as plt

from typetest.analyse import (
    plot_word_wpm_distribution,
    plot_wpm,
    plot_char_speeds,
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
        plot_wpm("")
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
        plot_wpm("")
        pd.read_csv.assert_called_once()
        plt.show.assert_not_called()

    def test_plot_char_speeds_not_enough_data(self):
        pd.read_csv = MagicMock(
            return_value=pd.DataFrame(
                columns=["char", "duration", "wpm", "timestamp"],
            )
        )
        plt.show = MagicMock()
        self.assertRaises(AssertionError, plot_char_speeds, "")
        pd.read_csv.assert_called_once()
        plt.show.assert_not_called()

    def test_plot_char_speeds(self):
        pd.read_csv = MagicMock(
            return_value=pd.DataFrame(
                columns=["char", "duration", "wpm", "timestamp"],
                data=[["a", 1, 1000, "2021-10-21T21:21+13:00"]],
            )
        )
        plt.show = MagicMock()
        plot_char_speeds("")
        pd.read_csv.assert_called_once()
        plt.show.assert_called_once()

    def test_plot_word_wpm_distribution(self):
        pd.read_csv = MagicMock(
            return_value=pd.DataFrame(
                columns=["word", "duration", "wpm", "timestamp"]
            )
        )
        plt.show = MagicMock()
        plot_word_wpm_distribution("")
        pd.read_csv.assert_called_once()
        plt.show.assert_called_once()
