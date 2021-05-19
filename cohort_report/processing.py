
import pandas as pd
import numpy as np
from pandas.api.types import is_categorical_dtype, is_bool_dtype, \
    is_datetime64_dtype, is_numeric_dtype
from pathlib import PurePosixPath
from typing import Dict

from .errors import ImportActionError, ColumnsDoNotMatch


def suppress_low_numbers(series, dtype, limit=6) -> pd.Series:
    """
    This takes in a series and based on type of series, it suppresses
    contents, and replaces with NaN if any count of any value is less
    than the limit (default 5 or less).

    :param series (pd.Series): A dataframe column
    :param dtype (numpy.dtype): Type of the data within this column
    :param limit (int): limit at which any counts below this should
        be suppressed
    :return: pd.Series
    """
    if is_categorical_dtype(dtype) or is_bool_dtype(dtype):
        if ~np.any(series.value_counts() < limit):
            return series
    elif is_datetime64_dtype(dtype) or is_numeric_dtype(dtype):
        if (
                ~np.any(pd.isnull(series).value_counts() < limit)
                and series[~pd.isnull(series)].count() >= limit
        ):
            return series

    # returns empty series if does not satisfy limit criteria
    empty_series = pd.Series()
    empty_series.name = series.name
    return empty_series


def load_study_cohort(path: str) -> pd.DataFrame:
    """
    Loads the study cohort (from study_definition.py being run),
    and returns a dataframe. This function allows different
    file types to be loaded (csv, csv.gz, dta, feather).

    :param path: (str) path to file
    :return (pd.Dataframe): data file loaded into a Pandas Dataframe
    """
    suffixes = PurePosixPath(path).suffixes
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
    :param df: (Dataframe) data to be changed and typed
    :param variables: config that maps variable name (i.e. column name) to type
    :return: Dataframe
    """
    if len(df.columns) != (len(variables.keys()) + 1):
        raise ColumnsDoNotMatch("The number of columns in your dataframe does not "
                                "match the number of variables in your config 'variable_type'")

    for column in df.columns:
        if column == "patient_id":
            continue
        elif column not in variables.keys():
            raise ColumnsDoNotMatch("Your dataframe contains columns not defined in the variable_type "
                                    "in your config in project.yaml")

    for column_name, category in variables.items():
        if category == "int":
            variables[column_name] = "int64"
        elif category == "float":
            variables[column_name] = "float64"
        elif category == "categorical":
            variables[column_name] = "category"
        elif category == "date":
            variables[column_name] = "category"
        elif category == "binary":
            variables[column_name] = "int64"

    df = df.astype(variables)
    return df


def change_binary_to_categorical(series: pd.Series) -> pd.Series:
    """
    If the series only contains 0s or 1s, it changes the series to a
    categorical type.
    :param series: Data series being transformed
    :return: series
    """
    # if the data is only ints of 0 or 1, it is a binary data type. this is
    # changed into category
    if series.isin([0, 1]).all():
        series = series.astype('category')

    return series
