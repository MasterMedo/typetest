from typetest.core  import get_test_raw, print_result, output_results
from typetest.util  import TypeTest, TypeTestDone, split_by_delimiters
from typetest       import cli, gui
from random         import shuffle

import typetest

if __name__ == '__main__':
    cli.parse()

    test_raw = get_test_raw()
    test_words = split_by_delimiters(test_raw, typetest.args['--delimiters'])

    if typetest.args['--shuffle-words']:
        shuffle(test_words)

    typetest.test = TypeTest(' '.join(test_words), word_by_word=True)

    try:
        gui.init()
        gui.play()

    except TypeTestDone as e:
        pass
    except KeyboardInterrupt as e:
        pass
    except Exception as e:
        gui.shutdown()
        raise

    gui.shutdown()

    typetest.test.submit()

    if typetest.args['--output']:
        output_results()

    if not typetest.args['--quiet']:
        print_result()
