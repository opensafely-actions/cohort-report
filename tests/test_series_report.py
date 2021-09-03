from unittest import mock

import pandas as pd
import pytest

from cohortreport.series_report import series_graph, series_report


class TestSeriesReport:
    def test_descriptive_report(self):
        testing_col = pd.Series(list([0, 10] * 6), dtype="float64")
        observed_report = series_report(testing_col)

        assert observed_report["count"] == 12
        assert observed_report["mean"] == 5

    def test_small_number_suppression(self):
        testing_col = pd.Series(dtype="float64")  # empty series
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
        testing_col = pd.Series(dtype="float64")  # empty series
        observed_graph = series_graph(testing_col)

        assert observed_graph == ""

    @mock.patch("plotly.express.histogram")
    def test_histogram_chart(self, mock):
        testing_col = pd.Series(list([0, 10] * 6), dtype="float64")
        series_graph(testing_col)
        mock.assert_called_once()

    @mock.patch("plotly.express.bar")
    def test_bar_chart(self, mock):
        testing_col = pd.Series(list(["orange", "green"] * 6), dtype="category")
        series_graph(testing_col)
        mock.assert_called_once()
