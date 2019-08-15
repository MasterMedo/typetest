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
from time       import time
from enum       import Enum
from random     import shuffle
from typing     import List
from operator   import eq
from itertools  import chain, zip_longest

__all__ = ['accuracy', 'cpm', 'dph', 'EndOfTestError', 'generate_test',
        'gross_speed', 'keystroke', 'keystrokes', 'net_speed',
        'true_gross_speed', 'true_wpm', 'TypingTest', 'wpm']

_whitespaces = '\t\n\x0b\x0c\r '

# For language specific characters see 'keystrokes_file_path'.
_keystrokes = [
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890`-={}:"|<>?',  # count as 2 keystrokes
    '~!@#$%^&*()_+']                                    # count as 3 keystrokes

class EndOfTestError(Exception):
    """Error raised when there are no more words or characters left
    in the typing 'test' for the 'text' to be compared to.

    """

    def __init__(self, message):
        super().__init__(message)


class TypingTest:
    """Object used to calculate statistics from a typing test.

    You need to initialize 'test' in init or it will be auto-generated.

    You can add the 'text' character by character, in chuncks,
    or at once. Use the method 'submit', or submit the text through init.

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
        self.text_words         = []
        self.correct_words      = []

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
            raise EndOfTestError('Test length exceeded!')

        self.test_char_i += 1
        self.text        += char

        return self.text[-1] == self.test[self.test_char_i-1]

    def addword(self, word: str) -> None:
        """Submit 'text' from the user input by word.

        Separates text by word but validates based on 'mode'.

        """

        self.text_raw += word

        if self.test_word_i >= len(self.test_words):
            raise EndOfTestError('Test length exceeded!')

        if any(d in word for d in self.delimiters):
            raise ValueError('Words have to be submitted without delimiters.')

        self.text_words.append(word)
        self.test_word_i += 1

        return self.text_words[-1] == self.test_words[self.test_word_i-1]

    def gross_speed(self) -> float:
        """Calculate the gross typing speed in wpm (words per minute).

        Gross typing speed takes both correctly and incorrectly
        typed keystrokes as well as invalid keystrokes into account.

        """

        return wpm(sum(map(keystroke, self.text_raw)), self.duration)

    def net_speed(self) -> float:
        """Calculate the net typing speed in wpm (words per minute).

        Net typing speed only takes correctly typed keystrokes into account.

        """

        return wpm(sum(self.correct_words_keystrokes), self.duration)

    def result(self) -> str:
        """
        """

        return stats(sum(self.correct_words_keystrokes), self.duration)

    def result_extensive(self) -> str:
        """
        """

        r = 'Extensive result:\n'
        r += '\nSpeed by word (correct words only):\n'
        r += f'{wpm(len(self.correct_words)*5, self.duration)} wpm\n'
        r += f'Duration: {self.duration:.{2}f} sec\n'
        r += '\nSpeed by keystroke (correct words only):\n'
        r += stats(sum(self.correct_words_keystrokes),  self.duration)
        r += '\nSpeed by character (correct words only):\n'
        r += stats(len(self.correct_words_chars),       self.duration)
        r += '\nSpeed by keystroke (correct chars only):\n'
        r += stats(sum(self.correct_chars_keystrokes),  self.duration)
        r += '\nSpeed by character (correct chars only):\n'
        r += stats(len(self.correct_chars),             self.duration)

        return r

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

## --------------------- Convinience interface -------------------------

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

def generate_test(language: str='english',
        difficulty: str='basic',
        shuffle_words: bool=False):
    """Generates a typing test with specified parameters.

    difficulty - word complexity ('basic', 'advanced')
    """

    with open(f'tests/{language}/{difficulty}', 'r') as f:
        test = f.read()

    if shuffle_words:
        test_words = test.split()
        shuffle(test_words)
        test = ' '.join(test_words)

    return test

def keystroke(char: str) -> int:
    """Return how many keystrokes does a 'char' count as.

    For language specific characters see 'keystrokes_file_path'.

    1 keystroke:
        a b c d e f g h i j k l m n o p q r s t u v w x y z
        [ ] ; ' \ / . ,
        ALL OTHER CHARACTERS NOT SPECIFIED IN THE 'keystrokes_file_path'
    2 keystrokes:
        A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
        1 2 3 4 5 6 7 8 9 0
        ` - = { } : " | < > ?
    3 keystrokes:
        ~ ! @ # $ % ^ & * ( ) _ +

    """

    for i, chars in enumerate(_keystrokes):
        if char in chars:
            return i+2

    return 1

def stats(keystrokes: int, duration: float) -> str:
    """Returns speed in wpm, cpm and dph
    """

    return  f'{wpm(keystrokes, duration):.{2}f} wpm\n' + \
            f'{cpm(keystrokes, duration):.{2}f} cpm\n' + \
            f'{dph(keystrokes, duration):.{2}f} dph'

def wpm(keystrokes: int, duration: float) -> float:
    """Calculate typing speed in wpm (words per minute).

    A word is considered 5 keystrokes.

    duration - how long the test took in seconds
    """

    words = keystrokes/5
    return words/duration*60
