import datetime
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd
import pytest
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pandas import testing

from cohortreport import processing
from cohortreport.errors import ImportActionError


class TestLoadStudyCohort:
    @mock.patch("cohortreport.processing.pd.read_csv")
    def test_csv(self, mock):
        f_in = Path("input.csv")
        processing.load_study_cohort(f_in)
        mock.assert_called_once_with(f_in)

    @mock.patch("cohortreport.processing.pd.read_csv")
    def test_csv_gz(self, mock):
        f_in = Path("input.csv.gz")
        processing.load_study_cohort(f_in)
        mock.assert_called_once_with(f_in, compression="gzip")

    @mock.patch("cohortreport.processing.pd.read_stata")
    def test_dta(self, mock):
        f_in = Path("input.dta")
        processing.load_study_cohort(f_in)
        mock.assert_called_once_with(f_in, preserve_dtypes=False)

    @mock.patch("cohortreport.processing.pd.read_stata")
    def test_dta_gz(self, mock):
        with pytest.raises(NotImplementedError):
            processing.load_study_cohort(Path("input.dta.gz"))

    @mock.patch("cohortreport.processing.pd.read_feather")
    def test_feather(self, mock):
        f_in = Path("input.feather")
        processing.load_study_cohort(f_in)
        mock.assert_called_once_with(f_in)

    def test_unsupported_file_type(self):
        with pytest.raises(ImportActionError):
            processing.load_study_cohort(Path("input.xlsx"))  # No chance!


class TestCheckColumnsMatch:
    @pytest.fixture
    def test_df(self):
        return pd.DataFrame(
            {"patient_id": [1, 2], "copd": [1, 0], "sex": ["male", "female"]}
        )

    def test_columns_no_match(self, test_df):
        with pytest.raises(AssertionError):
            processing.check_columns_match(
                test_df, {"not_copd": "float64", "sex": "categorical"}
            )

    def test_columns_match(self, test_df):
        observed_df = processing.check_columns_match(
            test_df, {"copd": "float64", "sex": "categorical"}
        )
        testing.assert_frame_equal(observed_df, test_df)


@pytest.fixture
def input_dataframe():
    return pd.DataFrame(
        {
            "patient_id": [1, 2],
            "test_binary": [1, 0],
            "test_categorical": ["male", "female"],
            "test_int": [56, 65],
            "test_date": [datetime.date(2021, 8, 31), datetime.date(2021, 8, 31)],
            "test_float": [1.2, 5.4],
        },
        dtype="str",
    )


class TestTypeVariables:
    def test_type_variable_match(self, input_dataframe):
        variable_types = {
            "test_binary": "binary",
            "test_categorical": "categorical",
            "test_int": "int",
            "test_date": "date",
            "test_float": "float",
        }
        typed_df = processing.type_variables_in_df(input_dataframe, variable_types)
        assert typed_df["test_binary"].dtype == "int64"
        assert typed_df["test_categorical"].dtype == "category"
        assert typed_df["test_int"].dtype == "int64"
        assert typed_df["test_date"].dtype == "category"
        assert typed_df["test_float"].dtype == "float64"


class TestIsDiscrete:
    def test_with_discrete(self):
        assert processing.is_discrete(pd.Series(dtype=bool))
        assert processing.is_discrete(pd.Series(dtype="boolean"))
        assert processing.is_discrete(pd.Series(dtype="category"))
        assert processing.is_discrete(pd.Series(dtype="datetime64[ns]"))
        assert processing.is_discrete(pd.Series(dtype="datetime64[ns, UTC]"))

    def test_with_not_discrete(self):
        assert not processing.is_discrete(pd.Series(dtype=float))
        assert not processing.is_discrete(pd.Series(dtype=int))


class TestIsContinuous:
    def test_with_continuous(self):
        assert processing.is_continuous(pd.Series(dtype=float))
        assert processing.is_continuous(pd.Series(dtype=int))

    def test_with_not_continuous(self):
        assert not processing.is_continuous(pd.Series(dtype=bool))
        assert not processing.is_continuous(pd.Series(dtype="boolean"))
        assert not processing.is_continuous(pd.Series(dtype="category"))
        assert not processing.is_continuous(pd.Series(dtype="datetime64[ns]"))
        assert not processing.is_continuous(pd.Series(dtype="datetime64[ns, UTC]"))


def test_summarize():
    # `summarize` is a thin wrapper around `Series.describe`. However, the
    # latter accepts arguments that we shouldn't pass without also making
    # changes to the docstring and to the cohort report itself (i.e. the HTML
    # file). Consequently, we mock the `Series` that we pass to `summarize` and
    # test that `Series.describe` was called without arguments.
    series = mock.MagicMock(spec_set=pd.Series)

    processing.summarize(series)

    series.describe.assert_called_once_with()


