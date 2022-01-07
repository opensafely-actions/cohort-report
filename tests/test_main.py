import json
import pathlib
import sys
from unittest import mock

from cohortreport import __main__


@mock.patch("cohortreport.__main__.run_action")
class TestMain:
    def test_with_config(self, mocked):
        config = {"output_path": "output", "variable_types": {}}
        input_files = ["output/input.csv"]

        test_args = ["", "--config", json.dumps(config)] + input_files
        with mock.patch.object(sys, "argv", test_args):
            __main__.main()

        mocked.assert_called_once_with(input_files=input_files, config=config)

    def test_without_config(self, mocked):
        with mock.patch.object(sys, "argv", ["", "output/input.feather"]):
            __main__.main()

        mocked.assert_called_once_with(
            input_files=["output/input.feather"],
            # Default config
            config={"output_path": "cohort_reports_outputs/", "variable_types": None},
        )


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
