"""Various utility functions."""
from functools import wraps
from os.path import dirname, isfile


def damerau_levenshtein_distance(word_1: str, word_2: str) -> int:
    """Calculates the distance between two words."""
    inf = len(word_1) + len(word_2)
    table = [
        [inf for _ in range(len(word_1) + 2)] for _ in range(len(word_2) + 2)
    ]

    for i in range(1, len(word_1) + 2):
        table[1][i] = i - 1
    for i in range(1, len(word_2) + 2):
        table[i][1] = i - 1

    last_encountered_cols = {}
    for col, char_1 in enumerate(word_1, 2):
        last_row = 0
        for row, char_2 in enumerate(word_2, 2):
            last_encountered_col = last_encountered_cols.get(char_2, 0)

            addition = table[row - 1][col] + 1
            deletion = table[row][col - 1] + 1
            substitution = table[row - 1][col - 1] + (
                0 if char_1 == char_2 else 1
            )

            transposition = (
                table[last_row - 1][last_encountered_col - 1]
                + (col - last_encountered_col - 1)
                + (row - last_row - 1)
                + 1
            )

            table[row][col] = min(
                addition, deletion, substitution, transposition
            )

            if char_1 == char_2:
                last_row = row
        last_encountered_cols[char_1] = col

    return table[len(word_2) + 1][len(word_1) + 1]


def check_files(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        basedir = dirname(__file__)
        resultsdir = "results"

        parser = func()

        # print(parser)
        files_missing = []

        graphs = {  # Type of graph: (arg_name, default_path)
            "wpm": ("output", f"{basedir}/{resultsdir}/results.csv"),
            "char": ("char_speeds", f"{basedir}/{resultsdir}/char_speeds.csv"),
            "word": ("word_speeds", f"{basedir}/{resultsdir}/word_speeds.csv"),
            "dist": ("word_speeds", f"{basedir}/{resultsdir}/word_speeds.csv"),
            "mistypes": (
                "mistyped",
                f"{basedir}/{resultsdir}/mistyped_words.csv",
            ),
        }

        for graph in graphs:
            if graph == parser["graphs"][0]:
                if parser[graphs[graph][0]]:
                    continue
                if isfile(graphs[graph][1]):
                    parser[graphs[graph][0]] = open(graphs[graph][1])
                else:
                    files_missing.append(graphs[graph][1])

        if files_missing:
            print(
                f"Results file(s) {str(files_missing)[1:-1]} not "
                + "found. Please do more typing tests with 'typetest' "
                + "before analysing the results"
            )
            exit(1)

        return parser

    return wrapper
