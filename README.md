# Cohort-report

## Summary

The reusable action `cohort-report` generates a report including (*i*) summary statistics and (*ii*) plots for each specified variable in an input file.
The example output below shows an example report for three different variable (`sex`, `bmi`, and `has_copd`).
Note that the output slightly varies across the different variables because the variable types are different. 

![Example output from Cohort Report](https://user-images.githubusercontent.com/477263/140117942-fbfde3fc-2ffc-41f9-b2d2-4128629cbb58.png)

## Usage

Consider the following extract from a study's `project.yaml` 

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

The `generate_report` action generates a report that contains a table and a chart for each variable in the input file.
The table contains unsafe statistics and should be checked thoroughly before it is released.
The chart contains statistics that have been made safe.
Cells in the underlying frequency table have been redacted, if:
* They contain less than 10 units
* They contain greater than 90% of the total number of units

Notice the `run` and `config` properties.

The `run` property passes an input file to a named version of cohort-report.
In this case, it passes *output/input.csv* to v3.0.0 of cohort-report.
The `config` property passes configuration to cohort-report; for more information, see *Configuration*.

Notice that the report is called `descriptives_[the name of the input file, without the extension].html`.
It is saved to the `output_path`; for more information, see *Configuration*.

### Configuration

`output_path`, which defaults to `cohort_reports_outputs`.
Save the outputs to the given path.
If the given path does not exist, then it is created.

---

`variable_types`, which is required for `.csv` and `.csv.gz` input files.
Cast the given variables to the given types.
Supported types:

* `binary`
* `categorical`
* `date`
* `float`
* `int`

## Multiple input files

The `run` property can pass multiple input files to a named version of cohort-report.
For example:

```yaml
actions:
  # 3.0.0.
  generate_report:
    run: cohort-report:v3.0.0 output/input_2021-01-01.csv output/input_2021-02-01.csv
    # 3.0.0.
```

However, if one or more input files are `.csv` or `.csv.gz` input files, then `variable_types` is required;
this will cast the given variables to the given types in all input files.
It will fail if an input file does not have the given variables.

## Developer docs

Please see [DEVELOPERS.md](DEVELOPERS.md).
