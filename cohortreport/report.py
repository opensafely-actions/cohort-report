import os
from pathlib import Path
from typing import Dict, Optional

import pkg_resources
from jinja2 import Template

from cohortreport.errors import ConfigAndFileMismatchError
from cohortreport.processing import (
    change_binary_to_categorical,
    group,
    load_study_cohort,
    plot,
    redact,
    save,
    summarize,
    type_variables_in_df,
)


def make_report(
    path: Path,
    output_dir: str,
    variable_types: Optional[Dict[str, str]],
) -> None:
    """Makes a report for a cohort.

    Args:
        path: a path to a file that contains a cohort; that is, a table with one row per
            patient.
        output_dir: a path to a directory where the report will be written.
        variable_types: for CSV files, a mapping of column names to column types. For
            other file types, this is optional (`None`).
    """
    if not isinstance(path, Path):
        raise TypeError(
            f" The path to the study population was a {type(path)}. "
            f"The path should be a Path."
        )

    if not isinstance(output_dir, str):
        raise TypeError(
            f" The output directory was a {type(output_dir)}. "
            f"The path should be a str."
        )

    # validate that config passed matches with file type
    ext = "".join(path.suffixes)
    if (ext == ".csv" or ext == ".csv.gz") and variable_types is None:
        raise ConfigAndFileMismatchError(
            f"If you pass a {ext} file, then you must also pass `variable_types`"
        )

    # loads data into dataframe
    df = load_study_cohort(path)

    # do type conversion if csv files by using variable type config passed in
    if variable_types is not None:
        df = type_variables_in_df(df=df, variables=variable_types)

    template_str = pkg_resources.resource_string(
        "cohortreport", "resources/report_template.html"
    )
    template = Template(template_str.decode("utf8"))

    os.makedirs(output_dir, exist_ok=True)

    # loops through the dataframe column by column and suppreses low
    # numbers, make a cohort report and then a graph
    reports = {}
    for name, series in df.iteritems():
        if name == "patient_id":
            continue

        transformed_series = change_binary_to_categorical(series=series)

        summarized_series = summarize(transformed_series)

        grouped_series = group(transformed_series)
        redacted_series = redact(grouped_series)
        figure = plot(redacted_series)
        path_to_figure = Path(output_dir) / f"{name}.png"
        save(figure, path_to_figure)

        report_dict = {
            "written_report": summarized_series,
            "graph": str(path_to_figure),
        }
        reports[name] = report_dict

    html = template.render(reports=reports)

    with open(
        f"{output_dir}/descriptives_{path.stem}.html", "w", encoding="utf-8"
    ) as f:
        f.write(html)
        print(f"Created cohort report at {output_dir}descriptives_{path.stem}.html")
