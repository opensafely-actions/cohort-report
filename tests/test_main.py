import errno
import pathlib
from unittest import mock

import pytest

from cohortreport import __main__


def test_convert_config_with_long_string():
    # It doesn't have to be a long JSON string; just a long string.
    long_string = "_" * 500
    with pytest.raises(OSError) as e:
        __main__.convert_config(long_string)
    assert e.value.errno == errno.ENAMETOOLONG


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
