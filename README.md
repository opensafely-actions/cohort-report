# Cohort-report

## Summary

Cohort-report outputs graphs of variables in a study input file.

![Example output from Cohort Report](https://user-images.githubusercontent.com/477263/140117942-fbfde3fc-2ffc-41f9-b2d2-4128629cbb58.png)

## Usage

Consider the following extract from a study's *project.yaml*:

```yaml
actions:

  generate_study_population:
    run: cohortextractor:latest generate_cohort
    outputs:
      highly_sensitive:
        cohort: output/input.csv

  generate_report:
    run: cohort-report:v2.1.0 output/input.csv
    needs: [generate_study_population]
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
      output_path: output/cohort_reports_outputs
    outputs:
      moderately_sensitive:
        reports: output/cohort_reports_outputs/descriptives_input.html
```

The `generate_report` action generates a report that contains a table and a chart for each variable in the input file.
The table contains unsafe statistics and should be checked thoroughly before it is released.
The chart contains statistics that have been made safe.
Cells in the underlying frequency table have been redacted, if:
* They contain less than 10 units
* They contain greater than 90% of the total number of units

Notice the `run` and `config` properties.

The `run` property passes a specific input file to a specific version of cohort-report.
In this case, the specific input file is *output/input.csv* and the specific version of cohort-report is v1.0.0.
The `config` property passes configuration to cohort-report; for more information, see *Configuration*.

Notice that the HTML document is called `descriptives_[the name of the specific input file, without the extension].html`.
It is saved to the `output_path` (see below).

### Configuration

`output_path`, which defaults to `cohort_reports_outputs`.
Save the outputs to the given path.
If the given path does not exist, then it is created.

---

`variable_types` - this is an optional argument that should be used if the input files contain data without a type, for example, a CSV.
cohort-report can take in other files such as '.feather' and '.dta' which contain the type of the data in each column.
In these cases, a `variable_types` config if not needed.

## Developer docs

Please see [DEVELOPERS.md](DEVELOPERS.md).
