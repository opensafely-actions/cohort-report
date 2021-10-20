from pathlib import Path
from typing import Dict

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_categorical_dtype,
    is_datetime64_dtype,
    is_numeric_dtype,
)

from cohortreport.errors import ImportActionError


def suppress_low_numbers(series: pd.Series, limit: int = 6) -> pd.Series:
    """
    This takes in a series and if any count of any one value is less than
    the limit, it suppresses the whole series and replaces it with
    NaN.

    Args:
        series: A dataframe column
        limit: limit at which any counts below this should
            be suppressed. Default value is 6.

    Returns:
         pd.Series: A series which is either the same as original or
            empty if small number suppressed
    """
    if is_categorical_dtype(series.dtype) or is_bool_dtype(series.dtype):
        if ~(series.value_counts() < limit).any():
            return series
    elif is_datetime64_dtype(series.dtype) or is_numeric_dtype(series.dtype):
        if (
            ~(series.value_counts() < limit).any()
            and series[~pd.isnull(series)].count() >= limit
        ):
            return series

    # returns empty series if does not satisfy limit criteria.
    # Set as float64 -  DeprecationWarning: The default dtype for empty
    # Series will be 'object' instead of 'float64' in a future version.
    empty_series = pd.Series(dtype="float64")
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


def check_columns_match(df: pd.DataFrame, variables: Dict) -> pd.DataFrame:
    """
    Checks the variable config contains all the columns within
    the dataframe passed in

    Args:
        df: Dataframe being checked.
        variables: Config of the columns

    Returns: Dataframe depending if df columns match the variable dict
    """
    if set(df.columns.drop("patient_id")) != set(variables.keys()):
        raise AssertionError("Columns do not match config")
    return df


def type_variables_in_df(df: pd.DataFrame, variables: Dict) -> pd.DataFrame:
    """
    Takes in a dataframe which has been loaded from either a csv or a csv.gz and
    therefore does not have type information. It takes in a variable dict which
    comes from the project.yaml and is passed in as a config json object.
    It then assigns various types to the df columns.

    Args:
        df: data to be changed and typed
        variables: config that maps variable name (i.e. column name) to type

    Returns:
        pd.Dataframe: Dataframes with types applied
    """
    # Check columns in variable dict match columns
    checked_df = check_columns_match(df=df, variables=variables)

    # Type columns
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

    typed_df = checked_df.astype(variables)
    return typed_df


def change_binary_to_categorical(series: pd.Series) -> pd.Series:
    """
    If the series only contains 0s or 1s, it changes the series to a
    categorical type.

    Args:
        series: Data series being transformed
    Returns:
        pd.Series: Series with binary values changed to categorical type.
    """
    # if the data is only ints of 0 or 1, it is a binary data type. this is
    # changed into category
    if series.isin([0, 1]).all():
        series = series.astype("category")

    return series
