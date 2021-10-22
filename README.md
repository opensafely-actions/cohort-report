# Cohort Report

## Summary

Cohort Report outputs graphs of variables in a study input file.

![alt text](https://user-images.githubusercontent.com/477263/135131698-615d25b7-ba1b-419b-92d7-58bb9aa828a7.png)

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
    run: cohortreport:v1.0.0 output/input.csv
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

The `generate_report` action outputs one HTML document with a graph for each variable specified.
Where graphs have a category of 5 or less, small number suppression is applied and the
whole graph is redacted.

Notice the `run` and `config` properties.

The `run` property passes a specific input table to a specific version of cohortreport.
In this case, the specific input file is *output/input.csv* and the specific version of cohortreport is v1.0.0.
The `config` property passes configuration to cohortreport; for more information, see *Configuration*.

### Configuration

`output_path`, which defaults to `cohort_reports_outputs`.
Save the outputs to the given path.
If the given path does not exist, then it is created.

---

`variable_types` - this is an optional argument that should be used if the input files
contain data without a type, for example, a CSV. `cohortreport` can take in other files
such as '.feather' and '.dta' which contain the type of the data in each column. In these
cases, a `variable_types` config if not needed.

## Developer docs

Please see [DEVELOPERS.md](DEVELOPERS.md).
