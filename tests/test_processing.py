import datetime
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest
from pandas import testing

from cohortreport import processing
from cohortreport.errors import ImportActionError


class TestSuppressSmallNumbers:
    def test_has_small_numbers_in_int64_boolean(self):
        col = pd.Series(list([0, 1] * 5), dtype="int64")
        res = processing.suppress_low_numbers(col)
        assert res.empty

    def test_has_no_small_numbers_in_int64_boolean(self):
        exp = pd.Series(list([0, 1] * 6), dtype="int64")
        obs = processing.suppress_low_numbers(exp)
        testing.assert_series_equal(obs, exp)

    def test_has_small_numbers_in_int64(self):
        col = pd.Series(list([1, 2] * 5), dtype="int64")
        res = processing.suppress_low_numbers(col)
        assert res.empty

    def test_has_no_small_numbers_in_int64(self):
        exp = pd.Series(list([1, 2] * 6), dtype="int64")
        obs = processing.suppress_low_numbers(exp)
        testing.assert_series_equal(obs, exp)

    def test_has_small_numbers_in_category_dtype(self):
        col = pd.Series(list(["Yes", "No"] * 5), dtype="category")
        res = processing.suppress_low_numbers(col)
        assert res.empty

    def test_has_no_small_numbers_in_category_dtype(self):
        exp = pd.Series(list(["Yes", "No"] * 6), dtype="category")
        obs = processing.suppress_low_numbers(exp)
        testing.assert_series_equal(obs, exp)

    def test_has_small_numbers_in_datetime64_dtype(self):
        dt1 = datetime.datetime(2021, 10, 12)
        dt2 = datetime.datetime(2021, 10, 11)
        col = pd.Series(list([dt1, dt2] * 5), dtype="datetime64[ns]")
        res = processing.suppress_low_numbers(col)
        assert res.empty

    def test_has_no_small_number_in_datetime64_dtype(self):
        dt1 = datetime.datetime(2021, 10, 12)
        dt2 = datetime.datetime(2021, 10, 11)
        exp = pd.Series(list([dt1, dt2] * 6), dtype="datetime64[ns]")
        obs = processing.suppress_low_numbers(exp)
        testing.assert_series_equal(obs, exp)

    def test_objects_return_empty(self):
        # Pandas can store any Python object incl. strings as Objects
        # As default, we want to stop this in case an unexpected object such as
        # another Data Object is passed through. This means that string
        # categories (e.g. "Yes", and "No") need to be specified as categorical,
        # and if they are not, they will be objects and these "objects" removed
        col = pd.Series(list(["Yes", "No"] * 6))
        res = processing.suppress_low_numbers(col)
        assert res.empty


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


class TestTypeVariables:
    @pytest.fixture
    def test_df(self):
        return pd.DataFrame(
            {
                "patient_id": [1, 2],
                "test_binary": [1, 0],
                "test_categorical": ["male", "female"],
                "test_int": [56, 65],
                "test_date": [
                    datetime.datetime(2021, 8, 31, 9, 50, 29, 628483),
                    datetime.datetime(2021, 8, 31, 9, 51, 15, 801522),
                ],
                "test_float": [1.2, 5.4],
            }
        )

    def test_type_variable_match(self, test_df):
        variable_dict = {
            "test_binary": "binary",
            "test_categorical": "categorical",
            "test_int": "int",
            "test_date": "date",
            "test_float": "float",
        }
        observed_df = processing.type_variables_in_df(
            df=test_df, variables=variable_dict
        )

        assert observed_df["test_binary"].dtype == "int64"
        assert observed_df["test_categorical"].dtype == "category"
        assert observed_df["test_int"].dtype == "int64"
        assert observed_df["test_date"].dtype == "category"
        assert observed_df["test_float"].dtype == "float64"
