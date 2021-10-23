import unittest
from unittest.mock import MagicMock

import pandas as pd
import matplotlib.pyplot as plt

from typetest.analyse import (
    plot_word_wpm_distribution,
    plot_wpm,
    plot_char_speeds,
    plot_n_best_word_speeds,
    plot_mistypes_distribution,
    wpm_data,
    wpm_logic,
)


class TestAnalyse(unittest.TestCase):
    def test_plot_wpm(self):
        pd.read_csv = self._wpm_df_mock_helper(
            [
                [
                    "2021-10-21t21:21+13:00",
                    1000,
                    100,
                    5,
                    5,
                    "ABCDA4846A3C2A8469DD77C921AB0B0BCD506B6E9F3",
                ],
                [
                    "2021-10-21t21:21+13:00",
                    1000,
                    100,
                    5,
                    5,
                    "ABCDA4846A3C2A8469DD77C921AB0B0BCD506B6E9F3",
                ],
            ],
        )
        plt.show = MagicMock()
        plot_wpm("")
        pd.read_csv.assert_called_once()
        plt.show.assert_called_once()

    def test_plot_wpm_returns_when_not_enough_data(self):
        pd.read_csv = self._wpm_df_mock_helper()
        plt.show = MagicMock()
        plot_wpm("")
        pd.read_csv.assert_called_once()
        plt.show.assert_not_called()
        
    def test_wpm_data(self):
        pd.read_csv = self._wpm_df_mock_helper()
        plt.show = MagicMock()
        data = wpm_data("")
        pd.read_csv.assert_called_once()
        self.assertIsNone(data)

    def _wpm_df_mock_helper(self, df_data=[]):
        return MagicMock(
            return_value=pd.DataFrame(
                columns=[
                    "timestamp",
                    "wpm",
                    "accuracy",
                    "actual_duration",
                    "duration",
                    "hash",
                ],
                data=df_data,
            )
        )

    def test_wpm_logic_no_data(self):
        df = pd.DataFrame(
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
        result = wpm_logic(df)
        self.assertIsNotNone(result)

    def test_wpm_logic(self):
        df = pd.DataFrame(
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
                    "2021-10-21t21:21+13:00",
                    1000,
                    100,
                    5,
                    5,
                    "ABCDA4846A3C2A8469DD77C921AB0B0BCD506B6E9F3",
                ],
                [
                    "2021-10-21t21:21+13:00",
                    1000,
                    100,
                    5,
                    5,
                    "ABCDA4846A3C2A8469DD77C921AB0B0BCD506B6E9F3",
                ],
            ],
        )
        result = wpm_logic(df)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(
            len(result["ABCDA4846A3C2A8469DD77C921AB0B0BCD506B6E9F3"]), 2
        )

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
        plot_n_best_word_speeds("", 2)
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
        plot_mistypes_distribution("")
        pd.read_csv.assert_called_once()
        plt.show.assert_called_once()
