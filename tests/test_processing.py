from pathlib import Path
from unittest import mock
import pandas as pd
from pandas import testing
import datetime as dt

import pytest

from cohortreport.errors import ImportActionError
from cohortreport.processing import load_study_cohort, suppress_low_numbers, check_columns_match, type_variables_in_df


class TestSuppressSmallNumbers:
    @staticmethod
    def column_factory(num_of_repeated_rows):
        expected_col = list([0, 1] * num_of_repeated_rows)
        return pd.Series(expected_col, dtype="float64")

    def test_has_small_numbers(self):
        col = self.column_factory(num_of_repeated_rows=5)
        res = suppress_low_numbers(col)
        testing.assert_series_equal(res, pd.Series(dtype="float64"))

    def test_has_no_small_numbers(self):
        col = self.column_factory(num_of_repeated_rows=6)
        res = suppress_low_numbers(col)
        testing.assert_series_equal(res, col)


class TestLoadStudyCohort:
    @mock.patch("cohortreport.processing.pd.read_csv")
    def test_csv(self, mock):
        f_in = Path("input.csv")
        load_study_cohort(f_in)
        mock.assert_called_once_with(f_in)

    @mock.patch("cohortreport.processing.pd.read_csv")
    def test_csv_gz(self, mock):
        f_in = Path("input.csv.gz")
        load_study_cohort(f_in)
        mock.assert_called_once_with(f_in, compression="gzip")

    @mock.patch("cohortreport.processing.pd.read_stata")
    def test_dta(self, mock):
        f_in = Path("input.dta")
        load_study_cohort(f_in)
        mock.assert_called_once_with(f_in, preserve_dtypes=False)

    @mock.patch("cohortreport.processing.pd.read_stata")
    def test_dta_gz(self, mock):
        with pytest.raises(NotImplementedError):
            load_study_cohort(Path("input.dta.gz"))

    @mock.patch("cohortreport.processing.pd.read_feather")
    def test_feather(self, mock):
        f_in = Path("input.feather")
        load_study_cohort(f_in)
        mock.assert_called_once_with(f_in)

    def test_unsupported_file_type(self):
        with pytest.raises(ImportActionError):
            load_study_cohort(Path("input.xlsx"))  # No chance!

class TestCheckColumnsMatch:
    @staticmethod
    def table_factory():
        return pd.DataFrame({"patient_id": [1, 2],
                                "copd": [1, 0],
                                "sex": ["male", "female"]})

    def test_columns_no_match(self):
        test_df = self.table_factory()
        with pytest.raises(AssertionError):
            check_columns_match(test_df, {"not_copd": "float64", "sex": "categorical"})

    def test_columns_with_match(self):
        expected_df = self.table_factory()
        observed_df = check_columns_match(expected_df, {"copd": "float64", "sex": "categorical"})
        testing.assert_frame_equal(observed_df, expected_df)


class TestTypeVariables:
    @staticmethod
    def table_factory():
        return pd.DataFrame({"patient_id": [1, 2],
                             "test_binary": [1, 0],
                             "test_categorical": ["male", "female"],
                             "test_int": [56, 65],
                             "test_date": [dt.datetime.now(), dt.datetime.now()],
                             "test_float": [1.2, 5.4]
                             })

    def test_type_variable_match(self):
        variable_dict = {
            "test_binary": "binary",
            "test_categorical": "categorical",
            "test_int": "int",
            "test_date": "date",
            "test_float": "float64"
        }
        test_df = self.table_factory()
        observed_df = type_variables_in_df(df=test_df, variables=variable_dict)

        assert observed_df['test_binary'].dtype == "int64"
        assert observed_df['test_categorical'].dtype == "category"
        assert observed_df['test_int'].dtype == "int64"
        assert observed_df['test_date'].dtype == "category"
        assert observed_df['test_float'].dtype == "float64"
