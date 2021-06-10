# Cohort Report Action 

### Action Summary
This is an action that can be called into the 
`project.yaml`. It requires data in
a support data file  format (`.csv`, `csv.gz`,
`.dta`, `feather`), and outputs a HTML document. 
Each variable has a report with some basic counts, or 
if appropriate means and ranges, and a graph
appropriate to that variable. 

Small number suppression is pre-set to 5 or less
meaning no report will be provided for variables 
with any count 5 or less. 

### Using Cohort Report Action 
The following example blocks should be included 
in the `project.yaml` file. File formats that retain
typing, such as a `.feather` file, only need to be 
a input file, and do not need a `--config`. 

Example `project.yaml`
```yaml 
inputs: 
  input: tests/test_data/input.feather
```

Other untyped file formats such as `.csv` need to be
passed a list of variables and their types. The typing
options available are:

- categorical
- numerical 
- binary
- date

Example
`project.yaml`
```yaml 
inputs: 
  input: tests/test_data/input.csv
config:
  variable_types:
    age: numerical
    sex: categorical
    ethnicity: categorical
    bmi: numerical
    diabetes: binary
    chronic_liver_disease: binary
    imd: categorical
    region: categorical
    stp: categorical
    rural_urban: categorical
    prior_covid_date: date
```