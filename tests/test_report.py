import pathlib

import pytest

from cohortreport import errors, report


@pytest.mark.parametrize(["ext"], [(".csv",), (".csv.gz",)])
def test_make_report_with_csv_file_but_without_variable_types(ext):
    with pytest.raises(errors.ConfigAndFileMismatchError):
        report.make_report(pathlib.Path(f"output/input{ext}"), "output", None)
