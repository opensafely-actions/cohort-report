import pandas as pd
from markupsafe import Markup
import pytest
from html.parser import HTMLParser

from cohortreport.series_report import series_graph, series_report


class TestSeriesReport:

    def test_descriptive_report(self):
        testing_col = pd.Series(list([0, 10] * 6), dtype="float64")
        observed_report = series_report(testing_col)

        assert observed_report['count'] == 12
        assert observed_report['mean'] == 5

    def test_small_number_suppression(self):
        testing_col = pd.Series() # empty series
        observed_report = series_report(testing_col)

        assert observed_report == "Suppressed due to low numbers"

    def test_only_accepts_series(self):
        testing_col = [1, 2, 3, 4]
        with pytest.raises(TypeError):
            series_report(testing_col)


class TestSeriesGraph:

    def test_only_accepts_series(self):
        testing_col = [1, 2, 3, 4]
        with pytest.raises(TypeError):
            series_graph(testing_col)

    def test_small_number_suppression(self):
        testing_col = pd.Series() # empty series
        observed_graph = series_graph(testing_col)

        assert observed_graph == ""

    def test_chart(self):
        testing_col = pd.Series(list([0, 10] * 6), dtype="float64")
        observed_graph = series_graph(testing_col)

        assert type(observed_graph) == Markup
