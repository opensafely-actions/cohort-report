import datetime
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest
from pandas import testing

from cohortreport import processing
from cohortreport.errors import ImportActionError


class TestSuppressSmallNumbers:
    @staticmethod
    def column_factory(num_of_repeated_rows):
        expected_col = list([0, 1] * num_of_repeated_rows)
        return pd.Series(expected_col, dtype="float64")

    def test_has_small_numbers(self):
        col = self.column_factory(num_of_repeated_rows=5)
        res = processing.suppress_low_numbers(col)
        testing.assert_series_equal(res, pd.Series(dtype="float64"))

    def test_has_no_small_numbers(self):
        exp = self.column_factory(num_of_repeated_rows=6)
        obs = processing.suppress_low_numbers(exp)
        testing.assert_series_equal(obs, exp)


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
            "test_float": "float64",
        }
        observed_df = processing.type_variables_in_df(
            df=test_df, variables=variable_dict
        )

        assert observed_df["test_binary"].dtype == "int64"
        assert observed_df["test_categorical"].dtype == "category"
        assert observed_df["test_int"].dtype == "int64"
        assert observed_df["test_date"].dtype == "category"
        assert observed_df["test_float"].dtype == "float64"


class TestBinaryToCategorical:
    def test_change_binary_to_categorical(self):
        assert (
            processing.change_binary_to_categorical(pd.Series([0, 1])).dtype
            == "category"
        )

    def test_does_not_change_floats_to_categorical(self):
        assert (
            processing.change_binary_to_categorical(pd.Series([0.0, 1.0])).dtype
            == "float64"
        )

    def test_does_not_change_numeric_to_categorical(self):
        exp = pd.Series([1, 3])
        obs = processing.change_binary_to_categorical(exp)
        assert obs.equals(exp)
