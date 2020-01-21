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

from re                     import split
from time                   import time
from typing                 import List
from itertools              import chain, zip_longest, takewhile, dropwhile
from typetest.keystrokes    import keystroke

__all__ = ['accuracy', 'cpm', 'dph', 'TypeTestDone', 'TypeTest', 'wpm']

_whitespaces = '\t\n\x0b\x0c\r '


class TypeTestDone(Exception):
    """Exception raised when there are no more words or characters left
    in the typing 'test' for the 'text' to be compared to, or when the
    time runs out if it's a timed test.

    """

    def __init__(self, message):
        super().__init__(message)


class TypeTest:
    """Object used to calculate statistics from a typing test.

    Simple usage:
        from util import TypeTest
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
            delimiters: str=' \n',
            word_by_word: bool=False,
            ) -> None:

        self.word_by_word = word_by_word
        self.delimiters = delimiters
        self.test = test
        self.text = ''

        self.text_raw = ''

        self.test_words = split_by_delimiters(test, delimiters)
        self.text_words = []
        self.text_times = []

        self.text = ''

        self.whitespaces = 0
        self.backspaces  = 0
        self.corrections = 0

        self.text_char_i = 0
        self.test_char_i = 0

        self.tmp_correct_keystrokes = 0
        self.tmp_speed_wpm          = 0
        self.duration               = 0

        self.text_word = ''
        self.test_word = ''.join(takewhile(lambda x: x not in delimiters, self.test))
        self.last_text_word = ''
        self.last_test_word = ''

## ---------------------- Public interface ----------------------------
    def addch(self, char: str) -> bool:
        """Only text, no words
        """

        self.text_times.append(time())
        self.triggered_new_word = False
        self.triggered_new_char = False
        self.triggered_deletion = False

        self.text_raw += char
        self.duration  = self.text_times[-1] - self.text_times[0]

        if char == '\b':
            if self.text and (not self.word_by_word or self.text[-1] not in self.delimiters):
                if self.text_word == self.test_word[:len(self.text_word)]:
                    self.tmp_correct_keystrokes -= keystroke(self.text[-1])
                self.triggered_deletion = True
                self.text_char_i -= 1
                self.text = self.text[:-1]
                self.text_word = self.text_word[:-1]

        elif self.word_by_word and char in self.delimiters:
            if not self.text or (self.text and self.text[-1] in self.delimiters):
                pass
            elif self.text and self.text[-1] not in self.delimiters:
                self.last_text_word = self.text_word
                self.last_test_word = self.test_word
                self.text_word = ''
                self.test_word = ''
                self.text += char
                self.triggered_new_word = True
                if self.last_text_word == self.last_test_word[:len(self.last_text_word)] \
                        and self.last_text_word != self.last_test_word:
                            self.tmp_correct_keystrokes -= sum(map(keystroke, self.last_text_word))
                for i in range(self.test_char_i, len(self.test)):
                    if self.test[self.test_char_i] in self.delimiters:
                        self.test_char_i += 1
                        for c in self.test[self.test_char_i:]:
                            if c in self.delimiters:
                                break
                            self.test_word += c
                        break
                    self.test_char_i += 1
                if self.test_char_i >= len(self.test):
                    raise TypeTestDone('done')

        else:
            self.text += char
            self.text_word += char
            self.text_char_i += 1
            self.triggered_new_char = True
            if char not in self.delimiters:
                if self.text_word == self.test_word[:len(self.text_word)]:
                    self.tmp_correct_keystrokes += keystroke(char)

        self.tmp_speed_wpm = wpm(self.tmp_correct_keystrokes, self.duration)

    def submit(self) -> None:
        """Submit 'text' from the user input.

        Counts 'char' and 'keystroke' fields.
        Character and keystroke counting depends on 'mode'.

        """

        self.text_words = split_by_delimiters(self.text, self.delimiters)

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

        self.accuracy = accuracy(sum(len(i) for i in self.test_words[:len(self.text_words)]),
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
            "true_speed":                   self.true_speed_wpm,
        }

## --------------------- Convinience interface -------------------------

def accuracy(total_keystrokes_required: int,
        correct_keystrokes: int,
        corrections: int) -> float:
    """
    """
    total_keystrokes = total_keystrokes_required + corrections
    if total_keystrokes == 0:
        return 0

    return correct_keystrokes/total_keystrokes*100

def cpm(keystrokes: int, duration: float) -> float:
    """Calculate typing speed in cpm (characters per minute).

    duration - in seconds

    """
    if duration == 0:
        return 0

    return keystrokes/duration*60

def dph(keystrokes: int, duration: float) -> float:
    """Calculate typing speed in dph (depressions per hour).

    duration - in seconds

    """
    if duration == 0:
        return 0

    return keystrokes/duration*3600

def wpm(keystrokes: int, duration: float) -> float:
    """Calculate typing speed in wpm (words per minute).

    A word is considered 5 keystrokes.

    duration - how long the test took in seconds
    """
    if duration == 0:
        return 0

    words = keystrokes/5
    return words/duration*60

def split_by_delimiters(text: str, delimiters: str=' \n') -> List[str]:
    """Split 'text' by 'delimiters'.
    """

    return list(filter(None, split('['+delimiters+']+', text)))
