Thanks for thinking about contributing! :tada:
Feel free to ask anything in the issues section.

# get the project up and running locally :zap:
1. `gh repo clone mastermedo/typetest` (git clone or fork)
2. `pip3 install poetry` (installs [poetry](https://python-poetry.org/docs/))
3. `poetry install` (installs typetest dependecies/requirements)
4. `poetry run flake8` ([lint](https://en.wikipedia.org/wiki/Lint_(software)) the codebase with [flake8](https://flake8.pycqa.org/en/latest/manpage.html))
5. `poetry run black .` ([format](https://en.wikipedia.org/wiki/Prettyprint) the codebase with [black](https://black.readthedocs.io/en/stable/))
6. `poetry run typetest` (run `typetest` locally)
7. `poetry run typetest-analyse` (run `typetest-analyse` locally)
