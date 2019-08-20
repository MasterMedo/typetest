"""Typing test essentials.

    through a class
    ---------------
        provide or generate a typing test
        submit text
        calculate typing speed, accuracy

    through individual methods
    --------------------------
        conduct calculations on already collected data

"""

# Copyright (C) 2019 Mislav Vuletić

from re         import split
from typing     import List
from itertools  import chain, zip_longest
from cli.keystrokes import keystroke

__all__ = ['accuracy', 'cpm', 'dph', 'TypeTestError', 'gross_speed',
        'net_speed', 'true_gross_speed', 'true_wpm', 'TypingTest', 'wpm']

_whitespaces = '\t\n\x0b\x0c\r '

class TypeTestError(Exception):
    """Error raised when there are no more words or characters left
    in the typing 'test' for the 'text' to be compared to.

    """

    def __init__(self, message):
        super().__init__(message)


class TypingTest:
    """Object used to calculate statistics from a typing test.

    Simple usage:
        from keytype import TypingTest
        import time

        start = time.time()
        test = TypingTest()
        for word in test.test_words:
            if time.time() > start + test.duration:
                break
            test.submit(input(f'{word}\n'))

        print(f'{test.wpm():.{2}f} wpm')
    """

    def __init__(self,
            test: str,
            delimiters: str=' \n'
            ) -> None:

        self.delimiters = delimiters
        self.test = test

        self.test_words = self._split(test)
        self.test_char_i = 0
        self.test_word_i = 0
        self.whitespaces = 0
        self.backspaces  = 0
        self.corrections = 0

        self.text_raw = ''
        self.text     = ''
        self.text_words    = []
        self.correct_words = []

## ---------------------- Private methods -----------------------------

    def _split(self, text: str) -> List[str]:
        """Split 'text' by 'delimiters'.
        """

        return list(filter(None, split('['+self.delimiters+']+', text)))

## ------------------------- Public interface -------------------------

    def addch(self, char: str) -> bool:
        """Submit a character from the user input.

        Compares the 'char' with the 'test'['test_char_i'].
        Returns elapsed time since last added character
        """

        self.text_raw += char

        if char == '\b':
            self.backspaces += 1
            if self.text:
                self.text = self.text[:-1]
            return False

        if self.test_char_i >= len(self.test):
            raise TypeTestError('Test length exceeded!')

        self.test_char_i += 1
        self.text        += char

        return self.text[-1] == self.test[self.test_char_i-1]

    def addword(self, word: str) -> None:
        """Submit 'text' from the user input by word.

        Separates text by word but validates based on 'mode'.

        """

        self.text_raw += word
        self.text += word

        if self.test_word_i >= len(self.test_words):
            raise TypeTestError('Test length exceeded!')

        if any(d in word for d in self.delimiters):
            raise ValueError('Words have to be submitted without delimiters.')

        self.text_words.append(word)
        self.test_word_i += 1

        return self.text_words[-1] == self.test_words[self.test_word_i-1]

    def submit(self, duration: float) -> None:
        """Submit 'text' from the user input.

        Counts 'char' and 'keystroke' fields.
        Character and keystroke counting depends on 'mode'.

        """

        self.duration = duration

        if not self.text_words:
            self.text_words = self._split(self.text_words)

        zipped_words = list(zip(self.text_words, self.test_words))
        zipped_chars = list(chain(*[zip_longest(*cc) for cc in zipped_words]))

        self.correct_words   = [i for i, j in zipped_words if i == j]
        self.incorrect_words = [i for i, j in zipped_words if i != j]
        self.invalid_words   = self.text_words[len(self.test_words)-1:]

        self.correct_chars   = [i for i, j in zipped_chars if i == j]
        self.incorrect_chars = [i for i, j in zipped_chars if i != j and i]
        self.invalid_chars   = [i for i, j in zipped_chars if not j and i] + \
                               list(chain(*self.invalid_words))

        self.correct_words_chars        = list(chain(*self.correct_words))
        self.incorrect_words_chars      = list(chain(*self.incorrect_words))
        self.invalid_words_chars        = list(chain(*self.invalid_words))

        self.correct_words_keystrokes   = list(map(keystroke, self.correct_words_chars))
        self.incorrect_words_keystrokes = list(map(keystroke, self.incorrect_words_chars))
        self.invalid_words_keystrokes   = list(map(keystroke, self.invalid_words_chars))

        self.correct_chars_keystrokes   = list(map(keystroke, self.correct_chars))
        self.incorrect_chars_keystrokes = list(map(keystroke, self.incorrect_chars))
        self.invalid_chars_keystrokes   = list(map(keystroke, self.invalid_chars))

        self.accuracy = accuracy(sum(len(i) for i in self.test_words[:self.test_word_i]),
                len(self.correct_words_chars),
                self.corrections)

        self.true_speed_wpm = wpm(len(self.correct_words)*5,          self.duration)
        self.true_speed_cpm = cpm(len(self.correct_words_chars),      self.duration)
        self.true_speed_dph = dph(len(self.correct_words_chars),      self.duration)
        self.speed_wpm      = wpm(sum(self.correct_words_keystrokes), self.duration)
        self.speed_cpm      = cpm(sum(self.correct_words_keystrokes), self.duration)
        self.speed_dph      = dph(sum(self.correct_words_keystrokes), self.duration)


        self.results = {
                "duration":                     self.duration,
                "correct_words":                self.correct_words,
                "incorrect_words":              self.incorrect_words,
                "invalid_words":                self.invalid_words,
                "correct_chars":                self.correct_chars,
                "incorrect_chars":              self.incorrect_chars,
                "invalid_chars":                self.invalid_chars,
                "correct_words_chars":          self.correct_words_chars,
                "incorrect_words_chars":        self.incorrect_words_chars,
                "invalid_words_chars":          self.invalid_words_chars,
                "correct_words_keystrokes":     self.correct_words_keystrokes,
                "incorrect_words_keystrokes":   self.incorrect_words_keystrokes,
                "invalid_words_keystrokes":     self.invalid_words_keystrokes,
                "correct_chars_keystrokes":     self.correct_chars_keystrokes,
                "incorrect_chars_keystrokes":   self.incorrect_chars_keystrokes,
                "invalid_chars_keystrokes":     self.invalid_chars_keystrokes,
                "accuracy":                     self.accuracy,
                "true_speed":                   self.true_speed_wpm
                }

## --------------------- Convinience interface -------------------------

def accuracy(total_keystrokes_required: int,
        correct_keystrokes: int,
        corrections: int) -> float:
    """
    """

    return correct_keystrokes/(total_keystrokes_required+corrections)*100

def cpm(keystrokes: int, duration: float) -> float:
    """Calculate typing speed in cpm (characters per minute).

    duration - in seconds

    """

    return keystrokes/duration*60

def dph(keystrokes: int, duration: float) -> float:
    """Calculate typing speed in dph (depressions per hour).

    duration - in seconds

    """

    return keystrokes/duration*3600

def wpm(keystrokes: int, duration: float) -> float:
    """Calculate typing speed in wpm (words per minute).

    A word is considered 5 keystrokes.

    duration - how long the test took in seconds
    """

    words = keystrokes/5
    return words/duration*60
