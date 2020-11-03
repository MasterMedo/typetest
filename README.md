## test your typing speed without leaving the terminal

![example](./img/example.gif)

This repo is home to a self-contained file `typetest`.
As is it is a near clone of [10fastfingers](https://10fastfingers.com/typing-test/english) with an added bonus of being able to see typing speed as you're typing.

Differences in the way typing speed is calculated and feedback across platforms got me interested in writing my own program for testing typing speed.
I've come to love how simple and unrestrictive [10fastfingers](https://10fastfingers.com/typing-test/english) and [keybr](https://keybr.com) feel compared to [typingclub](https://www.typingclub.com/) and [typeracer](https://www.typeracer.com).
They all have great advantages for varying purposes but when it comes to warming up or just waiting for some program to compile (*have you tried [compiling chromium](https://www.reddit.com/r/archlinux/comments/gdeiui/ungoogledchromium_taking_a_long_time_to_build/)?*) I am yet to find a rival to [10fastfingers](https://10fastfingers.com/typing-test/english).
That is why I decided to clone its functionality and add some features I love from other sites.

# typetest
`typetest` is a self-contained minimal typing test program written with [blessed](https://github.com/jquast/blessed/).
It calculates typing speed as sum of spaces and characters from **correctly written words** divided by test duration.
Adjustable settings are `DURATION`, `SHUFFLE` and `NUMBER_OF_ROWS`, which can be set using the command arguments.
The input text for the typing test is read from the standard input or using the [positional arguments](https://docs.python.org/3/glossary.html#term-argument).

# ideas for tests
Along with `typetest` this repository features sample tests.
Try them like so: `typetest -s -d 60 < common_200`.

Scrape something of the net, like a [featured article](https://en.wikipedia.org/wiki/Wikipedia:Featured_articles) on wikipedia.
If you create a file called `wiki_random` with the following contents:

```python
#!/usr/bin/env python3
import re
import requests
from bs4 import BeautifulSoup

word_pattern = re.compile(r"['A-Za-z\d\-]+[,\.\?\!]?")
url = 'https://en.wikipedia.org/wiki/Special:RandomInCategory/Featured_articles'

r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
for sup in soup.select('sup'):
    sup.extract()  # remove citations

text = ' '.join(p.text for p in soup.select('p'))
text = re.sub(r'\[.*?\]|\(.*?\)', '', text)
print(' '.join(re.findall(word_pattern, text)))
```
you can start the test with `wiki_random | typetest`.
Write your own scraper, you may find some suggestions [here](https://en.wikipedia.org/wiki/Lists_of_English_words).

```
usage: typetest [-h] [-d DURATION] [-r ROWS] [-s] [words [words ...]]

example:
  typetest -d 3.5 The typing seems really strong today.
  echo 'I love typing' | typetest
  typetest < test.txt

positional arguments:
  words                 provide words via args in lieu of stdin

optional arguments:
  -h, --help            show this help message and exit
  -d DURATION, --duration DURATION
                        duration in seconds
  -r ROWS, --rows ROWS  number of test rows to show
  -s, --shuffle         shuffle words

shortcuts:
  ^c / ctrl+c           end the test and get results now
  ^h / ctrl+h           backspace
  ^r / ctrl+r           restart the same test
  ^w / ctrl+w           delete a word
  ^u / ctrl+u           delete a word
```
