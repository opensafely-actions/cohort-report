# cohort-report-action
Action that can be run by project yaml which gives graphs of cohort variables. 

### Action Arguments
The action has one required argument called input_files. This is a file or list 
of files that you wish to run the cohort action on. 

##### Config structure
There is one optional argument `--config`. The config can be a string or a json file.

If the input file does not have typing inbuilt, the `--config` should contain
a key called `variable_types`containing the variable types as key-value pairs. See
[test1_config](tests/test_json/test1_config.json). 

If you require your cohort report to be saved 
in a particular folder, you can specify this in the `--config` with `output_path`. If 
no output path is provided, the default place is `cohort_reports_outputs/`. The action 
will make this folder if it does not exist. 
 
### Running this action
It can be run in two ways:

##### Run locally with Python
```bash
python3 entrypoint.py [inputfile] --config [config_json_file]

# for example to run test input file and config
python entrypoint.py tests/test_data/input.csv --config tests/test_json/test1_config.json
```

##### Running as CLI
You can pip install this package and use as a command line tool. 
```bash
cohortreport [inputfile or list of files] --config [config_json_file or json_str]

# for example to run an input file and config
cohortreport data/input.csv --config test_actions_jsons/test1_config.json

# to run list of input files and same config for each file
cohortreport data/input.csv data/second_input.csv --config test_actions_jsons/test1_config.json
```

### Project yaml
This action can be invoked from the `project.yaml`. This is passed into json. 

```yaml
actions: 
  cohort_report:
    run: cohortreport:latest input.csv
config:
    variable_types:
      age: int
      sex: categorical
      ethnicity: categorical
      bmi: float
      diabetes: binary
      chronic_liver_disease: binary
      imd: categorical
      region: categorical
      stp: categorical
      rural_urban: categorical
      prior_covid_date: date
    output_path: outputs
```

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
pip install -r dev_requirements.txt
```

## QA
Run `make` to access Makefile commands. Black, flake8 and mypy are available 
and have a standard setup. 

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