class TestGroup:
    def test_with_object(self):
        # handling an object series is undefined
        with pytest.raises(AssertionError):
            processing.group(pd.Series(dtype=object))

    def test_with_bool(self):
        obs = processing._group_discrete(
            pd.Series(
                [False],
                dtype=bool,
                name="has_condition",
            )
        )

        exp = pd.Series([1], index=[False], dtype=int, name="has_condition")
        testing.assert_series_equal(obs, exp)

    def test_with_float(self):
        obs = processing._group_continuous(pd.Series([1.0], dtype=float, name="bmi"))

        exp = pd.Series(
            [1],
            index=pd.IntervalIndex.from_tuples([(0.5, 1.5)]),
            dtype=int,
            name="bmi",
        )
        testing.assert_series_equal(obs, exp)


def test_group_discrete_with_float():
    with pytest.raises(TypeError):
        processing._group_discrete(pd.Series(dtype=float))


def test_group_continuous_with_bool():
    with pytest.raises(TypeError):
        processing._group_continuous(pd.Series(dtype=bool))


def test_redact():
    frequency_table = pd.Series(
        index=["0", "16-29", "30-39"],
        data=[
            10,  # does not fail either heuristic
            9,  # fails the "less than this number" heuristic
            172,  # fails the "greater than this percentage" heuristic
        ],
        dtype="int",
        name="age_band",
    )

    obs = processing.redact(frequency_table)

    exp = pd.Series(
        index=["0", "16-29", "30-39"],
        data=[
            10,  # not redacted
            np.nan,  # redacted
            np.nan,  # redacted
        ],
        dtype=float,  # cast from int to float because of np.nan
        name="age_band",
    )
    testing.assert_series_equal(obs, exp)


def test_get_unit_mask():
    # a frequency table with a count of 1 for False and a count of 19 for True
    frequency_table = pd.Series(
        index=[False, True],
        data=[1, 19],
        dtype="int",
        name="has_condition",
    )

    # cells that contain less than 10 units should be redacted
    obs_unit_mask = processing._get_unit_mask(frequency_table, 10)

    # We expect False to be redacted (i.e. the mask to have the value True), because it
    # has a count of 1. We expect True not to be redacted (i.e. the mask to have the
    # value False, because it has a count of 19.
    exp_unit_mask = pd.Series(
        index=[False, True],
        data=[True, False],
        dtype=bool,
        name="has_condition",
    )
    testing.assert_series_equal(obs_unit_mask, exp_unit_mask)


def test_get_unit_distribution_mask():
    # a frequency table with a count of 1 for False and a count of 19 for True
    frequency_table = pd.Series(
        index=[False, True],
        data=[1, 19],
        dtype="int",
        name="has_condition",
    )

    # cells that contain greater than 90% of the total number of units should be
    # redacted
    obs_unit_dist_mask = processing._get_unit_distribution_mask(frequency_table, 0.9)

    # We expect False not to be redacted (i.e. the mask to have the value False),
    # because it does not have greater than 90% of the total number of units. We expect
    # True to be redacted (i.e. to mask to have the value True), because it has greater
    # than 90% of the total number of units.
    exp_unit_dist_mask = pd.Series(
        index=[False, True],
        data=[False, True],
        dtype=bool,
        name="has_condition",
    )
    testing.assert_series_equal(obs_unit_dist_mask, exp_unit_dist_mask)


def test_series_with_interval_index_to_histogram():
    obs_hist, obs_bin_edges = processing._series_with_interval_index_to_histogram(
        pd.Series(
            [1, 2, 3],
            pd.IntervalIndex.from_tuples([(0.5, 1.5), (1.5, 2.5), (2.5, 3.5)]),
            dtype=int,
            name="bmi",
        )
    )

    exp_hist = np.array([1, 2, 3])
    exp_bin_edges = np.array([0.5, 1.5, 2.5, 3.5], dtype=float)
    assert np.array_equal(obs_hist, exp_hist)
    assert np.array_equal(obs_bin_edges, exp_bin_edges)


class TestPlotHist:
    def test_has_title(self):
        # Test the function's behaviour; did it return what we expected it to return?
        obs_fig = processing.plot(
            pd.Series(
                [1],
                pd.IntervalIndex.from_tuples([(0.5, 1.5)]),
                dtype=int,
                name="bmi",
            )
        )

        assert obs_fig.axes[0].get_title() == "bmi"

    @mock.patch("cohortreport.processing.plt.subplots")
    def test_is_histogram(self, mocked_subplots):
        # Test the function's implementation
        mocked_fig = mock.MagicMock(spec_set=Figure)
        mocked_ax = mock.MagicMock(spec_set=Axes)
        mocked_subplots.return_value = mocked_fig, mocked_ax

        processing.plot(
            pd.Series(
                [1],
                pd.IntervalIndex.from_tuples([(0.5, 1.5)]),
                dtype=int,
                name="bmi",
            )
        )

        mocked_ax.hist.assert_called_once()


class TestPlotBarh:
    def test_has_title(self):
        # Test the function's behaviour; did it return what we expected it to return?
        obs_fig = processing.plot(
            pd.Series(
                [1],
                index=[False],
                dtype=int,
                name="has_condition",
            )
        )

        assert obs_fig.axes[0].get_title() == "has_condition"

    def test_is_barh(self):
        # Test the function's implementation
        mocked_series = mock.MagicMock(spec_set=pd.Series)
        mocked_series.name = "has_condition"

        processing.plot(mocked_series)

        mocked_series.plot.barh.assert_called_once_with(title="has_condition")
