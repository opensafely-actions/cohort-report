import pandas as pd
import plotly.express as px
from pandas.api.types import is_categorical_dtype, is_numeric_dtype
from markupsafe import Markup
from typing import Union


def series_report(series: pd.Series) -> Union[pd.Series, str]:
    """
    Takes in a Series - i.e. a column name and outputs a HTML block
    with a styled title, and either a note describing data is suppressed
    or a description of the data

    Args:
        series (pd.Series): data column being reported on
    Returns:
        string or pd.Series
    """
    if not isinstance(series, pd.Series):
        raise TypeError(
            f"A {type(series)} has been passed to the series_report() function."
            f"This function accepts pandas Series only."
        )

    html = ""
    # if column values are NaN, creates reports suppressed
    if series.isnull().all():
        return "Suppressed due to low numbers"
    else:
        # else describes the data
        descriptive = series.describe()
        return descriptive


def series_graph(series: pd.Series) -> Union[str, Markup]:
    """
    Takes in a series (i.e. a column) and if contains data
    returns a histogram for numerical data, and a barchart for
    categorical data

     Args:
        series (pd.Series): data column that is being graphed
    Returns:
        str or Markup: HTML marked safe image or a string
    """
    if not isinstance(series, pd.Series):
        raise TypeError(
            f"A {type(series)} has been passed to the series_graph() function."
            f"This function accepts pandas Series only."
        )

    if series.isnull().all():
        return ""
    else:
        if is_numeric_dtype(series.dtype):
            fig = px.histogram(
                data_frame=series,
                x=series.name,
                title=f"Histogram showing distribution of {series.name}",
            )
            image = Markup(fig.to_html(full_html=False, default_width="50%"))
            return image
        elif is_categorical_dtype(series.dtype):
            data = series.value_counts()
            fig = px.bar(data_frame=data)
            fig.update_xaxes(categoryorder="category ascending")
            image = Markup(fig.to_html(full_html=False, default_width="50%"))
            return image
        else:
            return ""
