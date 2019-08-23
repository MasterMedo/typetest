from os             import walk
from json           import dumps
from random         import choice

import typetest

def output_results():
    with open(typetest.args['--output'], 'w') as f:
        if typetest.args['--output-format'] == 'json':
            f.write(dumps(typetest.test.results))

def print_result():
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

