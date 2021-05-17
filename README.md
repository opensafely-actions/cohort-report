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

[pyenv]: https://github.com/pyenv/pyenv
