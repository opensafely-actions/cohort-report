import itertools

import pandas as pd
import pytest

from cohortreport import report


@pytest.fixture
def path_to_input_csv(tmp_path):
    """Gets a `pathlib.Path` to an input CSV.

    The input CSV is similar to that generated by cohort-extractor from a study
    definition. It exists within a subdirectory of the default base temporary directory,
    which you can override by passing `--basetemp=my_basetemp` to `pytest`.
    """
    sex = {"M", "F"}
    age_band = {"0", "16-29"}
    has_copd = {0, 1}
    patient_records = pd.DataFrame(
        itertools.product(sex, age_band, has_copd),
        columns=("sex", "age_band", "has_copd"),
    )
    patient_records["patient_id"] = range(len(patient_records))

    path_to_input_csv = tmp_path / "input.csv"
    patient_records.to_csv(path_to_input_csv, index=False)

    return path_to_input_csv


def test_make_report(path_to_input_csv):
    """This is a smoke test: it's very coarse-grained and helps us to decide whether we
    should write more fine-grained tests."""
    path_to_output_dir = path_to_input_csv.parent
    report.make_report(
        path_to_input_csv,
        str(path_to_output_dir),
        {
            "sex": "categorical",
            "age_band": "categorical",
            "has_copd": "binary",
        },
    )
    assert (path_to_output_dir / f"descriptives_{path_to_input_csv.stem}.html").exists()
