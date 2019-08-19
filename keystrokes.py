__all__ = ['keystroke']

_whitespaces = '\t\n\x0b\x0c\r '

_keystrokes = [
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890`-={}:"|<>?',  # count as 2 keystrokes
    '~!@#$%^&*()_+']                                    # count as 3 keystrokes

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
