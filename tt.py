from blessed    import Terminal
from itertools  import zip_longest
from functools  import partial
from contextlib import suppress
import re, signal, time, random

term = Terminal()

DURATION = 60
SHUFFLE = True
FILE = 'typetest/tests/english/basic'
NUMBER_OF_ROWS = 2
normal, correct, wrong = term.normal, term.color(46), term.color(196)

redraw = True
def on_resize(*_):
    global redraw
    redraw = True

echo = partial(print, end = '', flush = True)
signal.signal(signal.SIGWINCH, on_resize)
get_words = partial(re.findall, r"[\w']+")

def draw(words, inwords, word_i, text, wpm, timestamp):
    output_lines = []
    print_line = False
    line, line_i, len_line = '', 0, 0
    for i, (word, inword) in enumerate(zip_longest(words, inwords)):
        if len_line + len(word) >= term.width:
            if print_line:
                if len_line < term.width:
                    line += term.clear_eol
                output_lines.append(line)
                if len(output_lines) >= NUMBER_OF_ROWS:
                    break
            line, line_i, len_line = '', line_i+1, 0

        if line:
             line += ' '
             len_line += 1

        if i == word_i:
            print_line = True
            color = correct if word == text else \
                    normal  if word.startswith(text) else \
                    wrong
            line += color + term.reverse(word)
        else:
            color = normal  if i >= len(inwords) else \
                    correct if word == inword else \
                    wrong
            line += color + word

        len_line += len(word)

    carret = term.reverse(' ')
    prompt = f'>>>{text}{carret}' + term.clear_eol
    stats = f'{wpm:3d} wpm | {timestamp}'
    position = term.move_x(term.width-len(stats))
    output_lines.append(prompt + position + stats)

    for line_i, line in enumerate(output_lines):
        if line_i >= term.height:
            break
        echo(term.move_yx(line_i, 0) + line)

if __name__ == '__main__':
    with open(FILE) as f:
        words = get_words(f.read()[:-1])

    if SHUFFLE:
        random.shuffle(words)

    timestamp = '00:00:00'
    counter = duration = wpm = 0
    word_i  = start    = end = 0
    text, inwords = '', []

    with term.cbreak(), \
            term.fullscreen(), \
            term.hidden_cursor(), \
            suppress(KeyboardInterrupt):
        while True:
            if word_i >= len(words) or start and time.time() - start > DURATION:
                break

            word = words[word_i]

            if redraw:
                draw(words, inwords, word_i, text, wpm, timestamp)
                redraw = False

            char = term.inkey(timeout=0.1)
            if not char:
                continue

            if not start:
                start = time.time()
            else:
                end = time.time()
                duration = end - start
                timestamp = time.strftime('%H:%M:%S', time.gmtime(duration))

            if char.name == 'KEY_BACKSPACE':
                text = text[:-1]
            elif char == ' ':
                if text:
                    inwords.append(text)
                    if text == word:
                        counter += len(word)
                        wpm = min(int(counter*12/duration), 999)
                    text = ''
                    word_i += 1
            else:
                text += char
            redraw = True

    print(f'file: {FILE}\nspeed: {wpm} wpm\nduration: {timestamp}')
