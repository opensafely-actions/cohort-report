from pathlib import Path
from typing import Dict, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from pandas import Series
from pandas.api.types import (
    is_bool_dtype,
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_interval_dtype,
    is_numeric_dtype,
)

from cohortreport.errors import ImportActionError


# Maps from external, user-facing types to internal, Pandas types.
TYPE_MAPPING = {
    "binary": "int64",
    "categorical": "category",
    "date": "category",
    "float": "float64",
    "int": "int64",
}


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


def coerce_columns(input_dataframe: pd.DataFrame, variable_types: Dict) -> pd.DataFrame:
    """Coerces the columns in the given data frame to the given types.

    `variable_types` maps from column names to the types in the list below:

    * `binary`
    * `categorical`
    * `date`
    * `float`
    * `int`

    Raises:
        ValueError: A variable's type was invalid (i.e. not in the list above).
            A variable's name was invalid (i.e. not a column in the given data frame).
    """
    try:
        dtypes = {
            v_name: TYPE_MAPPING[v_type] for v_name, v_type in variable_types.items()
        }
    except KeyError as e:
        raise ValueError("Invalid variable type") from e

    try:
        return input_dataframe.astype(dtypes)
    except KeyError as e:
        raise ValueError("Invalid variable name") from e


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


def is_discrete(series: Series) -> bool:
    """Check whether the given series is discrete."""
    tests = [is_bool_dtype, is_categorical_dtype, is_datetime64_any_dtype]
    return any(x(series) for x in tests)


def is_continuous(series: Series) -> bool:
    """Check whether the given series is continuous."""
    if result := is_bool_dtype(series):
        # bool is numeric but is not continuous
        return not result

    tests = [is_numeric_dtype]
    return any(x(series) for x in tests)


def summarize(series: Series) -> Series:
    """Computes summary statistics for a series.

    This is a thin wrapper around `Series.describe`. See that method's documentation for
    information about how the statistics generated for numeric data differ to the
    statistics generated for object data (strings and timestamps).

    The statistics are "unsafe", according to Brandt et al. Consequently, they require
    careful output checking.

    M. Brandt et al., 'Guidelines for the checking of output based on microdata
    research', Jan. 2010, Accessed: Oct. 28, 2021. [Online]. Available:
    https://uwe-repository.worktribe.com/output/983615
    """
    return series.describe()


def group(series: Series) -> Series:
    """Groups a series into a frequency table.

    Here, we're defining "frequency table" rather loosely; a table of the number of
    units by group.

    If `series` is discrete, then the frequency table will be the result of a group
    by/count operation on the units. The index of the series will contain the groups,
    including the "null" group. ("Null" is represented by the default missing value
    marker.)


    If `series` is continuous, then the frequency table will be the result of a binning
    operation on the units. The index of the series, which will be an `IntervalIndex`,
    will contain the bins.
    """
    if is_discrete(series):
        return _group_discrete(series)

    if is_continuous(series):
        return _group_continuous(series)

    assert False, series


def _group_discrete(series):
    if not is_discrete(series):
        raise TypeError("The series must be discrete")
    return series.value_counts(dropna=False)  # Retains series.name


def _group_continuous(series):
    if not is_continuous(series):
        raise TypeError("The series must be continuous")
    hist, bin_edges = np.histogram(series, bins="auto")
    idx = pd.IntervalIndex.from_arrays(left=bin_edges[:-1], right=bin_edges[1:])
    return pd.Series(hist, index=idx, name=series.name)


def redact(frequency_table: Series, less_than=10, greater_than_pct=0.9) -> Series:
    """Redacts a frequency table according to the given heuristics.

    The heuristics are from Brandt et al.

    M. Brandt et al., 'Guidelines for the checking of output based on microdata
    research', Jan. 2010, Accessed: Oct. 28, 2021. [Online]. Available:
    https://uwe-repository.worktribe.com/output/983615

    Args:
        frequency_table: a frequency table
        less_than: redact cells that contain less than this number of units
        greater_than_pct: redact cells that contain greater than this percentage of the
            total number of units

    Returns:
        The redacted frequency table. Cells that don't satisfy the given heuristics have
        their values replaced with the default missing value marker.
    """
    unit_mask = _get_unit_mask(frequency_table, less_than)
    unit_dist_mask = _get_unit_distribution_mask(frequency_table, greater_than_pct)
    return frequency_table.mask(unit_mask | unit_dist_mask)  # Retains series.name


def _get_unit_mask(frequency_table, less_than):
    """True for values that are less than `less_than`. Otherwise False."""
    return frequency_table < less_than


def _get_unit_distribution_mask(frequency_table, greater_than_pct):
    """True for values that are greater than `greater_than_pct` percentage of the total.
    Otherwise False"""
    return frequency_table / frequency_table.sum() > greater_than_pct


def plot(series: Series) -> Figure:
    """Plots a series.

    If `series` has an interval index, then it will be plotted as a histogram.
    Otherwise, it will be plotted as a bar chart.
    """
    if is_interval_dtype(series.index):
        return _plot_hist(series)
    else:
        return _plot_barh(series)


def _series_with_interval_index_to_histogram(series):
    """Transforms a series with an interval index to a two-tuple of histogram values and
    bin edges, as would be returned by `numpy.histogram`."""
    hist = series.values
    bin_edges = np.append(series.index.left.values, series.index.right.values[-1])
    return hist, bin_edges


def _plot_hist(series):
    hist, bin_edges = _series_with_interval_index_to_histogram(series)
    fig, ax = plt.subplots()
    ax.hist(x=bin_edges[:-1], bins=bin_edges, weights=hist)
    ax.set_title(series.name)
    return fig


def _plot_barh(series):
    ax = series.plot.barh(title=series.name)
    return ax.figure


def save(fig: Figure, f_path: Union[Path, str]):
    """Saves `fig` to `f_path`."""
    fig.savefig(f_path)
