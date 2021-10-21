import unittest

from typetest.utils import damerau_levenshtein_distance


class TestUtils(unittest.TestCase):
    def test_damerau_levenshtein_distance(self):
        self.assertEqual(damerau_levenshtein_distance("aa", "ab"), 1)
        self.assertEqual(damerau_levenshtein_distance("aa", "abc"), 2)
        self.assertEqual(damerau_levenshtein_distance("az", "abc"), 2)
        self.assertEqual(damerau_levenshtein_distance("Aa", "abc"), 3)
        self.assertEqual(damerau_levenshtein_distance("abc", "abc"), 0)
        self.assertEqual(damerau_levenshtein_distance("$@", "abc"), 3)
        self.assertEqual(damerau_levenshtein_distance("cba", "abc"), 2)
        self.assertEqual(damerau_levenshtein_distance("abacus", "abc"), 3)
