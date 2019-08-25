# WIP

# typetest
test your typing speed without leaving the terminal

![example](./img/example.gif)

### TODO
- cli
	- implement options (-abd --cpm...)
	- '#' in usage means not implemented
- gui
	-	handle ctrl keypresses manually

### Usage
```
Usage:
    cli.py  [-abehpsw] [-v | -q] [-d=<duration>] [-l=<layout>]
            [--delimiters=<string>] [-r=<directory> | -f=<file>]
            [-o=<file>] [--output-format=<format>]
            [--bg=<color> --fg=<color> --cc=<color> --wc=<color>]
    cli.py  (--help | --version)


Options:
    -a --all-correct-chars      Consider correct characters from both
                                correct and wrong words. #
    -b --beep                   Alert the user when he makes a mistake. #
    --bg=<color>                Terminal background color. [default: 0]
    --cc=<color>                Correct color. [default: 46]
    --cpm                       Show characters per minute. #
    -d --duration=<duration>    Limit duration of the typing test to
                                <duration>. #
    --delimiters=<string>       Delimiters to divide text file by.
                                Decoded with utf-8. [default: \\n ]
    --dph                       Show depressions per hour. #
    -e --endless                Repeat test endlessly, if -r is
                                specified randomizes every repetition. #
    -f --file=<file>            File to read the test from.
                                Overrides --root-dir option.
    --fg=<color>                Foreground main color. [default: 7]
    -h --hide                   Hide timer and dynamic wpm counter.
    --help                      Show this screen.
    -l --layout=<layout>        Keyboard layout for calculating
                                keystrokes. [default: qwerty] #
    -n --normalize              Use keystrokes over characters. #
    -o --output=<file>          File to store output result in.
    --output-format=<format>    File format to store output as; json,
                                csv. [default: json] #
    -p --prevent-wrong          Accept up to 4 correct chars in a row,
                                then block incorrect input. If -w is
                                set accept only correct words. #
    -q --quiet                  Print no results.
    -r --root-dir=<directory>   Root directory to randomize the test
                                from. [default: typetest/tests/english/]
    -s --shuffle-words          Shuffle words.
    -v --verbose                Show a more extensive result.
    --version                   Show version.
    -w --word-by-word           Evaluate word by word instead of
                                character by character. #
    --wc=<color>                Wrong color. [default: 196]

Shortcuts:
    ^C / Ctrl+c                 End the test and get results now.
    ^H / Ctrl+h                 Backspace.
    ^R / Ctrl+r                 Restart the same test. #
    ^W / Ctrl+w                 Delete a word. #

```
