<p align="center">
  <img src="https://user-images.githubusercontent.com/16375100/125825025-74b5b1cd-c5d2-40f1-902a-5b5902720d90.png" width="300"/>
</p>
<p align="center">Test your typing speed without leaving the terminal.</p>

<p align="center">
  <a href="https://pypi.org/project/typetest/">
    <img src="https://img.shields.io/pypi/v/typetest" alt="build" title="build"/>
  </a>
  <a href="https://github.com/mastermedo/typetest/LICENSE">
    <img src="https://img.shields.io/github/license/mastermedo/typetest" alt="license" title="license"/>
  </a>
  <a href="https://github.com/mastermedo/typetest">
    <img src="https://img.shields.io/github/languages/code-size/mastermedo/typetest" alt="build" title="build"/>
  </a>
  <a href="https://github.com/mastermedo/typetest/stargazers">
    <img src="https://img.shields.io/badge/maintainer-mastermedo-yellow" alt="maintainer" title="maintainer"/>
  </a>
</p>

<p align="center">
  <a href="https://github.com/mastermedo/typetest">
    <img src="https://raw.githubusercontent.com/MasterMedo/mastermedo.github.io/master/assets/img/typetest.svg" alt="demo" title="demo"/>
  </a>
</p>

## :clipboard: description
`typetest` is a self-contained minimal typing test program written with [blessed](https://github.com/jquast/blessed/).
As is, it is a near clone of [10fastfingers](https://10fastfingers.com/typing-test/english) with an added bonus of being able to see typing speed as you're typing.

## :zap: features
1. adjustable settings
2. storing test results
3. analysing mistakes
4. easy to track improvement

## :chart_with_upwards_trend: analyse test results with `typetest-analyse`!
![wpm](https://user-images.githubusercontent.com/16375100/125824726-6304ee64-ddf1-4456-879c-10daca45d91c.png)
![char_speeds](https://user-images.githubusercontent.com/16375100/125824817-5c2cbcae-fdcc-45c9-9a3b-ed5c3ec497a5.png)
![word_speeds](https://user-images.githubusercontent.com/16375100/125824889-a01bb4bb-1ed2-49ed-a0aa-9bd5f6b411c7.png)
![mistypes](https://user-images.githubusercontent.com/16375100/125824921-3ecdf9f4-804e-41ec-98a4-6343d0ffbbe2.png)
![dist](https://user-images.githubusercontent.com/16375100/125824933-01294d91-92c9-4ae0-9910-539f6d16507e.png)

## :shipit: installation

1. install python3
2. install pip (python package manager)
3. run `pip install typetest`
4. run `typetest`

Optionally
- make an alias for `typetest`, I use `tt`
- run `typetest-analyse` to get insights

## :bulb: ideas for tests
Along with `typetest` this repository features sample tests.
Try them like so: `typetest -s -d 60 -i common_200` or scrape something off the internet, like a [featured article](https://en.wikipedia.org/wiki/Wikipedia:Featured_articles) on wikipedia.

```python
#!/usr/bin/env python3
import re
import requests
from bs4 import BeautifulSoup

word_pattern = re.compile(r"['A-Za-z\d\-]+[,\.\?\!]?")  # symbols to keep
url = 'https://en.wikipedia.org/wiki/Special:RandomInCategory/Featured_articles'

r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
for sup in soup.select('sup'):
    sup.extract()  # remove citations

text = ' '.join(p.text for p in soup.select('p'))
text = re.sub(r'\[.*?\]|\(.*?\)', '', text)  # remove parenthesis
print(' '.join(re.findall(word_pattern, text)))
```
If you create a file called `wiki_random` you can start the test with `wiki_random | typetest`.
Write your own scraper, you may find some suggestions [here](https://en.wikipedia.org/wiki/Lists_of_English_words).

## :question: usage

```
usage: typetest [-h] [-d DURATION] [--hash HASH] [-i INPUT] [-o OUTPUT_DIRECTORY] [-s] [-r ROWS]

optional arguments:
  -h, --help            show this help message and exit
  -d DURATION, --duration DURATION
                        duration in seconds (default: inf)
  --hash HASH           custom hash (generated from input by default)
  -i INPUT, --input INPUT
                        file to read words from (default: sys.stdin)
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        file to store results in
                        (default: /home/medo/repos/typetest/typetest/results)
  -s, --shuffle         shuffle words (default: False)
  -r ROWS, --rows ROWS  number of test rows to show (default: 2)

example:
  typetest -i test.txt -s -d 60
  echo 'The typing seems really strong today.' | typetest -d 3.5
  typetest < test.txt

shortcuts:
  ^c / ctrl+c           end the test and get results now
  ^[ / ctrl+[ / esc     end the test and get results now
  ^h / ctrl+h / bksp    delete a character
  ^r / ctrl+r / tab     restart the same test
  ^s / ctrl+s           restart the test with words reshuffled
  ^w / ctrl+w           delete a word
  ^u / ctrl+u           delete a word
```

<p align="center">
  <a href="#">
    <img src="https://img.shields.io/badge/⬆️back_to_top_⬆️-white" alt="Back to top" title="Back to top"/>
  </a>
</p>
