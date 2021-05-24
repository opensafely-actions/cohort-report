import pandas as pd
import plotly.express as px
from pandas.api.types import is_categorical_dtype, is_numeric_dtype


def series_report(series: pd.Series) -> str:
    """
    Takes in a Series - i.e. a column name and outputs a HTML block
    with a styled title, and either a note describing data is suppressed
    or a description of the data

    :param series: (pd.Series) - data column being reported on
    :return: HTML string
    """
    # create title
    html = f"<h2>{series.name}</h2>"

    # if column values are NaN, creates reports suppressed
    if series.isnull().all():
        html += "<p> outputs suppressed (low number suppression)</p>"
    else:
        # else describes the data
        descriptive = series.describe()
        html += descriptive.to_frame().to_html(
            classes="df_style.css", float_format="{:10.2f}".format
        )
    return html


def series_graph(series: pd.Series) -> str:
    """
    Takes in a series (i.e. a column) and if contains data
    returns a histogram for numerical data, and a barchart for
    categorical data

    :param series: (pd.Series) data being graphed
    :return:
    """
    if series.isnull().all():
        return ""
    else:
        if is_numeric_dtype(series.dtype):
            fig = px.histogram(
                data_frame=series,
                x=series.name,
                title=f"Histogram showing distribution of {series.name}",
            )
            html = fig.to_html(full_html=False)
            return html
        elif is_categorical_dtype(series.dtype):
            data = series.value_counts()
            fig = px.bar(data_frame=data)
            fig.update_xaxes(categoryorder="category ascending")
            html = fig.to_html(full_html=False)
            return html
        # elif series.dtype == "object":
        #     print("object")
        else:
            return ""
