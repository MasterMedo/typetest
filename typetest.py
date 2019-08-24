from json           import dumps
from random         import shuffle
from pathlib        import Path
from typetest.util  import TypeTest, TypeTestDone, split_by_delimiters
from typetest       import cli, gui

import typetest

if __name__ == '__main__':
    cli.parse_args()

    if typetest.args['--file']:
        with open(typetest.args['--file'], 'r') as f:
            test_raw = f.read()

    test_words = split_by_delimiters(test_raw, typetest.args['--delimiters'])

    if typetest.args['--shuffle-words']:
        shuffle(test_words)

    typetest.test = TypeTest(' '.join(test_words), word_by_word=True)

    try:
        gui.init()
        while True:
            gui.draw_stdscr()
            if not typetest.args['--hide']:
                gui.draw_stats()
            c = gui.stdscr.get_wch()
            c = str(c) if c not in [127, 263] else '\b'
            typetest.test.addch(c)
            gui.change_word_colors()

    except TypeTestDone as e:
        gui.shutdown()
    except KeyboardInterrupt as e:
        gui.shutdown()
    except Exception as e:
        gui.shutdown()
        raise

    typetest.test.submit()

    if typetest.args['--output']:
        with open(typetest.args['--output'], 'w') as f:
            f.write(dumps(typetest.test.results))

    if not typetest.args['--quiet']:
        test = typetest.test
        if typetest.args['--verbose']:
            print(f'accuracy:       {test.accuracy:.{0}f}%')
            print(f'duration:       {test.duration:.{2}f} sec\n')
            print(f'correct words:  {len(test.correct_words)}')
            print(f'correct chars:  {len(test.correct_chars)}\n')
            print(f'true speed:     {test.true_speed_wpm:.{0}f} wpm')
            print(f'normalized:     {test.speed_wpm:.{0}f} wpm\n')
            print(f'true speed:     {test.true_speed_cpm:.{0}f} cpm')
            print(f'normalized:     {test.speed_cpm:.{0}f} cpm\n')
            print(f'true speed:     {test.true_speed_dph:.{0}f} dph')
            print(f'normalized:     {test.speed_dph:.{0}f} dph')

        else:
            print(f'accuracy:       {test.accuracy:.{0}f}%')
            print(f'duration:       {test.duration:.{2}f} sec')
            print(f'true speed:     {test.true_speed_wpm:.{0}f} wpm')
