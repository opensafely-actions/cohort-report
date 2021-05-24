from pathlib import PurePosixPath
from typing import Dict, Union

from cohort_report.errors import ConfigAndFileMismatchError
from cohort_report.processing import (
    change_binary_to_categorical,
    load_study_cohort,
    suppress_low_numbers,
    type_variables_in_df,
)
from cohort_report.series_report import series_graph, series_report
from resources.html_blocks import HTML_STR


def make_report(
    path: str, output_dir: str, input_file_name: str, variable_types: Union[Dict, None]
) -> None:
    """
    Loads the data and create a graph per column.

    Args:
        path (str): Path to the cohort created, usually by cohortextractor, or by other
            study definition creator tools (for example matching). This
            is a DataFrame, with patient_id as first column
        output_dir (str): Path to the output directory
        input_file_name (str): name of the input file
        variable_types (dict or None): Either none or a dict of the types of
        data in the column
            if not a typed input. For example, if plain csv.

    Returns:
        None
    """
    # validate that config passed matches with file type
    ext = PurePosixPath(path).suffix
    if ext == ".csv" or ext == ".csv.gz":
        if variable_types is None:
            raise ConfigAndFileMismatchError(
                f"You have loaded a file type - {ext} that expects "
                f"a variables_types config to be passed in."
            )

    # loads data into dataframe
    df = load_study_cohort(path)

    # do type conversion if csv files by using variable type config passed in
    if variable_types is not None:
        df = type_variables_in_df(df=df, variables=variable_types)

    # empty html to start with
    html = "<h1> Cohort Report </h1>"

    # loops through the dataframe column by column and suppreses low
    # numbers, make a cohort report and then a graph
    for name, series in df.iteritems():
        if name == "patient_id":
            continue
        series = suppress_low_numbers(series)
        transformed_series = change_binary_to_categorical(series=series)
        html += series_report(series=transformed_series)
        html += series_graph(series=transformed_series)

    with open(f"{output_dir}/descriptives_{input_file_name}.html", "w") as f:
        f.write(HTML_STR)
        f.write(html)
        f.write("</body></html>")
        print(
            f"Created cohort report at {output_dir}/descriptives_{input_file_name}.html"
        )
