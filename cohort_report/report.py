
from typing import Union, Dict
from pathlib import PurePosixPath

from cohort_report.series_report import series_report, series_graph
from cohort_report.processing import suppress_low_numbers, load_study_cohort, \
    type_variables_in_df, change_binary_to_categorical
from resources.html_blocks import HTML_STR
from cohort_report.errors import ConfigAndFileMismatchError


def make_report(path: str, output_dir: str, input_file_name: str, variable_types: Union[Dict, None]) -> None:
    """
    Loads the data into a dataframe, and then loops through a dataframe, and takes each column in turn, and
    creates a graph per column

    :param path: (str) Path to the cohort created, usually by cohortextractor, or by other
        study definition creator tools (for example matching). This
        is a DataFrame, with patient_id as first column

    :return:
    """
    # validate that config passed matches with file type
    ext = PurePosixPath(path).suffix
    if ext == ".csv" or ext == ".csv.gz":
        if variable_types == None:
            raise ConfigAndFileMismatchError(f"You have loaded a file type - {ext} that expects "
                                             f"a variables_types config to be passed in.")

    # loads data into dataframe
    df = load_study_cohort(path)

    # do type conversion if csv files by using variable type config passed in
    if variable_types != None:
        df = type_variables_in_df(df=df, variables=variable_types)

    # empty html to start with
    html = "<h1> Cohort Report </h1>"

    # loops through the dataframe column by column and suppreses low
    # numbers, make a cohort report and then a graph
    for name, dtype in zip(df.columns, df.dtypes):
        if name == "patient_id":
            continue
        series = suppress_low_numbers(df[name], dtype)
        transformed_series = change_binary_to_categorical(series=series)
        html += series_report(column_name=name, series=transformed_series)
        html += series_graph(column_name=name, series=transformed_series)


    with open(f"{output_dir}/descriptives_{input_file_name}.html", "w") as f:
        f.write(HTML_STR)
        f.write(html)
        f.write("</body></html>")
        print(f"Created cohort report at {output_dir}/descriptives_{input_file_name}.html")
