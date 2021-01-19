def damerau_levenshtein_distance(word1: str, word2: str) -> int:
    inf = len(word1) + len(word2)
    table = [[inf for _ in range(len(word1) + 2)]
             for _ in range(len(word2) + 2)]

    for i in range(1, len(word1) + 2):
        table[1][i] = i - 1
    for i in range(1, len(word2) + 2):
        table[i][1] = i - 1

    da = {}
    for col, c1 in enumerate(word1, 2):
        last_row = 0
        for row, c2 in enumerate(word2, 2):
            last_col = da.get(c2, 0)

            addition = table[row-1][col] + 1
            deletion = table[row][col-1] + 1
            substitution = table[row-1][col-1] + (0 if c1 == c2 else 1)

            transposition = table[last_row-1][last_col-1]\
                + (col - last_col - 1)\
                + (row - last_row - 1)\
                + 1

            table[row][col] = min(
                addition,
                deletion,
                substitution,
                transposition
            )

            if c1 == c2:
                last_row = row
        da[c1] = col

    return table[len(word2)+1][len(word1)+1]
