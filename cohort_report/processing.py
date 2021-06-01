from pathlib import Path
from typing import Dict

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_categorical_dtype,
    is_datetime64_dtype,
    is_numeric_dtype,
)

from .errors import ColumnsDoNotMatch, ImportActionError


def suppress_low_numbers(series: pd.Series, limit: int = 6) -> pd.Series:
    """
    This takes in a series and based on type of series, it suppresses
    contents, and replaces with NaN if any count of any value is less
    than the limit (default 5 or less).

    Args:
        series (pd.Series): A dataframe column
        limit (int): limit at which any counts below this should
            be suppressed. Default value is 6.

    Returns:
         pd.Series: A series which is either the same as original or
            empty if small number suppressed
    """
    if not isinstance(series, pd.Series):
        raise TypeError(
            f"A {type(series)} has been passed to the suppress_low_numbers() function."
            f"This function accepts pandas Series only."
        )

    if is_categorical_dtype(series.dtype) or is_bool_dtype(series.dtype):
        if ~(series.value_counts() < limit).any():
            return series
    elif is_datetime64_dtype(series.dtype) or is_numeric_dtype(series.dtype):
        if (
            ~(series.value_counts() < limit).any()
            and series[~pd.isnull(series)].count() >= limit
        ):
            return series

    # returns empty series if does not satisfy limit criteria
    empty_series = pd.Series()
    empty_series.name = series.name

    return empty_series


def load_study_cohort(path: Path) -> pd.DataFrame:
    """
    Loads the study cohort (from study_definition.py being run),
    and returns a dataframe. This function allows different
    file types to be loaded (csv, csv.gz, dta, feather).

    Args:
        path: path to file

    Returns:
        pd.Dataframe: The data loaded into a pandas Dataframe
    """


    # grabs ext off end of file
    suffixes = path.suffixes

    if suffixes == [".csv"]:
        df = pd.read_csv(path)
    elif suffixes == [".csv", ".gz"]:
        df = pd.read_csv(path, compression="gzip")
    elif suffixes == [".dta"]:
        df = pd.read_stata(path, preserve_dtypes=False)
    elif suffixes == [".dta", ".gz"]:
        # Current latest Pandas (v1.2.4) doesn't support reading .dta.gz files.
        # However, development Pandas does. Rather than write (and test) a function
        # for unzipping the file before passing it to read_stata, let's raise an error
        # and wait for development Pandas to be released.
        raise NotImplementedError()
    elif suffixes == [".feather"]:
        df = pd.read_feather(path)
    else:
        raise ImportActionError("Unsupported filetype attempted to be imported")
    return df


def type_variables_in_df(df: pd.DataFrame, variables: Dict) -> pd.DataFrame:
    """
    Takes in a datafrmae which has been loaded from either a csv or a csv.gz and
    therefore does not have type information. It takes in a variable dict which
    comes from the project.yaml and is passed in as a config json object.
    It then assigns various types to the df columns.

    Args:
        df (Dataframe): data to be changed and typed
        variables (Dict): config that maps variable name (i.e. column name) to type

    Returns:
        pd.Dataframe: Dataframes with types applied
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"A {type(df)} has been passed to the type_variables_in_df() function."
            f"This function accepts pandas Dataframe type only."
        )

    if len(df.columns) != (len(variables.keys()) + 1):
        raise ColumnsDoNotMatch(
            "The number of columns in your dataframe does not "
            "match the number of variables in your config 'variable_type'"
        )

    for column in df.columns:
        if column == "patient_id":
            continue
        elif column not in variables.keys():
            missing_columns = set(df.columns.drop("patient_id")) - set(variables)
            if missing_columns:
                missing_columns_str = ", ".join(list(missing_columns))
                raise ColumnsDoNotMatch(
                    f"Your data frame is missing columns: {missing_columns_str}"
                )

    for column_name, column_type in variables.items():
        if column_type == "int":
            variables[column_name] = "int64"
        elif column_type == "float":
            variables[column_name] = "float64"
        elif column_type == "categorical":
            variables[column_name] = "category"
        elif column_type == "date":
            variables[column_name] = "category"
        elif column_type == "binary":
            variables[column_name] = "int64"

    df = df.astype(variables)
    return df


def change_binary_to_categorical(series: pd.Series) -> pd.Series:
    """
    If the series only contains 0s or 1s, it changes the series to a
    categorical type.

    Args:
        series (pd.Series): Data series being transformed
    Returns:
        pd.Series: Series with binary values changed to categorical type.
    """
    if not isinstance(series, pd.Series):
        raise TypeError(
            f"A {type(series)} has been passed to the change_binary_to_categorical() "
            f"function. This function accepts pandas Series only."
        )
    # if the data is only ints of 0 or 1, it is a binary data type. this is
    # changed into category
    if series.isin([0, 1]).all():
        series = series.astype("category")

    return series
