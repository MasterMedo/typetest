import unittest
from unittest.mock import MagicMock

import pandas as pd
import matplotlib.pyplot as plt

from typetest.analyse import plot_word_wpm_distribution


class TestAnalyse(unittest.TestCase):
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
