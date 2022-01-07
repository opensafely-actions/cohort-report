import json
import pathlib
from unittest import mock

from cohortreport import __main__


class TestParseArgs:
    def test_with_config(self):
        config = {"output_path": "output", "variable_types": {}}
        input_files = ["output/input.csv"]
        test_args = ["--config", json.dumps(config)] + input_files
        args = __main__.parse_args(test_args)
        assert args.config == config
        assert args.input_files == input_files

    def test_without_config(self):
        input_files = ["output/input.csv"]
        args = __main__.parse_args(input_files)
        assert args.config is None
        assert args.input_files == input_files


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
