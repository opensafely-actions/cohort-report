import pathlib
from unittest import mock

from cohortreport import __main__


@mock.patch("cohortreport.__main__.make_report")
def test_run_action(mocked):
    __main__.run_action(
        ["output/input.csv"],
        {"output_path": "output", "variable_types": None},
    )

    mocked.assert_called_once_with(
        path=pathlib.Path("output/input.csv"),
        output_dir="output",
        variable_types=None,
    )
