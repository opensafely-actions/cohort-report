from pathlib import Path
from unittest import mock

import pytest

from cohort_report import errors, processing


class TestLoadStudyCohort:
    @mock.patch("cohort_report.processing.pd.read_csv")
    def test_csv(self, mock):
        f_in = Path("input.csv")
        processing.load_study_cohort(f_in)
        mock.assert_called_once_with(f_in)

    @mock.patch("cohort_report.processing.pd.read_csv")
    def test_csv_gz(self, mock):
        f_in = Path("input.csv.gz")
        processing.load_study_cohort(f_in)
        mock.assert_called_once_with(f_in, compression="gzip")

    @mock.patch("cohort_report.processing.pd.read_stata")
    def test_dta(self, mock):
        f_in = Path("input.dta")
        processing.load_study_cohort(f_in)
        mock.assert_called_once_with(f_in, preserve_dtypes=False)

    @mock.patch("cohort_report.processing.pd.read_stata")
    def test_dta_gz(self, mock):
        with pytest.raises(NotImplementedError):
            processing.load_study_cohort(Path("input.dta.gz"))

    @mock.patch("cohort_report.processing.pd.read_feather")
    def test_feather(self, mock):
        f_in = Path("input.feather")
        processing.load_study_cohort(f_in)
        mock.assert_called_once_with(f_in)

    def test_unsupported_file_type(self):
        with pytest.raises(errors.ImportActionError):
            processing.load_study_cohort(Path("input.xlsx"))  # No chance!
