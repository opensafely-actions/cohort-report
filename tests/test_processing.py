from pathlib import Path
from unittest import mock

import pytest

from cohortreport.errors import ImportActionError
from cohortreport.processing import load_study_cohort


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
