# cohort-report-action
Action that can be run by project yaml which gives graphs of cohort variables

## Local Development

For local (non-Docker) development, first install [pyenv][] and execute:

```sh
pyenv install $(pyenv local)
```

Then, execute:

```sh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## QA

```sh
bin/codestyle.sh .
```

## Tests

If you have a local development environment,
then the following command will write [pytest][]'s output to the terminal:

```sh
python -m pytest
```

You can also pass test modules, classes, methods, and functions to pytest:

```sh
python -m pytest tests/test_processing.py::test_load_study_cohort
```

[pyenv]: https://github.com/pyenv/pyenv
[pytest]: https://docs.pytest.org/en/stable/
