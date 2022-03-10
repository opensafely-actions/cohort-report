# Cohort-report

## Summary

The reusable action `cohort-report` generates a report including:

1. summary statistics; and
2. a chart for each variable in a specified input file.
The example output below shows an example report for three different variables: `sex`, `bmi`, and `has_copd`.

![Example output from Cohort Report](https://user-images.githubusercontent.com/477263/140117942-fbfde3fc-2ffc-41f9-b2d2-4128629cbb58.png)

## Usage

The `generate_report` action generates a report that contains a table and a chart for each variable in the input file.
The table contains unsafe statistics and should be checked thoroughly before it is released.
The chart contains statistics that have been made safe.
Cells in the underlying frequency tables are redacted automatically, if they:

1. contain less than 10 units; or
2. contain greater than 90% of the total number of units.

Consider the following extract from a study's *project.yaml*:

```yaml
actions:

  generate_study_population:
    run: cohortextractor:latest generate_cohort
    outputs:
      highly_sensitive:
        cohort: output/input.csv

  generate_report:
    run: cohort-report:v3.0.0 output/input.csv
    needs: [generate_study_population]
    config:
      variable_types:
          age: int
          bmi: float
          has_copd: binary
      output_path: output/cohort_reports_outputs
    outputs:
      moderately_sensitive:
        reports: output/cohort_reports_outputs/descriptives_input.html
        reports_charts: output/cohort_reports_outputs/*.png
```
 

The properties `run`, `needs`, and `outputs` are common to all OpenSAFELY actions, see [the project pipeline](https://docs.opensafely.org/actions-pipelines/) for more information.
In this case, the `run` property passes *output/input.csv* to v3.0.0 of `cohort-report`.

The following list describes the `config` properties that are specific to the reusable action `cohort-report`:

- **`config`**: Passes configuration options to `cohort-report`
  - **`variable_types`**: Is required for `.csv` and `.csv.gz` input files to cast the given variables to the given types.
    Supported types are: `binary`, `categorical`, `date`, `float`, and `int`.
  - **`output_path`**: Specify path for all outputs from this action (defaults to `cohort_reports_outputs`).
    If the given path does not exist, then it is created.

Notice that the report (`descriptives_[the name of the input file, without the extension].html`) as well as all charts (`[the name of the variable].png`) need to be added as outputs.


## Multiple input files

The `run` property can pass multiple input files to a named version of cohort-report.
For example:

```yaml
actions:
  # 3.0.0.
  generate_report:
    run: cohort-report:v3.0.0 output/input_2021-01-01.csv output/input_2021-02-01.csv
```

However, if one or more input files are `.csv` or `.csv.gz` input files, then `variable_types` is required;
this will cast the given variables to the given types in all input files.
It will fail if an input file does not have the given variables.

## Developer docs

Please see [DEVELOPERS.md](DEVELOPERS.md).
